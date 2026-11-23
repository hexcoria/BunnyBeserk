import sys
from PIL import Image
out = sys.argv[1]; rows = [r.split(',') for r in sys.argv[2:]]
ims = [[Image.open(p) for p in r] for r in rows]
w = max(sum(i.width for i in r) for r in ims); h = sum(r[0].height for r in ims)
s = Image.new('RGB', (w, h), 'white'); y = 0
for r in ims:
    x = 0
    for i in r: s.paste(i, (x, y)); x += i.width
    y += r[0].height
s.save(out)
