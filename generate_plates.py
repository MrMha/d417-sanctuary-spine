"""A3 vector architectural plates, shared v7 geometry, physically 1:50 at 100%.
All stroked geometry is clipped against real font label extents before output.
This produces geometric stroke breaks, rather than hiding collisions with paint.
"""
from pathlib import Path
import sys,json,math,html,textwrap
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT.parent/'submission_2026-11-18/python_deps'))
from PIL import ImageFont
PAPER='#faf8f3';INK='#21483f';SAGE='#dce5db';GOLD='#ac8651';GREY='#d6d7d2'
NAMES=['master_plan','scenarios_plan','mobility_plan','transfer_plan','rcp_plan','section','observation_detail','elevations_organ_support','pod_context']
TITLES=['Coordinated room plan','Airway / CPR working state','West-side mobilisation','Prepared bed transfer','Reflected ceiling & services','Section A-A','Observation, dignity & telemetry','Four-wall elevations & organ support','Tower D pod context & adaptable cassette']
FONT=Path(r'C:\Windows\Fonts\arial.ttf');BOLD=Path(r'C:\Windows\Fonts\arialbd.ttf')

def load_spec(): return json.loads((ROOT/'master_spec.json').read_text(encoding='utf-8'))

def trim_segment(a,b,r):
 """Return visible parts of a segment outside rectangle r (Liang-Barsky)."""
 x,y=a;dx=b[0]-x;dy=b[1]-y;t0,t1=0.,1.
 for p,q in [(-dx,x-r[0]),(dx,r[2]-x),(-dy,y-r[1]),(dy,r[3]-y)]:
  if abs(p)<1e-12:
   if q<0:return [(a,b)]
  else:
   t=q/p
   if p<0:t0=max(t0,t)
   else:t1=min(t1,t)
   if t0>t1:return [(a,b)]
 pieces=[]
 if t0>1e-8:pieces.append((a,(x+t0*dx,y+t0*dy)))
 if t1<1-1e-8:pieces.append(((x+t1*dx,y+t1*dy),b))
 return pieces

