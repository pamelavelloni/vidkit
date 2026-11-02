SR=48000; SFXEV=[]
SFX_PRI={"thud":4,"tock":4,"swipe":3,"pop":2,"page":2,"tap":1}
def _nz(n,seed): return np.random.RandomState(seed).randn(n).astype(np.float32)
def _lp1(x,cut):
    c=np.full(len(x),cut,np.float32) if np.isscalar(cut) else cut.astype(np.float32)
    a=1-np.exp(-2*np.pi*np.clip(c,20,SR/2.2)/SR); y=np.empty_like(x); z=0.0
    for i in range(len(x)): z+=a[i]*(x[i]-z); y[i]=z
    return y
def _hp1(x,cut): return x-_lp1(x,cut)
def _dec(n,a,d):
    t=np.arange(n,dtype=np.float32)/SR
    return np.clip(t/max(a,1e-5),0,1)*np.exp(-t/max(d,1e-5))
def _sfx_tap():
    n=int(0.09*SR); return _hp1(_nz(n,2),1800)*_dec(n,0.001,0.018)*2.2
def _sfx_swipe():
    n=int(0.34*SR); c=np.concatenate([np.linspace(420,7000,int(n*0.55),dtype=np.float32),np.linspace(7000,900,n-int(n*0.55),dtype=np.float32)])
    t=np.arange(n,dtype=np.float32)/SR; bell=np.sin(np.pi*np.clip(t/(n/SR),0,1))**1.6
    return _hp1(_lp1(_nz(n,3),c),300)*bell*3.2
def _sfx_page():
    n=int(0.26*SR); out=np.zeros(n,np.float32)
    for k,off in enumerate((0.0,0.07,0.15)):
        i=int(off*SR); m=min(n-i,int(0.08*SR))
        out[i:i+m]+=_hp1(_nz(m,10+k),2600)[:m]*_dec(m,0.002,0.022)*(1.0-0.2*k)
    return out*2.4
def _sfx_pop():      # bolla tonale da 1500 a 650 Hz, nessun rumore
    n=int(0.11*SR); t=np.arange(n,dtype=np.float32)/SR
    f=650+850*np.exp(-t/0.018); ph=2*np.pi*np.cumsum(f)/SR
    env=np.clip(t/0.0015,0,1)*np.exp(-t/0.028)
    return (np.sin(ph)+0.25*np.sin(2*ph))*env
def _sfx_tock():     # tocco di legno corto (stacchi e colpi di zoom)
    n=int(0.09*SR); t=np.arange(n,dtype=np.float32)/SR
    return (np.sin(2*np.pi*760*t)*np.exp(-t/0.022)+0.45*np.sin(2*np.pi*1920*t)*np.exp(-t/0.010))*np.clip(t/0.001,0,1)
SFX_FN={"tap":_sfx_tap,"swipe":_sfx_swipe,"page":_sfx_page,"pop":_sfx_pop,"thud":_sfx_tock,"tock":_sfx_tock}
SFX_GAIN={"tap":0.11,"swipe":0.16,"page":0.12,"pop":0.30,"thud":0.30,"tock":0.30}
SFX_LIVELLO=0.55     # picco effetti = circa -5 dB sotto il picco della voce
SFX_DUCK=0.75        # mentre lei parla scendono solo di circa 2,5 dB
def _sfx_thin(ev,gap=0.15):
    out=[]
    for t,n,g in sorted(ev):
        if out and t-out[-1][0]<gap:
            if SFX_PRI.get(n,1)>SFX_PRI.get(out[-1][1],1): out[-1]=(t,n,g)
            continue
        out.append((t,n,g))
    return out
