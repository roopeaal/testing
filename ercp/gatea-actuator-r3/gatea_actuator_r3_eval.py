from __future__ import annotations
import argparse, hashlib, json, math, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np
from numba import njit
import gatea_actuator_r3_qrm as qrm

SPEC_ID='ERCP-GATEA-ACTUATOR-R3-NIST-TO-DRAND-GITHUB-CPU-v1'
N=qrm.N
PINNED_ROUND=32_032_013
PINNED_UNIX=1_788_899_403
MAX_ACTUATION_LAG_SECONDS=21_600
RECEIVER_CHAIN=2
RECEIVER_FIRST=1_931_505
RECEIVER_LAST=1_932_016
QUICKNET_CHAIN='52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971'
QUICKNET_PUBLIC_KEY='83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a'
QUICKNET_SCHEME='bls-unchained-g1-rfc9380'
FIVE_SIGMA_ONE_SIDED_P=2.866515718791933e-7
ACTUATOR_BIT_OFFSET=28
ROUNDS_ONE=1024
ROUNDS_ZERO=16

@njit(cache=True)
def fwht_i64_inplace(a):
    n=a.shape[0];h=1
    while h<n:
        step=h*2
        for base in range(0,n,step):
            for j in range(h):
                u=a[base+j];v=a[base+j+h]
                a[base+j]=u+v;a[base+j+h]=u-v
        h=step

