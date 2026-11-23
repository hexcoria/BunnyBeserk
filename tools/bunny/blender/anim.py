# anim.py <painted.blend> <out.blend> : bakes every clip (30 fps, in place) as its own Action + NLA track
import bpy, sys, os, json, math
from mathutils import Vector as V
sys.path.append(os.path.dirname(__file__)); import posekit as K, poses as P
a = sys.argv[sys.argv.index('--')+1:]; bpy.ops.wm.open_mainfile(filepath=a[0]); out = a[1]
arm = bpy.data.objects['BunnyRig']; K.init(arm); P.init(json.load(open(a[0].replace('painted', 'rig').replace('.blend', '_landmarks.json'))))
FPS = 30; sc = bpy.context.scene; sc.render.fps = FPS
TAU = 2*math.pi; S = math.sin; C = math.cos
def bump(t, c, w):   # smooth 0..1..0 pulse centred on c, half-width w (periodic in t)
    d = (t - c + 0.5) % 1 - 0.5
    return 0.5*(1 + C(math.pi*d/w)) if abs(d) < w else 0.0
def ease(t): return t*t*(3 - 2*t)
def addr(sp, bone, r):
    o = sp['rot'].get(bone, (0, 0, 0)); sp['rot'][bone] = tuple(x + y for x, y in zip(o, r))
def offs(pts, d): return tuple(p + V(d) for p in pts)
# ---------- clip pose functions: t in [0,1] ----------
def idle_up(t):
    b = S(TAU*2*t); sp = P.up(breath=b, crouch=0.15 + 0.25*(0.5 + 0.5*S(TAU*2*t - 1.2)))
    tw = bump(t, 0.55, 0.05) - 0.6*bump(t, 0.62, 0.04)    # left ear twitch
    addr(sp, 'ear_L_02', (-35*tw, 0, 12*tw)); addr(sp, 'ear_L_01', (-8*tw, 0, 0))
    addr(sp, 'ear_R_02', (-10*bump(t, 0.85, 0.05), 0, 0))
    addr(sp, 'head', (0, 0, 4*S(TAU*t))); addr(sp, 'tail', (10*S(TAU*2*t), 0, 0))
    addr(sp, 'ear_L_01', (0, 0, 3*S(TAU*t))); addr(sp, 'ear_R_01', (0, 0, -3*S(TAU*t + 1)))
    return sp
def aim_up(t, recoil=0.0):
    b = 0.5*S(TAU*t); sp = P.up(breath=b, crouch=0.6, aimw=1)
    for s in 'LR':
        w, tp, spc = sp['hands'][s]; d = V((0, 0.035*recoil, 0.025*recoil)); sp['hands'][s] = (w + d, tp + d + V((0, 0, 0.012*recoil)), spc)
    addr(sp, 'spine_03', (-15*recoil, 0, 0)); addr(sp, 'spine_02', (-5*recoil, 0, 0)); addr(sp, 'hips', (-3*recoil, 0, 0)); addr(sp, 'head', (-10*recoil, 0, 0)); addr(sp, 'neck', (-4*recoil, 0, 0))
    for s in 'LR': addr(sp, 'ear_%s_01' % s, (-12 + 18*recoil, 0, 0)); addr(sp, 'ear_%s_02' % s, (-6 + 14*recoil, 0, 0))
    sp['root'] = tuple(x + y for x, y in zip(sp['root'], (0, 0.006*recoil, -0.004*recoil)))
    return sp
def fire_up(t):
    k = (t/0.12) if t < 0.12 else math.exp(-(t - 0.12)*7) * (1 - (t - 0.12)/0.88)**0.5 * C(TAU*1.2*(t - 0.12))
    k = k if t < 0.12 else k*(1 - ease(min(1, (t - 0.12)/0.88)))
    return aim_up(0.0, recoil=k) if t < 1 else aim_up(0.0)
def strafe_up(t):
    sp = aim_up(t)
    for s, ph in (('L', 0), ('R', 0.5)):
        u = (t + ph) % 1; sw = 0.018*S(TAU*u); lift = 0.016*max(0, S(TAU*u + math.pi/2))**1.5
        sp['feet'][s] = offs(sp['feet'][s], (sw, 0, lift))
    sp['root'] = tuple(x + y for x, y in zip(sp['root'], (0.008*S(TAU*t), 0, -0.004*abs(C(TAU*t)))))
    addr(sp, 'hips', (0, 0, 5*S(TAU*t))); addr(sp, 'spine_02', (0, 0, -3*S(TAU*t))); addr(sp, 'hips', (0, -4*S(TAU*t), 0))
    addr(sp, 'tail', (0, 0, -15*S(TAU*t)))
    return sp
def idle_fours(t):
    b = S(TAU*2*t); sp = P.fours(breath=b, look=4*S(TAU*t))
    addr(sp, 'head', (0, 0, 6*S(TAU*t)))
    tw = bump(t, 0.3, 0.05); addr(sp, 'ear_R_02', (-30*tw, 0, -10*tw)); addr(sp, 'ear_R_01', (-6*tw, 0, 0))
    addr(sp, 'tail', (25*bump(t, 0.7, 0.06), 0, 0))
    sp['root'] = tuple(x + y for x, y in zip(sp['root'], (0, 0, 0.002*b)))
    return sp
