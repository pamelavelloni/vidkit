    wp=ease_out(clamp01((t-0.25)/0.5))
    if wp>0.05: c.rrect(_X(16),_Y(76),_X(16+68*wp),_Y(89),FSC*2.0,fill=C_AS)
def _arrow(c,t):
    p=ease_out(clamp01((t-0.55)/0.4))
    if p<=0.02: return
    c.line(_m(bez((95,6),(101,30),(87,45),(67,48))),5.6,C_AR,p)
    if p>0.75:
        q=clamp01((p-0.75)/0.25)
        c.line(_m([(78,36),(66,48)]),5.6,C_AR,q); c.line(_m([(77,54),(66,48)]),5.6,C_AR,q)
def _rot(pts,cx,cy,deg):
    r=math.radians(deg); co,si=math.cos(r),math.sin(r)
    return [(cx+(x-cx)*co-(y-cy)*si, cy+(x-cx)*si+(y-cy)*co) for x,y in pts]
def _fig(c,cx,t,i,col=C_OT,dash=None,top=30,r=11):
    p=ease_out(clamp01((t-0.1-0.09*i)/0.7))
    if p<=0: return
    c.line(_m(circ(cx,top,r)),7.2,col,p,dash=dash)
    c.line(_m([(cx-20,top+48)]+bez((cx-20,top+48),(cx-20,top+22),(cx+20,top+22),(cx+20,top+48),24)[1:]),7.2,col,p,dash=dash)

def FR_mask(c,t):
    _card(c); _hl(c,t)
    ox=8*math.cos(t*2.0); oy=-5*math.sin(t*2.0+0.6)
    face=ellipse_pts(50,52,33,40,-90,270,n=64)
    g=[(x+11+ox,y-8+oy) for x,y in face]
    c.line(_m(g),5.6,mixw(C_AR,0.82),ease_out(clamp01((t-0.2)/0.7)),dash=(9,8))
    fst(c,face,0,t)
    blink=1-0.85*(max(0,math.sin(t*3.1))**14)
    for ex in (38,62):
        a=clamp01((t-0.5)/0.3)
        if a>0: c.poly([(_X(ex+5*math.cos(math.radians(k))),_Y(44+5*blink*math.sin(math.radians(k)))) for k in range(0,360,30)],fill=mixw(C_AR,a))
    fst(c,arcpts(50,60,16,30,150),2,t)
    _arrow(c,t)
def FR_rules(c,t):
    _card(c); _hl(c,t)
    fst(c,rrp(22,10,78,90,8),0,t)
    for i,y in enumerate((32,48,64)): fst(c,[(34,y),((66,58,66)[i],y)],i+1,t)
    acc(c,72,78,11,t,k=5.0,delay=0.6)
    q=clamp01((t-1.0)/0.3)
    if q>0: c.line(_m([(66,78),(71,83),(78,73)]),6,C_W,q)
    _arrow(c,t)
def FR_hourglass(c,t):
    _card(c); _hl(c,t)
    fst(c,[(24,10),(76,10)],0,t); fst(c,[(24,90),(76,90)],0,t)
    fst(c,[(30,14),(70,14),(50,48),(30,14)],1,t); fst(c,[(50,52),(70,86),(30,86),(50,52)],2,t)
    f=clamp01((t-0.6)/2.2)
    if f>0: c.poly(_m([(50-11*f,86),(50+11*f,86),(50,86-16*f)]),fill=C_AR)
    if t>0.6:
        y=54+((t*0.9)%1.0)*16; c.circle(_X(50),_Y(y),FSC*2.8,fill=C_AR)
    _arrow(c,t)
def FR_shield(c,t):
    _card(c); _hl(c,t)
    pts=[(50,8),(84,20),(84,46)]+bez((84,46),(84,70),(68,84),(50,94),20)+bez((50,94),(32,84),(16,70),(16,46),20)+[(16,20),(50,8)]
    if t>0.5: c.poly(_m(pts[:-1]),fill=mixw(C_AS,0.6*clamp01((t-0.5)/0.4)))
    fst(c,pts,0,t,dur=0.9)
    q=ease_out(clamp01((t-0.9)/0.35)); pul=1+0.06*math.sin(t*5)
    if q>0: c.line(_m([(34,50),(46,62),(68,38)]),8.5*pul,C_AR,q)
    _arrow(c,t)
def FR_seedling(c,t):
    _card(c); _hl(c,t)
    fst(c,[(24,90),(76,90)],0,t); fst(c,bez((50,90),(50,72),(52,60),(50,46),20),1,t)
    sway=4*math.sin(t*2.2)
    for k,(cx,cy,rot,col) in enumerate(((36,38,-35,C_OT),(64,30,35,C_AR))):
        s=ease_out(clamp01((t-0.6-0.25*k)/0.5))
        if s>0.03:
            pts=_rot(ellipse_pts(cx,cy,16*s,8*s,-90,270,rot=rot,n=40),50,46,sway)
            c.line(_m(pts),7,col,1.0)
    acc(c,16,14,6,t,k=3.0,delay=0.7)
    _arrow(c,t)
def FR_target(c,t):
    _card(c); _hl(c,t)
    fst(c,circ(50,56,34),0,t); fst(c,circ(50,56,21),1,t)
    acc(c,50,56,8,t,k=5.0,delay=0.5)
    p=ease_out(clamp01((t-0.45)/0.5)); off=(1-p)*55
    tip=(50+off,56-off); tail=(tip[0]+34,tip[1]-34)
    if p>0:
        c.line(_m([tail,tip]),6.5,C_OT,1.0); c.line(_m([(tail[0],tail[1]),(tail[0],tail[1]+12)]),6.5,C_OT,1.0); c.line(_m([tail,(tail[0]-12,tail[1])]),6.5,C_OT,1.0)
    _arrow(c,t)
