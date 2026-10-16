import subprocess, sys, array
RANGES=[(3.217,5.9),(8.413,11.3),(14.071,16.2),(19.64,22.95),(25.333,27.1),(29.9,32.5),(34.512,37.0),(40.105,42.3),(44.8,47.45),(50.26,52.0),(53.77,56.4),(57.01,59.5)]
def run(*a):
    return subprocess.run(a,capture_output=True,check=True).stdout
def analyze(p):
    raw=run('ffmpeg','-v','error','-i',p,'-vf','scale=8:8,format=gray','-f','rawvideo','-')
    nf=len(raw)//64; fl=[]; prev=False
    for k in range(nf):
        on=sum(raw[k*64:(k+1)*64])/64>128
        if on and not prev: fl.append(k/30)
        prev=on
    s=array.array('h'); s.frombytes(run('ffmpeg','-v','error','-i',p,'-ac','1','-ar','16000','-f','s16le','-'))
    bp=[]; prev=False
    for k in range(0,len(s)-80,80):
        on=max(abs(x) for x in s[k:k+80])>6000
        if on and not prev: bp.append(k/16000)
        prev=on
    return fl,bp,nf,len(s)/16000
print('expected total',round(sum(e-s for s,e in RANGES),3),'frame-rounded',round(sum(round(e*30)-round(s*30) for s,e in RANGES)/30,3))
for p in ('A.mp4','B.mp4'):
    fl,bp,nf,ad=analyze(p); errs=[]
    for f in fl:
        b=min(bp,key=lambda x:abs(x-f))
        if abs(b-f)<0.3: errs.append(round((b-f)*1000))
    print(p,'vdur',round(nf/30,3),'adur',round(ad,3),'pairs',len(errs),'min/max ms',min(errs),max(errs)); print(' ',errs)
