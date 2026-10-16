import subprocess, sys, array, json
RANGES=[(3.217,5.9),(8.413,11.3),(14.071,16.2),(19.64,22.95),(25.333,27.1),(29.9,32.5),(34.512,37.0),(40.105,42.3),(44.8,47.45),(50.26,52.0),(53.77,56.4),(57.01,59.5)]
def run(*a):
    r=subprocess.run(a,capture_output=True); 
    if r.returncode: print(r.stderr.decode()[-800:]); sys.exit(1)
    return r.stdout
# A: render.py style
with open('list.txt','w') as f:
    for i,(s,e) in enumerate(RANGES):
        d=e-s
        run('ffmpeg','-v','error','-y','-ss',f'{s:.3f}','-i','src.mp4','-t',f'{d:.3f}','-vf','scale=320:-2','-af',f'afade=t=in:st=0:d=0.03,afade=t=out:st={max(0,d-0.03):.3f}:d=0.03','-r','30','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000',f'seg{i}.mp4')
        f.write(f"file 'seg{i}.mp4'\n")
run('ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','list.txt','-c','copy','A.mp4')
# B: single pass, frame-exact
fps=30
v=[];a=[];n=0
for i,(s,e) in enumerate(RANGES):
    f0=round(s*fps); f1=round(e*fps)
    v.append(f"[0:v]select='between(n,{f0},{f1-1})',setpts=N/({fps}*TB)[v{i}]")
    a.append(f"[0:a]atrim=start={f0/fps}:end={f1/fps},asetpts=N/SR/TB[a{i}]")
cat=''.join(f"[v{i}][a{i}]" for i in range(len(RANGES)))
fc=';'.join(v+a)+f";{cat}concat=n={len(RANGES)}:v=1:a=1[v][a]"
run('ffmpeg','-v','error','-y','-i','src.mp4','-filter_complex',fc,'-map','[v]','-map','[a]','-r','30','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','B.mp4')
def analyze(p):
    raw=run('ffmpeg','-v','error','-i',p,'-vf','scale=8:8,format=gray','-f','rawvideo','-')
    nf=len(raw)//64
    flashes=[]; prev=False
    for k in range(nf):
        m=sum(raw[k*64:(k+1)*64])/64
        on=m>128
        if on and not prev: flashes.append(k/30)
        prev=on
    au=run('ffmpeg','-v','error','-i',p,'-ac','1','-ar','16000','-f','s16le','-')
    s=array.array('h'); s.frombytes(au)
    beeps=[]; quiet=0; win=80; prev=False
    for k in range(0,len(s)-win,win):
        pk=max(abs(x) for x in s[k:k+win])
        on=pk>6000
        if on and not prev: beeps.append(k/16000)
        prev=on
    return flashes,beeps,nf,len(s)/16000
for p in ('A.mp4','B.mp4'):
    fl,bp,nf,ad=analyze(p)
    err=[round((b-f)*1000,1) for f,b in zip(fl,bp)] if len(fl)==len(bp) else None
    print(p,'frames',nf,'vdur',round(nf/30,3),'adur',round(ad,3),'flashes',len(fl),'beeps',len(bp))
    print('  sync err ms (audio minus video) per marker:',err)
