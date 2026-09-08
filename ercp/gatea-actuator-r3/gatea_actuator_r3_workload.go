package main

import (
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "flag"
    "fmt"
    "math/bits"
    "os"
    "runtime"
    "time"
)

const (
    N = 1 << 18
    FieldBits = 9
    FieldSize = 1 << FieldBits
    FieldMask = FieldSize - 1
    GFModulus = (1 << 9) | (1 << 1) | 1
    RoundsActiveOne = 1024
    RoundsActiveZero = 16
    RoundsSham = 520
    PinnedRound uint64 = 32032013
    PinnedUnix int64 = 1788899403
    MaxLagSeconds int64 = 21600
    TargetBitOffset = 28
    AssignmentBitOffset = 56
)

type Source struct {
    Round uint64 `json:"round"`
    Randomness string `json:"randomness"`
    Signature string `json:"signature"`
}
type BLSEvidence struct {
    BLSVerified bool `json:"bls_verified"`
    Round uint64 `json:"round"`
    Randomness string `json:"randomness"`
    Signature string `json:"signature"`
}
type Checkpoint struct {
    Index int `json:"index"`
    ElapsedNS int64 `json:"elapsed_ns"`
    StateHex string `json:"state_hex"`
}
type ActuatorLog struct {
    Protocol string `json:"protocol"`
    SourceRound uint64 `json:"source_round"`
    Randomness string `json:"randomness"`
    TargetBitOffset int `json:"target_bit_offset"`
    AssignmentBitOffset int `json:"assignment_bit_offset"`
    TargetMessage28 uint32 `json:"target_message28"`
    AssignmentMessage28 uint32 `json:"assignment_message28"`
    AssignmentEvalMessage28 uint32 `json:"assignment_eval_message28"`
    TargetCodewordSHA256 string `json:"target_codeword_sha256"`
    AssignmentCodewordSHA256 string `json:"assignment_codeword_sha256"`
    ActiveCount int `json:"active_count"`
    ShamCount int `json:"sham_count"`
    ActiveTargetOneCount int `json:"active_target_one_count"`
    ActiveTargetZeroCount int `json:"active_target_zero_count"`
    RoundsActiveOne int `json:"rounds_active_one"`
    RoundsActiveZero int `json:"rounds_active_zero"`
    RoundsSham int `json:"rounds_sham"`
    TotalHashRounds uint64 `json:"total_hash_rounds"`
    StartedUTC string `json:"started_utc"`
    EndedUTC string `json:"ended_utc"`
    ElapsedSeconds float64 `json:"elapsed_seconds"`
    FinalStateHex string `json:"final_state_hex"`
    Checkpoints []Checkpoint `json:"checkpoints"`
    GOMAXPROCS int `json:"gomaxprocs"`
}