class Plate:
 def __init__(self,n,title,scale='1:50 at A3 / 100%'):
  self.n=n;self.title=title;self.scale=scale;self.fills=[];self.lines=[];self.labels=[];self.boxes=[];self.geometry_receipt={}
  self.text(64,54,'THE SANCTUARY SPINE  /  ROOM D417 - 044044  /  SSMC TOWER D LEVEL 4',15,bold=True)
  self.text(64,104,f'A{n}  |  {title}',30,bold=True)
  self.text(64,140,f'{scale}   |   All dimensions mm; local room axes X east, Y north, Z AFFL',14)
  self.line(64,164,1616,164,width=1.2)
  self.line(64,1118,1616,1118,width=1.2)
  self.text(64,1150,'MUSTAFA HISHAM ALI  /  KHALIFA UNIVERSITY  /  v7 DESIGN COORDINATION',12)
  self.text(1616,1150,f'A{n} / A9',12,anchor='end',bold=True)
 def line(self,x1,y1,x2,y2,color=INK,width=1,dash=None):self.lines.append(((x1,y1),(x2,y2),color,width,dash))
 def poly(self,pts,fill=None,color=INK,width=1,closed=True,dash=None):
  if fill:self.fills.append(f'<polygon points="{" ".join(f"{x:.3f},{y:.3f}" for x,y in pts)}" fill="{fill}"/>')
  for a,b in zip(pts,pts[1:]+(pts[:1] if closed else [])):self.line(*a,*b,color,width,dash)
 def rect(self,x,y,w,h,fill=None,color=INK,width=1):self.poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill,color,width)
 def ellipse(self,cx,cy,rx,ry,color=INK,width=1,fill=None,dash=None):
  pts=[(cx+rx*math.cos(i*math.tau/96),cy+ry*math.sin(i*math.tau/96)) for i in range(96)]
  self.poly(pts,fill,color,width,True,dash)
 def text(self,x,y,s,size=13,bold=False,anchor='start',color=INK,halo=True):
  # Font measurement is independent of SVG rendering; safety halo adds 5px.
  f=ImageFont.truetype(str(BOLD if bold else FONT),round(size*8))
  width=f.getlength(s)/8
  left=x-(width/2 if anchor=='middle' else width if anchor=='end' else 0)
  box=[left-4,y-size-4,left+width+4,y+5]
  self.labels.append((x,y,s,size,bold,anchor,color,box,halo));self.boxes.append(box)
 def paragraph(self,x,y,s,width=500,size=14,color=INK,leading=None):
  leading=leading or size*1.6
  words=s.split();row='';f=ImageFont.truetype(str(FONT),round(size*8))
  for word in words:
   test=(row+' '+word).strip()
   if f.getlength(test)/8>width and row:self.text(x,y,row,size,color=color);y+=leading;row=word
   else:row=test
  if row:self.text(x,y,row,size,color=color);y+=leading
  return y
 def dimh(self,a,b,y,label):
  self.line(a,y,b,y,width=.8)
  for x in [a,b]:self.line(x,y-10,x,y+12,width=.6);self.line(x-4,y+4,x+4,y-4,width=1.2)
  self.text((a+b)/2,y-10,label,12,anchor='middle')
 def dimv(self,x,a,b,label):
  self.line(x,a,x,b,width=.8)
  for y in [a,b]:self.line(x-10,y,x+10,y,width=.6);self.line(x-4,y+4,x+4,y-4,width=1.2)
  self.text(x-14,(a+b)/2+4,label,12,anchor='end')
 def arrow(self,a,b,color=INK,width=1.2,dash=None):
  self.line(*a,*b,color,width,dash);dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy) or 1;ux,uy=dx/l,dy/l
  for s in [-1,1]:self.line(*b,b[0]-ux*9+s*uy*4,b[1]-uy*9-s*ux*4,color,width)
 def note(self,x,y,title,body,width=600):
  self.text(x,y,title,16,True);return self.paragraph(x,y+27,body,width,14)+21
 def save(self,name):
  strokes=[]
  for a,b,col,width,dash in self.lines:
   pieces=[(a,b)]
   for rect in self.boxes:
    expanded=[rect[0]-width/2-1,rect[1]-width/2-1,rect[2]+width/2+1,rect[3]+width/2+1]
    pieces=[sub for p,q in pieces for sub in trim_segment(p,q,expanded)]
    if not pieces:break
   for p,q in pieces:
    if math.dist(p,q)<.2:continue
    dashattr=f' stroke-dasharray="{dash}"' if dash else ''
    strokes.append(f'<line x1="{p[0]:.4f}" y1="{p[1]:.4f}" x2="{q[0]:.4f}" y2="{q[1]:.4f}" stroke="{col}" stroke-width="{width}"{dashattr}/>')
  labels=[]
  for x,y,s,size,bold,anchor,col,box,halo in self.labels:
   rgb=tuple(int(col.lstrip('#')[i:i+2],16) for i in [0,2,4]);bg=INK if sum(rgb)>570 else PAPER
   if halo:labels.append(f'<rect data-background="label" x="{box[0]:.4f}" y="{box[1]:.4f}" width="{box[2]-box[0]:.4f}" height="{box[3]-box[1]:.4f}" rx="3" fill="{bg}" fill-opacity="0.96"/>')
   labels.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{col}">{html.escape(s)}</text>')
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 1680 1188" role="img" aria-label="Appendix A{self.n}: {html.escape(self.title)}"><title>Appendix A{self.n}: {html.escape(self.title)}</title><metadata id="geometry-receipt">{html.escape(json.dumps(self.geometry_receipt))}</metadata><rect data-background="page" width="1680" height="1188" fill="{PAPER}"/><g font-family="Arial, sans-serif">'+''.join(self.fills)+'<g id="geometry-layer">'+''.join(strokes)+'</g><g id="labels-layer">'+''.join(labels)+'</g></g></svg>'
  (ROOT/'plans'/f'{name}.svg').write_text(svg,encoding='utf-8')
  return {'plate':name,'number':self.n,'texts':len(self.labels),'visibleStrokeSegments':len(strokes),'viewBox':[1680,1188]}

