package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"runtime"
	"syscall"
	"time"

	drandcrypto "github.com/drand/drand/v2/crypto"
)

const (
	N                       = 1 << 18
	CellBytes               = 64
	FieldBits               = 9
	FieldSize               = 1 << FieldBits
	FieldMask               = FieldSize - 1
	GFModulus               = (1 << 9) | (1 << 1) | 1
	TargetRound      uint64 = 32094413
	AssignmentRound  uint64 = 32094613
	TargetUnix       int64  = 1789086603
	AssignmentUnix   int64  = 1789087203
	MaxStartLag      int64  = 600
	RoundsActiveOne         = 1024
	RoundsActiveZero        = 16
	RoundsSham              = 520
	Chain                   = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
	PublicKey               = "83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a"
	SchemeID                = "bls-unchained-g1-rfc9380"
)

var relays = []string{"https://api.drand.sh", "https://api2.drand.sh", "https://api3.drand.sh", "https://drand.cloudflare.com"}

type RelayRow struct {
	URL        string `json:"url"`
	Round      uint64 `json:"round"`
	Signature  string `json:"signature"`
	Randomness string `json:"randomness"`
}
type APIBeacon struct {
	Round      uint64 `json:"round"`
	Signature  string `json:"signature"`
	Randomness string `json:"randomness"`
}
type SourceBundle struct {
	Protocol                string     `json:"protocol"`
	FetchedUTC              string     `json:"fetched_utc"`
	ChainHash               string     `json:"chain_hash"`
	PublicKey               string     `json:"public_key"`
	SchemeID                string     `json:"scheme_id"`
	Round                   uint64     `json:"round"`
	RoundUnix               int64      `json:"round_unix"`
	Signature               string     `json:"signature"`
	Randomness              string     `json:"randomness"`
	Relays                  []RelayRow `json:"relays"`
	FourRelayExactAgreement bool       `json:"four_relay_exact_agreement"`
	SignatureToRandomness   bool       `json:"signature_to_randomness_sha256_verified"`
	BLSVerified             bool       `json:"bls_verified"`
	DrandVersion            string     `json:"drand_version"`
}
type Beacon struct {
	round uint64
	sig   []byte
}

func (b *Beacon) GetPreviousSignature() []byte { return nil }
func (b *Beacon) GetRound() uint64             { return b.round }
func (b *Beacon) GetSignature() []byte         { return b.sig }

type HostIdentity struct {
	Hostname         string `json:"hostname"`
	BootID           string `json:"boot_id"`
	CPUInfoSHA256    string `json:"cpuinfo_sha256"`
	RunnerName       string `json:"runner_name"`
	GitHubRunID      string `json:"github_run_id"`
	GitHubRunAttempt string `json:"github_run_attempt"`
	GitHubSHA        string `json:"github_sha"`
}
type PreMeta struct {
	Protocol        string       `json:"protocol"`
	SubstrateSHA256 string       `json:"substrate_sha256"`
	HostIdentity    HostIdentity `json:"host_identity"`
}
type Checkpoint struct {
	Index     int    `json:"index"`
	ElapsedNS int64  `json:"elapsed_ns"`
	StateHex  string `json:"state_hex"`
}
type ActuatorLog struct {
	Protocol                 string       `json:"protocol"`
	TargetRound              uint64       `json:"target_round"`
	AssignmentRound          uint64       `json:"assignment_round"`
	TargetRandomness         string       `json:"target_randomness"`
	AssignmentRandomness     string       `json:"assignment_randomness"`
	TargetMessage28          uint32       `json:"target_message28"`
	AssignmentMessage28      uint32       `json:"assignment_message28"`
	AssignmentEvalMessage28  uint32       `json:"assignment_eval_message28"`
	TargetCodewordSHA256     string       `json:"target_codeword_sha256"`
	AssignmentCodewordSHA256 string       `json:"assignment_codeword_sha256"`
	ActiveCount              int          `json:"active_count"`
	ShamCount                int          `json:"sham_count"`
	ActiveTargetOneCount     int          `json:"active_target_one_count"`
	ActiveTargetZeroCount    int          `json:"active_target_zero_count"`
	RoundsActiveOne          int          `json:"rounds_active_one"`
	RoundsActiveZero         int          `json:"rounds_active_zero"`
	RoundsSham               int          `json:"rounds_sham"`
	TotalHashRounds          uint64       `json:"total_hash_rounds"`
	StartedUTC               string       `json:"started_utc"`
	EndedUTC                 string       `json:"ended_utc"`
	ElapsedSeconds           float64      `json:"elapsed_seconds"`
	SubstratePreSHA256       string       `json:"substrate_pre_sha256"`
	SubstratePostSHA256      string       `json:"substrate_post_sha256"`
	HostIdentityPre          HostIdentity `json:"host_identity_pre"`
	HostIdentityPost         HostIdentity `json:"host_identity_post"`
	SameBootID               bool         `json:"same_boot_id"`
	SameHostname             bool         `json:"same_hostname"`
	Checkpoints              []Checkpoint `json:"checkpoints"`
	GOMAXPROCS               int          `json:"gomaxprocs"`
}