def sha256_file(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def parse_utc(s:str)->datetime:
    if s.endswith('Z'): s=s[:-1]+'+00:00'
    dt=datetime.fromisoformat(s)
    if dt.tzinfo is None: raise ValueError('naive timestamp')
    return dt.astimezone(timezone.utc)

def source_message_block(randomness_hex:str,bit_offset:int=ACTUATOR_BIT_OFFSET)->int:
    b=bytes.fromhex(randomness_hex)
    if len(b)!=32: raise SystemExit('drand randomness must be 32 bytes')
    if not 0<=bit_offset<=228: raise SystemExit('bad bit offset')
    v=0
    for k in range(28):
        pos=bit_offset+k
        v=(v<<1)|((b[pos//8]>>(7-(pos%8)))&1)
    return v

def exact_hard_tail(codec:qrm.QRM28, received_bits:np.ndarray, msg:int):
    rb=np.asarray(received_bits,dtype=np.uint8)
    if rb.size!=N: raise ValueError('receiver length')
    weights=(1-2*rb.astype(np.int16)).astype(np.int64)
    q,l,c=codec.split_message(int(msg))
    ph=codec.qphase(q)
    obs_vec=(weights*(1-2*ph.astype(np.int64))).copy();fwht_i64_inplace(obs_vec)
    observed=int(obs_vec[l])*(1 if c==0 else -1)
    ge=gt=0;total=0;sumsq=0
    phase=np.zeros(N,dtype=np.uint8);prev_gray=0
    for k in range(1<<qrm.Q_BITS):
        gray=k^(k>>1)
        if k:
            diff=gray^prev_gray;j=(diff&-diff).bit_length()-1;phase^=codec.qbasis[j]
        prev_gray=gray
        W=(weights*(1-2*phase.astype(np.int64))).copy();fwht_i64_inplace(W)
        ge += int(np.count_nonzero(W>=observed))+int(np.count_nonzero(-W>=observed))
        gt += int(np.count_nonzero(W>observed))+int(np.count_nonzero(-W>observed))
        sumsq += 2*int(np.dot(W,W));total += 2*W.size
    sd=math.sqrt(sumsq/total)
    return {'message':int(msg),'observed_score':int(observed),'null_sd_exact':sd,
            'standardized_score':observed/sd if sd else None,'tail_count_ge':int(ge),'tail_count_gt':int(gt),
            'message_space':int(total),'exact_one_sided_randomization_p':ge/total}

def validate_receiver(root:Path,lock:dict):
    receiver=(root/'GATEA_ACTUATOR_R3_RECEIVER.bin').read_bytes()
    if len(receiver)!=32768:raise SystemExit('receiver byte length')
    receiver_sha=hashlib.sha256(receiver).hexdigest()
    meta=json.loads((root/'GATEA_ACTUATOR_R3_RECEIVER_META.json').read_text())
    if receiver_sha!=meta['receiver_sha256']:raise SystemExit('receiver metadata hash mismatch')
    want=(RECEIVER_CHAIN,RECEIVER_FIRST,RECEIVER_LAST,512,'localRandomValue')
    got=(meta['chain_index'],meta['first_pulse'],meta['last_pulse'],meta['pulse_count'],meta['receiver_field'])
    if got!=want:raise SystemExit(f'receiver identity gate fail: {got}')
    if not (meta.get('strictly_increasing_timestamps') is True and meta.get('all_pulses_before_future_source') is True):raise SystemExit('receiver temporal integrity flags fail')
    if parse_utc(meta['last_timestamp']).timestamp()>=PINNED_UNIX:raise SystemExit('receiver not strictly earlier than source')
    if lock.get('receiver_sha256') and receiver_sha!=lock['receiver_sha256']:raise SystemExit('receiver frozen hash mismatch')
    return receiver,meta

def validate_source(source_path:Path,bls_path:Path):
    source=json.loads(source_path.read_text());bls=json.loads(bls_path.read_text())
    for k,v in {'chain_hash':QUICKNET_CHAIN,'public_key':QUICKNET_PUBLIC_KEY,'scheme_id':QUICKNET_SCHEME,'round':PINNED_ROUND}.items():
        if source.get(k)!=v:raise SystemExit(f'drand source gate fail: {k}')
    if len(source.get('relays',[]))!=4:raise SystemExit('exactly four relay records required')
    tuples={(int(x['round']),x['signature'],x['randomness']) for x in source['relays']}
    if len(tuples)!=1:raise SystemExit('relay agreement fail')
    rr,sig,rnd=next(iter(tuples))
    if rr!=PINNED_ROUND or sig!=source.get('signature') or rnd!=source.get('randomness'):raise SystemExit('canonical source mismatch')
    if hashlib.sha256(bytes.fromhex(sig)).hexdigest()!=rnd:raise SystemExit('signature/randomness fail')
    if not (bls.get('bls_verified') is True and bls.get('round')==PINNED_ROUND and bls.get('signature')==sig and bls.get('randomness')==rnd and bls.get('public_key')==QUICKNET_PUBLIC_KEY and bls.get('scheme_id')==QUICKNET_SCHEME):raise SystemExit('BLS evidence gate fail')
    return source,bls

def validate_actuator(log_path:Path,source:dict,codec:qrm.QRM28):
    a=json.loads(log_path.read_text())
    if a.get('protocol')!='ERCP-GATEA-ACTUATOR-R3-GITHUB-CPU-v1':raise SystemExit('actuator protocol')
    if a.get('source_round')!=PINNED_ROUND or a.get('randomness')!=source['randomness']:raise SystemExit('actuator source binding')
    if a.get('message_bit_offset')!=ACTUATOR_BIT_OFFSET:raise SystemExit('actuator bit offset')
    msg=source_message_block(source['randomness'])
    if a.get('message28')!=msg:raise SystemExit('actuator message binding')
    target=codec.encode_bits(msg);packed=np.packbits(target,bitorder='big').tobytes();cwsha=hashlib.sha256(packed).hexdigest()
    ones=int(target.sum());zeros=N-ones
    if a.get('codeword_sha256')!=cwsha or a.get('ones')!=ones or a.get('zeros')!=zeros:raise SystemExit('actuator codeword binding')
    if a.get('rounds_one')!=ROUNDS_ONE or a.get('rounds_zero')!=ROUNDS_ZERO:raise SystemExit('actuator rounds')
    total=ones*ROUNDS_ONE+zeros*ROUNDS_ZERO
    if a.get('total_hash_rounds')!=total:raise SystemExit('actuator total hash rounds')
    if a.get('gomaxprocs')!=1:raise SystemExit('actuator GOMAXPROCS')
    cps=a.get('checkpoints',[])
    if len(cps)!=N//4096 or [x.get('index') for x in cps]!=list(range(4095,N,4096)):raise SystemExit('actuator checkpoints')
    started=parse_utc(a['started_utc']);ended=parse_utc(a['ended_utc']);source_dt=datetime.fromtimestamp(PINNED_UNIX,tz=timezone.utc)
    if started<source_dt:raise SystemExit('actuator began before source')
    if started>source_dt+timedelta(seconds=MAX_ACTUATION_LAG_SECONDS):raise SystemExit('actuator start outside lag window')
    if not ended>started:raise SystemExit('actuator time ordering')
    return a

def evaluate(root:Path,source_path:Path,bls_path:Path,actuator_log:Path,out_path:Path):
    lock=json.loads((root/'GATEA_ACTUATOR_R3_LOCK.json').read_text())
    for name,want in lock['release_file_hashes'].items():
        p=root/name;got=sha256_file(p)
        if got!=want:raise SystemExit(f'release hash gate fail: {name}')
    receiver,meta=validate_receiver(root,lock);source,bls=validate_source(source_path,bls_path);codec=qrm.QRM28();act=validate_actuator(actuator_log,source,codec)
    rb=np.unpackbits(np.frombuffer(receiver,dtype=np.uint8),bitorder='big');msg=source_message_block(source['randomness'])
    t=time.time();stat=exact_hard_tail(codec,rb,msg);target=codec.encode_bits(msg);agree=int(np.count_nonzero(rb==target));p=stat['exact_one_sided_randomization_p']
    result={'protocol':SPEC_ID,'evaluated_utc':datetime.now(timezone.utc).isoformat(),'validity':'PASS',
      'receiver_source':'NIST Randomness Beacon 2.0 chain 2 localRandomValue pulses 1931505..1932016, frozen pre-source',
      'receiver_sha256':hashlib.sha256(receiver).hexdigest(),'receiver_last_timestamp':meta['last_timestamp'],'source_round':PINNED_ROUND,'randomness':source['randomness'],
      'future_actuated_message_bit_offset':ACTUATOR_BIT_OFFSET,'future_actuated_message_28':msg,'actuator_codeword_sha256':act['codeword_sha256'],
      'actuator_elapsed_seconds':act['elapsed_seconds'],'actuator_total_hash_rounds':act['total_hash_rounds'],'primary':stat,
      'hard_agreement_count':agree,'hard_agreement_fraction':agree/N,'five_sigma_one_sided_threshold':FIVE_SIGMA_ONE_SIDED_P,
      'strong_gateA_actuator_candidate':bool(p<=FIVE_SIGMA_ONE_SIDED_P),
      'interpretation':('GATE_A_FUTURE_ACTUATOR_PAST_CORRELATION_CANDIDATE_REQUIRES_INDEPENDENT_REPLICATION' if p<=FIVE_SIGMA_ONE_SIDED_P else 'NO_GATE_A_FUTURE_ACTUATOR_PAST_ANOMALY_IN_R3'),
      'scientific_scope':'prospective Gate-A actuator attribution screen; future message physically enacted on GitHub-hosted CPU after pinned source; no controllability or signalling claim','elapsed_seconds':time.time()-t}
    out_path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2,sort_keys=True))

def selftest():
    codec=qrm.QRM28();rnd='0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
    if source_message_block(rnd,0)!=0x0123456:raise SystemExit('block0 extraction failed')
    if source_message_block(rnd,28)!=0x789abcd:raise SystemExit('block1 extraction failed')
    msg=0x0A5A5A5;rb=codec.encode_bits(msg);r=exact_hard_tail(codec,rb,msg)
    if r['observed_score']!=N or r['tail_count_ge']!=1 or r['message_space']!=(1<<28):raise SystemExit(f'selftest failed: {r}')
    print(json.dumps({'selftest':'PASS','exact_p':r['exact_one_sided_randomization_p']},indent=2))

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True);sp.add_parser('selftest');e=sp.add_parser('evaluate')
    e.add_argument('--release-dir',required=True);e.add_argument('--source-json',required=True);e.add_argument('--bls-json',required=True);e.add_argument('--actuator-log',required=True);e.add_argument('--out',required=True)
    a=ap.parse_args()
    if a.cmd=='selftest':selftest()
    else:evaluate(Path(a.release_dir),Path(a.source_json),Path(a.bls_json),Path(a.actuator_log),Path(a.out))
if __name__=='__main__':main()
