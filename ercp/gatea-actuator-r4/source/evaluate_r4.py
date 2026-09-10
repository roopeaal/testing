from __future__ import annotations
import argparse, hashlib, json, math, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from numba import njit
import gatea_actuator_r4_qrm as qrm

SPEC_ID='ERCP-GATEA-ACTUATOR-R4-SAME-RUNNER-RANDOMIZED-MMAP-v1'
N=1<<18
TARGET_ROUND=32_094_413; TARGET_UNIX=1_789_086_603
ASSIGNMENT_ROUND=32_094_613; ASSIGNMENT_UNIX=1_789_087_203
MAX_START_LAG=600
CHAIN='52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971'
PUBLIC_KEY='83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a'
SCHEME='bls-unchained-g1-rfc9380'
FIVE_SIGMA=2.866515718791933e-7
ROUNDS_ACTIVE_ONE=1024; ROUNDS_ACTIVE_ZERO=16; ROUNDS_SHAM=520

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

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def parse_utc(s:str):
    if s.endswith('Z'):s=s[:-1]+'+00:00'
    return datetime.fromisoformat(s).astimezone(timezone.utc)

def extract28(h:str)->int:
    b=bytes.fromhex(h)
    if len(b)!=32:raise SystemExit('randomness length')
    return int.from_bytes(b[:4],'big')>>4

def ranks_from_latencies(lat:np.ndarray)->np.ndarray:
    if lat.shape!=(N,):raise ValueError('latency length')
    idx=np.arange(N,dtype=np.int64);order=np.lexsort((idx,lat.astype(np.int64)))
    ranks=np.empty(N,dtype=np.int64);ranks[order]=np.arange(N,dtype=np.int64)
    return ranks

def exact_tail(codec:qrm.QRM28,weights:np.ndarray,msg:int):
    w=np.asarray(weights,dtype=np.int64)
    if w.shape!=(N,):raise ValueError('weights length')
    q,l,c=codec.split_message(int(msg));ph=codec.qphase(q)
    obs=(w*(1-2*ph.astype(np.int64))).copy();fwht_i64_inplace(obs)
    observed=int(obs[l])*(1 if c==0 else -1)
    ge=gt=0;total=0;phase=np.zeros(N,dtype=np.uint8);prev=0
    for k in range(1<<qrm.Q_BITS):
        gray=k^(k>>1)
        if k:
            diff=gray^prev;j=(diff&-diff).bit_length()-1;phase^=codec.qbasis[j]
        prev=gray
        W=(w*(1-2*phase.astype(np.int64))).copy();fwht_i64_inplace(W)
        ge+=int(np.count_nonzero(W>=observed))+int(np.count_nonzero(-W>=observed))
        gt+=int(np.count_nonzero(W>observed))+int(np.count_nonzero(-W>observed))
        total+=2*W.size
    null_var=float(np.dot(w.astype(np.float64),w.astype(np.float64)))
    sd=math.sqrt(null_var)
    return {'message':int(msg),'observed_score':observed,'null_sd_exact':sd,'standardized_score':observed/sd if sd else None,
            'tail_count_ge':ge,'tail_count_gt':gt,'message_space':total,'exact_one_sided_randomization_p':ge/total}

def validate_source(s:dict,round_:int,unix_:int):
    for k,v in {'chain_hash':CHAIN,'public_key':PUBLIC_KEY,'scheme_id':SCHEME,'round':round_,'round_unix':unix_}.items():
        if s.get(k)!=v:raise SystemExit(f'source gate {round_} {k}')
    if s.get('bls_verified') is not True or s.get('drand_version')!='v2.1.7':raise SystemExit('BLS flag/version')
    rows=s.get('relays',[])
    if len(rows)!=4:raise SystemExit('four relays')
    tuples={(int(r['round']),r['signature'],r['randomness']) for r in rows}
    if len(tuples)!=1:raise SystemExit('relay agreement')
    rr,sig,rnd=next(iter(tuples))
    if rr!=round_ or sig!=s.get('signature') or rnd!=s.get('randomness'):raise SystemExit('canonical source')
    if hashlib.sha256(bytes.fromhex(sig)).hexdigest()!=rnd:raise SystemExit('signature/randomness')

