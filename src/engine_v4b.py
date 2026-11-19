# tiny-chess v4b: 0x88 alpha-beta, TT 64K, killers, history, MVV-LVA, QS,
# iterative deepening to a fixed node budget per game. No NMP/LMR.
# Eval: material + procedural PSTs (exact v4 tables), bishop pair +30.
# Root searches every legal move. Deterministic: no clock, no randomness.
import json,os,sys,urllib.request,urllib.error,random
V=[0,100,320,330,500,900,20000]
P=[[0]*128 for _ in range(8)]
for s in range(128):
 if s&136:continue
 r=s>>4;f=s&7;c=min(f,7-f)+min(r,7-r)
 P[1][s]=[0,0,4,8,16,28,48,0][r]+(f in(3,4))*[0,0,0,8,14,10,4,0][r]
 P[2][s]=8*c-24
 P[3][s]=5*c-8
 P[4][s]=(15 if r==6 else 0)+(5 if r==0 and f in(3,4) else 0)
 P[5][s]=2*c-6
 P[6][s]=[15,22,8,0,0,8,22,15][f] if r==0 else -12*r
 P[7][s]=8*c-20
R=random.Random(7)
Z=[R.getrandbits(64) for _ in range(1689)]
BUD=[30000,40000,45000,60000,75000,90000,120000,150000]
M=100000
B=[0]*128
W=1
C=0
E=-1
HM=0
H=0
S=0
NP=0
BW=0
BB=0
KW=0
KB=0
PA=[]
LIM=30000
N=0
Q=0
QLIM=60000
U=[]
TK=[0]*65536
TD=[0]*65536
TF=[0]*65536
TS=[0]*65536
TM=[0]*65536
KL=[[0,0] for _ in range(128)]
HS=[[0]*128 for _ in range(13)]
def ps(p,s):
 a=abs(p)
 if a==6:return 0
 v=V[a]+P[a][s if p>0 else s^112]
 return v if p>0 else -v
def atk(q,by):
 if by:
  for t in(q-15,q-17):
   if not(t&136) and B[t]==1:return 1
 else:
  for t in(q+15,q+17):
   if not(t&136) and B[t]==-1:return 1
 for d in(31,33,14,18,-31,-33,-14,-18):
  t=q+d
  if not(t&136) and B[t]==(2 if by else -2):return 1
 for d in(1,15,16,17,-1,-15,-16,-17):
  t=q+d
  if not(t&136) and B[t]==(6 if by else -6):return 1
 for d in(15,17,-15,-17):
  t=q+d
  while not(t&136):
   p=B[t]
   if p:
    if p==(3 if by else -3) or p==(5 if by else -5):return 1
    break
   t+=d
 for d in(1,16,-1,-16):
  t=q+d
  while not(t&136):
   p=B[t]
   if p:
    if p==(4 if by else -4) or p==(5 if by else -5):return 1
    break
   t+=d
 return 0
