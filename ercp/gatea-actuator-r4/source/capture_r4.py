from __future__ import annotations
import argparse, gzip, hashlib, json, mmap, os, platform, socket, struct, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

N=1<<18
CELL_BYTES=64
SUBSTRATE_BYTES=N*CELL_BYTES
TARGET_ROUND=32_094_413
TARGET_UNIX=1_789_086_603
ASSIGN_ROUND=32_094_613
ASSIGN_UNIX=1_789_087_203
TRIAL='ERCP-GATEA-ACTUATOR-R4-SAME-RUNNER-MMAP-v1'

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

REV9=tuple(int(f"{x:09b}"[::-1],2) for x in range(1<<9))

def bitrev18(x:int)->int:
    # Reverse the low and high 9-bit halves and swap them.
    # This is a bijection on exactly 18-bit coordinate indices.
    if not 0<=x<N: raise ValueError('bitrev18 input out of range')
    return (REV9[x & 0x1ff] << 9) | REV9[x >> 9]

def validate_bitrev18_permutation():
    seen=bytearray(N)
    for j in range(N):
        i=bitrev18(j)
        if seen[i]: raise SystemExit(f'bitrev18 is not a permutation; duplicate {i}')
        seen[i]=1
    if not all(seen): raise SystemExit('bitrev18 is not onto')

def host_identity():
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip() if Path('/proc/sys/kernel/random/boot_id').exists() else None
    cpu=Path('/proc/cpuinfo').read_bytes() if Path('/proc/cpuinfo').exists() else b''
    return {'hostname':socket.gethostname(),'boot_id':boot,'cpuinfo_sha256':hashlib.sha256(cpu).hexdigest(),
            'platform':platform.platform(),'runner_name':os.getenv('RUNNER_NAME'),'github_run_id':os.getenv('GITHUB_RUN_ID'),
            'github_run_attempt':os.getenv('GITHUB_RUN_ATTEMPT'),'github_sha':os.getenv('GITHUB_SHA')}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--outdir',required=True);ap.add_argument('--substrate',required=True);a=ap.parse_args()
    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True);sub=Path(a.substrate)
    validate_bitrev18_permutation()
    started=datetime.now(timezone.utc)
    if started.timestamp()>=TARGET_UNIX:raise SystemExit('capture began after target source')
    # Deterministic 16 MiB substrate, independent of all future sources.
    seed=b'ERCP-GATEA-ACTUATOR-R4-SUBSTRATE-v1'
    if not sub.exists():
        sub.write_bytes(hashlib.shake_256(seed).digest(SUBSTRATE_BYTES))
    if sub.stat().st_size!=SUBSTRATE_BYTES:raise SystemExit('substrate size')
    substrate_sha=sha256_file(sub)
    expected=hashlib.sha256(hashlib.shake_256(seed).digest(SUBSTRATE_BYTES)).hexdigest()
    if substrate_sha!=expected:raise SystemExit('substrate deterministic hash mismatch')
    lat=np.empty(N,dtype=np.uint32)
    with sub.open('r+b',buffering=0) as f:
        mm=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_WRITE)
        # Warm every page before measurement to suppress deterministic page-fault structure.
        sink=0
        for p in range(0,SUBSTRATE_BYTES,4096):sink^=mm[p]
        # Fixed bit-reversal traversal reduces simple sequential-prefetch structure.
        for j in range(N):
            i=bitrev18(j);pos=i*CELL_BYTES
            cell=mm[pos:pos+CELL_BYTES]
            t0=time.perf_counter_ns();s=cell
            for _ in range(8):s=hashlib.sha256(s).digest()
            dt=time.perf_counter_ns()-t0
            lat[i]=min(dt,0xffffffff)
            sink^=s[0]
        mm.close()
    # Deterministic rank transform; index breaks exact timing ties pre-source.
    idx=np.arange(N,dtype=np.int64)
    order=np.lexsort((idx,lat.astype(np.int64)))
    ranks=np.empty(N,dtype=np.int32);ranks[order]=np.arange(N,dtype=np.int32)
    bits=(ranks>=N//2).astype(np.uint8)
    packed=np.packbits(bits,bitorder='big').tobytes()
    (out/'R4_RECEIVER.bin').write_bytes(packed)
    (out/'R4_LATENCIES_U32.bin').write_bytes(lat.astype('<u4').tobytes())
    with gzip.GzipFile(filename=str(out/'R4_LATENCIES_U32.bin.gz'),mode='wb',compresslevel=9,mtime=0) as g:g.write((out/'R4_LATENCIES_U32.bin').read_bytes())
    ended=datetime.now(timezone.utc)
    if ended.timestamp()>=TARGET_UNIX:raise SystemExit('capture ended after target source')
    meta={'protocol':TRIAL,'capture_started_utc':started.isoformat(),'capture_ended_utc':ended.isoformat(),
          'N':N,'cell_bytes':CELL_BYTES,'substrate_bytes':SUBSTRATE_BYTES,'substrate_sha256':substrate_sha,
          'latencies_sha256':sha256_file(out/'R4_LATENCIES_U32.bin'),'latencies_gzip_sha256':sha256_file(out/'R4_LATENCIES_U32.bin.gz'),
          'receiver_sha256':hashlib.sha256(packed).hexdigest(),'receiver_ones':int(bits.sum()),'receiver_zeros':int(N-bits.sum()),
          'receiver_rule':'rank raw per-cell 8xSHA256 timing by (latency_ns,index); bit=1 iff rank>=N/2',
          'primary_receiver_weight_rule':'z_i=2*rank_i-(N-1), rank by (latency_ns,index)',
          'measurement_order':'18-bit bit-reversal traversal; result stored by coordinate index i',
          'target_round':TARGET_ROUND,'target_utc':datetime.fromtimestamp(TARGET_UNIX,timezone.utc).isoformat(),
          'assignment_round':ASSIGN_ROUND,'assignment_utc':datetime.fromtimestamp(ASSIGN_UNIX,timezone.utc).isoformat(),
          'host_identity':host_identity(),'timing_sink':int(sink)}
    (out/'R4_RECEIVER_META.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
    files=[out/'R4_RECEIVER.bin',out/'R4_LATENCIES_U32.bin',out/'R4_LATENCIES_U32.bin.gz',out/'R4_RECEIVER_META.json']
    (out/'SHA256SUMS_PRE.txt').write_text(''.join(f'{sha256_file(p)}  {p.name}\n' for p in files))
    print(json.dumps(meta,indent=2,sort_keys=True));print('R4_CAPTURE_PASS=true')
if __name__=='__main__':main()