def FR_lock(c,t):
    _card(c); _hl(c,t)
    e=ease_out(clamp01((t-0.55)/0.4)); off=-9*(1-e)
    fst(c,rrp(22,44,78,88,9),0,t)
    fst(c,[(34,44+off),(34,32+off)]+arcpts(50,32+off,16,180,360,24)+[(66,32+off),(66,44+off)],1,t)
    acc(c,50,62,6,t,k=4.0,delay=0.7); fst(c,[(50,67),(50,77)],2,t)
    _arrow(c,t)
def FR_checklist(c,t):
    _card(c); _hl(c,t)
    fst(c,rrp(24,14,76,90,8),0,t)
    c.rrect(_X(38),_Y(6),_X(62),_Y(20),FSC*3,fill=C_OD)
    for i,y in enumerate((36,56,76)):
        fst(c,rrp(32,y-7,46,y+7,3,4),i+1,t); fst(c,[(54,y),(68,y)],i+1,t)
        if i<2:
            q=ease_out(clamp01((t-0.9-0.4*i)/0.3))
            if q>0: c.line(_m([(35,y),(39,y+4),(44,y-4)]),6.5,C_AR,q)
        else: acc(c,39,y,3.2,t,k=7.0,delay=1.6)
    _arrow(c,t)
def FR_formazione(c,t):
    _card(c); _hl(c,t)
    for i,(y,x0,x1) in enumerate(((86,18,82),(66,24,76),(46,30,70))):
        e=ease_out(clamp01((t-0.15-0.22*i)/0.4))
        if e<=0: continue
        dy=(1-e)*-14
        c.line(_m(rrp(x0,y-16+dy,x1,y+dy,3,4)),7.2,C_OT,e)
        c.line(_m([(x0+6,y-8+dy),(x1-10,y-8+dy)]),4.5,C_OT if i!=1 else C_OD,e)
    q=clamp01((t-0.9)/0.3); pu=1+0.08*math.sin(t*5)
    if q>0: c.line(_m([(62,30),(62,30+14*q*pu)]),6,C_AR,1.0)
    _arrow(c,t)
def FR_forward(c,t):
    _card(c); _hl(c,t)
    for k in range(3):
        p=ease_out(clamp01((t-0.1-0.15*k)/0.4)); ph=(t*1.6-k*0.22)%1.0; u=max(0,math.sin(math.pi*ph))
        col=mixc(C_OT,C_AR,u) if t>0.8 else C_OT
        if p>0: c.line(_m([(18+k*22,26),(38+k*22,50),(18+k*22,74)]),8,col,p)
    _arrow(c,t)
def FR_onetoone(c,t):
    _card(c); _hl(c,t)
    _fig(c,28,t,0); _fig(c,72,t,1,col=C_OD)
    q=ease_out(clamp01((t-0.7)/0.5))
    if q>0: c.line(_m(bez((39,34),(46,16),(54,16),(61,34),30)),5.6,C_AR,q,dash=(9,7))
    acc(c,50,20,3.5,t,k=4.0,delay=1.2)
def FR_call(c,t):
    _card(c); _hl(c,t)
    fst(c,rrp(12,18,88,74,6),0,t)
    fst(c,[(40,74),(40,86)],1,t); fst(c,[(28,88),(72,88)],1,t)
    p=ease_out(clamp01((t-0.3)/0.6))
    if p>0:
        c.line(_m(circ(44,38,9)),6,C_OT,p); c.line(_m(bez((30,66),(30,52),(58,52),(58,66),20)),6,C_OT,p)
    if t>0.6 and int(t*2.2)%2==0: c.circle(_X(78),_Y(28),FSC*4.2,fill=C_AR)
    _arrow(c,t)
def FR_racconto(c,t):
    _card(c); _hl(c,t)
    fst(c,rrp(14,14,62,86,6),0,t)
    for i,y in enumerate((32,46,60)): fst(c,[(24,y),((52,48,40)[i],y)],i+1,t)
    q=ease_out(clamp01((t-0.8)/0.6))
    if q>0: c.line(_m(bez((40,60),(70,64),(66,34),(88,22),30)),5.6,C_AR,q)
    if q>0.95: acc(c,88,22,4,t,k=6.0,delay=0)
def FR_head(c,t):
    _card(c); _hl(c,t)
    fst(c,circ(46,40,22),0,t)
    fst(c,bez((14,90),(14,64),(78,64),(78,90),24),1,t)
    for j in range(3):
        ph=((t-0.7)*1.2-j*0.25)%1.0; pu=max(0,math.sin(math.pi*ph))
        if t>0.7: c.circle(_X(74+j*7),_Y(26-j*9),FSC*(2.2+1.6*pu+0.6*j),fill=mixw(C_AR,0.5+0.5*pu))
def FR_diventare(c,t):
    _card(c); _hl(c,t)
    _fig(c,24,t,0,col=mixw(C_AR,0.8),dash=(8,7))
    q=ease_out(clamp01((t-0.45)/0.35))
    if q>0: c.line(_m([(40,52),(40+16*q,52)]),6,C_AR,1.0)
    if q>0.8: c.line(_m([(50,45),(57,52),(50,59)]),6,C_AR,1.0)
    if t>0.6: _fig(c,76,t-0.6,0)
    acc(c,76,30,3,t,k=5,delay=1.4)
def FR_chat(c,t):
    _card(c); _hl(c,t)
    fst(c,rrp(10,14,90,66,14),0,t,dur=0.9)
    p=ease_out(clamp01((t-0.5)/0.3))
    if p>0: c.rect(_X(30),_Y(62),_X(44),_Y(70),C_W); c.line(_m([(30,66),(22,84),(44,66)]),7.2,C_OT,p)
    for k in range(3):
        a=clamp01((t-0.6-0.12*k)/0.2)
        if a>0: c.circle(_X(32+k*18),_Y(40-3*max(0,math.sin(t*7-k*0.9))),FSC*4.2,fill=mixw(C_AR if k==1 else C_OT,a))