def gen(cp=0):
 ms=[]
 for s in range(128):
  if s&136:continue
  p=B[s]
  if not p or (p>0)!=W:continue
  a=abs(p)
  if a==1:
   d=16 if W else -16
   t=s+d
   if not(t&136) and not B[t] and (not cp or (t>>4)==(7 if W else 0)):
    if (t>>4)==(7 if W else 0):
     for q in(2,3,4,5):ms.append(s|t<<7|q<<14)
    else:
     ms.append(s|t<<7)
     if (s>>4)==(1 if W else 6):
      u=s+2*d
      if not B[u]:ms.append(s|u<<7)
   for t in(s+d-1,s+d+1):
    if t&136:continue
    if B[t] and (B[t]>0)!=W:
     if (t>>4)==(7 if W else 0):
      for q in(2,3,4,5):ms.append(s|t<<7|q<<14)
     else:ms.append(s|t<<7)
    elif t==E:ms.append(s|t<<7)
  elif a==2:
   for d in(31,33,14,18,-31,-33,-14,-18):
    t=s+d
    if not(t&136) and (not B[t] or (B[t]>0)!=W) and (not cp or B[t]):ms.append(s|t<<7)
  elif a==6:
   for d in(1,15,16,17,-1,-15,-16,-17):
    t=s+d
    if not(t&136) and (not B[t] or (B[t]>0)!=W) and (not cp or B[t]):ms.append(s|t<<7)
   if not cp and W and s==4:
    if C&1 and not B[5] and not B[6] and B[7]==4 and not atk(4,0) and not atk(5,0) and not atk(6,0):ms.append(4|6<<7)
    if C&2 and not B[3] and not B[2] and not B[1] and B[0]==4 and not atk(4,0) and not atk(3,0) and not atk(2,0):ms.append(4|2<<7)
   elif not cp and not W and s==116:
    if C&4 and not B[117] and not B[118] and B[119]==-4 and not atk(116,1) and not atk(117,1) and not atk(118,1):ms.append(116|118<<7)
    if C&8 and not B[115] and not B[114] and not B[113] and B[112]==-4 and not atk(116,1) and not atk(115,1) and not atk(114,1):ms.append(116|114<<7)
  else:
   ds=(15,17,-15,-17) if a==3 else (1,16,-1,-16) if a==4 else (15,17,-15,-17,1,16,-1,-16)
   for d in ds:
    t=s+d
    while not(t&136):
     if B[t]:
      if (B[t]>0)!=W:ms.append(s|t<<7)
      break
     if not cp:ms.append(s|t<<7)
     t+=d
 return ms
def mk(m):
 global W,C,E,HM,H,S,NP,BW,BB,KW,KB
 s=m&127;t=(m>>7)&127;pr=m>>14
 p=B[s];a=abs(p)
 cap=0;cq=-1
 if a==1 and t==E and not B[t]:
  cq=t-16 if W else t+16;cap=B[cq]
 elif B[t]:
  cq=t;cap=B[t]
 rf=-1;rp=0
 if a==6 and (t-s==2 or s-t==2):
  rf=t+1 if t>s else t-2;rp=B[rf]
 nc=C
 if a==6:nc&=12 if W else 3
 if s==0 or t==0:nc&=~2
 if s==7 or t==7:nc&=~1
 if s==112 or t==112:nc&=~8
 if s==119 or t==119:nc&=~4
 ne=(s+t)//2 if a==1 and (t-s==32 or s-t==32) else -1
 U.append((m,p,cap,cq,rf,rp,C,E,HM,H,S,NP,BW,BB,KW,KB))
 H^=Z[(p+6)*128+s]
 if cap:H^=Z[(cap+6)*128+cq]
 q=(pr if pr else a)*(1 if W else -1)
 H^=Z[(q+6)*128+t]
 if rf>=0:
  r2=t-1 if rf==t+1 else t+1
  H^=Z[(rp+6)*128+rf];H^=Z[(rp+6)*128+r2]
 H^=Z[1665+C]^Z[1665+nc]
 if E>=0:H^=Z[1681+(E&7)]
 if ne>=0:H^=Z[1681+(ne&7)]
 H^=Z[1664]
 S-=ps(p,s)
 if cap:S-=ps(cap,cq)
 S+=ps(q,t)
 if rf>=0:
  S-=ps(rp,rf);S+=ps(rp,r2)
 B[s]=0;B[t]=q
 if cap and cq!=t:B[cq]=0
 if rf>=0:
  B[rf]=0;B[r2]=rp
 if a==6:
  if W:KW=t
  else:KB=t
 if cap:
  ca=abs(cap)
  if ca==3:
   if cap>0:BW-=1
   else:BB-=1
  if 1<ca<6:NP-=V[ca]
 if pr:
  if pr==3:
   if W:BW+=1
   else:BB+=1
  NP+=V[pr]
 HM=0 if a==1 or cap else HM+1
 C=nc;E=ne;W=not W