func mustHex(s string) []byte {
	b, e := hex.DecodeString(s)
	if e != nil {
		panic(e)
	}
	return b
}
func hashBytes(b []byte) string { h := sha256.Sum256(b); return hex.EncodeToString(h[:]) }
func hashFile(path string) string {
	f, e := os.Open(path)
	if e != nil {
		panic(e)
	}
	defer f.Close()
	h := sha256.New()
	if _, e = io.Copy(h, f); e != nil {
		panic(e)
	}
	return hex.EncodeToString(h.Sum(nil))
}
func readTrim(path string) string {
	b, e := os.ReadFile(path)
	if e != nil {
		return ""
	}
	return string(bytes.TrimSpace(b))
}
func hostIdentity() HostIdentity {
	hn, _ := os.Hostname()
	cpu, _ := os.ReadFile("/proc/cpuinfo")
	return HostIdentity{hn, readTrim("/proc/sys/kernel/random/boot_id"), hashBytes(cpu), os.Getenv("RUNNER_NAME"), os.Getenv("GITHUB_RUN_ID"), os.Getenv("GITHUB_RUN_ATTEMPT"), os.Getenv("GITHUB_SHA")}
}

func gfMul(a, b uint16) uint16 {
	a &= FieldMask
	b &= FieldMask
	var o uint16
	for b != 0 {
		if b&1 != 0 {
			o ^= a
		}
		b >>= 1
		a <<= 1
		if a&FieldSize != 0 {
			a ^= GFModulus
		}
	}
	return o & FieldMask
}
func gfSquare(a uint16) uint16 { return gfMul(a, a) }
func gfTrace(a uint16) uint8 {
	x := a & FieldMask
	t := x
	for i := 1; i < FieldBits; i++ {
		x = gfSquare(x)
		t ^= x
	}
	if t == 0 {
		return 0
	}
	if t == 1 {
		return 1
	}
	panic("trace")
}
func splitMessage(msg uint32) (q uint16, l uint32, c uint8) {
	if msg >= 1<<28 {
		panic("msg")
	}
	q = uint16(msg >> 19)
	s := msg & ((1 << 19) - 1)
	l = s >> 1
	c = uint8(s & 1)
	return
}
func popParity(x uint32) uint8 {
	x ^= x >> 16
	x ^= x >> 8
	x ^= x >> 4
	x &= 0xf
	return uint8((0x6996 >> x) & 1)
}
func codeBit(msg uint32, idx uint32) uint8 {
	q, l, c := splitMessage(msg)
	x := uint16(idx & FieldMask)
	y := uint16(idx >> FieldBits)
	qp := gfTrace(gfMul(q, gfMul(x, y)))
	return qp ^ popParity(idx&l) ^ c
}
func encodePacked(msg uint32) ([]byte, int) {
	out := make([]byte, N/8)
	ones := 0
	for i := 0; i < N; i++ {
		b := codeBit(msg, uint32(i))
		if b != 0 {
			out[i>>3] |= 1 << uint(7-(i&7))
			ones++
		}
	}
	return out, ones
}
func extract28(randomness string) uint32 {
	b := mustHex(randomness)
	if len(b) != 32 {
		panic("randomness length")
	}
	return uint32(b[0])<<20 | uint32(b[1])<<12 | uint32(b[2])<<4 | uint32(b[3]>>4)
}