def FR_nodo(c,t):
    _card(c); _hl(c,t)
    a=clamp01(t/0.6); e=ease_out(clamp01((t-0.6)/0.9)); r=16+7*e
    c.line(_m(ellipse_pts(50,36,r,r*0.95,100,470,n=56)),7.2,C_OT,a)
    q=clamp01((t-0.25)/0.5)
    if q>0:
        c.line(_m(bez((42,52),(50,66),(64,70),(88,84),30)),7.2,C_OT,q)
        c.line(_m(bez((58,52),(50,66),(36,70),(12,84),30)),7.2,C_OD,q)
    acc(c,88,84,4,t,k=5,delay=1.2)
def FR_identita(c,t):
    _card(c); _hl(c,t)
    fst(c,rrp(10,12,62,88,6),0,t)
    fst(c,[(20,72),(36,26),(52,72)],1,t); fst(c,[(26,56),(46,56)],2,t)
    for i,col in enumerate((C_OT,C_OD,C_AR)):
        p=ease_back(clamp01((t-0.5-0.18*i)/0.35),1.8)
        if p>0.02: c.line(_m(circ(78,26+i*24,8*p)),6,col,1.0)
    acc(c,78,74,3.5,t,k=5,delay=1.3)
FICONS={"mask":FR_mask,"rules":FR_rules,"hourglass":FR_hourglass,"shield":FR_shield,"seedling":FR_seedling,
    "target":FR_target,"lock":FR_lock,"checklist":FR_checklist,"formazione":FR_formazione,"forward":FR_forward,
    "onetoone":FR_onetoone,"call":FR_call,"racconto":FR_racconto,"head":FR_head,"diventare":FR_diventare,
    "chat":FR_chat,"nodo":FR_nodo,"identita":FR_identita}
# >>> ICONE NUOVE: aggiungerle qui sotto (def FR_nome + FICONS["nome"]=FR_nome) <<<

def finish_frecce(c):
    im=c.img.resize((GN,GN),Image.LANCZOS)
    a=np.asarray(im,np.float32)/255
    sa=a[...,3]; srgb=a[...,:3]*255
    sh=np.roll(cv2.GaussianBlur(sa,(0,0),9)*0.10,6,axis=0)
    shp=np.dstack([np.array([27,27,47],np.float32)*sh[...,None],sh])
    sp=np.dstack([srgb*sa[...,None],sa])
    return (sp+shp*(1-sa[...,None])).astype(np.float32)
def _icon_sprite(name,t):
    if name not in FICONS: raise SystemExit(f'icona "{name}" non ancora disegnata in stile 05: va disegnata (FR_{name}) prima del render')
    c=Cv(); FICONS[name](c,t); return finish_frecce(c)
GI_CX,GI_CY=540,CFG.get("icon_cy",1120)
def draw_graphics(frame,t):
    for s0,e0,name in GRAPHICS:
        if not (s0<=t<=e0): continue
        tau=t-s0; sp=_icon_sprite(name,tau)
        fin=ease_out(clamp01(tau/0.45))
        fout=0.0 if e0>=99 else ease_in(1-clamp01((e0-t)/0.3))
        al=clamp01(tau/0.3)*(1-fout)
        dy=(1-fin)*46+fout*30+6*math.sin(2*math.pi*tau/3.2)
        ang=2.2*math.sin(2*math.pi*tau/4.1)
        n=int(GN*CFG.get("icon_scale",0.9))
        img=cv2.resize(sp,(n,n),interpolation=cv2.INTER_AREA)
        M=cv2.getRotationMatrix2D((n/2,n/2),ang,1.0)
        img=cv2.warpAffine(img,M,(n,n),flags=cv2.INTER_LINEAR,borderValue=(0,0,0,0))
        blend(frame,img,int(GI_CX-n/2),int(GI_CY-n/2+dy),gain=al)
        return

# ===================== SEGMENTAZIONE PERSONA + COMPOSIZIONE =====================
CROP_H=1100
prev={"m":None}
def seg_update(frame):
    crop=frame[:CROP_H]
    x=cv2.resize(crop,(256,256),interpolation=cv2.INTER_AREA).astype(np.float32)/255
    it.set_tensor(_i["index"],x[None]); it.invoke()
    m=it.get_tensor(_o["index"])[0,:,:,0].copy()
    if prev["m"] is not None: m=0.65*m+0.35*prev["m"]
    prev["m"]=m
    return m
def make_mask(m):
    mm=np.clip((m-0.38)/0.30,0,1)
    mm=mm*mm*(3-2*mm)
    up=cv2.resize(mm,(W,CROP_H),interpolation=cv2.INTER_CUBIC)
    up=cv2.GaussianBlur(up,(0,0),2.2)
    full=np.zeros((H,W),np.float32); full[:CROP_H]=np.clip(up,0,1)
    return full
STACCHI=[]
def draw_wipe(frame,t):
    for s,dur,col in STACCHI:
        d=t-s
        if not (0<=d<=dur): continue
        q=d/dur; span=W*1.35; c=(W+span/2)-q*(W+span)
        yy=np.arange(H,dtype=np.float32)[:,None]; xx=np.arange(W,dtype=np.float32)[None,:]
        sl=(yy-H/2)*0.16
        m=np.clip((xx+sl-(c-span/2))/16,0,1)*np.clip(((c+span/2)-(xx+sl))/16,0,1)
        frame[:]=np.clip(frame.astype(np.float32)*(1-m[...,None])+np.array(col,np.float32)*m[...,None],0,255).astype(np.uint8)
def compose(frame,t,m):
    mf=make_mask(m)
    br=active_broll(t)
    if br is None:
        draw_behind(frame,t,mf)
        draw_graphics(frame,t)
        draw_front(frame,t)
    else:
        draw_broll(frame,t,br)
    out=apply_zoom(frame,t)
    draw_wipe(out,t)
    return out

# ===================== MOVIMENTO DI INQUADRATURA =====================
def _src_size():
    try:
        r=subprocess.run("ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 in.mov",shell=True,capture_output=True,text=True).stdout.strip().split(",")
        return int(r[0]),int(r[1])
    except Exception: return 1080,1920