class Room:
 def __init__(self,p,spec,ox=130,oy=690,s=.08):self.p=p;self.spec=spec;self.ox=ox;self.oy=oy;self.s=s
 def xy(self,x,y):return self.ox+x*self.s,self.oy-y*self.s
 def box(self,b,fill=GREY,color=INK,width=1,role=None):
  x1,y1,x2,y2=b;x,y=self.xy(x1,y2);self.p.rect(x,y,(x2-x1)*self.s,(y2-y1)*self.s,fill,color,width)
  if role and fill:self.p.fills[-1]=self.p.fills[-1].replace('<polygon',f'<polygon data-gm-role="{role}"')
 def label(self,x,y,s,size=12,bold=False):self.p.text(*self.xy(x,y),s,size,bold,anchor='middle')
 def draw(self,state='routine',dimensions=True):
  p=self.p;S=self.spec;poly=S['room']['polygon_mm'];pts=[self.xy(*q) for q in poly]
  p.poly(pts,'#f0eee4',INK,2)
  # Walls extrude outside the nominated design clear-face polygon.
  self.box([0,-150,8520,0],GREY);self.box([0,4465,6745,4615],GREY)
  self.box([8520,0,8670,520],GREY);self.box([8520,2740,8670,2975],GREY)
  a,b=poly[4],poly[3];dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy);off=(-dy/ll*195,dx/ll*195)
  p.poly([self.xy(*a),self.xy(*b),self.xy(b[0]+off[0],b[1]+off[1]),self.xy(a[0]+off[0],a[1]+off[1])],GREY,INK,1)
  self.box(S['pier']['bounds_mm'],'#c1c4bd')
  x1,y1,x2,y2=S['pier']['bounds_mm']
  for x in range(x1-320,x2+320,100):
   aa=(max(x,x1),y1+max(0,x1-x));bb=(min(x+320,x2),y1+min(320,x2-x))
   if aa[1]<y2 and bb[1]>y1:p.line(*self.xy(*aa),*self.xy(*bb),'#7a8277',.6)
  self.label((x1+x2)/2,4280,'PIER',11,True)
  # LIN36 / LIN37 colour zoning is a proposed interpretation of the finish codes.
  cx,cy=self.xy(4100,2100);p.ellipse(cx,cy,1900*self.s,1700*self.s,'#c4c8b8',.7,fill='#e4e8d9')
  head=S['bed']['head_y_mm']+(300 if state=='airway' else 0)
  shift=S['scenario_geometry']['organ_support']['bed_west_offset_mm'] if state=='organ_support' else 0
  left,right=3554-shift,4646-shift;cx=4100-shift
  self.box([2354,head,left,head+2235],'#e2ebe6','#8baf9d',.7)
  self.box([right,head,4850 if state=='organ_support' else 5846,head+2235],'#e2ebe6','#8baf9d',.7)
  if shift:
   p.poly([self.xy(3554,head),self.xy(4646,head),self.xy(4646,head+2235),self.xy(3554,head+2235)],color='#9d8a71',width=.8,dash='5 4')
  self.box([left,head,right,head+2235],'#b7d1c6',INK,1.4,role='active-bed-envelope')
  self.box([left,head+1995,right,head+2235],'#dce5df')
  self.label(cx,head+1100,'2235 x 1092',12)
  self.label(cx,head-80,'HEAD / SOUTH',10)
  self.label((2354+left)/2,head+1050,str(left-2354),12)
  if state=='organ_support':
   self.label((right+4850)/2,head+2100,'454',10,True)
   self.label(3900,3450,'250 WEST / 204 CENTERED BASELINE',10,True)
  else:self.label(5246,head+1050,'1200',12)
  self.label(cx,(head+2235+4465)/2,f'{4465-head-2235} FOOT',12,True)
  p.geometry_receipt.update({'scenario':state,'bedBoundsMm':[left,head,right,head+2235],'nominalEastGapMm':4850-right if shift else None,'bedWestOffsetMm':shift,'scalePxPerMm':self.s,'originPx':[self.ox,self.oy]})
  self.box([250,3580,2150,4400],'#d8c5a3');self.label(1200,3940,'FAMILY SLEEPER',10)
  self.box([2650,3840,3350,4400],'#bda984');self.label(3000,4060,'BELONGINGS',9)
  self.box([650,1250,1550,2110],'#91b1a0');self.label(1100,1660,'RECLINER FLAT' if state=='mobility' else 'RECLINER',10)
  self.box([0,0,5550,90],'#aa9670');self.label(4100,180,'SANCTUARY SPINE',10)
  self.box([5550,0,6850,415],'#b6c8b9')
  self.label(6200,275,'SLIDING CASEWORK',10);self.label(6200,115,'1300 x 415 mm',10)
  self.box([6860,0,6900,450],'#a7cbd1')
  self.box([6920,0,7300,380],'#cfb38d');self.label(7110,180,'WASTE',9)
  self.box(S['gold_master']['sealed_containment']['bounds_mm'],'#c6aaa0',role='sealed-containment')
  self.label(7110,830,'SEALED',8);self.label(7110,650,'044106',8)
  self.label(6300,560,'BCMA',9)
  self.box([7350,0,8000,580],'#c7ded9');cx,cy=self.xy(7675,290);p.ellipse(cx,cy,21,12)
  self.label(7675,1150,'TYPE A BASIN',10,True)
  p.arrow(self.xy(7675,1080),self.xy(7675,540),'#547c72',.7)
  for x,label in [(2770,'P1 MON / 4-CH'),(5070,'P2 VENT')]:
   self.box([x-220,930,x+220,1300],'#c3d5ce');self.label(x,1115,label,9)
  self.box([3650,4430,4550,4465],'#284c43');self.label(4100,4290,'ORIENTATION TV',10)
  cart=[5800,2350,6500,3150] if state=='airway' else [9000,1500,9700,2300]
  self.box(cart,'#b68b7c');self.label((cart[0]+cart[2])/2,(cart[1]+cart[3])/2,'CART',9)
  self.label(8200,1870,'2000 CLEAR',10)
  self.label(7000,3460,'WA31',10)
  if state=='organ_support':
   self.box([4850,1350,5450,1950],'#c8af81',role='crrt-envelope');self.label(5150,1630,'CRRT',11,True)
   self.box([4850,2300,5650,2950],'#b38177',role='ecmo-envelope');self.label(5250,2600,'ECMO',11,True)
   p.arrow(self.xy(5100,1450),self.xy(4950,90),GOLD,1,'5 4')
  if state=='mobility':
   p.arrow(self.xy(4100,2100),self.xy(1100,1680),'#a16a3c',2,'7 5')
   self.label(2550,2780,'WEST TRANSFER / EAST VENT',11,True)
  if state=='transfer':
   points=[self.xy(4100,2100),self.xy(6300,2100),self.xy(8000,1600),self.xy(9200,1600)]
   for a,b in zip(points,points[1:]):p.arrow(a,b,'#4e8d9b',1.7,'6 4')
  if dimensions:
   p.dimh(*[self.xy(0,0)[0],self.xy(8520,0)[0]],self.oy+80,'8520 DESIGN CLEAR WIDTH')
   p.dimh(self.xy(0,0)[0],self.xy(5440,0)[0],self.oy+42,'5440 TO PIER CENTRELINE')
   p.dimh(self.xy(5440,0)[0],self.xy(8520,0)[0],self.oy+42,'3080')
   p.dimv(self.ox-42,self.xy(0,4465)[1],self.oy,'4465')
   p.dimv(self.xy(8520,0)[0]+65,self.xy(0,2975)[1],self.oy,'2975')
   for a,b,label in [(0,520,'520'),(520,2740,'2220 R.O.'),(2740,2975,'235')]:
    # Avoid crowded short dimension labels using aligned leaders in right margin.
    yy=(self.xy(0,a)[1]+self.xy(0,b)[1])/2
    p.text(self.xy(8520,0)[0]+95,yy+4,label,11)
  return self