func fetchOne(base string, round uint64) (RelayRow, error) {
	u := fmt.Sprintf("%s/%s/public/%d", base, Chain, round)
	var last error
	for a := 0; a < 5; a++ {
		req, _ := http.NewRequest("GET", u, nil)
		req.Header.Set("User-Agent", "ERCP-GateA-Actuator-R4/1.0")
		cli := &http.Client{Timeout: 30 * time.Second}
		resp, e := cli.Do(req)
		if e == nil {
			raw, e2 := io.ReadAll(resp.Body)
			resp.Body.Close()
			if e2 == nil && resp.StatusCode == 200 {
				var x APIBeacon
				if e3 := json.Unmarshal(raw, &x); e3 == nil {
					return RelayRow{base, x.Round, x.Signature, x.Randomness}, nil
				} else {
					last = e3
				}
			} else {
				last = e2
			}
		} else {
			last = e
		}
		time.Sleep(time.Duration(a+1) * 2 * time.Second)
	}
	return RelayRow{}, last
}
func fetchVerified(round uint64, unix int64) SourceBundle {
	rows := make([]RelayRow, 0, 4)
	for _, base := range relays {
		r, e := fetchOne(base, round)
		if e != nil {
			panic(e)
		}
		if r.Round != round {
			panic("round mismatch")
		}
		sig := mustHex(r.Signature)
		if hashBytes(sig) != r.Randomness {
			panic("signature/randomness")
		}
		rows = append(rows, r)
	}
	for i := 1; i < len(rows); i++ {
		if rows[i].Round != rows[0].Round || rows[i].Signature != rows[0].Signature || rows[i].Randomness != rows[0].Randomness {
			panic("relay disagreement")
		}
	}
	scheme := drandcrypto.NewPedersenBLSUnchainedG1()
	if SchemeID != drandcrypto.SigsOnG1ID || scheme.Name != drandcrypto.SigsOnG1ID {
		panic("scheme")
	}
	pub := scheme.KeyGroup.Point()
	if e := pub.UnmarshalBinary(mustHex(PublicKey)); e != nil {
		panic(e)
	}
	sig := mustHex(rows[0].Signature)
	if e := scheme.VerifyBeacon(&Beacon{round: round, sig: sig}, pub); e != nil {
		panic(e)
	}
	return SourceBundle{"ERCP-GATEA-ACTUATOR-R4-drand-source-v1", time.Now().UTC().Format(time.RFC3339), Chain, PublicKey, SchemeID, round, unix, rows[0].Signature, rows[0].Randomness, rows, true, true, true, "v2.1.7"}
}
func writeJSON(path string, v any) {
	b, e := json.MarshalIndent(v, "", "  ")
	if e != nil {
		panic(e)
	}
	b = append(b, '\n')
	if e = os.WriteFile(path, b, 0644); e != nil {
		panic(e)
	}
}