SRC_W,SRC_H=_src_size()
def _split_long(shots,maxlen=4.2):
    out=[]; ends=[w["e"] for w in words if re.search(r"[.?!,:]$",w["w"])]
    for a,b in shots:
        segs=[(a,b)]
        while segs[-1][1]-segs[-1][0]>maxlen*1.4:
            a0,b0=segs[-1]; mid=(a0+b0)/2
            cand=[e for e in ends if a0+1.2<e<b0-1.2]
            cut=min(cand,key=lambda e:abs(e-mid)) if cand else mid
            segs[-1]=(a0,cut); segs.append((cut,b0))
        out+=segs
    return out
ZP=[1.00,1.14,1.04,1.19,1.08,1.16,1.02,1.18]
_A=(SRC_W/2,SRC_H*0.36458); _O=(540.0,700.0)
def cam_M(t):
    ci=len(CAM)-1
    for i,c in enumerate(CAM):
        if c["t0"]<=t<c["t1"]: ci=i; break
    c=CAM[ci]; u=clamp01((t-c["t0"])/max(1e-3,c["t1"]-c["t0"])); e=u*u*(3-2*u)
    z=c["z0"]+(c["z1"]-c["z0"])*e
    sc=(W/SRC_W)*z
    ox=_O[0]+c["px"]*clamp01((z-1)/0.1)
    return np.float32([[sc,0,ox-sc*_A[0]],[0,sc,_O[1]-sc*_A[1]]]),ci
def reframe(src,t):
    M,ci=cam_M(t)
    return cv2.warpAffine(src,M,(W,H),flags=cv2.INTER_CUBIC),ci

# ===================== ILLUSTRAZIONI A PENNELLO (si disegnano a mano) =====================
# Nuova illustrazione: funzione che costruisce le pennellate (come _cage_strokes) + fx_<nome> che chiama _brush_fx,
# registrata in FX. Servono circa 600 px liberi sopra la testa.
HERO_INK=BLU; HERO_ACC=RUG
def _smooth(rng,n,k):
    a=rng.normal(0,1,n+2*k+2); return np.convolve(a,np.ones(2*k+1)/(2*k+1),mode="same")[k+1:k+1+n]*math.sqrt(2*k+1)
def _rsample(pts,step=3.0):
    P=np.array(pts,float); seg=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]
    n=max(3,int(seg[-1]/step)+1); u=np.linspace(0,seg[-1],n); return np.stack([np.interp(u,seg,P[:,0]),np.interp(u,seg,P[:,1])],1)
def _arc(cx,cy,rx,ry,a0,a1,n=80):
    t=np.linspace(math.radians(a0),math.radians(a1),n); return [(cx+rx*math.cos(x),cy+ry*math.sin(x)) for x in t]
def brush_stroke(path,width,col,p,seed,amp=1.8,dry=0.6,ymax=None):
    """Una pennellata: tante setole, pressione che sale e scende, tratto asciutto verso la fine. p = parte gia' disegnata."""
    rng=np.random.RandomState(seed); P=_rsample(path,3.0); N=len(P)
    g=np.gradient(P,axis=0); nr=np.stack([-g[:,1],g[:,0]],1); nr/=np.maximum(np.linalg.norm(nr,axis=1,keepdims=True),1e-6)
    P=P+nr*(_smooth(rng,N,12)*amp)[:,None]
    sl=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]; t=sl/max(sl[-1],1e-6)
    wp=width*(0.50+0.50*np.sin(np.pi*np.clip(t,0.03,0.97))**0.45)*(1+0.10*_smooth(rng,N,5))
    B=max(6,int(width/2.2)); off=(np.arange(B)+0.5)/B-0.5+rng.uniform(-0.06,0.06,B); ab=rng.uniform(0.62,1.0,B)
    nch=(N+6)//7; gaps=rng.rand(B,nch)*rng.rand(B,nch)
    M=max(2,int(round(p*N))); Q=P[:M]; m=int(width)+6
    x0=max(0,int(Q[:,0].min())-m); y0=max(0,int(Q[:,1].min())-m); x1=min(W,int(Q[:,0].max())+m); y1=min(ymax or LH_,int(Q[:,1].max())+m)
    if x1<=x0 or y1<=y0: return None
    acc_=np.zeros((y1-y0,x1-x0),np.uint8)
    for b in range(B):
        Lb=P+nr*(off[b]*wp)[:,None]
        for ci,j in enumerate(range(0,M-1,7)):
            tj=t[min(j,N-1)]
            if gaps[b,ci]<dry*0.9*np.clip((tj-0.55)/0.45,0,1)**1.2: continue
            ch=Lb[j:min(j+8,M)]
            if len(ch)<2: continue
            th=max(1,int(round(wp[min(j,N-1)]/B*1.8)))
            q=np.round((ch-np.array([x0,y0]))*16).astype(np.int32)
            cv2.polylines(acc_,[q],False,int(255*ab[b]),th,cv2.LINE_AA,shift=4)
    a=cv2.GaussianBlur(acc_.astype(np.float32)/255,(0,0),0.7)
    gr=cv2.GaussianBlur(np.random.RandomState(seed+3).rand(*a.shape).astype(np.float32),(0,0),1.0); gr=0.86+0.30*(gr-gr.min())/(gr.max()-gr.min()+1e-6)
    rgb=np.array(col,np.float32)[None,None,:]*gr[...,None]
    return x0,y0,np.dstack([rgb*a[...,None],a])
def _hand_bar(a,b,rng,ext=7):
    a=np.array(a,float); b=np.array(b,float); d=(b-a)/np.linalg.norm(b-a); a=a-d*rng.uniform(0,ext); b=b+d*rng.uniform(0,ext)
    ts=np.linspace(0,1,24); bend=rng.uniform(-3,3)*np.sin(np.pi*ts); n=np.array([-d[1],d[0]])
    return [tuple(a+(b-a)*t+n*bd) for t,bd in zip(ts,bend)]