def evaluate(release:Path,pre:Path,post:Path,out:Path):
    lock=json.loads((release/'GATEA_ACTUATOR_R4_LOCK.json').read_text())
    if lock.get('protocol')!=SPEC_ID:raise SystemExit('lock protocol')
    for name,want in lock['release_file_hashes'].items():
        if sha256_file(release/name)!=want:raise SystemExit(f'release hash {name}')
    commit=json.loads((pre/'R4_PRE_SOURCE_COMMITMENT.json').read_text())
    meta=json.loads((pre/'R4_RECEIVER_META.json').read_text())
    for name in ['R4_RECEIVER.bin','R4_LATENCIES_U32.bin','R4_RECEIVER_META.json']:
        if sha256_file(pre/name)!=commit['file_sha256'][name]:raise SystemExit(f'precommit file hash {name}')
    if commit['workflow_trigger_sha']!=meta['host_identity']['github_sha'] or commit['github_run_id']!=meta['host_identity']['github_run_id']:raise SystemExit('trigger identity')
    if str(commit.get('github_run_attempt'))!='1' or str(meta['host_identity'].get('github_run_attempt'))!='1':raise SystemExit('only original run attempt 1 is valid')
    if parse_utc(commit['created_utc']).timestamp() >= TARGET_UNIX-1800:raise SystemExit('pre-source commitment margin <30 minutes')
    if commit.get('target_round')!=TARGET_ROUND or commit.get('assignment_round')!=ASSIGNMENT_ROUND:raise SystemExit('precommit future IDs')
    if parse_utc(meta['capture_ended_utc']).timestamp()>=TARGET_UNIX:raise SystemExit('receiver not pre-target')
    if meta['target_round']!=TARGET_ROUND or meta['assignment_round']!=ASSIGNMENT_ROUND:raise SystemExit('receiver future IDs')
    lat=np.fromfile(pre/'R4_LATENCIES_U32.bin',dtype='<u4')
    ranks=ranks_from_latencies(lat);z=2*ranks-(N-1)
    rb=np.frombuffer((pre/'R4_RECEIVER.bin').read_bytes(),dtype=np.uint8);bits=np.unpackbits(rb,bitorder='big')
    if bits.size!=N or not np.array_equal(bits,(ranks>=N//2).astype(np.uint8)):raise SystemExit('receiver bit reconstruction')
    target=json.loads((post/'R4_TARGET_SOURCE.json').read_text());assign=json.loads((post/'R4_ASSIGNMENT_SOURCE.json').read_text())
    validate_source(target,TARGET_ROUND,TARGET_UNIX);validate_source(assign,ASSIGNMENT_ROUND,ASSIGNMENT_UNIX)
    tmsg=extract28(target['randomness']);amsg=extract28(assign['randomness']);codec=qrm.QRM28();X=codec.encode_bits(tmsg);A=codec.encode_bits(amsg)
    log=json.loads((post/'R4_ACTUATOR_LOG.json').read_text())
    if log.get('protocol')!='ERCP-GATEA-ACTUATOR-R4-GITHUB-SAME-RUNNER-RANDOMIZED-v1':raise SystemExit('actuator protocol')
    expected={'target_round':TARGET_ROUND,'assignment_round':ASSIGNMENT_ROUND,'target_randomness':target['randomness'],'assignment_randomness':assign['randomness'],'target_message28':tmsg,'assignment_message28':amsg,'assignment_eval_message28':amsg^1,
              'rounds_active_one':ROUNDS_ACTIVE_ONE,'rounds_active_zero':ROUNDS_ACTIVE_ZERO,'rounds_sham':ROUNDS_SHAM,'gomaxprocs':1}
    for k,v in expected.items():
        if log.get(k)!=v:raise SystemExit(f'actuator gate {k}')
    if log.get('target_codeword_sha256')!=hashlib.sha256(np.packbits(X,bitorder='big').tobytes()).hexdigest():raise SystemExit('target codeword')
    if log.get('assignment_codeword_sha256')!=hashlib.sha256(np.packbits(A,bitorder='big').tobytes()).hexdigest():raise SystemExit('assignment codeword')
    active=int(A.sum());sham=N-active;a1=int(np.count_nonzero((A==1)&(X==1)));a0=int(np.count_nonzero((A==1)&(X==0)))
    if (log['active_count'],log['sham_count'],log['active_target_one_count'],log['active_target_zero_count'])!=(active,sham,a1,a0):raise SystemExit('actuator counts')
    total=a1*ROUNDS_ACTIVE_ONE+a0*ROUNDS_ACTIVE_ZERO+sham*ROUNDS_SHAM
    if log['total_hash_rounds']!=total:raise SystemExit('total workload')
    start=parse_utc(log['started_utc']).timestamp();end=parse_utc(log['ended_utc']).timestamp()
    if not(ASSIGNMENT_UNIX<=start<=ASSIGNMENT_UNIX+MAX_START_LAG and end>start):raise SystemExit('actuator timing')
    hp=log['host_identity_pre'];hq=log['host_identity_post'];mh=meta['host_identity']
    for key in ['hostname','boot_id','github_run_id','github_run_attempt']:
        if hp.get(key)!=mh.get(key) or hq.get(key)!=mh.get(key):raise SystemExit(f'same-runner {key}')
    if log.get('same_boot_id') is not True or log.get('same_hostname') is not True:raise SystemExit('same-runner flags')
    if log['substrate_pre_sha256']!=meta['substrate_sha256']:raise SystemExit('substrate continuity')
    if sha256_file(release/'r4_actuator')!=commit['actuator_binary_sha256']:raise SystemExit('actuator binary hash')
    # Direction is frozen by physical workload: X=1 is +504 rounds vs sham and X=0 is -504 rounds vs sham.
    xsign=2*X.astype(np.int64)-1
    primary_weights=z*xsign
    primary=exact_tail(codec,primary_weights,amsg^1)
    source_main=exact_tail(codec,z,tmsg^1)
    assignment_main=exact_tail(codec,z,amsg^1)
    p=primary['exact_one_sided_randomization_p']
    result={'protocol':SPEC_ID,'evaluated_utc':datetime.now(timezone.utc).isoformat(),'validity':'PASS',
      'receiver_sha256':meta['receiver_sha256'],'latencies_sha256':meta['latencies_sha256'],'substrate_pre_sha256':meta['substrate_sha256'],'substrate_post_sha256':log['substrate_post_sha256'],
      'target_round':TARGET_ROUND,'assignment_round':ASSIGNMENT_ROUND,'target_message28':tmsg,'assignment_message28':amsg,
      'primary_randomized_actuator_interaction':primary,'secondary_target_source_main_effect':source_main,'secondary_assignment_main_effect':assignment_main,
      'five_sigma_one_sided_threshold':FIVE_SIGMA,'strong_candidate':bool(p<=FIVE_SIGMA),
      'interpretation':'GATE_A_LOCAL_FUTURE_ACTUATOR_INTERACTION_CANDIDATE_REQUIRES_INDEPENDENT_REPLICATION' if p<=FIVE_SIGMA else 'NO_GATE_A_LOCAL_FUTURE_ACTUATOR_INTERACTION_IN_R4',
      'scientific_scope':'same GitHub-hosted runner and persistent mmap file across pre-source timing receiver and later independently randomized target/active-sham physical CPU+memory actuation; primary conditions on receiver and target and randomizes over independent later assignment message; no signalling claim'}
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2,sort_keys=True))

