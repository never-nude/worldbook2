import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert '_atlasBoot' not in text, 'load_quality already applied - aborting.'
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)
text=patch(text,'''  // A few hand-fixes where bbox-centre lands badly (antimeridian / scattered isles)
  ISO_CENTROID.USA=[-98.5,39.5]; ISO_CENTROID.RUS=[94,62]; ISO_CENTROID.FRA=[2.5,46.5];
  ISO_CENTROID.NOR=[9,61]; ISO_CENTROID.NZL=[172,-41]; ISO_CENTROID.CHL=[-71,-35];''',
'''  Object.assign(ISO_CENTROID, {
    USA:[-98.5,39.5],RUS:[94,62],FRA:[2.5,46.5],NOR:[9,61],NZL:[172,-41],CHL:[-71,-35],
    NLD:[5.3,52.2],GBR:[-1.8,52.8],ESP:[-3.7,40.3],PRT:[-8,39.6],DNK:[9.5,56],DEU:[10.4,51.2],
    ITA:[12.5,42.8],GRC:[22,39.5],IRL:[-8,53.4],ISL:[-19,65],FIN:[26,64],SWE:[15,62],
    AUS:[134,-25],CAN:[-106,58],ECU:[-78.5,-1.4],FJI:[178,-17.7],KIR:[173,1.4],
    IDN:[118,-2.5],PHL:[122,12],MYS:[102,3.7],JPN:[138,37],KOR:[128,36.5],PRK:[127,40],
    IND:[79,22],CHN:[104,35.5],PAK:[69,30],SAU:[45,24],IRN:[53,32],IRQ:[44,33],ARE:[54,24],
    QAT:[51.2,25.3],KWT:[47.8,29.3],OMN:[57,21],YEM:[47,15.5],JOR:[36,31],LBN:[35.8,33.9],
    SYR:[38,35],ISR:[35,31.5],TUR:[35,39],
    ZAF:[25,-29],NGA:[8,9.5],EGY:[30,27],DZA:[3,28],LBY:[18,27],MAR:[-6,32],TUN:[9,34],
    AGO:[18,-12],COD:[23,-2.5],COG:[15,-1],GAB:[11.7,-0.6],CMR:[12,6],CIV:[-5.5,7.5],GHA:[-1,8],
    SEN:[-14.5,14.5],GIN:[-10,10.5],ETH:[39,9],KEN:[38,0.5],TZA:[35,-6],UGA:[32,1.3],ZMB:[27,-13],
    ZWE:[29,-19],MOZ:[35,-18],MDG:[47,-19],SDN:[30,15],SSD:[31,7],SOM:[46,5],TCD:[19,15],
    MLI:[-2,17],NER:[9,17],BFA:[-1.5,12],ERI:[39,15.5],BDI:[30,-3.4],CAF:[20,7],MRT:[-10,20],
    BRA:[-52,-10],ARG:[-64,-35],COL:[-73,4],PER:[-75,-9.5],VEN:[-66,7],BOL:[-65,-17],
    PRY:[-58,-23],URY:[-56,-33],GUY:[-59,5],SUR:[-56,4],MEX:[-102,23],GTM:[-90.5,15.5],
    HND:[-87,15],SLV:[-89,13.8],NIC:[-85,13],CRI:[-84,10],PAN:[-80,9],CUB:[-79,21.5],
    DOM:[-70.5,19],HTI:[-72.3,19],JAM:[-77.3,18.1],
    KAZ:[68,48],UZB:[63,41],TKM:[59,39],TJK:[71,38.5],KGZ:[75,41],MNG:[103,46],AFG:[66,34],
    NPL:[84,28],BTN:[90.4,27.4],BGD:[90,24],LKA:[80.7,7.9],MMR:[96,21],THA:[101,15],VNM:[106,16],
    KHM:[105,12.5],LAO:[103,18],SGP:[103.8,1.35],TWN:[121,23.7],HKG:[114.1,22.3],
    POL:[19,52],UKR:[31,49],CZE:[15.5,49.8],SVK:[19.5,48.7],HUN:[19,47],ROU:[25,46],BGR:[25,42.7],
    AUT:[14,47.6],CHE:[8,47],BEL:[4.5,50.6],LUX:[6.1,49.8],BLR:[28,53.5],SRB:[21,44],HRV:[16,45.4],
    BIH:[18,44],ALB:[20,41],MKD:[21.7,41.6],SVN:[15,46],LTU:[24,55],LVA:[25,57],EST:[26,59],
    MDA:[28.5,47],GEO:[43.5,42],ARM:[45,40],AZE:[48,40.3]
  });''','centroids')
text=patch(text,'map.on("load",()=>{ try{',
  'let _atlasBooted=false;\nfunction _atlasBoot(){ if(_atlasBooted) return; _atlasBooted=true; try{','boot-open')
text=patch(text,'''  startSpin();
  wireTimeBar(); updateTimeLabel();
  document.getElementById("loading").style.display="none";

  requestAnimationFrame(()=>{ try{''',
'''  wireTimeBar(); updateTimeLabel();
  let _revealed=false;
  const _reveal=()=>{ if(_revealed) return; _revealed=true;
    document.getElementById("loading").style.display="none";
    startSpin();
    requestAnimationFrame(()=>{ try{''','reveal-open')
text=patch(text,'''  }catch(e2){ console.error("Atlas deferred init:",e2); } });
  }catch(_e){ console.error("Atlas init error:",_e); }
  finally{ document.getElementById("loading").style.display="none"; }
});''',
'''  }catch(e2){ console.error("Atlas deferred init:",e2); } });
  };
  map.once("idle", _reveal); setTimeout(_reveal, 4500);
  }catch(_e){ console.error("Atlas init error:",_e); document.getElementById("loading").style.display="none"; }
}
if(map.isStyleLoaded()) _atlasBoot(); else map.on("load", _atlasBoot);
{ let _w=0; const _wi=setInterval(function(){ if(_atlasBooted||_w++>40){ clearInterval(_wi); return; } if(map.isStyleLoaded()) _atlasBoot(); }, 250); }''','reveal-close')
open(OUT,"w",encoding="utf-8").write(text)
print("OK: paint-gated reveal + robust boot + centroid table")
