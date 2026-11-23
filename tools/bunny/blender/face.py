import bpy, sys, os
sys.path.append(os.path.dirname(__file__)); import rlib
a = sys.argv[sys.argv.index('--')+1:]; bpy.ops.wm.open_mainfile(filepath=a[0])
sc = rlib.setup(600); sc.display.shading.color_type = 'SINGLE'
# ortho front of the head: 0.2 m wide centred at z 0.42 -> pixel (px,py) = x = (px-300)/3000, z = 0.42 - (py-300)/3000
rlib.shot(rlib.cam('F', (0, -2, 0.42), (0, 0, 0.42), ortho=0.2), a[1])
