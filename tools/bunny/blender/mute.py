# mute.py: run on an opened blend (blender -b <outdir>/bunny_example.blend --python mute.py); leaves only idle_up's NLA track unmuted, saves in place
import bpy
arm = bpy.data.objects['Armature']
for t in arm.animation_data.nla_tracks: t.mute = t.name != 'idle_up'
bpy.ops.wm.save_mainfile(compress=True)
print('MUTED', [(t.name, t.mute) for t in arm.animation_data.nla_tracks])
