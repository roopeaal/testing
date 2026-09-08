package main

import (
    "crypto/sha256"
    "encoding/binary"
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
    RoundsOne = 1024
    RoundsZero = 16
    PinnedRound uint64 = 32032013
    PinnedUnix int64 = 1788899403
    MaxLagSeconds int64 = 21600
)

type Source struct {
    Round uint64 `json:"round"`
    Randomness string `json:"randomness"`
    Signature string `json:"signature"`
    ChainHash string `json:"chain_hash"`
    SchemeID string `json:"scheme_id"`
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
    MessageBitOffset int `json:"message_bit_offset"`
    Message28 uint32 `json:"message28"`
    CodewordSHA256 string `json:"codeword_sha256"`
    Ones int `json:"ones"`
    Zeros int `json:"zeros"`
    RoundsOne int `json:"rounds_one"`
    RoundsZero int `json:"rounds_zero"`
    TotalHashRounds uint64 `json:"total_hash_rounds"`
    StartedUTC string `json:"started_utc"`
    EndedUTC string `json:"ended_utc"`
    ElapsedSeconds float64 `json:"elapsed_seconds"`
    FinalStateHex string `json:"final_state_hex"`
    Checkpoints []Checkpoint `json:"checkpoints"`
    GOMAXPROCS int `json:"gomaxprocs"`
}

func gfMul(a, b uint16) uint16 {
    a &= FieldMask
    b &= FieldMask
    var o uint16
    for b != 0 {
        if b&1 != 0 { o ^= a }
        b >>= 1
        a <<= 1
        if a&FieldSize != 0 { a ^= GFModulus }
    }
    return o & FieldMask
}

func gfSquare(a uint16) uint16 { return gfMul(a,a) }

func gfTrace(a uint16) uint8 {
    x := a & FieldMask
    t := x
    for i:=1; i<FieldBits; i++ { x = gfSquare(x); t ^= x }
    if t == 0 { return 0 }
    if t == 1 { return 1 }
    panic(fmt.Sprintf("GF trace outside GF(2): %d", t))
}

func splitMessage(msg uint32) (q uint16, l uint32, c uint8) {
    if msg >= 1<<28 { panic("message out of range") }
    q = uint16(msg >> 19)
    s := msg & ((1<<19)-1)
    l = s >> 1
    c = uint8(s & 1)
    return
}

func codeBit(msg uint32, idx uint32) uint8 {
    q,l,c := splitMessage(msg)
    x := uint16(idx & FieldMask)
    y := uint16(idx >> FieldBits)
    xy := gfMul(x,y)
    qp := gfTrace(gfMul(q,xy))
    lp := uint8(bits.OnesCount32(idx & l) & 1)
    return qp ^ lp ^ c
}

func encodePacked(msg uint32) ([]byte,int) {
    out := make([]byte,N/8)
    ones := 0
    for i:=0; i<N; i++ {
        b := codeBit(msg,uint32(i))
        if b != 0 { out[i>>3] |= 1 << uint(7-(i&7)); ones++ }
    }
    return out,ones
}

func extractBlock28(randomnessHex string, bitOffset int) uint32 {
    raw,err := hex.DecodeString(randomnessHex)
    if err != nil || len(raw)!=32 { panic("randomness must be 32-byte hex") }
    if bitOffset < 0 || bitOffset+28 > 256 { panic("bad bit offset") }
    var v uint32
    for k:=0; k<28; k++ {
        pos := bitOffset+k
        bit := (raw[pos/8] >> uint(7-(pos%8))) & 1
        v = (v<<1) | uint32(bit)
    }
    return v
}