def _cage_strokes(x0,total,base,S,speed=0.42):
    key=("cage_brush",int(x0),int(total),int(base),int(S),speed)
    if key in _cache: return _cache[key]
    cx=x0+total/2; R=total/2+78; ry=0.13*R; ytop=base-0.93*S; by=base+0.20*S+34
    Hd=max(40,min(0.20*R,ytop-60)); n=16; ths=[2*math.pi*(k+0.5)/n for k in range(n)]
    rng=np.random.RandomState(11); st=[]
    def add(path,w,col,layer,t0,dur): st.append(dict(path=path,w=w,col=col,layer=layer,t0=t0*speed,dur=max(0.12,dur*speed),seed=len(st)*13+5))
    add(_arc(cx,by,R,ry,180,360),21,HERO_INK,"B",0.35,0.5); add(_arc(cx,by,R,ry,0,180),21,HERO_INK,"F",0.55,0.5)
    bars=sorted(range(n),key=lambda k:math.cos(ths[k]))[::2]
    for i,k in enumerate(sorted(bars,key=lambda k:math.cos(ths[k]))):
        c_,s_=math.cos(ths[k]),math.sin(ths[k])
        add(_hand_bar((cx+R*c_,ytop+ry*s_),(cx+R*c_,by+ry*s_),rng),22,HERO_INK,"F" if s_>=0 else "B",0.9+0.11*i,0.30)
    add(_arc(cx,ytop,R,ry,180,360),21,HERO_INK,"B",2.1,0.5); add(_arc(cx,ytop,R,ry,0,180),21,HERO_INK,"F",2.3,0.5)
    for i,k in enumerate(sorted(range(n),key=lambda k:math.cos(ths[k]))[::2]):
        c_,s_=math.cos(ths[k]),math.sin(ths[k]); pts=[]
        for psi in np.linspace(0,math.radians(88),26):
            rho=R*math.cos(psi); pts.append((cx+rho*c_,ytop+ry*(rho/R)*s_-Hd*math.sin(psi)))
        add(pts,15,HERO_INK,"F" if s_>=0 else "B",2.5+0.09*i,0.35)
    psi=math.radians(46); rr=R*math.cos(psi); yy=ytop-Hd*math.sin(psi)
    add(_arc(cx,yy,rr,ry*rr/R,180,360,60),14,HERO_INK,"B",2.9,0.4); add(_arc(cx,yy,rr,ry*rr/R,0,180,60),14,HERO_INK,"F",2.95,0.4)
    add(_arc(cx,ytop-Hd-26,22,30,0,360,50),13,HERO_INK,"F",3.3,0.35)
    px,py=cx-0.744*R,by+0.6*ry
    body=[(px-61,py+78),(px+61,py+78),(px+61,py+183),(px-61,py+183)]
    shk=[(px-37,py+82),(px-37,py+40)]+[(px+37*math.cos(a),py+40-40*math.sin(a)) for a in np.linspace(math.pi,0,24)]+[(px+37,py+40),(px+37,py+82)]
    add(shk,16,HERO_INK,"F",3.5,0.35); add(body+[body[0]],15,HERO_INK,"F",3.75,0.5)
    for i in range(7): add([(px-47+i*17,py+182),(px-31+i*17,py+92)],16,HERO_ACC,"F",4.25+0.06*i,0.18)
    add(_arc(px,py+128,9,9,0,360,20),7,HERO_INK,"F",4.7,0.2); add([(px,py+128),(px,py+152)],7,HERO_INK,"F",4.85,0.15)
    _cache[key]=st; return st
def _brush_fx(L,tau,g,text,strokes_fn,word_fade=0.30):
    S,lt,total,base,x0=_word(text,900,440); st=strokes_fn(x0,total,base,S)
    v=int(tau*FPS)//3%3; wa=g*clamp01(tau/word_fade)
    def run_(layer):
        for s in st:
            if s["layer"]!=layer: continue
            p=ease_in_out((tau-s["t0"])/s["dur"])
            if p<=0: continue
            if p>=1:
                k=("bs",id(s),v)
                if k not in _cache: _cache[k]=brush_stroke(s["path"],s["w"],s["col"],1.0,s["seed"]*7+v)
                r=_cache[k]
            else: r=brush_stroke(s["path"],s["w"],s["col"],p,s["seed"]*7+v)
            if r is not None: over(L,r[2],r[0],r[1],g)
    run_("B")
    for it_ in lt: place(L,it_["sp"],x0+it_["x"],base,it_["adv"],S,gain=wa,dy=(1-ease_in_out(tau/word_fade))*30)
    run_("F")
    return {"glow":0.1}
def _fingerprint_strokes(x0,total,base,S,speed=1.0):
    key=("fp_brush",int(x0),int(total),int(base),int(S),speed)
    if key in _cache: return _cache[key]
    cx=W/2; cy=max(330,base-0.35*S+20); R=min(330,cy-30); rng=np.random.RandomState(21); st=[]
    def add(path,w,col,t0,dur): st.append(dict(path=path,w=w,col=col,layer="B",t0=t0*speed,dur=max(0.12,dur*speed),seed=len(st)*13+7))
    n=9
    for i in range(n):
        r=40+i*(R-40)/(n-1); rx=r*0.86; ry=r*1.0; a0=rng.uniform(-70,40)+(0 if i%2 else 180); span=rng.uniform(250,305)
        col=HERO_ACC if i in (2,6) else HERO_INK
        add(_arc(cx,cy,rx,ry,a0,a0+span,70),19 if i>1 else 15,col,0.12*i,0.42)
    add(_arc(cx,cy-6,20,28,20,330,30),14,HERO_ACC,0.0,0.3)
    _cache[key]=st; return st
