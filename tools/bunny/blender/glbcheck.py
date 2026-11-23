import json, struct, sys, io
d = open(sys.argv[1], 'rb').read(); assert d[:4] == b'glTF'
L = struct.unpack('<I', d[12:16])[0]; J = json.loads(d[20:20+L]); binoff = 20 + L + 8; B = d[binoff:]
print('nodes', len(J['nodes']), 'meshes', len(J['meshes']), 'skins', len(J['skins']), 'cameras', len(J.get('cameras', [])), 'lights', 'KHR_lights_punctual' in json.dumps(J.get('extensions', {})))
sk = J['skins'][0]; print('joints', len(sk['joints'])); print('bone names', [J['nodes'][j]['name'] for j in sk['joints']])
tris = 0
for m in J['meshes']:
    for p in m['primitives']:
        acc = J['accessors'][p['indices']]; tris += acc['count'] // 3
        pos = J['accessors'][p['attributes']['POSITION']]; print('POSITION min', [round(x, 3) for x in pos['min']], 'max', [round(x, 3) for x in pos['max']], 'attrs', sorted(p['attributes']))
print('triangles', tris)
for im in J.get('images', []):
    bv = J['bufferViews'][im['bufferView']]; png = B[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]
    w, h = struct.unpack('>II', png[16:24]); print('image', im.get('name'), im['mimeType'], w, 'x', h, 'embedded')
for mt in J['materials']: print('material', mt['name'], list(mt.get('pbrMetallicRoughness', {}).keys()))
for an in J['animations']:
    tmax = max(J['accessors'][s['input']]['max'][0] for s in an['samplers'])
    print('clip %-14s %.3f s  channels %d' % (an['name'], tmax, len(an['channels'])))
# facing: nose = vertex with the largest z among those at head height
import array
pos = J['accessors'][J['meshes'][0]['primitives'][0]['attributes']['POSITION']]; bv = J['bufferViews'][pos['bufferView']]
o = bv.get('byteOffset', 0) + pos.get('byteOffset', 0); arr = array.array('f', B[o:o + pos['count']*12])
pts = [arr[i:i+3] for i in range(0, len(arr), 3)]
head = [p for p in pts if 0.33 < p[1] < 0.45]
print('front of head z max %.3f vs back z min %.3f (character faces +Z if |max| > |min|)' % (max(p[2] for p in head), min(p[2] for p in head)))
