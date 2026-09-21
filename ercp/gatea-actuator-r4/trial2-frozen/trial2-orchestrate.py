from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, time

LOCK_SHA256="599ca4bd33bf767c3e3f4469bb2b1229962e1b55f650bf0aa825ee880c4d3a45"
TARGET_ROUND=32_397_413
ASSIGNMENT_ROUND=32_397_613
TARGET_UNIX=1_789_995_603
ASSIGNMENT_UNIX=1_789_996_203

def h(p:pathlib.Path)->str:
    q=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            q.update(b)
    return q.hexdigest()

def load_and_verify_release(release:pathlib.Path):
    lockp=release/"GATEA_ACTUATOR_R4_LOCK.json"
    got=h(lockp)
    if got!=LOCK_SHA256:
        raise SystemExit(f"immutable lock SHA mismatch: {got}")
    lock=json.loads(lockp.read_text())
    if lock.get("protocol")!="ERCP-GATEA-ACTUATOR-R4-SAME-RUNNER-RANDOMIZED-MMAP-v1":
        raise SystemExit("protocol")
    if lock.get("status")!="PRESOURCE_DESIGN_LOCK_TRIAL2":
        raise SystemExit("lock status")
    fs=lock["future_sources"]
    if fs["target"]["round"]!=TARGET_ROUND or fs["assignment"]["round"]!=ASSIGNMENT_ROUND:
        raise SystemExit("future IDs")
    for name,want in lock["release_file_hashes"].items():
        got=h(release/name)
        if got!=want:
            raise SystemExit(f"release hash {name}: {got} != {want}")
    return lock

def verify_release(release:pathlib.Path):
    load_and_verify_release(release)
    if time.time()>=TARGET_UNIX-1800:
        raise SystemExit("less than 30 min before target")
    if os.environ.get("GITHUB_RUN_ATTEMPT")!="1":
        raise SystemExit("only run attempt 1 is eligible")
    print("R4_TRIAL2_RELEASE_GATE=PASS")
    print("R4_TRIAL2_LOCK_SHA256="+LOCK_SHA256)

def make_commitment(release:pathlib.Path,pre:pathlib.Path,build:pathlib.Path,out:pathlib.Path):
    load_and_verify_release(release)
    if time.time()>=TARGET_UNIX-1800:
        raise SystemExit("precommit margin <30 minutes")
    if os.environ.get("GITHUB_RUN_ATTEMPT")!="1":
        raise SystemExit("attempt")
    meta=json.loads((pre/"R4_RECEIVER_META.json").read_text())
    if meta.get("target_round")!=TARGET_ROUND or meta.get("assignment_round")!=ASSIGNMENT_ROUND:
        raise SystemExit("receiver future IDs")
    ended=datetime.datetime.fromisoformat(meta["capture_ended_utc"])
    if ended.timestamp()>=TARGET_UNIX:
        raise SystemExit("receiver ended after target")
    names=["R4_RECEIVER.bin","R4_LATENCIES_U32.bin","R4_LATENCIES_U32.bin.gz","R4_RECEIVER_META.json","R4_CAPTURE_STDOUT.txt"]
    release_names=["capture_r4.py","gatea_actuator_r4_qrm.py","actuate_r4.go","evaluate_r4.py","go.mod","requirements.txt","README.md","GATEA_ACTUATOR_R4_LOCK.json","r4_actuator"]
    orch=pathlib.Path(__file__)
    c={
      "protocol":"ERCP-GATEA-ACTUATOR-R4-TRIAL2-PRESOURCE-COMMITMENT-v1",
      "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "workflow_trigger_sha":os.environ.get("GITHUB_SHA"),
      "github_run_id":os.environ.get("GITHUB_RUN_ID"),
      "github_run_attempt":os.environ.get("GITHUB_RUN_ATTEMPT"),
      "target_round":TARGET_ROUND,
      "target_utc":"2026-09-21T13:00:03Z",
      "assignment_round":ASSIGNMENT_ROUND,
      "assignment_utc":"2026-09-21T13:10:03Z",
      "lock_sha256":LOCK_SHA256,
      "orchestration_sha256":h(orch),
      "statement":"Receiver, frozen analysis, target/assignment IDs, and actuator executable existed before either future drand source. No future source is fetched before the wait ends at/after assignment UTC.",
      "file_sha256":{n:h(pre/n) for n in names},
      "release_sha256":{n:h(release/n) for n in release_names},
      "actuator_binary_sha256":h(release/"r4_actuator"),
      "go_sum_sha256":h(build/"go.sum"),
      "substrate_sha256":meta["substrate_sha256"],
      "receiver_sha256":meta["receiver_sha256"],
      "latencies_sha256":meta["latencies_sha256"],
      "scientific_validity":"Only GITHUB_RUN_ATTEMPT=1 is confirmatory; any failed/cancelled attempt is INVALID/INCONCLUSIVE and is never rerun as confirmatory."
    }
    out.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
    print(json.dumps(c,indent=2,sort_keys=True))
    print("R4_TRIAL2_PRESOURCE_COMMITMENT=PASS")

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    v=sp.add_parser("verify-release");v.add_argument("--release-dir",required=True)
    m=sp.add_parser("make-commitment");m.add_argument("--release-dir",required=True);m.add_argument("--pre-dir",required=True);m.add_argument("--build-dir",required=True);m.add_argument("--out",required=True)
    a=ap.parse_args()
    if a.cmd=="verify-release":
        verify_release(pathlib.Path(a.release_dir))
    else:
        make_commitment(pathlib.Path(a.release_dir),pathlib.Path(a.pre_dir),pathlib.Path(a.build_dir),pathlib.Path(a.out))
if __name__=="__main__":
    main()