def _thread_strokes(x0,total,base,S,speed=0.75):
    key=("thread_brush",int(x0),int(total),int(base),int(S),speed)
    if key in _cache: return _cache[key]
    cy=base-0.33*S; A=0.36*S; lam=540.0; st=[]
    def y_of(x): return cy+A*math.sin(2*math.pi*x/lam+0.6)
    def add(path,w,col,layer,t0,dur): st.append(dict(path=path,w=w,col=col,layer=layer,t0=t0*speed,dur=max(0.12,dur*speed),seed=len(st)*13+9))
    xs=[-40,300,560,830,1120]
    for k in range(4):
        pts=[(x,y_of(x)) for x in np.linspace(xs[k],xs[k+1],40)]
        add(pts,17,HERO_INK,"B" if k%2==0 else "F",0.42*k,0.55)
    cxk=W/2+40; yk=y_of(cxk)
    add(_arc(cxk,yk-52,64,52,100,430,60),13,HERO_ACC,"F",1.75,0.5)
    add(_arc(cxk+6,yk-50,22,18,0,360,30),11,HERO_ACC,"F",2.2,0.25)
    _cache[key]=st; return st
def fx_cage_brush(L,tau,g,text): return _brush_fx(L,tau,g,text,_cage_strokes)
def fx_fingerprint_brush(L,tau,g,text): return _brush_fx(L,tau,g,text,_fingerprint_strokes)
def fx_thread_brush(L,tau,g,text): return _brush_fx(L,tau,g,text,_thread_strokes)
def fx_duevoci(L,tau,g,text):
    """Frase a due voci: prima riga in bastone, seconda in corsivo con pennellata. "text": "ti costa|clienti" """
    parts=[p.strip() for p in text.split("|") if p.strip()]
    l1=parts[0] if parts else text; l2=parts[1] if len(parts)>1 else ""
    MAXW=980
    def _fit2(txt,f,cap):
        S=fit_size([txt],f,MAXW,cap)
        for _ in range(8):
            _l,t_=letters(txt,f,S,CREAM)
            if t_<=MAXW or S<=96: break
            S=max(96,int(S*MAXW/t_)-1)
        return S
    S1=_fit2(l1,F_SANS,255); S2=_fit2(l2 or l1,F_SERIF,265)
    lt1,t1=letters(l1,F_SANS,S1,CREAM)
    y1=BEHIND_CY+0.3*S1-0.46*S2
    y1+=max(0.0,175-(y1-0.80*S1))
    x1=W/2-t1/2
    for it_ in lt1:
        p=clamp01((tau-0.03*it_["i"])/0.34); e=ease_out(p)
        place(L,it_["sp"],x1+it_["x"],y1,it_["adv"],S1,sx=0.94+0.06*e,sy=0.94+0.06*e,gain=g*clamp01(tau/0.07),dy=(1-e)*34)
    if not l2: return {"glow":0.30}
    lt2,t2=letters(l2,F_SERIF,S2,CREAM); y2=y1+0.92*S2; x2=W/2-t2/2
    for it_ in lt2:
        p=clamp01((tau-0.34-0.035*it_["i"])/0.38); e=ease_back(p,1.5)
        if p<=0: continue
        place(L,it_["sp"],x2+it_["x"],y2,it_["adv"],S2,sx=0.80+0.20*e,sy=0.80+0.20*e,gain=g*clamp01(p*4))
    pr=ease_out(clamp01((tau-0.78)/0.45))
    if pr>0.01:
        r=brush_stroke([(x2-14,y2+34),(x2+t2*0.34,y2+24),(x2+t2*0.7,y2+38),(x2+t2+16,y2+28)],15,HERO_ACC,pr,45,amp=1.4,dry=0.45,ymax=LH_)
        if r is not None: over(L,r[2],r[0],r[1],g)
    return {"glow":0.30}
# nome -> (funzione, durata di default)
FX={"slice":(fx_slice,1.9),"ruler":(fx_ruler,2.1),"cage":(fx_cage,2.3),"rise":(fx_rise,2.0),
    "scatter":(fx_scatter,2.2),"fill":(fx_fill,2.0),"think":(fx_think,2.1),"strike":(fx_strike,1.75),"stamp":(fx_stamp,1.6),
    "cage_brush":(fx_cage_brush,2.7),"fingerprint_brush":(fx_fingerprint_brush,2.6),"thread_brush":(fx_thread_brush,2.0),"duevoci":(fx_duevoci,2.4)}
# colpo di zoom associato all'effetto: (ritardo, ampiezza, durata, scossa)
PUNCH_RULES={"slice":(0.35,0.03,0.45,0),"ruler":(0.05,0.025,0.4,0),"cage":(GAB_T0+0.06*7+0.25,0.06,0.5,10),
    "cage_brush":(1.35,0.04,0.45,6),"rise":(0.0,0.03,0.4,0),"scatter":(0.5,0.03,0.45,0),"fill":(0.0,0.035,0.55,0),"think":(0.0,0.03,0.45,0),"stamp":(0.3,0.065,0.5,11)}
def _pil_pm(img):
    a=np.asarray(img,np.float32)/255.0; return np.dstack([a[...,:3]*a[...,3:4]*255.0,a[...,3]])
def _sticker(L,cx,cy,size,tau,g,rot=12):
    p=clamp01(tau/0.35); e=ease_back(p,2.2)
    if e<=0.02: return
    n=int(size*1.6); img=Image.new("RGBA",(n*3,n*3),(0,0,0,0)); d=ImageDraw.Draw(img); c=n*1.5; r=size*1.5*0.46
    for a in (0,45,90,135):
        a_=math.radians(a); d.line([(c-r*math.cos(a_),c-r*math.sin(a_)),(c+r*math.cos(a_),c+r*math.sin(a_))],fill=RUG+(255,),width=int(size*1.5*0.17))
    for a in (0,45,90,135):
        a_=math.radians(a)
        for sg in (-1,1): d.ellipse([c+sg*r*math.cos(a_)-size*1.5*0.085,c+sg*r*math.sin(a_)-size*1.5*0.085,c+sg*r*math.cos(a_)+size*1.5*0.085,c+sg*r*math.sin(a_)+size*1.5*0.085],fill=RUG+(255,))
    img=img.resize((n,n),Image.LANCZOS); M=cv2.getRotationMatrix2D((n/2,n/2),rot,max(0.05,e))
    pm=_pil_pm(img); pm=cv2.warpAffine(pm,M,(n,n),flags=cv2.INTER_LINEAR,borderValue=(0,0,0,0)); over(L,pm,int(cx-n/2),int(cy-n/2),g*clamp01(p*3))
