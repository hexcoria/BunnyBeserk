import bpy, random
from mathutils import Vector
def sample(o, n=150000, seed=1):
    me = o.data; me.calc_loop_triangles(); rnd = random.Random(seed)
    tris = [(me.vertices[t.vertices[0]].co, me.vertices[t.vertices[1]].co, me.vertices[t.vertices[2]].co, t.area) for t in me.loop_triangles]
    tot = sum(t[3] for t in tris); pts = []
    for a, b, c, ar in tris:
        k = ar / tot * n; m = int(k) + (1 if rnd.random() < k - int(k) else 0)
        for _ in range(m):
            u, v = rnd.random(), rnd.random()
            if u + v > 1: u, v = 1-u, 1-v
            pts.append(a + (b-a)*u + (c-a)*v)
    return pts
def runs(vals, b=0.004, minn=4):
    import collections
    c = collections.Counter(int((x+2)//b) for x in vals)
    ks = sorted(k for k, n in c.items() if n >= minn); out = []
    for k in ks:
        if out and k - out[-1][1] <= 1: out[-1][1] = k
        else: out.append([k, k])
    return [(round(s*b-2, 3), round((e+1)*b-2, 3)) for s, e in out]