def common_footer(p,y=880):
 p.text(96,y,'FINISH / MEP COORDINATION',16,True)
 p.paragraph(96,y+28,'LIN36 / LIN37 identify the source floor zoning. Proposed finish: welded, slip-resistant resilient linoleum; R10 selection target. P05 is a partition code; PT-ANTI is a proposed coating specification. Acoustic oak-look HPL: NRC 0.85 system target with an IPC-approved cleanable facing.',width=1460,size=14)
 p.text(96,y+120,'DESIGN TARGETS: 350 kg hoist system; 4 O2 + 4 Air + 4 Vac; 24 essential-power outlets; 6 Cat6A; dialysis reserve.',14,True)
 p.text(96,y+153,'Datum reconciliation and commissioning gates: submission pages 9-10. Do not scale a fitted browser or PDF print.',13)

def scale_arrows(p):
 p.text(1060,720,'1:50 GRAPHIC SCALE / A3',13,True)
 for i in range(3):p.rect(1060+i*80,740,80,12,INK if i%2==0 else PAPER)
 for i in range(4):p.text(1060+i*80,775,f'{i} m',12,anchor='middle')
 p.arrow((1450,790),(1450,710));p.text(1450,694,'LOCAL N',12,True,anchor='middle')
 p.text(1390,824,'True-north rotation 90.66 deg: verify',11)
 p.arrow((1200,825),(1128,852),GOLD);p.text(1220,855,'Qibla: 259 deg true bearing target',12)