def _run_fx(fn,L,tau,g,text,bf,st):
    global BIGF
    BIGF=bf; r=fn(L,tau,g,text)
    if st:
        if "|" in text: _sticker(L,W-150,BEHIND_CY-150,110,tau-0.45,g)
        else:
            S,lt,total,base,x0=_word(text,900,440); _sticker(L,min(W-80,x0+total+30),base-0.95*S,110,tau-0.45,g)
    return r

# ===================== B-ROLL IN MOTION GRAPHIC =====================
BROLL=[]
BR_BG=BLU; BR_BG2=(34,92,120); BR_CREAM=(255,255,255); BR_INK=BLU
def _wrap(text,fnt,maxw):
    out=[]; cur=""
    for w_ in text.split():
        t_=(cur+" "+w_).strip()
        if fnt.getlength(t_)<=maxw or not cur: cur=t_
        else: out.append(cur); cur=w_
    if cur: out.append(cur)
    return out
def _br_bg():
    k=("brbg",)
    if k in _cache: return _cache[k]
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    v=np.clip(np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H*0.42)/(H*0.62))**2),0,1)
    c0=np.array(BR_BG2,np.float32); c1=np.array(BR_BG,np.float32)
    bg=c0*(1-v[...,None])+c1*v[...,None]
    g=np.random.RandomState(5).rand(H,W).astype(np.float32); g=cv2.GaussianBlur(g,(0,0),1.1); g=(g-g.mean())/(g.std()+1e-6)
    bg=np.clip(bg+g[...,None]*3.0,0,255); _cache[k]=bg; return bg
def _br_title(L,tau,text):
    if not text: return
    p=ease_out(clamp01((tau-0.05)/0.35)); img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    f=font(F_SERIF,92); d.text((W/2,150-(1-p)*24),text,font=f,fill=WHITE+(int(255*p),),anchor="mm")
    over(L,_pil_pm(img),0,0,1.0)
    q=ease_out(clamp01((tau-0.2)/0.4)); r=brush_stroke([(W/2-230,205),(W/2,214),(W/2+230,203)],12,HERO_ACC,q,31,ymax=H)
    if r is not None: over(L,r[2],r[0],r[1],1.0)
def _br_icon(name,t,size):
    return cv2.resize(_icon_sprite(name,t),(size,size),interpolation=cv2.INTER_AREA)
def _arrow_brush(L,x0,y0,x1,y1,p,seed):
    mx=(x0+x1)/2+18
    r=brush_stroke([(x0,y0),(mx,(y0+y1)/2),(x1,y1)],15,HERO_ACC,p,seed,amp=1.6,dry=0.4,ymax=H)
    if r is not None: over(L,r[2],r[0],r[1],1.0)
    if p>0.82:
        q=clamp01((p-0.82)/0.18)
        for dx in (-34,34):
            r2=brush_stroke([(x1+dx,y1-36),(x1,y1+6)],12,HERO_ACC,q,seed+7,amp=1.0,dry=0.3,ymax=H)
            if r2 is not None: over(L,r2[2],r2[0],r2[1],1.0)