def uk(m):
 global W,C,E,HM,H,S,NP,BW,BB,KW,KB
 o=U.pop()
 mm=o[0];s=mm&127;t=(mm>>7)&127
 p=o[1];cap=o[2];cq=o[3];rf=o[4];rp=o[5]
 B[t]=0;B[s]=p
 if cap:B[cq]=cap
 if rf>=0:
  r2=t-1 if rf==t+1 else t+1
  B[r2]=0;B[rf]=rp
 W=not W;C=o[6];E=o[7];HM=o[8];H=o[9];S=o[10];NP=o[11];BW=o[12];BB=o[13];KW=o[14];KB=o[15]
def su(f):
 global B,W,C,E,HM,H,S,NP,BW,BB,KW,KB
 B=[0]*128
 del U[:]
 fs=f.split()
 r=7
 for row in fs[0].split('/'):
  fl=0
  for ch in row:
   if ch.isdigit():fl+=int(ch)
   else:
    p='PNBRQK'.find(ch.upper())+1
    if ch.islower():p=-p
    B[r*16+fl]=p;fl+=1
  r-=1
 W=fs[1]=='w'
 C=0
 for ch in fs[2]:
  if ch in 'KQkq':C|=1<<'KQkq'.find(ch)
 E=-1
 if fs[3]!='-':E=(int(fs[3][1])-1)*16+'abcdefgh'.find(fs[3][0])
 HM=int(fs[4]) if len(fs)>4 else 0
 S=0;NP=0;BW=0;BB=0;H=0
 for s in range(128):
  if s&136:continue
  p=B[s]
  if not p:continue
  S+=ps(p,s)
  a=abs(p)
  if a==6:
   if p>0:KW=s
   else:KB=s
  elif a==3:
   if p>0:BW+=1
   else:BB+=1
  if 1<a<6:NP+=V[a]
  H^=Z[(p+6)*128+s]
 if not W:H^=Z[1664]
 H^=Z[1665+C]
 if E>=0:H^=Z[1681+(E&7)]
def uci(m):
 s=m&127;t=(m>>7)&127
 u=chr(97+(s&7))+str((s>>4)+1)+chr(97+(t&7))+str((t>>4)+1)
 pr=m>>14
 if pr:u+='nbrq'[pr-2]
 return u
def pm(u):
 s='abcdefgh'.find(u[0])+(int(u[1])-1)*16
 t='abcdefgh'.find(u[2])+(int(u[3])-1)*16
 pr='nbrq'.find(u[4])+2 if len(u)>4 else 0
 return s|t<<7|pr<<14
def ev():
 q=S+(30 if BW>1 else 0)-(30 if BB>1 else 0)
 return q if W else -q
def od(ms,pl,tm):
 sc=[]
 for m in ms:
  s=m&127;t=(m>>7)&127;p=B[s];v=0
  if m==tm:v=30000
  elif B[t]:v=10000+10*V[abs(B[t])]-V[abs(p)]
  elif m>>14:v=8000+V[m>>14]
  elif t==E and abs(p)==1:v=10900
  elif m==KL[pl][0]:v=7000
  elif m==KL[pl][1]:v=6500
  else:v=min(HS[p+6][t],6000)
  sc.append((v,m))
 sc.sort(key=lambda x:-x[0])
 return [m for v,m in sc]
def qs(a,b,pl):
 global Q
 Q+=1
 if Q>=QLIM:return ev()
 st=ev()
 if st>=b:return st
 if st>a:a=st
 k=KW if W else KB
 chk=atk(k,not W)
 if chk:ms=gen()
 else:ms=gen(1)
 ms=od(ms,pl,0)
 lg=0
 for m in ms:
  mk(m)
  k2=KW if not W else KB
  if atk(k2,W):
   uk(m);continue
  lg+=1
  sc=-qs(-b,-a,pl+1)
  uk(m)
  if Q>=QLIM:break
  if sc>=b:return sc
  if sc>a:a=sc
 if chk and not lg:return -M+pl
 return a
