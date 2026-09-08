from __future__ import annotations
from math import comb, cosh
from pathlib import Path
from typing import Sequence
import hashlib
import numpy as np

N=1<<18
FIELD_BITS=9; FIELD_SIZE=1<<FIELD_BITS; FIELD_MASK=FIELD_SIZE-1
GF_MODULUS=(1<<9)|(1<<1)|1  # x^9+x+1, irreducible over GF(2)
Q_BITS=9; L_BITS=18; C_BITS=1; MESSAGE_BITS=28
ROW_SPACE=comb(50,5)*comb(12,2)
SPEC_ID='ERCP-GATEA-ACTUATOR-R3-GF512-full-QRM28-v1'
assert ROW_SPACE==139_838_160 and Q_BITS+L_BITS+C_BITS==28


def gf_mul(a:int,b:int)->int:
    a&=FIELD_MASK;b&=FIELD_MASK;o=0
    while b:
        if b&1:o^=a
        b>>=1;a<<=1
        if a&FIELD_SIZE:a^=GF_MODULUS
    return o&FIELD_MASK

def gf_square(a:int)->int:return gf_mul(a,a)
def gf_trace(a:int)->int:
    x=a&FIELD_MASK;t=x
    for _ in range(1,FIELD_BITS):x=gf_square(x);t^=x
    if t not in (0,1):raise AssertionError
    return t

def multiplication_table()->np.ndarray:
    tab=np.empty((FIELD_SIZE,FIELD_SIZE),dtype=np.uint16)
    for a in range(FIELD_SIZE):tab[a]=np.fromiter((gf_mul(a,b) for b in range(FIELD_SIZE)),dtype=np.uint16,count=FIELD_SIZE)
    return tab

def trace_table()->np.ndarray:return np.asarray([gf_trace(a) for a in range(FIELD_SIZE)],dtype=np.uint8)
def gf2_rank_rows(rows:list[int],width:int)->int:
    a=list(map(int,rows));rank=0
    for col in range(width-1,-1,-1):
        piv=next((r for r in range(rank,len(a)) if (a[r]>>col)&1),None)
        if piv is None:continue
        a[rank],a[piv]=a[piv],a[rank];v=a[rank]
        for r in range(len(a)):
            if r!=rank and ((a[r]>>col)&1):a[r]^=v
        rank+=1
        if rank==width:break
    return rank

def polarization_rank(a:int)->int:
    if a==0:return 0
    C=np.zeros((FIELD_BITS,FIELD_BITS),dtype=np.uint8)
    for i in range(FIELD_BITS):
        for j in range(FIELD_BITS):C[i,j]=gf_trace(gf_mul(a,gf_mul(1<<i,1<<j)))
    rows=[]
    for i in range(FIELD_BITS):
        r=0
        for j in range(FIELD_BITS):
            if C[i,j]:r|=1<<(FIELD_BITS+j)
        rows.append(r)
    for j in range(FIELD_BITS):
        r=0
        for i in range(FIELD_BITS):
            if C[i,j]:r|=1<<i
        rows.append(r)
    return gf2_rank_rows(rows,2*FIELD_BITS)

def fwht(values:np.ndarray)->np.ndarray:
    a=np.asarray(values,dtype=np.int32).copy();h=1;n=a.size
    while h<n:
        x=a.reshape(-1,2*h);u=x[:,:h].copy();v=x[:,h:].copy();x[:,:h]=u+v;x[:,h:]=u-v;a=x.reshape(-1);h*=2
    return a

def fwht_float(values:np.ndarray)->np.ndarray:
    a=np.asarray(values,dtype=np.float64).copy();h=1;n=a.size
    while h<n:
        x=a.reshape(-1,2*h);u=x[:,:h].copy();v=x[:,h:].copy();x[:,:h]=u+v;x[:,h:]=u-v;a=x.reshape(-1);h*=2
    return a

def parity_table()->np.ndarray:return (np.bitwise_count(np.arange(N,dtype=np.uint32))&1).astype(np.uint8)