def _balloon(L,cx,cy,text,p,icon=None,tau_i=0.0,tail=0,fs=74,maxw=700):
    e=ease_back(clamp01(p),1.9); al=int(255*clamp01(p*2.5))
    if e<=0.03: return 0,0
    f=font(F_SANS,fs); lines=_wrap(text,f,maxw)
    tw=int(max(f.getlength(l) for l in lines)); ic=170 if icon else 0
    w_=tw+ic+130; h_=max(210,len(lines)*int(fs*1.3)+96)
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    x0=cx-w_/2
    d.rounded_rectangle([x0,cy-h_/2,x0+w_,cy+h_/2],radius=min(60,h_//2),fill=BR_CREAM+(al,))
    if tail:
        tx=x0+70 if tail<0 else x0+w_-70
        d.polygon([(tx-12,cy+h_/2-6),(tx+62,cy+h_/2-6),(tx+(-16 if tail<0 else 76),cy+h_/2+58)],fill=BR_CREAM+(al,))
    ty=cy-(len(lines)-1)*fs*0.65
    for k,l in enumerate(lines): d.text((x0+65+ic,ty+k*fs*1.3),l,font=f,fill=BR_INK+(al,),anchor="lm")
    pm=_pil_pm(img)
    if abs(e-1)>0.01:
        M=np.float32([[e,0,(1-e)*cx],[0,e,(1-e)*cy]]); pm=cv2.warpAffine(pm,M,(W,H),flags=cv2.INTER_LINEAR)
    over(L,pm,0,0,1.0)
    if icon:
        ii=_br_icon(icon,max(0.0,tau_i),int(170*e)); over(L,ii,int(cx-w_*e/2+36*e),int(cy-85*e),clamp01(p*2.5))
    return w_,h_
def _br_schema(L,tau,cfg):
    nodes=cfg["nodes"]; n=len(nodes); D=cfg.get("_dur",2.2)
    _br_title(L,tau,cfg.get("title"))
    y0,y1=max(430,int(H*0.26)),1420
    ys=[y0+(y1-y0)*i/max(1,n-1) for i in range(n)] if n>1 else [(y0+y1)/2]
    step=(0.60*D)/max(1,n); t0s=[0.22*D+step*i for i in range(n)]
    hs=[]
    for i,nd in enumerate(nodes):
        icon,label=(nd if isinstance(nd,(list,tuple)) else (None,nd))
        p=clamp01((tau-t0s[i])/0.40)
        w_,h_=_balloon(L,W/2,ys[i],label,p,icon=icon,tau_i=tau-t0s[i])
        hs.append(h_ or 190)
    for i in range(n-1):
        q=clamp01((tau-t0s[i]-0.30)/0.38)
        if q<=0: continue
        ya=ys[i]+hs[i]/2+16; yb=ys[i+1]-hs[i+1]/2-18
        _arrow_brush(L,W/2,ya,W/2,yb,q,40+i)
        if cfg.get("negato") and q>0.9:
            z=clamp01((q-0.9)/0.1); cy_=(ya+yb)/2
            for k_,(dx,dy) in enumerate(((-52,-52),(52,-52))):
                r=brush_stroke([(W/2-dx,cy_-dy),(W/2+dx,cy_+dy)],16,HERO_ACC,z,70+k_,amp=1.0,dry=0.3,ymax=H)
                if r is not None: over(L,r[2],r[0],r[1],1.0)
FORME={
 "freccia_su": lambda: [(150,1330),(360,1180),(560,1240),(760,900),(930,620)],
 "zigzag":     lambda: [(140,900),(300,1180),(450,820),(610,1160),(770,760),(930,1040)],
 "onda":       lambda: [(120,1000+260*math.sin(x/160.0)) for x in range(0,840,30)],
 "cerchio":    lambda: [(540+360*math.cos(math.radians(a)),980+360*math.sin(math.radians(a))) for a in np.linspace(-80,290,70)],
 "discesa":    lambda: [(150,700),(380,860),(560,820),(780,1150),(930,1330)],
}
def _br_linea(L,tau,cfg):
    D=cfg.get("_dur",2.2); _br_title(L,tau,cfg.get("title"))
    forma=cfg.get("forma","freccia_su")
    pts=FORME.get(forma,FORME["freccia_su"])()
    if forma=="onda": pts=[(x+120,y) for x,y in pts]
    p=clamp01((tau-0.12*D)/(0.58*D))
    r=brush_stroke(pts,22,BR_CREAM,p,19,amp=1.6,dry=0.35,ymax=H)
    if r is not None: over(L,r[2],r[0],r[1],1.0)
    if cfg.get("punta",forma in ("freccia_su","discesa")) and p>0.88:
        q=clamp01((p-0.88)/0.12); x1,y1=pts[-1]; x0_,y0_=pts[-2]
        base=math.degrees(math.atan2(y1-y0_,x1-x0_))
        for k_,da in ((0,148),(1,-148)):
            a_=math.radians(base+da); r2=brush_stroke([(x1,y1),(x1+100*math.cos(a_),y1+100*math.sin(a_))],18,BR_CREAM,q,23+k_,amp=1.0,dry=0.3,ymax=H)
            if r2 is not None: over(L,r2[2],r2[0],r2[1],1.0)
    if cfg.get("nota"):
        q=clamp01((tau-0.62*D)/0.35)
        if q>0.02:
            img=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(img).text((W/2,1560),cfg["nota"],font=font(F_HAND,96),fill=HERO_ACC+(int(255*q),),anchor="mm")
            over(L,_pil_pm(img),0,0,1.0)
def _br_bubbles(L,tau,cfg):
    items=cfg["items"]; _br_title(L,tau,cfg.get("title"))
    for i,txt in enumerate(items):
        t0=0.3+0.42*i; p=clamp01((tau-t0)/0.4)
        if p<=0: continue
        e=ease_back(p,1.9); left=(i%2==0); f=font(F_SANS,58); lines=_wrap(txt,f,620)
        w_=int(max(f.getlength(l) for l in lines))+110; h_=len(lines)*76+70; cy=470+i*330
        x0=130 if left else W-130-w_; sc=0.55+0.45*e; shake=(8*math.sin(tau*40)*clamp01(1-(tau-t0-0.4)/0.5) if i==len(items)-1 and tau>t0+0.4 else 0)
        img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img); al=int(255*clamp01(p*2.5))
        d.rounded_rectangle([x0,cy-h_/2,x0+w_,cy+h_/2],radius=50,fill=BR_CREAM+(al,))
        tx=x0+60 if left else x0+w_-60
        d.polygon([(tx-10,cy+h_/2-6),(tx+60,cy+h_/2-6),(tx+(-14 if left else 74),cy+h_/2+56)],fill=BR_CREAM+(al,))
        for j,l in enumerate(lines): d.text((x0+55,cy-h_/2+35+38+j*76),l,font=f,fill=BR_INK+(al,),anchor="lm")
        M=np.float32([[sc,0,(1-sc)*(x0+w_/2)+shake],[0,sc,(1-sc)*cy]])
        pm=cv2.warpAffine(_pil_pm(img),M,(W,H),flags=cv2.INTER_LINEAR)
        over(L,pm,0,0,1.0)
BR_FN={"schema":_br_schema,"flow":_br_schema,"fumetti":_br_bubbles,"bubbles":_br_bubbles,"linea":_br_linea}
def active_broll(t):
    for s,e,cfg in BROLL:
        if s<=t<=e: return (s,e,cfg)
    return None
def draw_broll(frame,t,br):
    s,e,cfg=br; tau=t-s; tin=0.30; tout=0.24
    pin=ease_out(clamp01(tau/tin)); pout=ease_in(clamp01((t-(e-tout))/tout))
    yy=np.arange(H,dtype=np.float32)[:,None]; xx=np.arange(W,dtype=np.float32)[None,:]
    wob=14*np.sin(xx/70.0)
    mask=np.clip((yy-(H*(1-pin)+wob))/18,0,1)*(1-pout)
    m=mask[...,None]; bg=_br_bg()
    frame[:]=np.clip(frame.astype(np.float32)*(1-m)+bg*m,0,255).astype(np.uint8)
    L=np.zeros((H,W,4),np.float32); BR_FN[cfg["type"]](L,tau,cfg)
    a=L[...,3:4]*m*(1-pout); rgb=L[...,:3]*m*(1-pout)
    frame[:]=np.clip(frame.astype(np.float32)*(1-a)+rgb,0,255).astype(np.uint8)

# ===================== SUONI (sintetizzati, nitidi; niente fruscii sul parlato) =====================