func runActuator(sourcePath, blsPath, outPath string, dryRun bool) {
    var s Source
    raw,err:=os.ReadFile(sourcePath); if err!=nil { panic(err) }
    if err=json.Unmarshal(raw,&s); err!=nil { panic(err) }
    var ev BLSEvidence
    raw,err=os.ReadFile(blsPath); if err!=nil { panic(err) }
    if err=json.Unmarshal(raw,&ev); err!=nil { panic(err) }
    if s.Round!=PinnedRound || ev.Round!=PinnedRound || !ev.BLSVerified || ev.Randomness!=s.Randomness || ev.Signature!=s.Signature { panic("source/BLS gate failed") }
    now:=time.Now().UTC()
    if !dryRun {
        if now.Unix() < PinnedUnix { panic("actuation before pinned future source forbidden") }
        if now.Unix() > PinnedUnix+MaxLagSeconds { panic("actuation outside frozen +6h lag window") }
    }
    msg:=extractBlock28(s.Randomness,28)
    packed,ones:=encodePacked(msg)
    h:=sha256.Sum256(packed)
    runtime.GOMAXPROCS(1)

    seed:=sha256.Sum256(append([]byte("ERCP-GATEA-ACTUATOR-R3-v1|"),packed...))
    state:=seed
    checkpoints:=make([]Checkpoint,0,N/4096)
    started:=time.Now().UTC()
    var total uint64
    for i:=0; i<N; i++ {
        b:=codeBit(msg,uint32(i))
        state[0] ^= byte(i)
        state[1] ^= byte(i>>8)
        state[2] ^= byte(i>>16)
        state[3] ^= b
        rounds:=RoundsZero
        if b!=0 { rounds=RoundsOne }
        for r:=0; r<rounds; r++ { state=sha256.Sum256(state[:]) }
        total += uint64(rounds)
        if (i+1)%4096==0 {
            checkpoints=append(checkpoints,Checkpoint{Index:i,ElapsedNS:time.Since(started).Nanoseconds(),StateHex:hex.EncodeToString(state[:])})
        }
    }
    ended:=time.Now().UTC()
    log:=ActuatorLog{
        Protocol:"ERCP-GATEA-ACTUATOR-R3-GITHUB-CPU-v1",SourceRound:s.Round,Randomness:s.Randomness,
        MessageBitOffset:28,Message28:msg,CodewordSHA256:hex.EncodeToString(h[:]),Ones:ones,Zeros:N-ones,
        RoundsOne:RoundsOne,RoundsZero:RoundsZero,TotalHashRounds:total,StartedUTC:started.Format(time.RFC3339Nano),
        EndedUTC:ended.Format(time.RFC3339Nano),ElapsedSeconds:ended.Sub(started).Seconds(),FinalStateHex:hex.EncodeToString(state[:]),
        Checkpoints:checkpoints,GOMAXPROCS:1,
    }
    out,_:=json.MarshalIndent(log,"","  "); out=append(out,'\n')
    if err:=os.WriteFile(outPath,out,0644); err!=nil { panic(err) }
    fmt.Printf("ACTUATOR_EXECUTED=true MESSAGE=%d CODEWORD_SHA256=%s ONES=%d ZEROS=%d TOTAL_HASH_ROUNDS=%d ELAPSED=%.6f\n",msg,log.CodewordSHA256,log.Ones,log.Zeros,log.TotalHashRounds,log.ElapsedSeconds)
}

func selftest() {
    tests:=[]struct{hex string; off int; want uint32}{
        {"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",0,0x0123456},
        {"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",28,0x789abcd},
    }
    for _,t:=range tests { got:=extractBlock28(t.hex,t.off); if got!=t.want { panic(fmt.Sprintf("extract selftest off=%d got=%x want=%x",t.off,got,t.want)) } }
    msgs:=[]uint32{0,1,0x0A5A5A5,0x0FFFFFFF}
    for _,m:=range msgs { packed,ones:=encodePacked(m); h:=sha256.Sum256(packed); fmt.Printf("SELFTEST message=%d ones=%d sha256=%s\n",m,ones,hex.EncodeToString(h[:])) }
    if gfTrace(0)!=0 || gfMul(1,511)!=511 { panic("GF sanity failed") }
    var buf [4]byte
    binary.BigEndian.PutUint32(buf[:],msgs[2])
    fmt.Printf("SELFTEST_MESSAGE_HEX=%s\n",hex.EncodeToString(buf[:]))
}

func main() {
    mode:=flag.String("mode","selftest","selftest|actuate")
    source:=flag.String("source","","source json")
    bls:=flag.String("bls","","BLS evidence json")
    out:=flag.String("out","ACTUATOR_R3_LOG.json","actuator log")
    dry:=flag.Bool("dry-run",false,"allow synthetic pre-source validation")
    flag.Parse()
    switch *mode {
    case "selftest": selftest()
    case "actuate": if *source=="" || *bls=="" { panic("source and bls required") }; runActuator(*source,*bls,*out,*dry)
    default: panic("unknown mode")
    }
}
