# Poll a Meshy text-to-3d task (preview or refine) and download everything: model.glb/.fbx, thumb.png, tex0_*.png maps, task json (signed URLs only, no key).
# set -a; . ~/.config/hexcoria/meshy.env; set +a
# python3 -I tools/bunny/meshy/meshy_dl.py <task id> <out dir>      (re-run to re-poll if a map is missing; exits 2 if refine lacks emission/normal)
import sys, os, json, time, urllib.request
tid, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers={'Authorization': 'Bearer ' + os.environ['MESHY_API_KEY']})).read()
for _ in range(180):
    d = json.loads(get('https://api.meshy.ai/openapi/v2/text-to-3d/' + tid)); print(d['status'], d.get('progress'), flush=True)
    if d['status'] in ('SUCCEEDED', 'FAILED', 'CANCELED'): break
    time.sleep(10)
json.dump(d, open(os.path.join(out, 'text-to-3d_task.json'), 'w'), indent=1)
if d['status'] != 'SUCCEEDED': print(d.get('task_error')); sys.exit(1)
def save(u, n): open(os.path.join(out, n), 'wb').write(urllib.request.urlopen(u).read()); print('saved', n)
for k, v in d['model_urls'].items():
    if k in ('glb', 'fbx'): save(v, 'model.' + k)
if d.get('thumbnail_url'): save(d['thumbnail_url'], 'thumb.png')
got = set()
for i, t in enumerate(d.get('texture_urls') or []):
    for k, v in t.items():
        if v: save(v, 'tex%d_%s.png' % (i, k)); got.add(k)
if d.get('mode', 'refine') == 'refine' or d.get('texture_urls'):
    miss = {'base_color', 'normal', 'emission'} - got
    if miss: print('MISSING maps:', sorted(miss)); sys.exit(2)