func selftest() {
	if extract28("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef") != 0x0123456 {
		panic("extract")
	}
	msgs := []uint32{0, 1, 0x0A5A5A5, 0x0FFFFFFF}
	for _, m := range msgs {
		p, o := encodePacked(m)
		fmt.Printf("SELFTEST message=%d ones=%d sha256=%s\n", m, o, hashBytes(p))
	}
	fmt.Println("R4_ACTUATOR_SELFTEST=PASS")
}
func run(preDir, substrate, outDir string) {
	os.MkdirAll(outDir, 0755)
	raw, e := os.ReadFile(preDir + "/R4_RECEIVER_META.json")
	if e != nil {
		panic(e)
	}
	var pre PreMeta
	if e = json.Unmarshal(raw, &pre); e != nil {
		panic(e)
	}
	if pre.Protocol != "ERCP-GATEA-ACTUATOR-R4-SAME-RUNNER-MMAP-v1" {
		panic("pre protocol")
	}
	hiPre := pre.HostIdentity
	hiNow := hostIdentity()
	if hiPre.BootID == "" || hiNow.BootID != hiPre.BootID || hiNow.Hostname != hiPre.Hostname || hiNow.GitHubRunID != hiPre.GitHubRunID || hiNow.GitHubRunAttempt != hiPre.GitHubRunAttempt {
		panic("same-runner identity gate")
	}
	now := time.Now().Unix()
	if now < AssignmentUnix {
		panic("actuation before assignment source")
	}
	if now > AssignmentUnix+MaxStartLag {
		panic("actuation start too late")
	}
	if hashFile(substrate) != pre.SubstrateSHA256 {
		panic("substrate changed before actuation")
	}
	target := fetchVerified(TargetRound, TargetUnix)
	assign := fetchVerified(AssignmentRound, AssignmentUnix)
	writeJSON(outDir+"/R4_TARGET_SOURCE.json", target)
	writeJSON(outDir+"/R4_ASSIGNMENT_SOURCE.json", assign)
	targetMsg := extract28(target.Randomness)
	assignMsg := extract28(assign.Randomness)
	tp, _ := encodePacked(targetMsg)
	ap, _ := encodePacked(assignMsg)
	th := hashBytes(tp)
	ah := hashBytes(ap)
	f, e := os.OpenFile(substrate, os.O_RDWR, 0600)
	if e != nil {
		panic(e)
	}
	defer f.Close()
	data, e := syscall.Mmap(int(f.Fd()), 0, N*CellBytes, syscall.PROT_READ|syscall.PROT_WRITE, syscall.MAP_SHARED)
	if e != nil {
		panic(e)
	}
	runtime.GOMAXPROCS(1)
	active, sham, a1, a0 := 0, 0, 0, 0
	var total uint64
	cps := make([]Checkpoint, 0, N/4096)
	started := time.Now().UTC()
	if started.Unix() < AssignmentUnix || started.Unix() > AssignmentUnix+MaxStartLag {
		panic("actuator timing gate")
	}
	for i := 0; i < N; i++ {
		x := codeBit(targetMsg, uint32(i))
		a := codeBit(assignMsg, uint32(i))
		cell := data[i*CellBytes : (i+1)*CellBytes]
		var seed []byte
		rounds := RoundsSham
		if a == 1 {
			active++
			seed = make([]byte, 0, 80)
			seed = append(seed, []byte("R4ACTIVE|")...)
			seed = append(seed, byte(x))
			seed = append(seed, cell...)
			if x == 1 {
				a1++
				rounds = RoundsActiveOne
			} else {
				a0++
				rounds = RoundsActiveZero
			}
		} else {
			sham++
			seed = make([]byte, 0, 80)
			seed = append(seed, []byte("R4SHAM|\x00")...)
			seed = append(seed, cell...)
		}
		state := sha256.Sum256(seed)
		for r := 0; r < rounds; r++ {
			state = sha256.Sum256(state[:])
		}
		copy(cell[:32], state[:])
		total += uint64(rounds)
		if (i+1)%4096 == 0 {
			cps = append(cps, Checkpoint{i, time.Since(started).Nanoseconds(), hex.EncodeToString(state[:])})
		}
	}
	if e := syscall.Munmap(data); e != nil {
		panic(e)
	}
	if e := f.Sync(); e != nil {
		panic(e)
	}
	ended := time.Now().UTC()
	post := hostIdentity()
	log := ActuatorLog{"ERCP-GATEA-ACTUATOR-R4-GITHUB-SAME-RUNNER-RANDOMIZED-v1", TargetRound, AssignmentRound, target.Randomness, assign.Randomness, targetMsg, assignMsg, assignMsg ^ 1, th, ah, active, sham, a1, a0, RoundsActiveOne, RoundsActiveZero, RoundsSham, total, started.Format(time.RFC3339Nano), ended.Format(time.RFC3339Nano), ended.Sub(started).Seconds(), pre.SubstrateSHA256, hashFile(substrate), hiPre, post, post.BootID == hiPre.BootID, post.Hostname == hiPre.Hostname, cps, 1}
	writeJSON(outDir+"/R4_ACTUATOR_LOG.json", log)
	fmt.Printf("R4_ACTUATOR_EXECUTED=true target=%d assign=%d active=%d sham=%d rounds=%d elapsed=%.3f\n", targetMsg, assignMsg, active, sham, total, log.ElapsedSeconds)
}
func main() {
	mode := flag.String("mode", "selftest", "selftest|run")
	pre := flag.String("pre-dir", "pre", "")
	sub := flag.String("substrate", "substrate.bin", "")
	out := flag.String("out-dir", "post", "")
	flag.Parse()
	if *mode == "selftest" {
		selftest()
		return
	}
	if *mode != "run" {
		panic("mode")
	}
	run(*pre, *sub, *out)
}
