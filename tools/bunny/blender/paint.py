# paint.py <rig.blend> <out.blend> <tex.png> : PLACEHOLDER base-colour texture (Meshy refine was not run).
# Rasterises every UV triangle into a 1024 map and colours each texel from its rest-pose position, normal and dominant bone.
# Face features (eyes, nose) were measured from a front ortho render (renders/face_front.png).
import bpy, sys, os, json, numpy as np
a = sys.argv[sys.argv.index('--')+1:]; bpy.ops.wm.open_mainfile(filepath=a[0]); out, texp = a[1], a[2]
LM = json.load(open(a[0].replace('.blend', '_landmarks.json')))
o = bpy.data.objects['Body']; me = o.data; me.calc_loop_triangles(); N = 1024
names = {g.index: g.name for g in o.vertex_groups}
dom = [names[max(v.groups, key=lambda g: g.weight).group] if v.groups else '' for v in me.vertices]
uv = me.uv_layers.active.data
def srgb(c): return np.array(c, float)/255   # byte image: pixels are stored as sRGB
FUR, FURD, CREAM, PINK, NOSE, RED, WHITE, IRIS, PUPIL = [srgb(c) for c in ((214, 168, 122), (184, 134, 92), (248, 238, 218), (244, 176, 182), (226, 110, 132), (214, 36, 40), (255, 255, 255), (70, 45, 30), (14, 10, 10))]
zn, ze = LM['neck_z'], LM['ear_base_z']
EYES = [(-0.040, 0.413), (0.042, 0.415)]; NOSEP = (0.0, 0.386)
def colour(P, Nn, bone):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]; n = len(P)
    t = np.clip((z - 0.05) / 0.5, 0, 1)[:, None]; c = FUR*(1-t*0.25) + FURD*(t*0.25)
    c = np.broadcast_to(c, (n, 3)).copy()
    def put(m, col): c[m] = col
    head = bone == 'head'; ear = np.char.startswith(bone, 'ear'); front = Nn[:, 1] < -0.25
    # belly, muzzle/cheeks, paws, toes, tail: cream
    put((z > 0.08) & (z < zn + 0.01) & (Nn[:, 1] < -0.35) & (np.abs(x) < 0.075), CREAM)
    put(head & front & (((x/0.07)**2 + ((z-0.372)/0.034)**2) < 1), CREAM)
    put(np.char.startswith(bone, 'hand') | np.char.startswith(bone, 'toe') | (bone == 'tail'), CREAM)
    put(np.char.startswith(bone, 'foot') & (z < 0.02), CREAM)
    # inner ears
    put(ear & (Nn[:, 1] < -0.3) & (z > ze + 0.01), PINK)
    # headband: a band around the head just under the ear roots, plus the knot on top
    put(head & (z > ze - 0.042) & (z < ze - 0.024), RED)
    put((np.abs(x) < 0.018) & (z > ze - 0.012) & (np.abs(y) < 0.03) & ~ear, RED)
    # eyes
    for ex, ez in EYES:
        m = head & (y < -0.04)
        d = ((x-ex)/0.017)**2 + ((z-ez)/0.023)**2
        put(m & (d < 1), WHITE)
        ix = ex - np.sign(ex)*0.004; di = ((x-ix)/0.011)**2 + ((z-ez+0.002)/0.015)**2
        put(m & (di < 1), IRIS); put(m & (di < 0.4), PUPIL)
        dh = ((x-(ix+0.004))/0.0045)**2 + ((z-(ez+0.006))/0.0045)**2
        put(m & (dh < 1), WHITE)
    dn = ((x-NOSEP[0])/0.014)**2 + ((z-NOSEP[1])/0.01)**2
    put(head & (y < -0.07) & (dn < 1), NOSE)
    return c
img = np.zeros((N, N, 3)); fill = np.zeros((N, N), bool)
V = np.array([v.co for v in me.vertices]); VN = np.array([v.normal for v in me.vertices]); D = np.array(dom)
for tri in me.loop_triangles:
    U = np.array([uv[l].uv for l in tri.loops]) * N - 0.5
    x0, y0 = np.floor(U.min(0)).astype(int); x1, y1 = np.ceil(U.max(0)).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, N-1), min(y1, N-1)
    if x1 < x0 or y1 < y0: continue
    gx, gy = np.meshgrid(np.arange(x0, x1+1), np.arange(y0, y1+1)); G = np.stack([gx.ravel(), gy.ravel()], 1).astype(float)
    A, B, C = U; den = (B[1]-C[1])*(A[0]-C[0]) + (C[0]-B[0])*(A[1]-C[1])
    if abs(den) < 1e-12: continue
    w0 = ((B[1]-C[1])*(G[:, 0]-C[0]) + (C[0]-B[0])*(G[:, 1]-C[1])) / den
    w1 = ((C[1]-A[1])*(G[:, 0]-C[0]) + (A[0]-C[0])*(G[:, 1]-C[1])) / den; w2 = 1 - w0 - w1
    m = (w0 > -0.02) & (w1 > -0.02) & (w2 > -0.02)
    if not m.any(): continue
    W = np.stack([w0[m], w1[m], w2[m]], 1); vi = list(tri.vertices)
    P = W @ V[vi]; Nn = W @ VN[vi]; Nn /= np.linalg.norm(Nn, axis=1, keepdims=True) + 1e-9
    bone = D[vi][np.argmax(W, 1)]
    g = G[m].astype(int); img[g[:, 1], g[:, 0]] = colour(P, Nn, bone); fill[g[:, 1], g[:, 0]] = True
print('texels filled %.1f%%' % (100*fill.mean()))
for _ in range(8):   # dilate into the gutters so mip-maps and seams do not bleed black
    ys, xs = np.where(~fill); acc = np.zeros((len(ys), 3)); cnt = np.zeros(len(ys))
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        yy, xx = np.clip(ys+dy, 0, N-1), np.clip(xs+dx, 0, N-1); f = fill[yy, xx]
        acc[f] += img[yy[f], xx[f]]; cnt[f] += 1
    k = cnt > 0; img[ys[k], xs[k]] = acc[k] / cnt[k][:, None]; fill[ys[k], xs[k]] = True
im = bpy.data.images.new('bunny_basecolor', N, N, alpha=False)
px = np.concatenate([img, np.ones((N, N, 1))], 2).astype(np.float32)
im.pixels.foreach_set(px.ravel()); im.filepath_raw = texp; im.file_format = 'PNG'; im.save()
im.pack()
mat = bpy.data.materials.new('Bunny'); mat.use_nodes = True; nt = mat.node_tree
bs = nt.nodes['Principled BSDF']; tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = im
nt.links.new(tx.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.85; bs.inputs['Metallic'].default_value = 0.0
me.materials.clear(); me.materials.append(mat)
bpy.ops.wm.save_as_mainfile(filepath=out)
