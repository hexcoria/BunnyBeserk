# Pose solver: spec -> per-bone local quaternions. Character faces -Y, left = +X, up = +Z (Blender).
# Rotations are degrees about the armature's axes (rx > 0 pitches an upright bone forward), composed down chains.
import bpy, math
from mathutils import Vector as V, Euler, Quaternion, Matrix
ARM = None
def init(arm): 
    global ARM; ARM = arm
def upd(): bpy.context.view_layer.update()
def reset():
    for pb in ARM.pose.bones:
        pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
def rot(name, r):
    if not r: return
    b = ARM.data.bones[name]; R = b.matrix_local.to_quaternion()
    Q = Euler([math.radians(x) for x in r], 'XYZ').to_quaternion()
    ARM.pose.bones[name].rotation_quaternion = R.inverted() @ Q @ R
def aim(name, target):
    pb = ARM.pose.bones[name]; h = pb.head.copy(); cur = pb.tail - h; des = V(target) - h
    if des.length < 1e-6: return
    q = cur.rotation_difference(des)
    pb.matrix = Matrix.Translation(h) @ q.to_matrix().to_4x4() @ Matrix.Translation(-h) @ pb.matrix
    upd()
def ik2(up, lo, target, pole):
    pu = ARM.pose.bones[up]; S = pu.head.copy(); l1 = ARM.data.bones[up].length; l2 = ARM.data.bones[lo].length
    T = V(target); d = T - S; dl = min(d.length, (l1 + l2) * 0.999); dl = max(dl, abs(l1 - l2) * 1.01 + 1e-4)
    dn = d.normalized(); a = (l1*l1 - l2*l2 + dl*dl) / (2*dl); h = math.sqrt(max(l1*l1 - a*a, 0))
    p = V(pole) - dn * V(pole).dot(dn); p = p.normalized() if p.length > 1e-6 else V((0, 0, 1))
    aim(up, S + dn*a + p*h); aim(lo, S + dn*dl)
def chest_pt(p):   # a rest-space point carried by spine_03
    b = ARM.data.bones['spine_03']; pb = ARM.pose.bones['spine_03']
    return pb.matrix @ (b.matrix_local.inverted() @ V(p))
CENTRAL = ['hips', 'spine_01', 'spine_02', 'spine_03', 'neck', 'head', 'ear_L_01', 'ear_L_02', 'ear_R_01', 'ear_R_02', 'tail', 'clavicle_L', 'clavicle_R']
def solve(spec):
    """spec: root=(x,y,z) offset, rootr=(rx,ry,rz), rot={bone:(rx,ry,rz)},
       feet={'L': (ankle, ball, tip)} world points, hands={'L': (wrist, tip, space)} space 'chest' or 'world',
       knee_pole, elbow_pole per side optional. Returns {bone: Quaternion}, root location."""
    reset()
    root = ARM.pose.bones['root']; rb = ARM.data.bones['root']; R = rb.matrix_local.to_3x3()
    root.location = R.inverted() @ V(spec.get('root', (0, 0, 0)))
    rot('root', spec.get('rootr'))
    for n, r in spec.get('rot', {}).items(): rot(n, r)
    upd()
    for s, sg in (('L', 1), ('R', -1)):
        f = spec['feet'][s]
        ik2('thigh_'+s, 'shin_'+s, f[0], spec.get('knee_pole', {}).get(s, (sg*0.2, -1, 0.3)))
        aim('foot_'+s, f[1]); aim('toe_'+s, f[2])
        hw, ht, sp = spec['hands'][s]
        if sp == 'chest': hw, ht = chest_pt(hw), chest_pt(ht)
        ik2('upperarm_'+s, 'forearm_'+s, hw, spec.get('elbow_pole', {}).get(s, (sg*0.6, 0.6, -0.4)))
        aim('hand_'+s, ht)
    out = {pb.name: pb.rotation_quaternion.copy() for pb in ARM.pose.bones}
    return out, root.location.copy()
def apply(q, loc):
    for n, v in q.items(): ARM.pose.bones[n].rotation_quaternion = v
    ARM.pose.bones['root'].location = loc; upd()
def blend(a, b, t):
    (qa, la), (qb, lb) = a, b
    return {n: qa[n].slerp(qb[n], t) for n in qa}, la.lerp(lb, t)