def sr(d,a,b,pl):
 global N
 N+=1
 if N>=LIM:return ev()
 if H in PA or HM>=100:return 0
 if a<-M+pl:a=-M+pl
 if b>M-pl:b=M-pl
 if a>=b:return a
 i=H&65535
 tm=0
 if TK[i]==H and TD[i]>=d:
  tm=TM[i]
  sc=TS[i]
  if sc>90000:sc-=pl
  elif sc<-90000:sc+=pl
  if TF[i]==0:return sc
  if TF[i]==1:
   if sc>a:a=sc
  elif sc<b:b=sc
  if a>=b:return sc
 if d<=0:return qs(a,b,pl)
 ms=od(gen(),pl,tm)
 k=KW if W else KB
 chk=atk(k,not W)
 ao=a;best=-M-1;bm=0;lg=0
 for m in ms:
  s=m&127;t=(m>>7)&127
  cp=1 if B[t] or (t==E and abs(B[s])==1) else 0
  PA.append(H)
  mk(m)
  k2=KW if not W else KB
  if atk(k2,W):
   uk(m);PA.pop();continue
  lg+=1
  sc=-sr(d-1,-b,-a,pl+1)
  uk(m);PA.pop()
  if sc>best:best=sc;bm=m
  if sc>a:a=sc
  if sc>=b:
   if not cp:
    if m!=KL[pl][0]:KL[pl][1]=KL[pl][0];KL[pl][0]=m
    HS[B[s]+6][t]+=d*d
   if TD[i]<=d:
    TD[i]=d;TF[i]=1;TM[i]=m;TK[i]=H;TS[i]=sc+pl if sc>90000 else sc-pl if sc<-90000 else sc
   return sc
 if not lg:return -M+pl if chk else 0
 fl=2 if best<=ao else 0
 if TD[i]<=d:
  TD[i]=d;TF[i]=fl;TM[i]=bm;TK[i]=H;TS[i]=best+pl if best>90000 else best-pl if best<-90000 else best
 return best
def rt():
 global N,Q,QLIM
 N=0;Q=0;QLIM=2*LIM
 ms=od(gen(),0,0)
 lg=[]
 for m in ms:
  PA.append(H);mk(m)
  k=KW if not W else KB
  if not atk(k,W):lg.append(m)
  uk(m);PA.pop()
 if not lg:return 0
 rs={};best=lg[0];d=0
 while N<LIM:
  d+=1
  lg.sort(key=lambda m:-rs.get(m,0))
  cur=0;cs=-M-1;a=-M;done=1
  for m in lg:
   PA.append(H);mk(m)
   sc=-sr(d-1,-M,-a,1)
   uk(m);PA.pop()
   rs[m]=sc
   if sc>cs:cs=sc;cur=m
   if sc>a:a=sc
   if N>=LIM:done=0;break
  if done and cur:
   best=cur
   if cs>90000:break
  if not done:break
 return best
def pt(p,b):
 r=urllib.request.Request(URL+p,data=json.dumps(b).encode(),headers={'content-type':'application/json'})
 try:
  with urllib.request.urlopen(r) as x:return json.load(x)
 except urllib.error.HTTPError as e:sys.exit(p+': HTTP '+str(e.code))
if __name__=='__main__':
 URL=os.environ.get('MAKEFUN_ENV_URL') or sys.exit('MAKEFUN_ENV_URL is not set')
 while 1:
  g=pt('/game',{})
  if g['status']=='done':break
  while g['status']=='your_move':
   su(g['start_fen'])
   PA[:]=[H]
   for mv in g['moves']:
    mk(pm(mv));PA.append(H)
   LIM=BUD[min(g['game'],8)-1]
   m=rt()
   if not m:
    g=pt('/resign',{'game':g['game']});break
   g=pt('/move',{'game':g['game'],'move':uci(m)})
  print('game '+str(g['game'])+': '+str(g['outcome'])+' by '+str(g['reason']),file=sys.stderr)
 print('done: '+str(g.get('wins'))+' won, '+str(g.get('draws'))+' drawn, '+str(g.get('losses'))+' lost',file=sys.stderr)
