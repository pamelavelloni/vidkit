#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vidkit: video verticali di Pamela (Instagram / TikTok, 9:16). File unico (novembre 2026).

Comandi, in ordine (istruzioni complete nella skill "video-social-verticali"):
  setup     font, modello persona/sfondo, modello di riconoscimento vocale (una volta per sessione)
  prep      audio, foglio delle inquadrature sheet.png, pause
  asr       tempi reali delle parole sul girato -> words_orig.json (trascrizione da config "blocks" o da trascrizione.txt)
  mappa     il parlato frase per frase con le pause, per scrivere il copione
  montage   taglia silenzi / applica il copione -> edited.mov + map.json
  timing    sposta le parole sul montato -> words.json (stampa il parlato montato da rileggere)
  check     controlla config e sincronia
  test t1 t2 ...   fotogrammi di prova -> test_row.png
  icone n1 n2 ...  prova delle icone stile 05 -> icone.png
  bozza     VIDKIT_FASE=1 (testi) o 2 (+ animazioni): render veloce, un fotogramma su due
  full      render finale con suoni e volume -14 LUFS -> out.mp4
  audio     rifa SOLO suoni e volume su out.mp4 gia' renderizzato (pochi secondi)

Cartella di lavoro: in.mov + config.json (+ trascrizione.txt). VIDKIT_CONFIG, VIDKIT_ASSETS per cambiare i percorsi.
"""
import sys, json, re, math, subprocess, os, shutil
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS=1080,1920,30
CFG_PATH=os.environ.get("VIDKIT_CONFIG","config.json")
CFG=json.load(open(CFG_PATH)) if os.path.exists(CFG_PATH) else {}
ASSETS=os.environ.get("VIDKIT_ASSETS",os.path.expanduser("~/vidkit_assets"))
FD=ASSETS+"/fonts/"; SEG_MODEL=ASSETS+"/selfie_segmentation.tflite"
# font: Eroina = Hanken Grotesk ExtraBold, Saggia = Playfair Display corsivo, Burlona = Nothing You Could Do (a mano)
F_SANS=FD+"HankenGrotesk-ExtraBold.ttf"; F_BOLD=F_SANS; F_REG=FD+"HankenGrotesk-Regular.ttf"
F_SERIF=FD+"PlayfairDisplay-MediumItalic.ttf"; F_HAND=FD+"NothingYouCouldDo.ttf"
BIGF=F_SANS

# ---- palette "Blu, bordeaux e ruggine": blu e bordeaux in primo piano, ruggine solo nei dettagli, bianco ----
BLU=(16,58,80); BORD=(92,26,51); RUG=(184,87,42)
WHITE=(255,255,255); ACC=RUG; CREAM=WHITE
SIZE_BASE=88; SIZE_KEY=128
FRONT_CY=CFG.get("front_cy",1370)
BEHIND_CY=CFG.get("behind_cy",335)
BBOX=CFG.get("behind_box")            # solo per forzare a mano la posizione dei testi grandi

words=[]; CHUNKS=None; EFFECTS=[]; PUNCH=[]; GRAPHICS=[]; KEYKIND={}; CAM=[]; SHOTS=[]
def norm(w): return re.sub(r"[^\wàèéìòù]","",w.lower())
def run(cmd,**kw): return subprocess.run(cmd,shell=True,**kw)


# ===================== STRUMENTI DI BASE (sprite, testo, easing) =====================
_cache={}
def font(path,size):
    k=(path,size)
    if k not in _cache: _cache[k]=ImageFont.truetype(path,size)
    return _cache[k]
SHS=0.6
def sprite(text,path,size,color,shadow=True,key=None):
    k=("s",text,path,size,color,shadow,key)
    if k in _cache: return _cache[k]
    f=font(path,size); pad=int(size*0.35)+14
    l,t,r,b=f.getbbox(text,anchor="ls")
    w=int(r-l)+2*pad; h=int(size*1.5)+2*pad; base=pad+int(size*1.05)
    A=Image.new("L",(w,h),0); d=ImageDraw.Draw(A); d.text((pad-l,base),text,font=f,fill=255,anchor="ls")
    a=np.asarray(A,np.float32)/255
    if shadow:
        sh=np.asarray(A.filter(ImageFilter.GaussianBlur(max(5,size*0.07))),np.float32)/255*(0.85 if key=='b' else SHS)
        sh=np.roll(sh,int(size*0.05),axis=0)
        alpha=a+sh*(1-a)
    else: alpha=a
    rgb=np.zeros((h,w,3),np.float32); rgb[:]=np.array(color,np.float32)
    pm=np.dstack([rgb*a[...,None]+np.array(BLU,np.float32)*(alpha-a)[...,None],alpha])
    adv=f.getlength(text)
    out=dict(img=pm,w=w,h=h,base=base,pad=pad,adv=adv,l=l)
    _cache[k]=out; return out
def scaled(sp,s):
    if abs(s-1)<1e-3: return sp["img"],sp["w"],sp["h"],sp["base"],sp["pad"]
    nw=max(2,int(sp["w"]*s)); nh=max(2,int(sp["h"]*s))
    return cv2.resize(sp["img"],(nw,nh),interpolation=cv2.INTER_LINEAR),nw,nh,int(sp["base"]*s),int(sp["pad"]*s)
def blend(frame,pm,x,y,mask=None,gain=1.0):
    h,w=pm.shape[:2]
    x0,y0=max(0,x),max(0,y); x1,y1=min(W,x+w),min(H,y+h)
    if x1<=x0 or y1<=y0: return
    p=pm[y0-y:y1-y,x0-x:x1-x]
    a=p[...,3:4]*gain
    rgb=p[...,:3]*gain
    if mask is not None:
        m=mask[y0:y1,x0:x1,None]
        a=a*(1-m); rgb=rgb*(1-m)
    reg=frame[y0:y1,x0:x1].astype(np.float32)
    frame[y0:y1,x0:x1]=np.clip(reg*(1-a)+rgb,0,255).astype(np.uint8)
def ease_back(x,c1=1.7):
    x=min(max(x,0),1); c3=c1+1
    return 1+c3*(x-1)**3+c1*(x-1)**2
def ease_out(x): x=min(max(x,0),1); return 1-(1-x)**3
def ease_in(x): x=min(max(x,0),1); return x*x*x
def ease_in_out(x): x=min(max(x,0),1); return x*x*(3-2*x)
def clamp01(x): return min(max(x,0.0),1.0)

# ===================== SOTTOTITOLI =====================
FUNC={"la","le","il","lo","a","di","che","tu","quel","un","e","o","in","mi","si","non","come","se","ma","è","l'avrebbe"}
def build_chunks():
    chunks=[];cur=[]
    for i,w in enumerate(words):
        cur.append(i)
        nxt=words[i+1] if i+1<len(words) else None
        gap=(nxt["s"]-w["e"]) if nxt else 9
        tok=w["w"]; core=tok.lower().strip(",.?!:")
        strong=bool(re.search(r"[.?!:]$",tok)); comma=tok.endswith(",")
        if nxt is None or strong or gap>0.45 or (comma and len(cur)>=2) or (len(cur)>=3 and core not in FUNC) or len(cur)>=5:
            chunks.append(cur);cur=[]
    def contiguous(a,b): return words[b[0]]["s"]-words[a[-1]]["e"]<0.45
    out=[]
    i=0
    while i<len(chunks):
        c=chunks[i]
        if len(c)==1:
            if out and contiguous(out[-1],c) and len(out[-1])<=4 and not re.search(r"[.?!:]$",words[out[-1][-1]]["w"]):
                out[-1]=out[-1]+c; i+=1; continue
            if i+1<len(chunks) and contiguous(c,chunks[i+1]) and len(chunks[i+1])<=3 and not re.search(r"[.?!:]$",words[c[-1]]["w"]):
                out.append(c+chunks[i+1]); i+=2; continue
        out.append(c); i+=1
    return out
def word_sprite(w):
    if w["role"]=="k": return sprite(w["w"],F_HAND,int(SIZE_KEY*1.45),WHITE) if w.get("kind")=="hand" else sprite(w["w"],F_SERIF,SIZE_KEY,WHITE)
    return sprite(w["w"],F_SANS,SIZE_BASE,WHITE)
def layout(ci):
    ws=[words[i] for i in CHUNKS[ci]]
    sps=[word_sprite(w) for w in ws]
    gap=0.3*SIZE_BASE
    def lw(lst): return sum(s["adv"] for s in lst)+gap*(len(lst)-1)
    lines=[list(range(len(ws)))]
    if lw(sps)>940:
        best=min(range(1,len(ws)),key=lambda k:abs(lw(sps[:k])-lw(sps[k:])))
        lines=[list(range(best)),list(range(best,len(ws)))]
    pos=[None]*len(ws)
    LH=SIZE_BASE*1.45
    y0=FRONT_CY-(len(lines)-1)*LH/2+SIZE_BASE*0.33
    for li,ln in enumerate(lines):
        tw=lw([sps[j] for j in ln]); x=W/2-tw/2
        for j in ln:
            pos[j]=(x,y0+li*LH); x+=sps[j]["adv"]+gap
    return ws,sps,pos

# ===================== LAYER 'DIETRO DI LEI' (testi grandi) =====================
LH_=1000
def over(L,img,x,y,gain=1.0):
    h,w=img.shape[:2]
    x0,y0=max(0,x),max(0,y); x1,y1=min(L.shape[1],x+w),min(L.shape[0],y+h)
    if x1<=x0 or y1<=y0: return
    p=img[y0-y:y1-y,x0-x:x1-x]*gain
    reg=L[y0:y1,x0:x1]
    L[y0:y1,x0:x1]=p+reg*(1-p[...,3:4])
TRACK={F_SANS:-0.045}
def _trk(path,size): return size*TRACK.get(path,0.0)
def letters(text,path,size,color,key='b'):
    f=font(path,size); out=[]; tr=_trk(path,size)
    for i,ch in enumerate(text):
        if ch==' ': continue
        sp=sprite(ch,path,size,color,True,key)
        x=f.getlength(text[:i])+i*tr; adv=f.getlength(text[:i+1])-f.getlength(text[:i])
        out.append(dict(ch=ch,sp=sp,x=x,adv=adv,i=i,n=len(text)))
    return out,f.getlength(text)+max(0,len(text)-1)*tr
def ring_sprite(ch,path,size,color):
    k=("ring",ch,path,size,color)
    if k in _cache: return _cache[k]
    sp=sprite(ch,path,size,color,True,'b')
    f=font(path,size); pad=sp["pad"]; l=sp["l"]
    w,h,base=sp["w"],sp["h"],sp["base"]
    sw=max(3,int(size*0.012))
    A=Image.new("L",(w,h),0); ImageDraw.Draw(A).text((pad-l,base),ch,font=f,fill=255,anchor="ls")
    S=Image.new("L",(w,h),0); ImageDraw.Draw(S).text((pad-l,base),ch,font=f,fill=255,anchor="ls",stroke_width=sw,stroke_fill=255)
    a=np.asarray(A,np.float32)/255; s_=np.asarray(S,np.float32)/255
    ring=np.clip(s_-a,0,1)
    rgb=np.zeros((h,w,3),np.float32); rgb[:]=np.array(color,np.float32)
    out=np.dstack([rgb*ring[...,None],ring]); _cache[k]=out; return out
def place(L,sp,lx,base,adv,size,sx=1.0,sy=1.0,rot=0.0,gain=1.0,blur=0.0,dx=0.0,dy=0.0,img=None):
    if gain<=0.003: return
    img=sp["img"] if img is None else img
    h,w=img.shape[:2]
    px=(sp["pad"]-sp["l"])+adv/2; py=sp["base"]-size*0.28
    tx=lx+adv/2+dx; ty=base-size*0.28+dy
    c,s_=math.cos(math.radians(rot)),math.sin(math.radians(rot))
    Lm=np.array([[c*sx,-s_*sy],[s_*sx,c*sy]],np.float32)
    corners=np.array([[0,0],[w,0],[w,h],[0,h]],np.float32)-np.array([px,py],np.float32)
    dst=corners@Lm.T+np.array([tx,ty],np.float32)
    m=int(blur*3)+2
    x0=int(math.floor(dst[:,0].min()))-m; y0=int(math.floor(dst[:,1].min()))-m
    x1=int(math.ceil(dst[:,0].max()))+m; y1=int(math.ceil(dst[:,1].max()))+m
    bw,bh=x1-x0,y1-y0
    if bw<=1 or bh<=1 or bw>4000 or bh>4000: return
    t0=np.array([tx-x0,ty-y0],np.float32)-Lm@np.array([px,py],np.float32)
    M=np.hstack([Lm,t0[:,None]]).astype(np.float32)
    out=cv2.warpAffine(img,M,(bw,bh),flags=cv2.INTER_LINEAR,borderValue=(0,0,0,0))
    if blur>0.3: out=cv2.GaussianBlur(out,(0,0),blur)
    over(L,out,x0,y0,gain)
def fit_size(lines,path,maxw,maxS,base=360):
    f=font(path,base); wmax=max(f.getlength(l) for l in lines)
    return int(max(150,min(maxS,base*maxw/wmax)))
def rect(L,x0,y0,x1,y1,color,alpha=1.0):
    x0,y0,x1,y1=int(x0),int(y0),int(x1),int(y1)
    if x1<=x0 or y1<=y0: return
    h,w=y1-y0,x1-x0
    patch=np.zeros((h,w,4),np.float32); patch[...,:3]=np.array(color,np.float32); patch[...,3]=1
    e=min(4,h//2)
    if e>0:
        ramp=np.ones(h,np.float32); ramp[:e]=np.linspace(0.25,1,e); ramp[-e:]=np.linspace(1,0.25,e); patch*=ramp[:,None,None]
    pm=patch.copy(); pm[...,:3]=np.array(color,np.float32)*patch[...,3:4]
    over(L,pm,x0,y0,alpha)
def dot(L,cx,cy,r,color,alpha):
    n=int(r*2+6); yy,xx=np.mgrid[0:n,0:n].astype(np.float32); c=n/2
    d=np.sqrt((xx-c)**2+(yy-c)**2); a=np.clip(r+0.8-d,0,1)
    pm=np.dstack([np.array(color,np.float32)[0]*a,np.array(color,np.float32)[1]*a,np.array(color,np.float32)[2]*a,a])
    over(L,pm,int(cx-c),int(cy-c),alpha)
def _word(text,maxw=1000,maxS=440):
    S=fit_size([text],BIGF,maxw,maxS); lt,total=letters(text,BIGF,S,CREAM)
    return S,lt,total,BEHIND_CY+0.3*S,W/2-total/2
def shift_x(a,dx):
    out=np.zeros_like(a); dx=int(dx)
    if dx>=0: out[:,dx:]=a[:,:a.shape[1]-dx] if dx>0 else a
    else: out[:,:dx]=a[:,-dx:]
    return out
GAB_T0=0.25
def fx_fill(L,tau,g,text):
    S=fit_size([text],BIGF,1000,440)
    lt,total=letters(text,BIGF,S,CREAM)
    base=BEHIND_CY+0.3*S; x0=W/2-total/2; n=len(lt)
    for it in lt:
        i=it["i"]; p=clamp01((tau-0.05*i)/0.6)
        sp=it["sp"]; ring=ring_sprite(it["ch"],BIGF,S,CREAM)
        rise=(1-ease_out(p))*34
        a_ring=clamp01(tau/0.15)*g
        place(L,sp,x0+it["x"],base,it["adv"],S,img=ring,gain=a_ring,dy=rise)
        img=sp["img"]
        if p<1:
            hh=img.shape[0]; ycut=(sp["base"]+0.32*S)-p*(1.2*S)
            vis=np.clip((np.arange(hh)-ycut)/14+0.5,0,1).astype(np.float32)[:,None,None]
            img=img*vis
        if p>0: place(L,sp,x0+it["x"],base,it["adv"],S,img=img,gain=g,dy=rise)
    done=0.05*n+0.7
    return {"glow":0.25+0.55*clamp01((tau-done+0.2)/0.3)*(1-clamp01((tau-done-0.5)/0.5))}
def fx_think(L,tau,g,text):
    S=fit_size([text],BIGF,1000,440)
    lt,total=letters(text,BIGF,S,CREAM)
    base=BEHIND_CY+0.3*S; x0=W/2-total/2
    for it in lt:
        i=it["i"]; p=clamp01((tau-0.07*i)/0.42)
        if p<=0: continue
        e=ease_out(p)
        bob=7*math.sin(2*math.pi*(tau*0.8+i*0.13))*clamp01((tau-0.6)/0.4)
        place(L,it["sp"],x0+it["x"],base,it["adv"],S,sx=0.88+0.12*e,sy=0.88+0.12*e,gain=g*e,blur=(1-e)*16,dy=(1-e)*44+bob)
    ytop=max(80,base-0.98*S)
    for j in range(3):
        ph=((tau-0.7)*1.25-j*0.22)%1.0
        pulse=max(0,math.sin(math.pi*ph))
        if tau>0.7: dot(L,W/2+(j-1)*78,ytop,13+11*pulse,CREAM,g*(0.45+0.55*pulse))
    return {"glow":0.3+0.2*math.sin(tau*3)*0.5}
def fx_strike(L,tau,g,text):
    S=fit_size([text],BIGF,1000,440)
    lt,total=letters(text,BIGF,S,CREAM)
    base=BEHIND_CY+0.3*S; x0=W/2-total/2
    for it in lt:
        i=it["i"]; pin=clamp01((tau-0.03*i)/0.35); q=clamp01((tau-1.12-0.045*i)/0.45)
        dx=-(1-ease_out(pin))*140+ease_in(q)*300
        place(L,it["sp"],x0+it["x"],base,it["adv"],S,gain=g*pin*(1-q),dx=dx)
    pr=ease_out(clamp01((tau-0.62)/0.28)); fade=1-clamp01((tau-1.18)/0.4)
    y=base-0.30*S
    rect(L,x0-14,y-0.022*S,x0-14+(total+28)*pr,y+0.022*S,(255,255,255),g*fade)
    return {"glow":0.2}
def fx_slice(L,tau,g,text):
    S,lt,total,base,x0=_word(text)
    T=np.zeros_like(L)
    for it in lt: place(T,it["sp"],x0+it["x"],base,it["adv"],S,gain=g*clamp01(tau/0.12))
    split=int(base-0.30*S); p=ease_out(clamp01(tau/0.45)); dx=(1-p)*120
    T2=np.concatenate([shift_x(T[:split],-dx),shift_x(T[split:],dx)],axis=0)
    if tau<0.55: rect(T2,x0-20,split-3,x0+total+20,split+3,(255,255,255),g*(1-clamp01(tau/0.55)))
    L[:]=T2+L*(1-T2[...,3:4])
    return {"glow":0.3}
def fx_ruler(L,tau,g,text):
    S,lt,total,base,x0=_word(text)
    n=len(lt)
    for it in lt:
        i=it["i"]; p=clamp01((tau-0.07*i)/0.2); e=1-(1-p)**4
        place(L,it["sp"],x0+it["x"],base,it["adv"],S,gain=g*clamp01(p*5),dy=-(1-e)*170)
    rt=ease_out(clamp01((tau-0.07*n-0.1)/0.5)); y=base+0.14*S
    if rt>0:
        rect(L,x0,y,x0+total*rt,y+6,(255,255,255),g)
        k=0
        while x0+k*22<=x0+total*rt:
            h=28 if k%5==0 else 14
            rect(L,x0+k*22-2,y,x0+k*22+2,y+6+h,(255,255,255),g*0.9); k+=1
    return {"glow":0.2}
def fx_cage(L,tau,g,text):
    S,lt,total,base,x0=_word(text,900,440)
    for it in lt:
        p=clamp01((tau-0.04*it["i"])/0.3); place(L,it["sp"],x0+it["x"],base,it["adv"],S,gain=g*p,dy=(1-ease_out(p))*40)
    top=base-1.0*S; bot=base+0.2*S; Hh=bot-top; n=8
    for k,x in enumerate(np.linspace(x0-14,x0+total+14,n)):
        p=clamp01((tau-GAB_T0-0.06*k)/0.25); e=ease_in(p)
        ytop=top-(1-e)*(Hh+170)
        if p>0: rect(L,x-7,ytop,x+7,ytop+Hh,(255,255,255),g)
    tl=GAB_T0+0.06*(n-1)+0.25
    if tau>tl:
        pr=ease_out(clamp01((tau-tl)/0.15))
        rect(L,x0-26,top-12,x0-26+(total+52)*pr,top+4,(255,255,255),g)
        rect(L,x0-26,bot-4,x0-26+(total+52)*pr,bot+12,(255,255,255),g)
    return {"glow":0.2}
def fx_rise(L,tau,g,text):
    S,lt,total,base,x0=_word(text,1000,420)
    n=len(lt); rise=0.045*S
    for it in lt:
        i=it["i"]; p=clamp01((tau-0.06*i)/0.35); e=ease_out(p)
        dy=-(i-(n-1)/2)*rise+(1-e)*55
        place(L,it["sp"],x0+it["x"],base,it["adv"],S,gain=g*clamp01(p*3),dy=dy)
    return {"glow":0.2+0.3*clamp01((tau-0.5)/0.4)}
def fx_scatter(L,tau,g,text):
    S,lt,total,base,x0=_word(text,1000,400)
    rng=np.random.RandomState(7)
    offs=[(rng.uniform(-230,230),rng.uniform(-170,170),rng.uniform(-35,35),rng.uniform(0.75,1.25)) for _ in lt]
    n=len(lt)
    for it in lt:
        i=it["i"]; dx0,dy0,r0,s0_=offs[i]
        q=clamp01((tau-0.3-0.025*i)/0.4); k=1-ease_back(q,1.4)
        place(L,it["sp"],x0+it["x"],base,it["adv"],S,sx=1+(s0_-1)*k,sy=1+(s0_-1)*k,rot=r0*k,gain=g*clamp01(tau/0.15),dx=dx0*k,dy=dy0*k)
    tq=ease_out(clamp01((tau-0.3-0.025*n-0.25)/0.3)); y=base+0.12*S
    if tq>0: rect(L,x0,y,x0+total*tq,y+6,ACC,g*0.9)
    return {"glow":0.25}
def fx_stamp(L,tau,g,text):
    S,lt,total,base,x0=_word(text,1000,440); tc=0.25
    for it in lt:
        p=clamp01((tau-tc)/0.2); sc=2.0-1.0*ease_in(p) if p<1 else 1.0; sq=0.0
        if p>=1: r=clamp01((tau-tc-0.2)/0.22); sq=0.13*(1-r)*math.cos(r*6)
        lx=W/2+(x0+it["x"]+it["adv"]/2-W/2)*sc-it["adv"]/2
        place(L,it["sp"],lx,base+(sc-1)*S*0.1,it["adv"],S,sx=sc*(1+sq),sy=sc*(1-sq),gain=g*clamp01((tau-tc)/0.07),blur=(1-p)*9)
    return {"glow":0.25+0.7*clamp01(1-(tau-tc-0.2)/0.5) if tau>tc else 0.25}

# Testi grandi piazzati da soli: se sopra la testa c'e' spazio vanno sopra a tutta larghezza; se no nella fascia
# libera piu' larga di lato, all'altezza del viso, e possono entrare un po' dietro i capelli (livello "dietro").
PLACE={}
BIG_MIN=CFG.get("big_min",620)
def _auto_place(mask):
    m=mask[:1100]>0.35
    rows=np.where(m.any(axis=1))[0]; top=int(rows[0]) if len(rows) else 1100
    if top>=380:
        return (1.0,W/2,max(200,top/2+40))
    best=None
    for cy in (260,340,420,500,580):
        occ=m[max(0,cy-110):cy+110].mean(axis=0)>0.04
        x=0
        while x<W:
            if not occ[x]:
                y=x
                while y<W and not occ[y]: y+=1
                if best is None or y-x>best[0]+30: best=(y-x,x,y,cy)
                x=y
            else: x+=1
    if best is None: return (1.0,W/2,BEHIND_CY)
    free,x0,x1,cy=best
    wbox=min(1000,max(BIG_MIN,free*1.10))
    k=wbox/1000.0
    cx=(x0+x1)/2
    if x0>W/2-50: cx=x1-k*500
    if x1<W/2+50: cx=x0+k*500
    cx=min(W-24-k*500,max(24+k*500,cx))
    return (k,cx,cy)
def draw_behind(frame,t,maskfull):
    act=[e for e in EFFECTS if e[0]<=t<=e[1]]
    if not act: return
    L=np.zeros((LH_,W,4),np.float32); glow=0.0; key=act[0][0]
    for s0,e0,fn in act:
        g=min(1.0,(e0-t)/0.25)
        r=fn(L,t-s0,g) or {}
        glow=max(glow,r.get("glow",0))
    if BBOX: pl=(float(BBOX.get("w",560))/1000.0,float(BBOX.get("cx",760)),float(BBOX.get("cy",BEHIND_CY)))
    else:
        if key not in PLACE: PLACE[key]=_auto_place(maskfull)
        pl=PLACE[key]
    k,cx,cy=pl
    if abs(k-1)>1e-3 or abs(cx-W/2)>1 or abs(cy-BEHIND_CY)>1:
        M=np.float32([[k,0,cx-k*W/2],[0,k,cy-k*BEHIND_CY]])
        L=cv2.warpAffine(L,M,(W,LH_),flags=cv2.INTER_LINEAR,borderValue=(0,0,0,0))
    if glow>0.01:
        small=cv2.resize(L[...,3],(W//2,LH_//2),interpolation=cv2.INTER_AREA)
        gb=cv2.GaussianBlur(small,(0,0),15); gb=cv2.resize(gb,(W,LH_),interpolation=cv2.INTER_LINEAR)*glow
        G=np.dstack([BLU[0]*gb,BLU[1]*gb,BLU[2]*gb,gb]); L=L+G*(1-L[...,3:4])
    blend(frame,L,0,0,mask=maskfull)

# ===================== SOTTOTITOLI DAVANTI + PAROLE CHIAVE =====================
KEYSTYLE={}
def _halo(T,sigma=15.0,gain=0.95,col=BLU):
    a=T[...,3]
    if a.max()<=0.01: return T
    hh,ww=T.shape[:2]
    small=cv2.resize(a,(max(2,ww//2),max(2,hh//2)),interpolation=cv2.INTER_AREA)
    gb=cv2.GaussianBlur(small,(0,0),sigma); gb=np.clip(cv2.resize(gb,(ww,hh),interpolation=cv2.INTER_LINEAR)*gain,0,1)
    G=np.dstack([col[0]*gb,col[1]*gb,col[2]*gb,gb])
    return T+G*(1-T[...,3:4])
def _hand_underline(frame,x,y,total,p,fade,seed=77,col=None):
    if p<=0.01: return
    pts=[(x-10,y+4),(x+total*0.33,y-5),(x+total*0.68,y+6),(x+total+12,y-2)]
    r=brush_stroke(pts,13,col or ACC,p,seed,amp=1.2,dry=0.45,ymax=H)
    if r is not None: blend(frame,r[2],r[0],r[1],gain=fade)
def chip_img(w,h,r,color,alpha):
    key=("chip",w,h,r,color,alpha)
    if key in _cache: return _cache[key]
    im=Image.new("L",(w,h),0); ImageDraw.Draw(im).rounded_rectangle([0,0,w-1,h-1],radius=r,fill=255)
    a=np.asarray(im.filter(ImageFilter.GaussianBlur(0.8)),np.float32)/255*alpha
    pm=np.dstack([np.array(color,np.float32)*a[...,None],a]); _cache[key]=pm; return pm
def _draw_hand_key(frame,w,x,yb,tau,fade):
    S=int(SIZE_KEY*1.45); lt,total=letters(w["w"],F_HAND,S,WHITE,None)
    X0=int(x)-80; Y0=int(yb-S*1.25); T=np.zeros((int(S*1.9),int(total)+200,4),np.float32)
    for it in lt:
        i=it["i"]; p=clamp01((tau-0.04*i)/0.3); e=ease_back(p,1.8)
        place(T,it["sp"],x-X0+it["x"],yb-Y0,it["adv"],S,sx=0.5+0.5*e,sy=0.5+0.5*e,rot=-4,gain=fade*clamp01(tau/0.06),dy=(1-ease_out(p))*16)
    blend(frame,_halo(T,13.0,0.9),X0,Y0)
    _hand_underline(frame,x,yb+16,total,ease_out(clamp01((tau-0.3)/0.4)),fade,seed=91)
def draw_key_word(frame,w,wi,sp,x,yb,tau,fade):
    kind=KEYKIND.get(wi,"pop"); S=SIZE_KEY
    if kind=="hand": return _draw_hand_key(frame,w,x,yb,tau,fade)
    style=KEYSTYLE.get(wi,CFG.get("key_style","sfumatura"))
    pill=style in ("pillola","pill","rettangolo")
    lt,total=letters(w["w"],F_SERIF,S,WHITE,None)
    X0=int(x)-80; Y0=int(yb-S*1.25); T=np.zeros((int(S*1.9),int(total)+200,4),np.float32)
    if pill:
        h_=int(S*0.98); chip=chip_img(int(total+64),h_,h_//2,BORD,0.94)
        over(T,chip,int(x-X0-32),int(yb-Y0-S*0.80),min(1,tau/0.12)*fade)
    for it in lt:
        i=it["i"]; lx=x-X0+it["x"]; base=yb-Y0
        if kind=="flip":
            p=clamp01((tau-0.05*i)/0.34); sy=math.cos(math.pi*(1-p))
            place(T,it["sp"],lx,base,it["adv"],S,sx=1.0,sy=sy if abs(sy)>0.02 else 0.02,gain=fade*clamp01(tau/0.05),dy=(1-ease_out(p))*-14)
        elif kind=="shrink":
            p=clamp01(tau/0.42); sc=0.88+0.75*(1-ease_out(p))
            place(T,it["sp"],total/2+x-X0+(it["x"]-total/2)*sc,base,it["adv"],S,sx=sc,sy=sc,gain=fade*clamp01(tau/0.06))
        elif kind=="jitter":
            p=clamp01(tau/0.4); amp=(1-p)*11
            dx=amp*math.sin(tau*70+i*1.7); a=1.0 if p>0.5 else 0.65+0.35*abs(math.sin(tau*55+i))
            e=ease_back(clamp01(tau/0.2),1.7)
            place(T,it["sp"],lx,base,it["adv"],S,sx=0.6+0.4*e,sy=0.6+0.4*e,gain=fade*a*clamp01(tau/0.05),dx=dx)
        else:
            p=clamp01((tau-0.03*i)/0.3); e=ease_back(p,2.2); sc=0.45+0.55*e
            place(T,it["sp"],lx,base,it["adv"],S,sx=sc,sy=sc,gain=fade*clamp01(tau/0.06),dy=(1-ease_out(p))*22)
    blend(frame,T if pill else _halo(T),X0,Y0)
    if kind=="underline":
        _hand_underline(frame,x,yb+18,total,ease_out(clamp01((tau-0.28)/0.36)),fade,seed=63)
def draw_front(frame,t):
    act=None
    for ci,c in enumerate(CHUNKS):
        s=words[c[0]]["s"]; e=words[c[-1]]["e"]
        nxt=words[CHUNKS[ci+1][0]]["s"] if ci+1<len(CHUNKS) else 99
        hold=min(nxt-0.03,e+0.3) if nxt-e<0.5 else e+0.3
        if s-0.02<=t<=hold: act=(ci,hold); break
    if act is None: return
    ci,hold=act
    ws,sps,pos=layout(ci)
    fade=1.0 if hold-t>0.1 else max(0,(hold-t)/0.1)
    for j,(w,sp,(x,yb)) in enumerate(zip(ws,sps,pos)):
        tau=t-w["s"]
        if tau<0: continue
        wi=CHUNKS[ci][j]
        if w["role"]=="k":
            draw_key_word(frame,w,wi,sp,x,yb,tau,fade); continue
        p=tau/0.16
        sc=0.8+0.2*ease_back(p,1.7) if p<1 else 1.0
        rise=(1-ease_out(p))*8
        al=min(1,tau/0.07)*fade
        img,nw,nh,base,pad=scaled(sp,sc)
        px=int(x+sp["adv"]/2-nw/2); py=int(yb-base+rise)
        blend(frame,img,px,py,gain=al)
def apply_zoom(frame,t):
    z=1.0; dx=dy=0.0
    for t0,amp,dur,shake in PUNCH:
        d=t-t0
        if 0<=d<=dur:
            r=d/dur; z+=amp*(1-r)**2*(1 if r>0.04 else r/0.04)
            if shake:
                dx+=shake*math.sin(d*95)*(1-r)**2; dy+=shake*0.8*math.cos(d*83)*(1-r)**2
    if z<=1.0005 and abs(dx)+abs(dy)<0.3: return frame
    cx,cy=W/2,H*0.42
    M=np.float32([[z,0,(1-z)*cx+dx],[0,z,(1-z)*cy+dy]])
    return cv2.warpAffine(frame,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)

# ===================== DISEGNO VETTORIALE (icone, b-roll) =====================
SS=3; GN=300
def resample(pts,step=2.0):
    P=np.array(pts,float)
    seg=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]
    L=seg[-1]
    if L<=0: return [tuple(P[0])]*2
    n=max(2,int(L/step)+1); u=np.linspace(0,L,n)
    return list(zip(np.interp(u,seg,P[:,0]),np.interp(u,seg,P[:,1])))
def arcpts(cx,cy,r,a0,a1,n=64):
    return [(cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a))) for a in np.linspace(a0,a1,n)]
def bez(p0,p1,p2,p3,n=80):
    out=[]
    for u in np.linspace(0,1,n):
        v=1-u
        out.append((v**3*p0[0]+3*v*v*u*p1[0]+3*v*u*u*p2[0]+u**3*p3[0], v**3*p0[1]+3*v*v*u*p1[1]+3*v*u*u*p2[1]+u**3*p3[1]))
    return out
class Cv:
    def __init__(s):
        s.K=SS*GN/300.0
        s.img=Image.new("RGBA",(SS*GN,SS*GN),(0,0,0,0)); s.d=ImageDraw.Draw(s.img)
    def P(s,pts): return [(x*s.K,y*s.K) for x,y in pts]
    def line(s,pts,w,color,p=1.0,dash=None):
        pts=resample(pts,2.0); n=len(pts)
        if p<1: pts=pts[:max(2,int((n-1)*clamp01(p))+1)]
        if len(pts)<2 or p<=0: return
        if dash:
            dl,gl=max(1,int(dash[0]/2)),max(1,int(dash[1]/2)); i=0
            while i<len(pts)-1:
                s._poly(pts[i:i+dl+1],w,color); i+=dl+gl
        else: s._poly(pts,w,color)
    def _poly(s,pts,w,color):
        P=s.P(pts); Wd=w*s.K
        if len(P)>=2: s.d.line(P,fill=color,width=max(1,int(Wd)),joint="curve")
        r=Wd/2
        for (x,y) in (P[0],P[-1]): s.d.ellipse([x-r,y-r,x+r,y+r],fill=color)
    def circle(s,cx,cy,r,fill=None,outline=None,w=0):
        K=s.K; s.d.ellipse([(cx-r)*K,(cy-r)*K,(cx+r)*K,(cy+r)*K],fill=fill,outline=outline,width=int(w*K))
    def rrect(s,x0,y0,x1,y1,r,fill=None,outline=None,w=0):
        K=s.K; s.d.rounded_rectangle([x0*K,y0*K,x1*K,y1*K],radius=r*K,fill=fill,outline=outline,width=int(w*K))
    def rect(s,x0,y0,x1,y1,fill):
        K=s.K; s.d.rectangle([x0*K,y0*K,x1*K,y1*K],fill=fill)
    def poly(s,pts,fill): s.d.polygon(s.P(pts),fill=fill)
    def text(s,x,y,txt,path,size,color):
        K=s.K; f=ImageFont.truetype(path,max(2,int(size*K)))
        s.d.text((x*K,y*K),txt,font=f,fill=color,anchor="mm")
def ellipse_pts(cx,cy,rx,ry,a0=0,a1=360,rot=0,n=48):
    r=math.radians(rot); out=[]
    for a in np.linspace(a0,a1,n):
        x=rx*math.cos(math.radians(a)); y=ry*math.sin(math.radians(a))
        out.append((cx+x*math.cos(r)-y*math.sin(r), cy+x*math.sin(r)+y*math.cos(r)))
    return out
C_OT=BLU+(255,); C_OD=BORD+(255,); C_AR=RUG+(255,); C_AS=(240,212,196,255); C_OTI=(224,231,236,255); C_W=(255,255,255,255)
def mixc(a,b,u): return tuple(int(a[i]+(b[i]-a[i])*u) for i in range(3))+(255,)
def mixw(col,a): return tuple(int(255+(col[i]-255)*a) for i in range(3))+(255,)

# ===================== ICONE STILE 05 "FRECCE A MANO" (stile fisso) =====================
# Scheda bianca col filo blu, disegno SOLO A CONTORNO che si traccia, evidenziatore ruggine chiaro, freccia a mano
# ruggine, accenti ruggine che pulsano. Mai forme piene grandi. Coordinate 0-100 dentro la scheda.
# Nuova icona: def FR_nome(c,t) con _card, _hl, fst/c.line(_m(...)), acc, _arrow; poi FICONS["nome"]=FR_nome.
FX0,FY0,FSC=65.0,62.0,1.7
def _m(pts): return [(FX0+FSC*x,FY0+FSC*y) for x,y in pts]
def _X(x): return FX0+FSC*x
def _Y(y): return FY0+FSC*y
def circ(cx,cy,r,n=56): return [(cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a))) for a in np.linspace(-90,270,n)]
def rrp(x0,y0,x1,y1,r,n=8):
    pts=[]
    for (cx,cy,a0) in ((x1-r,y0+r,-90),(x1-r,y1-r,0),(x0+r,y1-r,90),(x0+r,y0+r,180)):
        pts+=[(cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a))) for a in np.linspace(a0,a0+90,n)]
    return pts+[pts[0]]
def fst(c,pts,i,t,col=C_OT,w=7.2,delay=0.1,dur=0.7):
    p=ease_out(clamp01((t-delay-0.09*i)/dur))
    if p>0: c.line(_m(pts),w,col,p)
def acc(c,cx,cy,r,t,col=C_AR,k=6.0,delay=0.5):
    a=clamp01((t-delay)/0.3)
    if a>0: c.circle(_X(cx),_Y(cy),FSC*r*(1+0.12*math.sin(t*k)),fill=mixw(col,a))
def _card(c):
    c.rrect(20,20,280,280,14,fill=C_W)
    c.rrect(20,20,280,280,14,outline=C_OT,w=3)
def _hl(c,t):
