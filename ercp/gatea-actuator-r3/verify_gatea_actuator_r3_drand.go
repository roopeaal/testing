package main

import (
    "bytes"
    "encoding/hex"
    "encoding/json"
    "fmt"
    "os"

    drandcrypto "github.com/drand/drand/v2/crypto"
)

type Source struct {
    ChainHash  string `json:"chain_hash"`
    PublicKey  string `json:"public_key"`
    SchemeID   string `json:"scheme_id"`
    Round      uint64 `json:"round"`
    Signature  string `json:"signature"`
    Randomness string `json:"randomness"`
}
type Beacon struct { round uint64; sig []byte }
func (b *Beacon) GetPreviousSignature() []byte { return nil }
func (b *Beacon) GetRound() uint64 { return b.round }
func (b *Beacon) GetSignature() []byte { return b.sig }

type Evidence struct {
    BLSVerified bool `json:"bls_verified"`
    Round uint64 `json:"round"`
    Signature string `json:"signature"`
    Randomness string `json:"randomness"`
    PublicKey string `json:"public_key"`
    SchemeID string `json:"scheme_id"`
    DrandVersion string `json:"drand_version"`
}
func mustHex(s string) []byte { b,e:=hex.DecodeString(s); if e!=nil { panic(e) }; return b }

func main(){
    if len(os.Args)!=3 { fmt.Fprintln(os.Stderr,"usage: verify SOURCE.json EVIDENCE.json"); os.Exit(2) }
    raw,err:=os.ReadFile(os.Args[1]); if err!=nil { panic(err) }
    var s Source; if err=json.Unmarshal(raw,&s); err!=nil { panic(err) }
    scheme:=drandcrypto.NewPedersenBLSUnchainedG1()
    if s.SchemeID!=drandcrypto.SigsOnG1ID || scheme.Name!=drandcrypto.SigsOnG1ID { fmt.Fprintln(os.Stderr,"scheme mismatch"); os.Exit(3) }
    pub:=scheme.KeyGroup.Point(); if err:=pub.UnmarshalBinary(mustHex(s.PublicKey)); err!=nil { fmt.Fprintln(os.Stderr,"public key decode",err); os.Exit(4) }
    sig:=mustHex(s.Signature); got:=drandcrypto.RandomnessFromSignature(sig); want:=mustHex(s.Randomness)
    if !bytes.Equal(got,want) { fmt.Fprintln(os.Stderr,"randomness mismatch"); os.Exit(5) }
    if err:=scheme.VerifyBeacon(&Beacon{round:s.Round,sig:sig},pub); err!=nil { fmt.Fprintln(os.Stderr,"BLS verify failed",err); os.Exit(6) }
    ev:=Evidence{true,s.Round,s.Signature,s.Randomness,s.PublicKey,s.SchemeID,"v2.1.7"}
    out,_:=json.MarshalIndent(ev,"","  "); out=append(out,'\n')
    if err:=os.WriteFile(os.Args[2],out,0644); err!=nil { panic(err) }
    fmt.Printf("BLS_VERIFIED=true ROUND=%d SCHEME=%s RANDOMNESS=%s\n",s.Round,s.SchemeID,s.Randomness)
}