def gait(t, A, flight, flex, ph_lr=0.06, hind_lift=0.03, front_lift=0.035):
    """Rabbit bound in place. Hind feet: stance 0..0.40 sweeping back, swing after. Flight ~0.40..0.58. Front paws: stance 0.58..0.92."""
    sp = P.fours(); rz = 0
    for s, dph in (('L', 0), ('R', ph_lr)):
        u = (t - dph) % 1
        if u < 0.40: hy, hz = -A + 2*A*(u/0.40), 0
        else: v = (u - 0.40)/0.60; hy, hz = A - 2*A*ease(v), hind_lift*S(math.pi*v)
        sp['feet'][s] = offs(sp['feet'][s], (0, hy, hz))
        w = (u - 0.58) % 1
        if w < 0.34: fy, fz = -A + 2*A*(w/0.34), 0
        else: v = (w - 0.34)/0.66; fy, fz = A - 2*A*ease(v), front_lift*S(math.pi*v)
        wpt, tpt, spc = sp['hands'][s]; sp['hands'][s] = (wpt + V((0, fy, fz)), tpt + V((0, fy, fz*0.6)), spc)
    up = flight*bump(t, 0.49, 0.13); ext = S(TAU*(t - 0.25))     # ext > 0: stretched out, < 0: gathered
    sp['root'] = tuple(x + y for x, y in zip(sp['root'], (0, 0, up)))
    addr(sp, 'hips', (-3*ext*flex - 2*bump(t, 0.35, 0.15) + 4*bump(t, 0.7, 0.12), 0, 0))
    addr(sp, 'spine_01', (-3*ext*flex, 0, 0)); addr(sp, 'spine_02', (-2.5*ext*flex, 0, 0)); addr(sp, 'spine_03', (2*ext*flex, 0, 0))
    addr(sp, 'neck', (6*ext*flex, 0, 0)); addr(sp, 'head', (-4*bump(t, 0.75, 0.15)*flex, 0, 0))
    for s in 'LR':   # ears trail the bounce
        addr(sp, 'ear_%s_01' % s, (-10*S(TAU*(t - 0.15))*flex, 0, 0)); addr(sp, 'ear_%s_02' % s, (-14*S(TAU*(t - 0.3))*flex, 0, 0))
    addr(sp, 'tail', (20*S(TAU*(t - 0.1)), 0, 0))
    return sp
def hop(t): return gait(t, A=0.03, flight=0.03, flex=1.0)
def run(t): return gait(t, A=0.05, flight=0.045, flex=1.5, ph_lr=0.08, hind_lift=0.04, front_lift=0.045)
CLIPS = [('idle_up', 2.0, idle_up, True), ('aim_up', 1.0, aim_up, True), ('fire_up', 0.4, fire_up, False),
         ('strafe_up', 0.8, strafe_up, True), ('idle_fours', 2.0, idle_fours, True),
         ('hop', 0.5, hop, True), ('run', 0.4, run, True)]
TRANS = [('drop_to_fours', 0.267, idle_up, idle_fours), ('rise_to_up', 0.267, idle_fours, idle_up)]
ad = arm.animation_data_create(); info = {}
def bake(name, frames, posefn):
    # Solve every frame first with no action and every NLA track muted: an active action or track is
    # evaluated on each depsgraph update and would overwrite the pose mid-solve.
    ad.action = None
    for tr in ad.nla_tracks: tr.mute = True
    poses = [posefn(f / frames) for f in range(frames + 1)]
    act = bpy.data.actions.new(name); act.use_fake_user = True; ad.action = act
    prev = {}
    for f, (q, loc) in enumerate(poses):
        for n, v in q.items():
            if n in prev and prev[n].dot(v) < 0: v = -v.copy()
            prev[n] = v; pb = arm.pose.bones[n]; pb.rotation_quaternion = v
            pb.keyframe_insert('rotation_quaternion', frame=f, group=n)
        arm.pose.bones['root'].location = loc; arm.pose.bones['root'].keyframe_insert('location', frame=f, group='root')
    for fc in K.fcurves(act) if hasattr(K, 'fcurves') else act.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    tr = ad.nla_tracks.new(); tr.name = name; st = tr.strips.new(name, 0, act); st.name = name
    ad.action = None
    info[name] = dict(frames=frames, seconds=round(frames / FPS, 3))
for name, dur, fn, loop in CLIPS:
    n = round(dur*FPS)
    if name == 'fire_up': bake(name, n, lambda t: K.solve(fire_up(t) if t < 1 else aim_up(0)))
    else: bake(name, n, lambda t, fn=fn: K.solve(fn(t)))
    info[name]['loop'] = loop
for name, dur, fa, fb in TRANS:
    n = round(dur*FPS); ad.action = None
    for tr in ad.nla_tracks: tr.mute = True
    A = K.solve(fa(0)); B = K.solve(fb(0))
    def tf(t, A=A, B=B, name=name):
        q, l = K.blend(A, B, ease(t))
        # a little anticipation: ears flop and the body dips mid-way
        return q, l + V((0, 0, -0.012*math.sin(math.pi*t)))
    bake(name, n, tf); info[name]['loop'] = False
for tr in ad.nla_tracks: tr.mute = False
K.reset(); K.upd()
json.dump(info, open(out.replace('.blend', '_clips.json'), 'w'), indent=1)
print('CLIPS', json.dumps(info))
bpy.ops.wm.save_as_mainfile(filepath=out)
