# Pose specs for the two stances, built from the rig's landmarks.
import math
from mathutils import Vector as V
LM = None
def init(lm):
    global LM; LM = lm
def leg(s): g = LM['leg_'+s]; return V(g['ankle']), V(g['ball']), V(g['tip'])
def armw(s): m = LM['arm_'+s]; return V(m['wrist']), V(m['tip'])
def up(t=0.0, breath=0.0, crouch=0.0, aimw=0.0, sway=0.0):
    """Upright: on the hind legs, front paws as hands. aimw blends the arms to a two-handed aim in front."""
    feet = {s: leg(s) for s in 'LR'}
    hands = {}
    for s, sg in (('L', 1), ('R', -1)):
        w, tp = armw(s)
        rel = V((sg*0.125, -0.03, 0.225)); relt = V((sg*0.14, -0.055, 0.205))   # relaxed: paws a bit lower and forward
        aw = V((sg*0.035, -0.085 - (0.01 if s == 'L' else 0), 0.262)); at = V((sg*0.012, -0.115, 0.265))
        hands[s] = (rel.lerp(aw, aimw), relt.lerp(at, aimw), 'chest')
    b = breath
    rot = {'hips': (-2 + 2*crouch, sway, 0), 'spine_01': (2 + 1.5*b, 0, 0), 'spine_02': (1.5*b, 0, 0), 'spine_03': (-2 - 2.5*b - 4*aimw, 0, 0),
           'neck': (0, 0, 0), 'head': (2 - 1*b + 3*aimw, 0, 0),
           'ear_L_01': (-3*b, 0, 0), 'ear_R_01': (-3*b, 0, 0)}
    return dict(root=(0, 0, -0.008*crouch - 0.002*b), rot=rot, feet=feet, hands=hands)
def fours(breath=0.0, pitch=0.0, look=0.0):
    """On all fours: body pitched forward ~90 degrees, front paws on the ground under the shoulders."""
    feet = {}
    for s in 'LR':
        a, bl, tp = leg(s)
        # haunches down: heel on the ground, foot flat a little behind its rest place
        dy = 0.03
        feet[s] = (V((a.x, a.y + dy + 0.03, 0.03)), V((bl.x, bl.y + dy, 0.012)), V((tp.x, tp.y + dy, 0.010)))
    hands = {}
    for s, sg in (('L', 1), ('R', -1)):
        hands[s] = (V((sg*0.07, -0.20, 0.03)), V((sg*0.075, -0.235, 0.006)), 'world')
    p = pitch; b = breath
    rot = {'hips': (38 + p, 0, 0), 'spine_01': (20 + 0.5*p + 1.5*b, 0, 0), 'spine_02': (18 + 1.5*b, 0, 0), 'spine_03': (12 - 2*b, 0, 0),
           'neck': (-45 - 0.5*p, 0, 0), 'head': (-35 - 0.5*p + look, 0, 0),
           'ear_L_01': (-20, 0, 0), 'ear_R_01': (-20, 0, 0), 'ear_L_02': (-10, 0, 0), 'ear_R_02': (-10, 0, 0),
           'tail': (-30, 0, 0)}
    return dict(root=(0, 0.02, -0.045), rot=rot, feet=feet, hands=hands, knee_pole={'L': (0.3, -1, 0.6), 'R': (-0.3, -1, 0.6)},
                elbow_pole={'L': (0.4, 1, 0.2), 'R': (-0.4, 1, 0.2)})
