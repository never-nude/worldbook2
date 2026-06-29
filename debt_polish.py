import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert 'glide between vertices' not in text, 'debt_polish already applied - aborting.'
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)
text=patch(text,
'''      const f=( phase + d/it.nDots + it.i*0.013 ) % 1;
      const idx=Math.min(it.pts.length-1, Math.floor(f*it.pts.length));
      const dc = it.two ? (idx<it.pts.length/2?F.fromColor:F.toColor) : it.dotCol;
      dots.push({type:"Feature",properties:{w:it.w,c:dc,from:it.from,to:it.to},geometry:{type:"Point",coordinates:it.pts[idx]}});''',
'''      const f=( phase + d/it.nDots + it.i*0.013 ) % 1;
      const fp=f*(it.pts.length-1), i0=Math.floor(fp), fr=fp-i0;          // glide between vertices (smooth)
      const a=it.pts[i0], b=it.pts[Math.min(i0+1,it.pts.length-1)];
      const co=[a[0]+(b[0]-a[0])*fr, a[1]+(b[1]-a[1])*fr];
      const dc = it.two ? (i0<it.pts.length/2?F.fromColor:F.toColor) : it.dotCol;
      dots.push({type:"Feature",properties:{w:it.w,c:dc,from:it.from,to:it.to},geometry:{type:"Point",coordinates:co}});''',
'dot-interp')
text=patch(text,
  '    if(t-lastDot>=33){                                     // dots at ~30fps, not 60 — halves the per-frame work',
  '    if(t-lastDot>=16){                                     // ~60fps dots — cheap now lines are cached; smooth glide',
  'dot-fps')
text=patch(text,
  '''    b+=`<div class="lg-row"><span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:${F.dotColor||'#cfe2ff'};margin:0 12px 0 9px"></span>direction of movement</div>`;''',
  '''    b+=`<div class="lg-row"><span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:${F.dotColor||'#cfe2ff'};margin:0 12px 0 9px"></span>direction of movement</div>`;
    if(F.baseColorProp){ b+=`<div class="lg-row" style="margin-top:8px;color:var(--muted);font-size:10.5px">Country shade — ${F.dir==="in"?"total owed":"total lent"}:</div>`+
      `<div class="lg-grad" style="background:linear-gradient(90deg,#1a2433,${F.color})"></div>`+
      `<div class="lg-scale"><span>none</span><span>most</span></div>`+
      `<div class="lg-row" style="color:var(--muted);font-size:10.5px;margin-top:5px;line-height:1.4">${F.dir==="in"?"Lenders (e.g. China) aren't shaded here — they're the arc origins. See \\u201cmoney lent out.\\u201d":"Borrowers aren't shaded here — they're where the arcs land. See \\u201cmoney owed.\\u201d"}</div>`; }''',
  'base-legend')
lines=text.split('\n')
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
META['layers']=[l for l in META['layers'] if l.get('key') not in ('debtorDebt','creditorDebt')]
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
print("OK: choropleths removed; dots glide @60fps; base-shade legend added")
