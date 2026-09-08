from __future__ import annotations
import argparse, hashlib, json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

CHAIN='52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971'
PUBLIC_KEY='83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a'
SCHEME='bls-unchained-g1-rfc9380'
GENESIS=1692803367
PERIOD=3
PINNED_ROUND=32_032_013
PINNED_UNIX=1_788_899_403
RELAYS=('https://api.drand.sh','https://api2.drand.sh','https://api3.drand.sh','https://drand.cloudflare.com')

def get_json(url:str):
    last=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'ERCP-GateA-Actuator-R3/1.0'})
            with urllib.request.urlopen(req,timeout=20) as r:return json.loads(r.read().decode())
        except Exception as e:
            last=e
            if attempt<3: time.sleep(3*(attempt+1))
    raise last

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,default=PINNED_ROUND);ap.add_argument('--out',required=True);a=ap.parse_args()
    rnd=int(a.round)
    if rnd!=PINNED_ROUND: raise SystemExit('source substitution forbidden: wrong round')
    rows=[]
    for base in RELAYS:
        url=f'{base}/{CHAIN}/public/{rnd}'
        x=get_json(url)
        row={'url':base,'round':int(x['round']),'signature':x['signature'],'randomness':x['randomness']}
        if row['round']!=rnd:raise SystemExit(f'round mismatch from {base}')
        if hashlib.sha256(bytes.fromhex(row['signature'])).hexdigest()!=row['randomness']:
            raise SystemExit(f'signature/randomness mismatch from {base}')
        rows.append(row)
    tuples={(r['round'],r['signature'],r['randomness']) for r in rows}
    if len(tuples)!=1:raise SystemExit('four-relay exact agreement failed')
    rr,sig,randomness=next(iter(tuples))
    out={'protocol':'ERCP-GATEA-ACTUATOR-R3-drand-source-v1','fetched_utc':datetime.now(timezone.utc).isoformat(),
      'chain_hash':CHAIN,'public_key':PUBLIC_KEY,'scheme_id':SCHEME,'genesis_time':GENESIS,'period_seconds':PERIOD,
      'round':rr,'round_unix':GENESIS+(rr-1)*PERIOD,'signature':sig,'randomness':randomness,'relays':rows,
      'four_relay_exact_agreement':True,'signature_to_randomness_sha256_verified':True}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