class QRM28:
    def __init__(self):
        self.mul=multiplication_table();self.tr=trace_table();idx=np.arange(N,dtype=np.uint32);self.x=(idx&FIELD_MASK).astype(np.uint16);self.y=(idx>>FIELD_BITS).astype(np.uint16);self.xy=self.mul[self.x,self.y];self.parity=parity_table();self.qbasis=np.empty((Q_BITS,N),dtype=np.uint8)
        for j in range(Q_BITS):self.qbasis[j]=self.tr[self.mul[1<<j,self.xy]]
        self.idx=np.arange(N,dtype=np.uint32)
    def qphase(self,q:int)->np.ndarray:
        ph=np.zeros(N,dtype=np.uint8)
        for j in range(Q_BITS):
            if (q>>j)&1:ph^=self.qbasis[j]
        return ph
    @staticmethod
    def split_message(msg:int):
        if not 0<=msg<(1<<28):raise ValueError
        q=msg>>19;s=msg&((1<<19)-1);l=s>>1;c=s&1;return q,l,c
    @staticmethod
    def join_message(q:int,l:int,c:int)->int:return (int(q)<<19)|(int(l)<<1)|int(c)
    def encode_bits(self,msg:int)->np.ndarray:
        q,l,c=self.split_message(msg);return (self.qphase(q)^self.parity[np.bitwise_and(self.idx,np.uint32(l))]^np.uint8(c)).astype(np.uint8,copy=False)
    def _error_key(self,received_bits:np.ndarray,msg:int)->bytes:
        e=np.asarray(received_bits,dtype=np.uint8)^self.encode_bits(msg)
        return np.packbits(e,bitorder='big').tobytes()
    def decode_full(self,received_bits:np.ndarray):
        rb=np.asarray(received_bits,dtype=np.uint8)
        if len(rb)!=N:raise ValueError
        y=(1-2*rb.astype(np.int16)).astype(np.int32)
        best=-1; best_qs=[]; first_best_W=None
        phase=np.zeros(N,dtype=np.uint8);prev_gray=0
        for k in range(1<<Q_BITS):
            gray=k^(k>>1)
            if k:
                diff=gray^prev_gray;j=(diff&-diff).bit_length()-1;phase^=self.qbasis[j]
            prev_gray=gray
            W=fwht(y*(1-2*phase.astype(np.int32)))
            local=int(np.abs(W).max())
            if local>best:
                best=local;best_qs=[gray];first_best_W=W.copy()
            elif local==best:
                best_qs.append(gray)
        chosen=None;best_key=None;tie_count=0
        for qi,qv in enumerate(best_qs):
            if qi==0:
                W=first_best_W
            else:
                ph=self.qphase(qv);W=fwht(y*(1-2*ph.astype(np.int32)))
            locs=np.flatnonzero(np.abs(W)==best)
            for aa in locs:
                val=int(W[int(aa)]); c=0 if val>=0 else 1
                msg=self.join_message(qv,int(aa),c); tie_count+=1
                if chosen is None:
                    chosen=msg; continue
                if best_key is None:best_key=self._error_key(rb,int(chosen))
                key=self._error_key(rb,msg)
                if key<best_key:chosen=msg;best_key=key
        if chosen is None:raise AssertionError('decoder found no candidate')
        return int(chosen),int((N-best)//2),int(best),int(tie_count)

    def decode_full_index_tie(self,received_bits:np.ndarray):
        rb=np.asarray(received_bits,dtype=np.uint8)
        if len(rb)!=N:raise ValueError
        y=(1-2*rb.astype(np.int16)).astype(np.int32)
        best=-1;best_qs=[];phase=np.zeros(N,dtype=np.uint8);prev_gray=0
        for k in range(1<<Q_BITS):
            gray=k^(k>>1)
            if k:
                diff=gray^prev_gray;j=(diff&-diff).bit_length()-1;phase^=self.qbasis[j]
            prev_gray=gray
            W=fwht(y*(1-2*phase.astype(np.int32)));local=int(np.abs(W).max())
            if local>best:best=local;best_qs=[gray]
            elif local==best:best_qs.append(gray)
        chosen=None;tie_count=0
        for qv in best_qs:
            ph=self.qphase(qv);W=fwht(y*(1-2*ph.astype(np.int32)));absW=np.abs(W);locs=np.flatnonzero(absW==best)
            tie_count+=int(locs.size)
            vals=W[locs];cs=(vals<0).astype(np.uint64)
            msgs=(np.uint64(qv)<<np.uint64(19)) | (locs.astype(np.uint64)<<np.uint64(1)) | cs
            local_min=int(msgs.min())
            if chosen is None or local_min<chosen:chosen=local_min
        if chosen is None:raise AssertionError('decoder found no candidate')
        return int(chosen),int((N-best)//2),int(best),int(tie_count)

    def decode_soft(self,soft_values:np.ndarray):
        y=np.asarray(soft_values,dtype=np.float64)
        if len(y)!=N or not np.all(np.isfinite(y)): raise ValueError
        best=-np.inf; chosen=None; ties=0
        phase=np.zeros(N,dtype=np.uint8); prev_gray=0
        for k in range(1<<Q_BITS):
            gray=k^(k>>1)
            if k:
                diff=gray^prev_gray;j=(diff&-diff).bit_length()-1;phase^=self.qbasis[j]
            prev_gray=gray;q=gray
            de=y*(1.0-2.0*phase.astype(np.float64)); W=fwht_float(de)
            absW=np.abs(W); local=float(absW.max())
            tol=1e-10*max(1.0,abs(local),abs(best) if np.isfinite(best) else 1.0)
            if local < best-tol: continue
            locs=np.flatnonzero(np.abs(absW-local)<=tol)
            if local>best+tol:best=local; chosen=None; ties=0
            for aa in locs:
                val=float(W[int(aa)]); c=0 if val>=0 else 1
                msg=self.join_message(q,int(aa),c); ties+=1
                if chosen is None or msg<chosen: chosen=msg
        return int(chosen),float(best),int(ties)

def exact_weight_enumerator():
    return {0:1,N:1,N//2:(1<<19)-2,N//2-256:511*(1<<18),N//2+256:511*(1<<18)}
def minimum_distance():return N//2-256

def bsc_bhattacharyya_from_pmatch(p:float)->float:
    q=1-float(p);return 2*(p*q)**0.5
def ml_frame_error_union_bound_p(p:float)->float:
    z=bsc_bhattacharyya_from_pmatch(p);s=0.0
    for w,c in exact_weight_enumerator().items():
        if w:s+=c*(z**w)
    return min(1.0,0.5*s)
def solve_p_for_union_bound(target=.01):
    lo,hi=.5,.55
    for _ in range(80):
        mid=(lo+hi)/2
        if ml_frame_error_union_bound_p(mid)<=target:hi=mid
        else:lo=mid
    return hi
