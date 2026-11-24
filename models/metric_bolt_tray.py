from pathlib import Path
import numpy as np, trimesh as tm, manifold3d as md
from shapely.geometry import box, LineString
from shapely.ops import unary_union
from xml.etree import ElementTree as E
import zipfile,json
out=Path(__file__).resolve().parents[1] / 'static/models/metric-bolt-tray'
def rounded(x,y,w,h,r):
 return box(x+r,y+r,x+w-r,y+h-r).buffer(r,quad_segs=10)
def section(p):
 polys=list(p.geoms) if p.geom_type=='MultiPolygon' else [p]
 from shapely.geometry.polygon import orient
 loops=[]
 for a in polys:
  a=orient(a,1)
  loops += [np.array(r.coords)[:-1] for r in [a.exterior,*a.interiors]]
 return md.CrossSection(loops)
def solid(p,z,h): return section(p).extrude(h).translate((0,0,z))
def mesh(m):
 a=m.to_mesh(); t=tm.Trimesh(a.vert_properties[:,:3],a.tri_verts)
 assert t.is_volume and t.is_watertight
 return t
deck=52.4
centers=[54,109,157,198.5]
body=solid(rounded(0,0,219,201,5),0,deck)
holes=[]
cutters=[]
for row in range(9):
 depth=10+5*row
 band=172-20*row
 for size,cx in enumerate(centers,3):
  radius=(size+1.0)/2
  pitch,count={3:(8,7),4:(10,5),5:(11.5,4),6:(13,3)}[size]
  for dy in (-5,5):
   n=count-int(dy<0 and size>=5)
   for i in range(n):
    x=cx+(i-(n-1)/2)*pitch
    y=band+dy
    holes.append((x,y,depth,radius))
    stem=md.Manifold.cylinder(depth-.4,radius,circular_segments=64)
    lip=md.Manifold.cylinder(.8,radius,radius+.8,circular_segments=64)
    cutters.append((stem+lip.translate((0,0,depth-.4))).translate((x,y,deck-depth)))
# Shallow recessed lines group each pair of subrows without lifting bolt heads.
for i in range(8):
 y=162-i*20
 cutters.append(solid(box(3,y-.5,216,y+.5),deck-.4,.8))
for x in (83,134.5,180):
 cutters.append(solid(box(x-.6,4,x+.6,182),deck-.4,.8))
body=body-md.Manifold.batch_boolean(cutters,md.OpType.Add)
# Engraver-style single stroke glyphs, rounded caps and joins.
paths={'M':[[(0,0),(0,6),(2.5,2.6),(5,6),(5,0)]],
'0':[[(.7,0),(2.1,0),(2.8,.8),(2.8,5.2),(2.1,6),(.7,6),(0,5.2),(0,.8),(.7,0)]],
'1':[[(0,4.9),(1.5,6),(1.5,0)],[(.2,0),(2.8,0)]],
'2':[[(0,5),(0.8,6),(2.1,6),(2.8,5.2),(2.8,4),(0,0),(2.8,0)]],
'3':[[(0,6),(2,6),(2.8,5.2),(2.8,3.8),(2,3),(0.8,3)],[(2,3),(2.8,2.2),(2.8,.8),(2,0),(0,0)]],
'4':[[(2.2,0),(2.2,6),(0,2.2),(3.1,2.2)]],
'5':[[(2.8,6),(0,6),(0,3.2),(2,3.2),(2.8,2.4),(2.8,.8),(2,0),(0,0)]],
'6':[[(2.6,6),(1.2,6),(0,4.8),(0,.8),(.8,0),(2,0),(2.8,.8),(2.8,2.5),(2,3.3),(0,3.3)]],
'm':[[(0,0),(0,3.1)],[(0,2.6),(.8,3.2),(1.6,2.6),(1.6,0)],[(1.6,2.6),(2.4,3.2),(3.2,2.6),(3.2,0)]]}
acc=[]
def label(s,cx,y,k,w):
 pieces=[]; offset=0
 for ch in s:
  for path in paths[ch]:
   pieces.append(LineString([(offset+a*k,b*k) for a,b in path]).buffer(w/2,quad_segs=5))
  offset+=max(a for path in paths[ch] for a,b in path)*k+w+1.1
 from shapely.affinity import translate
 g=unary_union(pieces); l,_,r,_=g.bounds
 acc.append(translate(g,cx-(l+r)/2,y))
for size,cx in enumerate(centers,3): label('M'+str(size),cx,189,1.10,1.6)
for row in range(9):
 label(str(10+5*row)+'mm',13,172-20*row-2.3,.78,1.1)
# Divider strokes separate adjacent diameter groups on the shared deck.
for x in (83,134.5,180):
 acc.append(box(x-.6,183,x+.6,197))
accent=solid(unary_union(acc),deck,.8)
parts=[mesh(body),mesh(accent)]; fused=mesh(body+accent)
assert len(fused.split())==1
fused.export(out/'metric-bolt-tray.stl')
root=E.Element('model',{'xmlns':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02','unit':'millimeter','xml:lang':'en-US'})
res=E.SubElement(root,'resources'); mat=E.SubElement(res,'basematerials',id='1')
colors=['#195B5B','#FFCB72']
for name,color in zip(['Deep teal','Amber'],colors): E.SubElement(mat,'base',name=name,displaycolor=color+'FF')
data=[]
for idx,t in enumerate(parts):
 obj=E.SubElement(res,'object',id=str(2+idx),type='model',name=['Tray','Raised markings'][idx],pid='1',pindex=str(idx))
 m=E.SubElement(obj,'mesh'); vs=E.SubElement(m,'vertices'); fs=E.SubElement(m,'triangles')
 for v in t.vertices: E.SubElement(vs,'vertex',**dict(zip('xyz',[f'{p:.6f}' for p in v])))
 for f in t.faces: E.SubElement(fs,'triangle',**dict(zip(['v1','v2','v3'],map(str,f))))
 data.append(dict(vertices=t.vertices.round(5).flatten().tolist(),faces=t.faces.flatten().tolist(),color=colors[idx]))
obj=E.SubElement(res,'object',id='4',type='model',name='Metric bolt tray'); comp=E.SubElement(obj,'components')
for i in ['2','3']: E.SubElement(comp,'component',objectid=i)
E.SubElement(E.SubElement(root,'build'),'item',objectid='4')
with zipfile.ZipFile(out/'metric-bolt-tray.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('3D/3dmodel.model',E.tostring(root,encoding='utf-8',xml_declaration=True))
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
(out/'geometry.json').write_text(json.dumps(data,separators=(',',':')))
print(fused.extents, len(fused.faces))