def generate():
 S=load_spec();(ROOT/'plans').mkdir(exist_ok=True);receipts=[]
 for n,title in enumerate(TITLES,1):
  p=Plate(n,title,'1:250 source-calibrated pod trace at A3 / matrix not to scale' if n==9 else '1:50 at A3 / 100% (main plans)')
  p.geometry_receipt={'roomClearMm':[8520,4465],'pierBoundsMm':S['pier']['bounds_mm'],'wa31LengthMm':S['observation']['angled_length_mm']}
  if n<=5:
   state={1:'routine',2:'airway',3:'mobility',4:'transfer',5:'routine'}[n]
   r=Room(p,S).draw(state)
   x=1040;y=245
   if n==1:
    y=p.note(x,y,'DESIGN ENVELOPE','8520 x 4465 mm clear-face design coordinates. Bed head Y=905; panel Y=90; fascia Y=65.',515)
    y=p.note(x,y,'FOOT CLEARANCE / FOUR STATES','Routine 1325; extended 1071; airway 1025; airway + extension 771. Nominal envelope 2235 x 1092.',515)
    y=p.note(x,y,'SOURCE RECONCILIATION','5440 terminates at the pier centreline. Structural pier retained at X=4890..5990, Y=4145..4465.',515)
    p.note(x,y,'CLOSED-LOOP CLEAN / SEALED DIRTY ROUTES','044108 / 044109 clean supply to BCMA prep verification. Separate wet-side sealed-liner bedpan holding; closed transport to 044106. Wet towels stay east of the splash screen.',515)
   elif n==2:
    y=p.note(x,y,'AIRWAY WORKING STATE','Bed rolled 300 mm north by staff. Head-to-panel gap 1115; foot gap 1025 retracted / 771 extended.',515)
    y=p.note(x,y,'STAGED RESUSCITATION','Crash cart parks in the northeast pocket for routine care. Staff position it for a procedure; no automatic equipment movement.',515)
    p.note(x,y,'CLINICAL HANDOFF','Lateral nominal care bands are 1200. Active equipment and service lines reduce local space; scenario clearances remain explicit.',515)
   elif n==3:
    y=p.note(x,y,'AIRWAY CIRCUIT STAYS EAST','P2 ventilator and breathing circuit are east of the bed-to-recliner transfer route. P1 carries monitor + four infusion channels.',515)
    y=p.note(x,y,'H-FRAME TRANSFER','Rail X=1150 / 5750; travel Y=1100..3450; bridge +2600 AFFL. 350 kg system capacity target.',515)
    p.note(x,y,'WORKFLOW','Staff manage the patient, infusion lines and sling. The plotted centre path is the proposed transfer sequence.',515)
   elif n==4:
    y=p.note(x,y,'ENTRY OPENING 044044 H=2410','2000 mm clear telescopic slide inside 2220 x 2410 mm rough opening. Leaf and breakout hardware selected at detailed design.',515)
    y=p.note(x,y,'BED-ONLY TRANSPORT STUDY','Trajectory shows the intended route. Patient attachments, staff, head-end equipment and corridor approaches are commissioning inputs.',515)
    p.note(x,y,'RETURN TO PREPARED STATE','Close casework drawer, release staff-controlled brake, stow AAC and lift strap, manage all lines, clear the route.',515)
   elif n==5:
    # Ceiling anchor-to-working-head vectors north-west in plan.
    for ax,hx,label in [(3150,2770,'P1'),(5450,5070,'P2')]:
     p.ellipse(*r.xy(ax,850),6,6,fill=PAPER);p.arrow(r.xy(ax,850),r.xy(hx,1150),GOLD,1.5);r.label(ax,630,label+' ANCHOR',10)
    r.box([2900,1250,5300,3050],None,'#897651',1.5)
    for b in [[2780,1130,5420,3170],[2825,1175,5375,3125]]:
     a,bx,c,d=b;p.poly([r.xy(a,bx),r.xy(c,bx),r.xy(c,d),r.xy(a,d)],color='#4e8d9b',width=1,dash='5 4')
    r.box(S['gold_master']['ventilation']['return_bounds_mm'],'#9fc6c4',role='low-return')
    r.label(8100,780,'LOW RETURN',9)
    r.box(S['gold_master']['ventilation']['brief_return_zone_mm'],None,'#b39b79',.6)
    for xx in [1150,5750]:p.line(*r.xy(xx,1100),*r.xy(xx,3450),'#6f6d62',3)
    for xx in [2950,5250]:
     for yy in [1300,3000]:p.ellipse(*r.xy(xx,yy),5,5,GOLD,1.2,fill='#efe2ba')
    y=p.note(x,y,'COORDINATED CEILING TARGETS','Soffit +2850; sky underside +2750; hoist bridge +2600 AFFL. Sky coffer 2400 x 1800 with perimeter HEPA slot supply; downward-wash intent toward a low-level east return.',515)
    y=p.note(x,y,'FOUR AIMABLE PROCEDURE SPOTS','Task target >=10,000 lux at selected cannulation planes; Ra >=95; R9 >=90. Verify shadowing, spectrum and glare.',515)
    p.note(x,y,'MEP BALANCE + CLEAR RETURN','P1 (3150,850) / P2 (5450,850). Return intake X8100..8460 avoids the bin/basin blocking the brief zone X7000..7500. Pressure / ACH / HEPA integrity / flow pattern: Stage-2 CFD, TAB and smoke testing.',515)
   common_footer(p);scale_arrows(p)
  elif n==6:
   ox,oy,s=240,780,.12
   X=lambda y:ox+y*s;Z=lambda z:oy-z*s
   p.rect(X(0)-18,Z(2850),18,2850*s,GREY);p.rect(X(4465),Z(2850),18,2850*s,GREY)
   p.rect(X(0),Z(0),4465*s,20,GREY)
   for z,label in [(2850,'+2850 SOFFIT'),(2750,'+2750 SKY'),(2600,'+2600 HOIST'),(2410,'+2410 DOOR LINTEL'),(2400,'+2400 PROPOSED WA31 LINTEL'),(1660,'+1660 ORIENTATION'),(1000,'+1000 WA31 SILL'),(700,'+700 WEST SPANDREL')]:
    xx=1060;yy=Z(z);p.line(X(0),yy,xx-18,yy,'#a8b4aa',.7,'5 5')
    # Datum annotation column uses fixed leading, connected by separate leaders.
    row={2850:290,2750:330,2600:370,2410:410,2400:450,1660:520,1000:600,700:650}[z]
    p.line(xx-18,yy,xx+20,row-5,'#89988f',.7);p.text(xx+36,row,label,15)
   p.rect(X(905),Z(930),2235*s,35,'#bdcfc4');p.rect(X(1250),Z(2750),1800*s,12,'#bedce5')
   p.rect(X(0),Z(1450),90*s,1450*s,'#bfa77f')
   p.text(78,550,'SANCTUARY SPINE',14,True);p.text(78,578,'y=90 / FASCIA y=65',12)
   p.dimh(X(0),X(4465),830,'4465 CLEAR-FACE DESIGN DEPTH')
   p.dimh(X(905),X(3140),865,'2235 RETRACTED BED')
   p.note(96,950,'DATUM DISCIPLINE','+2410 is the entry-door rough lintel. Existing WA31 slit is +1000..+1400; proposed enlarged glazing is +1000..+2400. Levels are distinct.',1450)
  elif n==7:
   p.text(120,250,'REFERENCE WA31',20,True);p.text(720,250,'PROPOSED FAIL-CLEAR PNLC',20,True)
   for x in [120,720]:p.rect(x,290,450,480,'#e5e3d9',INK,2)
   p.rect(145,560,400,80,'#c9ddda');p.text(345,678,'+1000 to +1400 / 400 high',17,anchor='middle')
   p.rect(745,340,400,280,'#c4dedb');p.rect(950,350,182,120,'#17343b')
   p.text(960,372,'SIMULATED DATA',10,True,color='#c9efe2')
   for yy,label in [(395,'ECG / HR 74'),(423,'PLETH / SpO2 98%'),(451,'ABP / 118-76')]:
    p.text(959,yy,label,9,color='#b7e5d3');
    for i in range(18):p.line(1070+i*3,yy-5+math.sin(i)*3,1073+i*3,yy-5+math.sin(i+1)*3,'#84cbb8',.8)
   p.text(945,670,'+1000 to +2400 / 1400 high',17,anchor='middle')
   p.note(1230,310,'DIRECT VIEW','Central face/chest viewing zone stays free of telemetry.',350)
   p.note(1230,480,'STAFF PRIORITY','Hardwired Awrah clear override. Target fail-clear response <100 ms at system level.',350)
   p.note(1230,680,'HUD OPTICS','Staff-facing screen only; smoked contrast backing behind the upper-right rectangle.',350)
   p.note(96,950,'MOCK-UP / FAILURE TEST','Compare seated and standing staff eyes against bed heights and Fowler positions. Validate privacy segmentation, loss-of-power response, cleaning, glare and view angles.',1450)
  elif n==8:
   # Four dimensioned elevations plus an organ-support plan from the same source.
   for col,(wall,width) in enumerate([('SOUTH SANCTUARY SPINE',8520),('NORTH ORIENTATION WALL',8520)]):
    ox=100+col*800;oy=450;s=.08
    p.text(ox,220,wall,17,True)
    p.rect(ox,oy-2850*s,width*s,2850*s,'#e7e3d8')
    p.dimh(ox,ox+width*s,oy+32,'8520')
    if col==0:
     p.rect(ox,oy-2200*s,5550*s,2200*s,'#c7b38f');p.rect(ox,oy-1450*s,5550*s,300*s,'#789b88')
     p.rect(ox+5550*s,oy-2220*s,1300*s,2220*s,'#e2e7dc');p.rect(ox+5550*s,oy-1400*s,1300*s,500*s,PAPER)
     p.line(ox+6880*s,oy,ox+6880*s,oy-1850*s,'#6da29b',3)
     p.rect(ox+7350*s,oy-865*s,650*s,60*s,'#d2e4db')
     p.text(ox+18,oy-125,'FASCIA +1150..1450',11);p.text(ox+18,oy-96,'RO RESERVE / STOP +1350',11)
     p.text(ox+420,oy-178,'UPPERS +1400..2150',10);p.text(ox+420,oy-135,'PREP +900..1400',10)
     p.text(ox+525,oy-80,'BASIN +865',11)
    else:
     p.rect(ox+3650*s,oy-1950*s,900*s,580*s,'#264b42');p.text(ox+4100*s,oy-143,'TV +1660',11,anchor='middle',color='#f0f3df')
     p.rect(ox+S['pier']['bounds_mm'][0]*s,oy-2850*s,1100*s,2850*s,GREY)
     p.rect(ox+6745*s,oy-2400*s,(8520-6745)*s,1400*s,'#c5ddd8')
     p.text(ox+30,oy-48,'WA31: +1000..2400 / QIBLA 259 deg',11)
   for i,wall in enumerate(['WEST DAYLIGHT ELEVATION','EAST ENTRY ELEVATION']):
    ox=100+i*800;oy=718;s=.08;p.text(ox,480,wall,16,True);p.rect(ox,oy-2850*s,4465*s,2850*s,'#e8e5dc')
    if i==0:p.rect(ox+500*s,oy-2800*s,3295*s,2100*s,'#c5dce2')
    else:p.rect(ox+520*s,oy-2410*s,2220*s,2410*s,'#c6dad3')
    p.text(ox+400,600,'+700 spandrel / 3295 glazed bay' if i==0 else '2220 x 2410 rough opening',13)
    p.text(ox+400,630,'500 + 3295 + 670 = 4465' if i==0 else '2000 clear telescopic slide',13)
   r=Room(p,S,ox=100,oy=1090,s=.08).draw('organ_support',False)
   p.text(950,810,'MAXIMUM ORGAN SUPPORT',17,True)
   p.paragraph(950,845,'CRRT 600 x 600 at X4850..5450 / Y1350..1950. ECMO 800 x 650 at X4850..5650 / Y2300..2950. Centered bed leaves 204 mm east device clearance; a staff-planned 250 mm west offset (X3304..4396) expands the nominal east procedure gap to 454 mm while retaining a 950 mm west band.',630,14)
   p.paragraph(950,1020,'Plan positioning before cannulation, then lock casters. Stage-2 verifies rails, hand-crank access and line envelopes. Bag-based CRRT remains independent of the RO reserve.',630,13)
  else:
   ctx=json.loads((ROOT/'source_context_geometry.json').read_text(encoding='utf-8'));ox,oy=90,245;cw,ch=ctx['width'],ctx['height']
   p.text(90,220,'SCALED ARCHITECTURAL TRACE / ToD-4th-PART a',17,True)
   clip=f'<defs><clipPath id="context-crop"><rect x="{ox}" y="{oy}" width="{cw}" height="{ch}"/></clipPath></defs>'
   p.fills.append(clip)
   for path in ctx['paths']:
    commands=[];points=[];last=None;start=None
    for cmd in path['commands']:
     tag=cmd[0];vals=cmd[1:];vals=[v+(ox if i%2==0 else oy) for i,v in enumerate(vals)];commands.append(tag+' '.join(str(v) for v in vals))
     if tag=='M':last=(vals[0],vals[1]);start=last
     elif tag=='L':
      q=(vals[0],vals[1]);points.append((last,q));last=q
     elif tag=='C':
      a=last;b=vals[:2];c=vals[2:4];d=vals[4:6]
      for j in range(1,13):
       t=j/12;u=1-t;q=(u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1]);points.append((last,q));last=q
     elif tag=='Z' and last and start:points.append((last,start));last=start
    if path['fill']:p.fills.append(f'<path d="{" ".join(commands)}" fill="{path["fill"]}" fill-rule="evenodd" clip-path="url(#context-crop)"/>')
    if path['stroke']:
     for a,b in points:
      if a and b and all(ox<=q[0]<=ox+cw and oy<=q[1]<=oy+ch for q in [a,b]):p.line(*a,*b,'#849087',path['width'])
   labs=ctx['roomLabelCoordinates'];pos=lambda key:(ox+labs[key][0],oy+labs[key][1])
   for key in labs:
    label=key+' / D417' if key=='044044' else key+' / D407' if key=='044048' else key
    p.text(*pos(key),label,10,True,anchor='middle')
   a=pos('044043');b=pos('044044');p.arrow((a[0],a[1]+8),(b[0]+25,b[1]-5),'#386d5b',2,'5 4')
   clean=pos('044109');meds=pos('044108');soiled=pos('044106');toilet=pos('044094');door=(ox+213,oy+445)
   # Route overlays are diagrammatic corridor intentions on the scaled architectural trace.
   for start,via,end,col in [(clean,(ox+215,oy+300),door,'#4e8a65'),(meds,(ox+230,oy+370),door,'#4e8a65'),(door,(ox+315,oy+370),soiled,'#b3833b'),(door,(ox+220,oy+457),toilet,'#b3833b')]:
    p.line(*start,*via,col,1.6,'6 5');p.arrow(via,end,col,1.6,'6 5')
   p.text(90,945,'1:250 GRAPHIC SCALE / calibrated from 9100 mm grid 32-33',13,True)
   for i in range(3):p.rect(90+i*80,963,80,10,INK if i%2==0 else PAPER)
   for i in range(4):p.text(90+i*80,999,f'{i*5} m',11,anchor='middle')
   x=850;y=235
   y=p.note(x,y,'POD CONNECTIONS','044111 central nurse station; 044043 shared Cs observation alcove for 044042 and D417; 044109 clean utility / 044108 meds; 044106 soiled / 044094 toilet; 044098 stretcher alcove.',720)
   y=p.note(x,y,'OBSERVATION STRATEGY','Direct observation is assigned to local alcove 044043. Central-station awareness is indirect: intervening walls prevent assuming an unobstructed diagonal view to the patient.',720)
   p.text(x,y,'KIT-OF-PARTS / ADAPTABLE CASSETTE',17,True);y+=38
   for title,body in [('STANDARD ADULT / 044044 D417','Integrated service cassette, staff-first observation and a west family zone.'),('AIRBORNE ISOLATION / 044034-35','Adapt to anteroom 044036: pressure indication and pass-through PPE cabinet. A -5 Pa study setpoint is conditional on an approved full pressure cascade.'),('MEDICAL ICU / 044048 D407','Reuse the cassette and finish palette; adapt services, equipment envelopes, door and observation interfaces to the host room.')]:
    y=p.note(x,y,title,body,720)
   p.paragraph(850,1000,'Green: closed-loop clean supply from 044108 / 044109 to bedside BCMA verification. Amber: sealed-liner dirty transport to 044106, with holding on the wet side. Routes proceed through Stage-2 operational review.',720,13)
   p.text(90,1085,'Derived vector excerpt: SSMC supplied project record drawing. The complete source PDF is not redistributed.',12)
  receipts.append(p.save(NAMES[n-1]))
 (ROOT/'plans/PLATE_MANIFEST.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8')
 return receipts

if __name__=='__main__':print(json.dumps(generate(),indent=2))