def selftest():
    codec=qrm.QRM28();m=0x0A5A5A5;w=(1-2*codec.encode_bits(m).astype(np.int64));r=exact_tail(codec,w,m)
    if r['observed_score']!=N or r['tail_count_ge']!=1:raise SystemExit(f'exact tail selftest {r}')
    target=0x0123456;assign=0x0789abc;X=codec.encode_bits(target);A=codec.encode_bits(assign)
    z=(2*A.astype(np.int64)-1)*(2*X.astype(np.int64)-1)
    p=exact_tail(codec,z*(2*X.astype(np.int64)-1),assign^1)
    if p['observed_score']!=N or p['tail_count_ge']!=1:raise SystemExit(f'interaction orientation selftest {p}')
    print(json.dumps({'selftest':'PASS','exact_p':r['exact_one_sided_randomization_p'],'interaction_exact_p':p['exact_one_sided_randomization_p']},indent=2))

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True);sp.add_parser('selftest');e=sp.add_parser('evaluate');e.add_argument('--release-dir',required=True);e.add_argument('--pre-dir',required=True);e.add_argument('--post-dir',required=True);e.add_argument('--out',required=True);a=ap.parse_args()
    if a.cmd=='selftest':selftest()
    else:evaluate(Path(a.release_dir),Path(a.pre_dir),Path(a.post_dir),Path(a.out))
if __name__=='__main__':main()