func gfMul(a,b uint16) uint16 {
    a&=FieldMask;b&=FieldMask;var o uint16
    for b!=0 {
        if b&1!=0{o^=a}
        b>>=1;a<<=1
        if a&FieldSize!=0{a^=GFModulus}
    }
    return o&FieldMask
}
func gfSquare(a uint16)uint16{return gfMul(a,a)}
func gfTrace(a uint16)uint8{
    x:=a&FieldMask;t:=x
    for i:=1;i<FieldBits;i++{x=gfSquare(x);t^=x}
    if t==0{return 0};if t==1{return 1};panic("trace")
}
func splitMessage(msg uint32)(q uint16,l uint32,c uint8){
    if msg>=1<<28{panic("msg")}
    q=uint16(msg>>19);s:=msg&((1<<19)-1);l=s>>1;c=uint8(s&1);return
}
func codeBit(msg uint32,idx uint32)uint8{
    q,l,c:=splitMessage(msg)
    x:=uint16(idx&FieldMask);y:=uint16(idx>>FieldBits);xy:=gfMul(x,y)
    qp:=gfTrace(gfMul(q,xy));lp:=uint8(bits.OnesCount32(idx&l)&1)
    return qp^lp^c
}
func encodePacked(msg uint32)([]byte,int){
    out:=make([]byte,N/8);ones:=0
    for i:=0;i<N;i++{b:=codeBit(msg,uint32(i));if b!=0{out[i>>3]|=1<<uint(7-(i&7));ones++}}
    return out,ones
}
func extractBlock28(randomnessHex string,off int)uint32{
    raw,err:=hex.DecodeString(randomnessHex);if err!=nil||len(raw)!=32{panic("randomness")}
    if off<0||off+28>256{panic("offset")}
    var v uint32
    for k:=0;k<28;k++{pos:=off+k;v=(v<<1)|uint32((raw[pos/8]>>uint(7-(pos%8)))&1)}
    return v
}
func runActuator(sourcePath,blsPath,outPath string,dry bool){
    var s Source;raw,err:=os.ReadFile(sourcePath);if err!=nil{panic(err)};if err=json.Unmarshal(raw,&s);err!=nil{panic(err)}
    var ev BLSEvidence;raw,err=os.ReadFile(blsPath);if err!=nil{panic(err)};if err=json.Unmarshal(raw,&ev);err!=nil{panic(err)}
    if s.Round!=PinnedRound||ev.Round!=PinnedRound||!ev.BLSVerified||ev.Randomness!=s.Randomness||ev.Signature!=s.Signature{panic("source/BLS gate")}
    now:=time.Now().UTC()
    if !dry {
        if now.Unix()<PinnedUnix{panic("pre-source actuation")}
        if now.Unix()>PinnedUnix+MaxLagSeconds{panic("late actuation")}
    }
    targetMsg:=extractBlock28(s.Randomness,TargetBitOffset)
    assignMsg:=extractBlock28(s.Randomness,AssignmentBitOffset)
    targetPacked,_:=encodePacked(targetMsg);assignPacked,_:=encodePacked(assignMsg)
    targetH:=sha256.Sum256(targetPacked);assignH:=sha256.Sum256(assignPacked)
    seedBytes:=append([]byte("ERCP-GATEA-ACTUATOR-R3-RANDOMIZED-v2|"),targetPacked...)
    seedBytes=append(seedBytes,assignPacked...)
    state:=sha256.Sum256(seedBytes)
    runtime.GOMAXPROCS(1)
    active,sham,activeOne,activeZero:=0,0,0,0
    var total uint64
    cps:=make([]Checkpoint,0,N/4096)
    started:=time.Now().UTC()
    for i:=0;i<N;i++{
        x:=codeBit(targetMsg,uint32(i))
        a:=codeBit(assignMsg,uint32(i))
        state[0]^=byte(i);state[1]^=byte(i>>8);state[2]^=byte(i>>16);state[3]^=x;state[4]^=a
        rounds:=RoundsSham
        if a==1 {
            active++
            if x==1{activeOne++;rounds=RoundsActiveOne}else{activeZero++;rounds=RoundsActiveZero}
        } else { sham++ }
        for r:=0;r<rounds;r++{state=sha256.Sum256(state[:])}
        total+=uint64(rounds)
        if (i+1)%4096==0{cps=append(cps,Checkpoint{Index:i,ElapsedNS:time.Since(started).Nanoseconds(),StateHex:hex.EncodeToString(state[:])})}
    }
    ended:=time.Now().UTC()
    log:=ActuatorLog{
        Protocol:"ERCP-GATEA-ACTUATOR-R3-GITHUB-CPU-RANDOMIZED-v2",
        SourceRound:s.Round,Randomness:s.Randomness,
        TargetBitOffset:TargetBitOffset,AssignmentBitOffset:AssignmentBitOffset,
        TargetMessage28:targetMsg,AssignmentMessage28:assignMsg,AssignmentEvalMessage28:assignMsg^1,
        TargetCodewordSHA256:hex.EncodeToString(targetH[:]),AssignmentCodewordSHA256:hex.EncodeToString(assignH[:]),
        ActiveCount:active,ShamCount:sham,ActiveTargetOneCount:activeOne,ActiveTargetZeroCount:activeZero,
        RoundsActiveOne:RoundsActiveOne,RoundsActiveZero:RoundsActiveZero,RoundsSham:RoundsSham,
        TotalHashRounds:total,StartedUTC:started.Format(time.RFC3339Nano),EndedUTC:ended.Format(time.RFC3339Nano),
        ElapsedSeconds:ended.Sub(started).Seconds(),FinalStateHex:hex.EncodeToString(state[:]),Checkpoints:cps,GOMAXPROCS:1,
    }
    out,_:=json.MarshalIndent(log,"","  ");out=append(out,'\n');if err:=os.WriteFile(outPath,out,0644);err!=nil{panic(err)}
    fmt.Printf("ACTUATOR_EXECUTED=true TARGET=%d ASSIGN=%d ACTIVE=%d SHAM=%d TOTAL_HASH_ROUNDS=%d ELAPSED=%.6f\n",
        targetMsg,assignMsg,active,sham,total,log.ElapsedSeconds)
}
func selftest(){
    h:="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    wants:=map[int]uint32{0:0x0123456,28:0x789abcd,56:0xef01234}
    for off,w:=range wants{g:=extractBlock28(h,off);if g!=w{panic(fmt.Sprintf("extract %d %x %x",off,g,w))}}
    msgs:=[]uint32{0,1,0x0A5A5A5,0x0FFFFFFF}
    for _,m:=range msgs{p,o:=encodePacked(m);hh:=sha256.Sum256(p);fmt.Printf("SELFTEST message=%d ones=%d sha256=%s\n",m,o,hex.EncodeToString(hh[:]))}
    fmt.Println("SELFTEST_RANDOMIZED_ACTUATOR=PASS")
}
func main(){
    mode:=flag.String("mode","selftest","selftest|actuate");source:=flag.String("source","","");bls:=flag.String("bls","","");out:=flag.String("out","ACTUATOR_R3_LOG.json","");dry:=flag.Bool("dry-run",false,"");flag.Parse()
    if *mode=="selftest"{selftest();return}
    if *mode!="actuate"||*source==""||*bls==""{panic("usage")}
    runActuator(*source,*bls,*out,*dry)
}
