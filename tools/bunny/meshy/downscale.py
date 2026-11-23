# downscale.py <refine dir> <texdir> : Meshy refine maps (2048) -> the 1024 maps retex.py loads
# (bunny_basecolor/normal/roughness.png). Lanczos; reproduces the shipped maps exactly. Needs Pillow.
import sys, os
from PIL import Image
src, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
for a, b in (('base_color', 'basecolor'), ('normal', 'normal'), ('roughness', 'roughness')):
    Image.open(os.path.join(src, 'tex0_%s.png' % a)).resize((1024, 1024), Image.LANCZOS).save(os.path.join(out, 'bunny_%s.png' % b))
    print('saved', 'bunny_%s.png' % b)