def _dur(path):
    try: return float(subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{path}"',shell=True,capture_output=True,text=True).stdout.strip())
    except Exception: return (words[-1]["e"]+1.5) if words else 60.0
def cmd_sfx():
    import wave
    setup_render()
    if CFG.get("sfx",{}).get("enabled",True) is False or not SFXEV:
        if os.path.exists("sfx.wav"): os.remove("sfx.wav")
        print("sound design disattivato"); return
    ev=_sfx_thin(SFXEV); n=int(_dur("edited.mov")*SR)+SR
    buf=np.zeros(n,np.float32); cache={}
    mul=float(CFG.get("sfx",{}).get("gain",1.0))
    raw=subprocess.run('ffmpeg -v error -i edited.mov -f s16le -ac 1 -ar 16000 -',shell=True,capture_output=True).stdout
    v=np.abs(np.frombuffer(raw,np.int16).astype(np.float32))/32768
    w0=800; env=np.array([v[k:k+w0].mean() for k in range(0,max(1,len(v)-w0),w0)]); thr=np.percentile(env,70)*0.5
    vpk=float(np.percentile(v,99.9))
    for t,name,g in ev:
        if name not in cache: cache[name]=SFX_FN[name]()
        k=int(t*16000/w0); duck=SFX_DUCK if 0<=k<len(env) and env[k]>thr else 1.0
        s=cache[name]; i=int(max(0,t)*SR); m=min(len(s),n-i)
        if m>0: buf[i:i+m]+=s[:m]*SFX_GAIN[name]*g*duck
    pk=float(np.abs(buf).max())
    if pk>1e-6: buf*=min(0.95,max(0.02,vpk*SFX_LIVELLO*mul))/pk
    with wave.open("sfx.wav","wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(buf,-1,1)*32767).astype("<i2").tobytes())
    print(f"sfx.wav: {len(ev)} effetti ({', '.join(sorted(set(n_ for _,n_,_ in ev)))})")
def _audio_args():
    ins=""; chains=[]; labs=["[1:a]"]; idx=2
    if os.path.exists("sfx.wav"):
        ins+=" -i sfx.wav"; labs.append(f"[{idx}:a]"); idx+=1
    mus=CFG.get("musica") or {}
    if mus.get("file") and os.path.exists(mus["file"]):
        ins+=f' -i "{mus["file"]}"'; chains.append(f'[{idx}:a]volume={mus.get("gain",-23)}dB,atrim=0:{_dur("edited.mov"):.2f},afade=t=in:d=0.6,afade=t=out:st={max(0,_dur("edited.mov")-1.2):.2f}:d=1.2[mus]')
        labs.append("[mus]"); idx+=1
    ln=CFG.get("loudness",-14)
    if len(labs)==1:
        if ln is None: return "",""," -map 1:a"
        return "",f' -filter_complex "[1:a]loudnorm=I={ln}:TP=-1.5:LRA=11[aout]"',' -map "[aout]"'
    mix="".join(labs)+f"amix=inputs={len(labs)}:duration=first:normalize=0"
    chains.append(mix+("[aout]" if ln is None else f"[mx];[mx]loudnorm=I={ln}:TP=-1.5:LRA=11[aout]"))
    return ins,' -filter_complex "'+";".join(chains)+'"',' -map "[aout]"'

# ===================== CONFIGURAZIONE -> STATO DI RENDER =====================
def _wi(name,occ=0):
    c=[i for i,w in enumerate(words) if norm(w["w"])==norm(name)]
    if len(c)<=occ: raise SystemExit(f'parola non trovata nella trascrizione: "{name}" (occorrenza {occ})')
    return c[occ]
def ws(n,o=0): return words[_wi(n,o)]["s"]
def we(n,o=0): return words[_wi(n,o)]["e"]

# Fasi: VIDKIT_FASE=1 solo testi (icone, b-roll e stacchi spenti); 2 e 3 tutto. I suoni li mette solo "full".
FASE=int(os.environ.get("VIDKIT_FASE","3"))
COLORI={"blu":BLU,"bordeaux":BORD,"bord":BORD,"ruggine":RUG,"bianco":(255,255,255)}
def setup_render():
    global CFG,words,CHUNKS,EFFECTS,PUNCH,GRAPHICS,KEYKIND,KEYSTYLE,it,_i,_o,BROLL,STACCHI,SFXEV
    if FASE<2:
        CFG=dict(CFG); CFG["icons"]=[]; CFG["broll"]=[]; CFG["stacchi"]=[]
    words=json.load(open("words.json"))
    for w in words: w["role"]="n"
    EFFECTS=[]; PUNCH=[]; KEYKIND={}; KEYSTYLE={}; STACCHI=[]; SFXEV=[]
    for b in CFG.get("behind",[]):
        i=_wi(b["word"],b.get("occ",0)); words[i]["role"]="b"
        fn,dur=FX[b["effect"]]; dur=b.get("dur",dur); text=b.get("text") or norm(words[i]["w"])
        s=words[i]["s"]-0.08
        bf=F_SERIF if b.get("font")=="serif" else F_SANS
        EFFECTS.append((s,s+dur,(lambda L,tau,g,fn=fn,text=text,bf=bf,st=b.get("sticker",False): _run_fx(fn,L,tau,g,text,bf,st))))
        pr=PUNCH_RULES.get(b["effect"])
        if pr: PUNCH.append((s+pr[0],pr[1],pr[2],pr[3]))
        SFXEV.append((s+0.04,"pop",1.2))
        if pr and pr[3]>0: SFXEV.append((s+pr[0],"thud",1.0))
    for k in CFG.get("keys",[]):
        i=_wi(k["word"],k.get("occ",0)); words[i]["role"]="k"; words[i]["kind"]=k.get("kind","pop"); KEYKIND[i]=k.get("kind","pop")
        if k.get("style"): KEYSTYLE[i]=k["style"]
    GRAPHICS=[]
    for ic in CFG.get("icons",[]):
        a=ic["from"]; b=ic["to"]
        s=ws(a[0],a[1] if len(a)>2 else 0)+a[-1]
        e=99.0 if b[0]=="fine" else we(b[0],b[1] if len(b)>2 else 0)+b[-1]
        GRAPHICS.append((s,e,ic["icon"]))
    GRAPHICS.sort()
    GRAPHICS=[(s,(min(e,GRAPHICS[i+1][0]-0.03) if i+1<len(GRAPHICS) else e),n) for i,(s,e,n) in enumerate(GRAPHICS)]
    for s,_e,_n in GRAPHICS: SFXEV.append((s+0.05,"pop",1.0))
    BROLL=[]
    for br in CFG.get("broll",[]):
        a=br["from"]; b_=br["to"]
        s_=ws(a[0],a[1] if len(a)>2 else 0)+a[-1]; e_=we(b_[0],b_[1] if len(b_)>2 else 0)+b_[-1]
        br["_dur"]=e_-s_
        BROLL.append((s_,e_,br))
        SFXEV+=[(s_,"swipe",1.0),(e_-0.18,"swipe",0.7)]
        D=e_-s_; items=br.get("nodes") or br.get("items") or []
        if br.get("type")=="linea": SFXEV.append((s_+0.12*D,"page",0.9))
        for i in range(len(items)):
            SFXEV.append((s_+(0.22*D+(0.60*D/max(1,len(items)))*i)+0.06,"pop",1.0))
    for st in CFG.get("stacchi",[]):
        a=st["at"]; t0=ws(a[0],a[1] if len(a)>2 else 0)+a[-1]
        d=st.get("dur",0.26); col=COLORI.get(st.get("colore","blu"),BLU)
        STACCHI.append((t0,d,col)); SFXEV.append((t0+0.02,"thud",0.8))
    CHUNKS=build_chunks()
    from ai_edge_litert.interpreter import Interpreter
    it=Interpreter(model_path=SEG_MODEL); it.allocate_tensors()
    _i=it.get_input_details()[0]; _o=it.get_output_details()[0]
    setup_camera()
def setup_camera():
    global SHOTS,CAM
    mp=json.load(open("map.json"))["map"]
    SHOTS=_split_long([(m_["dst"],m_["dst"]+m_["src"][1]-m_["src"][0]) for m_ in mp])
    CAM=[]; k=0
    for a_,b_ in SHOTS:
        if b_-a_<0.7 and CAM: z0=z1=CAM[-1]["z1"]; px=CAM[-1]["px"]
        else:
            z0=ZP[k%8]; z1=z0+0.045
            if k%2==1: z0,z1=z1,z0
            px=(1 if k%2 else -1)*min(28,540*(min(z0,z1)-1)*0.35); k+=1
        CAM.append(dict(t0=a_,t1=b_,z0=z0,z1=z1,px=px))

# ===================== SETUP, ANALISI, TEMPI DELLE PAROLE, MONTAGGIO =====================
ASR_DIR=ASSETS+"/asr/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/"
ASR_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2"
def cmd_setup():
    os.makedirs(FD,exist_ok=True); tmp=ASSETS+"/_tmp"; os.makedirs(tmp,exist_ok=True)
    run("pip install --break-system-packages -q ai-edge-litert fonttools opencv-python-headless pillow numpy sherpa-onnx 2>/dev/null")
    if not os.path.exists(SEG_MODEL):
        run(f"cd {tmp} && npm pack --silent @mediapipe/selfie_segmentation >/dev/null 2>&1 && tar xzf mediapipe-selfie_segmentation-*.tgz && cp package/selfie_segmentation.tflite {SEG_MODEL}")
    need={"HankenGrotesk-ExtraBold":("@fontsource/hanken-grotesk","hanken-grotesk-latin-800-normal"),"HankenGrotesk-Regular":("@fontsource/hanken-grotesk","hanken-grotesk-latin-400-normal"),
          "PlayfairDisplay-MediumItalic":("@fontsource/playfair-display","playfair-display-latin-500-italic"),
          "NothingYouCouldDo":("@fontsource/nothing-you-could-do","nothing-you-could-do-latin-400-normal")}
    from fontTools.ttLib import TTFont
    for out,(pkg,fname) in need.items():
        dst=f"{FD}{out}.ttf"
        if os.path.exists(dst): continue
        d=f"{tmp}/{pkg.split('/')[1]}"; os.makedirs(d,exist_ok=True)
        run(f"cd {d} && npm pack --silent {pkg} >/dev/null 2>&1 && tar xzf *.tgz")
        f=TTFont(f"{d}/package/files/{fname}.woff"); f.flavor=None; f.save(dst)
    if not os.path.exists(ASR_DIR+"tokens.txt"):
        os.makedirs(ASSETS+"/asr",exist_ok=True)
        run(f"cd {ASSETS}/asr && curl -sL {ASR_URL} | tar xj")
    print("font:",sorted(os.listdir(FD)),"| persona:",os.path.exists(SEG_MODEL),"| modello vocale:",os.path.exists(ASR_DIR+"tokens.txt"))

def speech_segments():
    a=np.frombuffer(run('ffmpeg -v error -i audio.wav -f s16le -ac 1 -ar 16000 -',capture_output=True).stdout,dtype=np.int16).astype(np.float32)
    w=800; e50=np.array([np.sqrt(np.mean(a[k:k+w]**2)) for k in range(0,len(a)-w,w)])
    th=max(150,np.percentile(e50,25)*3); sp=e50>th
    segs=[];s=None
    for k,v in enumerate(sp):
        if v and s is None: s=k
        if not v and s is not None: segs.append((s*0.05,k*0.05)); s=None
    if s is not None: segs.append((s*0.05,len(sp)*0.05))
    m=[]
    for s_,e_ in segs:
        if m and s_-m[-1][1]<0.25: m[-1]=(m[-1][0],e_)
        else: m.append((s_,e_))
    return [x for x in m if x[1]-x[0]>0.12], e50

def cmd_prep():
    if not os.path.exists("in.mov"): raise SystemExit("manca in.mov nella cartella")
    dur=float(run("ffprobe -v error -show_entries format=duration -of csv=p=0 in.mov",capture_output=True,text=True).stdout)
    info=run("ffprobe -v error -select_streams v -show_entries stream=width,height,r_frame_rate -of csv=p=0 in.mov",capture_output=True,text=True).stdout.strip()
    run("ffmpeg -v error -y -i in.mov -vn -ac 1 -ar 16000 audio.wav")
    run('ffmpeg -v error -y -i in.mov -vf "fps=1/4,scale=200:-1,tile=6x3" -frames:v 1 sheet.png')
    segs,_=speech_segments(); json.dump(segs,open("segs.json","w"))
    print(f"durata {dur:.2f}s  video {info}  parlato in {len(segs)} frasi")

def _blocks():
    """La trascrizione: "blocks" nel config oppure trascrizione.txt cosi' com'e' copiata da CapCut: (0:00) testo (0:11) testo ..."""
    b=CFG.get("blocks")
    if b: return b
    if not os.path.exists("trascrizione.txt"): return []
    parts=re.split(r"\((\d+):(\d{1,2})\)",open("trascrizione.txt",encoding="utf-8").read())
    out=[]
    for i in range(1,len(parts)-2,3):
        txt=" ".join(parts[i+2].split())
        if txt: out.append({"stamp":int(parts[i])*60+int(parts[i+1]),"text":txt})
    return out
def syl(w):
    k=re.sub(r"[^\wàèéìòù]","",w.lower()); ov=CFG.get("syl",{})
    if k in ov: return ov[k]
    return max(1,len(re.findall(r"[aeiouàèéìòù]+",k)))
def _asr_words(wav="audio.wav"):
    import sherpa_onnx
    rec=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=ASR_DIR+"encoder.int8.onnx",decoder=ASR_DIR+"decoder.int8.onnx",
        joiner=ASR_DIR+"joiner.int8.onnx",tokens=ASR_DIR+"tokens.txt",model_type="nemo_transducer",num_threads=4)
    a=np.frombuffer(run(f'ffmpeg -v error -i {wav} -f s16le -ac 1 -ar 16000 -',capture_output=True).stdout,np.int16).astype(np.float32)/32768
    segs,_=speech_segments()
    chunks=[]; cur=None
    for s_,e_ in segs:
        if cur and e_-cur[0]<=22: cur[1]=e_
        else:
            if cur: chunks.append(cur)
            cur=[s_,e_]
    if cur: chunks.append(cur)
    out=[]
    for s_,e_ in chunks:
        a0=max(0,s_-0.25); a1=min(len(a)/16000,e_+0.25)
        st=rec.create_stream(); st.accept_waveform(16000,a[int(a0*16000):int(a1*16000)]); rec.decode_stream(st); r=st.result
        cw=None
        for tok,ts in zip(r.tokens,r.timestamps):
            t=a0+ts
            if tok.startswith(" ") or cw is None:
                if cw: out.append(cw)
                cw={"w":tok.strip(),"s":t,"last":t}
            else: cw["w"]+=tok; cw["last"]=t
        if cw: out.append(cw)
    for i,w in enumerate(out):
        nxt=out[i+1]["s"] if i+1<len(out) else w["last"]+0.3
        w["e"]=min(w["last"]+0.16,nxt-0.01) if nxt-w["last"]<0.6 else w["last"]+0.22
        w["s"]=round(w["s"],3); w["e"]=round(max(w["e"],w["s"]+0.06),3); del w["last"]
    return out
def _nw(w): return re.sub(r"[^a-zàèéìòùáíóú0-9]","",w.lower())
def _align_transcript(asr,toks):
    """Mette i tempi del riconoscimento sulle parole della trascrizione (che resta la grafia giusta)."""
    import difflib
    A=[_nw(x["w"]) for x in asr]; B=[_nw(t) for t in toks]
    T=[None]*len(toks)
    sm=difflib.SequenceMatcher(None,A,B,autojunk=False)
    for op,a0,a1,b0,b1 in sm.get_opcodes():
        if op=="equal" or (op=="replace" and a1-a0==b1-b0):
            for k in range(b1-b0): T[b0+k]=(asr[a0+k]["s"],asr[a0+k]["e"])
        elif op=="replace":
            s_,e_=asr[a0]["s"],asr[a1-1]["e"]; sy=[syl(t) for t in toks[b0:b1]]; tot=sum(sy); c=0
            for k in range(b1-b0):
                T[b0+k]=(s_+(e_-s_)*c/tot, s_+(e_-s_)*(c+sy[k])/tot); c+=sy[k]
    matched=sum(1 for t in T if t)
    i=0
    while i<len(T):
        if T[i] is None:
            j=i
            while j<len(T) and T[j] is None: j+=1
            s_=T[i-1][1] if i>0 else max(0,(T[j][0] if j<len(T) else 0)-0.3*(j-i))
            e_=T[j][0] if j<len(T) else s_+0.3*(j-i)
            sy=[syl(t) for t in toks[i:j]]; tot=sum(sy); c=0
            for k in range(i,j):
                T[k]=(s_+(e_-s_)*c/tot,s_+(e_-s_)*(c+sy[k-i])/tot); c+=sy[k-i]
            i=j
        else: i+=1
    return [{"w":toks[i],"s":round(T[i][0],3),"e":round(max(T[i][1],T[i][0]+0.05),3)} for i in range(len(toks))],matched
def _snap_to_segments(words_,segs):
    """Ogni frase deve iniziare e finire dove inizia e finisce la voce: i tempi si riscalano dentro la frase."""
    if not words_ or not segs: return words_
    grp={}
    for i,w in enumerate(words_):
        mid=(w["s"]+w["e"])/2; best=None; bd=9
        for j,(a_,b_) in enumerate(segs):
            d=0 if a_<=mid<=b_ else min(abs(mid-a_),abs(mid-b_))
            if d<bd: bd=d; best=j
        if bd<=0.45: grp.setdefault(best,[]).append(i)
    for j,ids in grp.items():
        a_,b_=segs[j]; s0=words_[ids[0]]["s"]; e0=words_[ids[-1]]["e"]
        if e0-s0<0.05: continue
        k=(b_-a_)/(e0-s0)
        for i in ids:
            words_[i]["s"]=round(a_+(words_[i]["s"]-s0)*k,3); words_[i]["e"]=round(a_+(words_[i]["e"]-s0)*k,3)
    return words_
def cmd_asr():
    """Riconosce il parlato del girato ORIGINALE e scrive words_orig.json (parole della trascrizione, tempi reali)."""
    if not os.path.exists("audio.wav"): cmd_prep()
    asr=_asr_words(); json.dump(asr,open("asr_raw.json","w"),ensure_ascii=False)
    toks=[]
    for b in _blocks(): toks+=b["text"].split()
    if toks:
        out,m=_align_transcript(asr,toks)
        print(f"riconoscimento: {len(asr)} parole sentite, {m}/{len(toks)} parole della trascrizione agganciate ({100*m/len(toks):.0f}%)")
        if m<0.75*len(toks): print("  ATTENZIONE: la trascrizione non sembra di questo file, va richiesta quella giusta")
    else:
        out=[{"w":x["w"],"s":x["s"],"e":x["e"]} for x in asr]
        print(f"riconoscimento: {len(asr)} parole (senza trascrizione: controllare a mano la grafia di nomi e sigle)")
    segs,_=speech_segments(); out=_snap_to_segments(out,segs)
    json.dump(out,open("words_orig.json","w"),ensure_ascii=False)
def cmd_mappa():
    """Il parlato del girato frase per frase, con inizio, fine e pause reali: da qui si scrive il copione."""
    w=json.load(open("words_orig.json")); prev_e=0
    line=[]
    for x in w:
        gap=x["s"]-prev_e
        if line and gap>0.35:
            print(f'{line[0]["s"]:7.2f}-{line[-1]["e"]:7.2f}  '+" ".join(y["w"] for y in line)); print(f"           pausa {gap:.2f}s")
            line=[]
        line.append(x); prev_e=x["e"]
    if line: print(f'{line[0]["s"]:7.2f}-{line[-1]["e"]:7.2f}  '+" ".join(y["w"] for y in line))
def _segs_muti(segs):
    """Pezzi di 'parlato' senza parole dentro: rumori (tosse, schiarite, respiri) da buttare."""
    if not os.path.exists("words_orig.json"): return set()
    w=json.load(open("words_orig.json"))
    return {j for j,(a_,b_) in enumerate(segs) if not any(x["s"]<b_+0.05 and x["e"]>a_-0.05 for x in w)}
def cmd_montage():
    if not os.path.exists("audio.wav"): cmd_prep()
    mc=CFG.get("montage",{}); PRE,POST,MERGE=mc.get("pre",0.07),mc.get("post",0.12),mc.get("merge",0.12)
    dur=float(run("ffprobe -v error -show_entries format=duration -of csv=p=0 in.mov",capture_output=True,text=True).stdout)
    segs,_=speech_segments()
    muti=_segs_muti(segs)
    if muti:
        print(f"  {len(muti)} rumori senza parole buttati: "+", ".join(f"{segs[j][0]:.2f}-{segs[j][1]:.2f}" for j in sorted(muti)))
        segs=[x for j,x in enumerate(segs) if j not in muti]
    sn=lambda x: round(x*FPS)/FPS
    pezzi=CFG.get("copione")
    if pezzi:
        iv=[]
        for p_ in pezzi:
            A,B=float(p_["da"]),float(p_["a"]); sub=[]
            for s_,e_ in segs:
                a_=max(A,s_-PRE); b_=min(B,e_+POST)
                if b_-a_<=0.05: continue
                if sub and a_<=sub[-1][1]+MERGE: sub[-1][1]=max(sub[-1][1],b_)
                else: sub.append([a_,b_])
            iv+=[[sn(a_),sn(b_)] for a_,b_ in sub]
    elif mc.get("enabled",True):
        iv=[]
        for s_,e_ in segs:
            a_=max(0,s_-PRE); b_=min(dur,e_+POST)
            if iv and a_<=iv[-1][1]+MERGE: iv[-1][1]=max(iv[-1][1],b_)
            else: iv.append([a_,b_])
        iv=[[sn(a_),sn(b_)] for a_,b_ in iv]
        mm=[]
        for a_,b_ in iv:
            if mm and a_<=mm[-1][1]+1e-6: mm[-1][1]=max(mm[-1][1],b_)
            else: mm.append([a_,b_])
        iv=mm
    else: iv=[[0.0,sn(dur)]]
    MAP=[]; d0=0.0
    for a_,b_ in iv: MAP.append({"src":[a_,b_],"dst":d0}); d0+=b_-a_
    print(f"durata originale {dur:.2f}s -> montato {d0:.2f}s, {len(iv)} scene, tagliati {dur-d0:.2f}s")
    json.dump({"map":MAP,"dur_new":d0,"dur_src":dur},open("map.json","w"))
    V='-c:v libx264 -crf 14 -preset fast -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k'
    if len(iv)<=12:
        fc=[]
        for i,(a_,b_) in enumerate(iv):
            fc.append(f"[0:v]trim=start={a_:.4f}:end={b_:.4f},setpts=PTS-STARTPTS,fps={FPS}[v{i}]")
            d=b_-a_; f=0.012
            fc.append(f"[0:a]atrim=start={a_:.4f}:end={b_:.4f},asetpts=PTS-STARTPTS,afade=t=in:d={f},afade=t=out:st={max(0,d-f):.4f}:d={f}[a{i}]")
        fc.append("".join(f"[v{i}][a{i}]" for i in range(len(iv)))+f"concat=n={len(iv)}:v=1:a=1[v][a]")
        open("fc.txt","w").write(";\n".join(fc))
        r=run(f'ffmpeg -v error -y -i in.mov -filter_complex_script fc.txt -map "[v]" -map "[a]" {V} edited.mov')
        if r.returncode: print("ffmpeg ERRORE",r.returncode)
    else:
        os.makedirs("pezzi",exist_ok=True); names=[]
        for i,(a_,b_) in enumerate(iv):
            d=b_-a_; f=0.012; nm=f"pezzi/p{i:03d}.mov"; names.append(nm)
            run(f'ffmpeg -v error -y -accurate_seek -ss {a_:.4f} -i in.mov -t {d:.4f} '
                f'-vf "fps={FPS}" -af "afade=t=in:d={f},afade=t=out:st={max(0,d-f):.4f}:d={f}" {V} {nm}')
        open("pezzi/lista.txt","w").write("\n".join(f"file '{os.path.basename(n)}'" for n in names))
        r=run('ffmpeg -v error -y -f concat -safe 0 -i pezzi/lista.txt -c copy edited.mov')
        if r.returncode: print("ffmpeg ERRORE",r.returncode)
        shutil.rmtree("pezzi",ignore_errors=True)
def cmd_timing():
    """Sposta le parole (tempi reali) sul montato. Una frase che il copione usa due volte compare due volte."""
    if not os.path.exists("words_orig.json"): cmd_asr()
    out=json.load(open("words_orig.json"))
    mp=json.load(open("map.json")); MAP=mp["map"]; taglia=bool(CFG.get("copione"))
    keep=[]
    for w_ in out:
        mid=(w_["s"]+w_["e"])/2; hit=False
        for m_ in MAP:
            a_,b_=m_["src"]
            if a_-1e-6<=mid<=b_+1e-6:
                s2=m_["dst"]+max(0,w_["s"]-a_); e2=m_["dst"]+min(b_,w_["e"])-a_
                keep.append({"w":w_["w"],"s":round(s2,3),"e":round(max(e2,s2+0.05),3)}); hit=True
        if not hit and not taglia:
            nx=[m_["dst"] for m_ in MAP if m_["src"][0]>mid]
            t_=nx[0] if nx else mp["dur_new"]; keep.append({"w":w_["w"],"s":t_,"e":t_+0.05})
    keep.sort(key=lambda x:x["s"])
    json.dump(keep,open("words.json","w"),ensure_ascii=False)
    print(len(keep),"parole sul montato")
    print("PARLATO MONTATO (da rileggere come un testo):"," ".join(x["w"] for x in keep))
def cmd_check():
    setup_render()
    print("== testi grandi:"," | ".join(f'{b["effect"]} "{words[_wi(b["word"],b.get("occ",0))]["w"]}" {words[_wi(b["word"],b.get("occ",0))]["s"]-0.08:.1f}s' for b in CFG.get("behind",[])))
    print("== parole chiave:",[(words[i]["w"],k,KEYSTYLE.get(i,CFG.get("key_style","sfumatura"))) for i,k in KEYKIND.items()])
    for t0,d,_c in STACCHI:
        coll=[b["word"] for b in CFG.get("behind",[]) if abs(words[_wi(b["word"],b.get("occ",0))]["s"]-0.08-t0)<1.6]
        print(f'== stacco a {t0:.2f}s'+(f'  ATTENZIONE: cade sopra il testo grande "{coll[0]}"' if coll else ""))
    if GRAPHICS:
        dur=json.load(open("map.json"))["dur_new"]
        print(f"== icone ({len(GRAPHICS)} in {dur:.0f}s):"," | ".join(f"{n} {s:.1f}" for s,e,n in GRAPHICS))
        mancano=[n for _,_,n in GRAPHICS if n not in FICONS]
        if mancano: print("   DA DISEGNARE in stile 05:",mancano)
    for s_,e_,br in BROLL: print(f"== broll {br['type']} {s_:.2f}-{e_:.2f} ({e_-s_:.1f}s)")
    try:
        raw=subprocess.run('ffmpeg -v error -i edited.mov -f s16le -ac 1 -ar 16000 -',shell=True,capture_output=True).stdout
        av=np.abs(np.frombuffer(raw,np.int16).astype(np.float32))/32768; wn=160
        env=np.array([av[k:k+wn].mean() for k in range(0,len(av)-wn,wn)])
        env=np.convolve(env,np.ones(7)/7,'same'); thr=float(np.percentile(env,55)); hz=100
        mp=json.load(open("map.json"))["map"]; err=[]; male=[]
        for m_ in mp:
            d0=m_["dst"]; d1=d0+(m_["src"][1]-m_["src"][0])
            g=[x for x in words if d0-0.05<=x["s"]<d1]
            if not g: continue
            k=int(d0*hz)
            while k<min(len(env),int((d0+0.9)*hz)) and env[k]<thr: k+=1
            d=k/hz-g[0]["s"]; err.append(d)
            if abs(d)>0.25: male.append(f'{g[0]["w"]} a {g[0]["s"]:.1f}s ({d:+.2f})')
        if err:
            md=float(np.median(err))
            print(f"== sincronia: scarto mediano {md:+.2f}s su {len(err)} attacchi"+("  (ok)" if abs(md)<=0.12 else "  ATTENZIONE: sposta le parole di %+.2fs"%(-md)))
            if male: print("   da ascoltare:"," | ".join(male[:6]))
    except Exception as e: print("== sincronia: non verificabile",e)
    lunghi=[" ".join(words[i]["w"] for i in c) for c in CHUNKS if len(c)>5]
    if lunghi: print("== sottotitoli oltre 5 parole:",lunghi)

# ===================== RENDER =====================
def cmd_render(fname,preview=False):
    if not preview: cmd_sfx()
    elif os.path.exists("sfx.wav"): os.remove("sfx.wav")
    setup_render()
    ains,afc,amap=("",""," -map 1:a") if preview else _audio_args()   # bozze: voce originale, senza suoni
    dec=subprocess.Popen("ffmpeg -v error -i edited.mov -f rawvideo -pix_fmt rgb24 -",shell=True,stdout=subprocess.PIPE)
    enc=subprocess.Popen(f"ffmpeg -v error -y -f rawvideo -pix_fmt rgb24 -s {W}x{H} -r {FPS} -i - -i edited.mov{ains}{afc} -map 0:v{amap} -c:v libx264 -preset {'veryfast' if preview else 'medium'} -crf {23 if preview else 17} -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -shortest -movflags +faststart {fname}",shell=True,stdin=subprocess.PIPE)
    n=0; lastc=-1; last=None
    while True:
        buf=dec.stdout.read(SRC_W*SRC_H*3)
        if len(buf)<SRC_W*SRC_H*3: break
        if preview and n%2==1 and last is not None:
            enc.stdin.write(last); n+=1; continue
        src=np.frombuffer(buf,np.uint8).reshape(SRC_H,SRC_W,3)
        fr,ci=reframe(src,n/FPS)
        if ci!=lastc: prev["m"]=None; lastc=ci
        m=seg_update(fr); fr=compose(fr,n/FPS,m)
        last=fr.tobytes(); enc.stdin.write(last); n+=1
        if n%600==0: print(n,flush=True)
    enc.stdin.close(); enc.wait(); print("fatto",n,"fotogrammi ->",fname)
def cmd_audio():
    """Rifa solo suoni, musica e volume sopra il video di out.mp4, senza ri-renderizzare le immagini."""
    if not os.path.exists("out.mp4"): raise SystemExit("manca out.mp4: prima 'full'")
    cmd_sfx(); ains,afc,amap=_audio_args()
    r=run(f"ffmpeg -v error -y -i out.mp4 -i edited.mov{ains}{afc} -map 0:v{amap} -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out_audio.mp4")
    if r.returncode==0: os.replace("out_audio.mp4","out.mp4"); print("audio rifatto -> out.mp4")
    else: print("ffmpeg ERRORE",r.returncode)

# ===================== COMANDI =====================
if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "help"
    if cmd=="setup": cmd_setup()
    elif cmd=="prep": cmd_prep()
    elif cmd=="asr": cmd_asr()
    elif cmd=="mappa": cmd_mappa()
    elif cmd=="montage": cmd_montage()
    elif cmd=="timing": cmd_timing()
    elif cmd=="check": cmd_check()
    elif cmd=="chunks":
        setup_render()
        for c in CHUNKS: print(f'{words[c[0]]["s"]:.2f}-{words[c[-1]]["e"]:.2f}',' '.join(words[i]["w"]+("*" if words[i]["role"]=="k" else "#" if words[i]["role"]=="b" else "") for i in c))
    elif cmd=="icone":
        names=sys.argv[2:]; row=[]
        for nm in names:
            for tt in (0.5,1.2,2.5):
                sp=_icon_sprite(nm,tt); bg=np.zeros((300,300,3),np.float32); bg[:]=BLU
                a=sp[...,3:4]; row.append(cv2.resize(np.clip(bg*(1-a)+sp[...,:3],0,255).astype(np.uint8),(150,150),interpolation=cv2.INTER_AREA))
        rows=[np.hstack(row[i:i+12]+[np.zeros_like(row[0])]*(12-len(row[i:i+12]))) for i in range(0,len(row),12)] if len(row)>12 else [np.hstack(row)]
        Image.fromarray(np.vstack(rows)).save("icone.png"); print("scritto icone.png (150 px, la misura piu' piccola in cui si vedono)")
    elif cmd=="test":
        setup_render(); ts=[float(x) for x in sys.argv[2:]]; out=[]
        for t in ts:
            st=max(0,t-0.4)
            run(f"ffmpeg -v error -y -ss {st} -i edited.mov -frames:v 13 -f rawvideo -pix_fmt rgb24 tmp.raw")
            raw=np.fromfile("tmp.raw",np.uint8).reshape(-1,SRC_H,SRC_W,3)
            prev["m"]=None; lastc=-1
            for k in range(len(raw)-1):
                f_,ci=reframe(raw[k],st+k/FPS)
                if ci!=lastc: prev["m"]=None; lastc=ci
                seg_update(f_.copy())
            te=st+(len(raw)-1)/FPS
            fr,ci=reframe(raw[-1],te)
            if ci!=lastc: prev["m"]=None
            m=seg_update(fr); PLACE.clear(); out.append(compose(fr,te,m))
        if os.path.exists("tmp.raw"): os.remove("tmp.raw")
        for n,fr in enumerate(out): Image.fromarray(fr).save(f"test_{n}.png")
        Image.fromarray(np.hstack([cv2.resize(f,(270,480),interpolation=cv2.INTER_AREA) for f in out])).save("test_row.png")
        print("scritto test_row.png (270x480 per fotogramma; test_N.png a piena risoluzione solo se serve un dettaglio)")
    elif cmd=="sfx": cmd_sfx()
    elif cmd=="bozza": cmd_render(f"bozza{FASE}.mp4",preview=True)
    elif cmd=="full": cmd_render("out.mp4")
    elif cmd=="audio": cmd_audio()
    else: print(__doc__)
