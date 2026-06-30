import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { ContactShadows, Environment, Float, Line, OrbitControls } from '@react-three/drei'
import { useReducedMotion } from 'motion/react'
import { SectionHeader } from '../components/SectionHeader'
import type * as THREE from 'three'

function NetworkNode({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={position}>
      <sphereGeometry args={[0.075, 24, 24]} />
      <meshStandardMaterial color="#d69b63" emissive="#3a1f10" metalness={0.35} roughness={0.38} />
    </mesh>
  )
}

function NetworkObject() {
  const group = useRef<THREE.Group>(null)
  const reduceMotion = useReducedMotion()
  const nodes: [number, number, number][] = [
    [-1.45, -0.2, 0.2],
    [-0.72, 0.82, -0.18],
    [0, -0.72, 0.42],
    [0.78, 0.58, -0.34],
    [1.42, -0.1, 0.18],
  ]

  useFrame(({ clock, pointer }) => {
    if (!group.current || reduceMotion) {
      return
    }

    group.current.rotation.y = clock.getElapsedTime() * 0.18 + pointer.x * 0.14
    group.current.rotation.x = pointer.y * 0.08
  })

  return (
    <Float speed={1.25} rotationIntensity={0.22} floatIntensity={0.35}>
      <group ref={group}>
        <Line points={nodes} color="#d69b63" lineWidth={1.25} transparent opacity={0.72} />
        <Line
          points={[nodes[1], nodes[3], nodes[2], nodes[0], nodes[4]]}
          color="#cad6cf"
          lineWidth={0.8}
          transparent
          opacity={0.32}
        />
        {nodes.map((position) => (
          <NetworkNode key={position.join(':')} position={position} />
        ))}
        <mesh scale={[1.9, 1.9, 1.9]}>
          <icosahedronGeometry args={[1, 1]} />
          <meshStandardMaterial color="#cad6cf" wireframe transparent opacity={0.12} />
        </mesh>
      </group>
    </Float>
  )
}

export function Lab() {
  return (
    <section id="lab" className="signal-section relative min-h-[88svh] overflow-hidden bg-[#0b0c0b] px-5 py-24 sm:px-8 sm:py-32 lg:px-10">
      <div className="absolute left-0 top-1/2 h-px w-full bg-white/10">
        <div className="signal-line h-px w-full scale-x-0 bg-copper" />
      </div>
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[0.86fr_1.14fr] lg:items-center">
        <SectionHeader
          kicker="3D network study"
          title="A small connected object, built into the page."
          body="The 3D piece is intentionally restrained: a few nodes, signal paths, and motion that point back to IoT and networks instead of acting as decoration."
        />
        <div className="h-[360px] min-h-[320px] sm:h-[440px] lg:h-[620px]">
          <Canvas camera={{ position: [0, 0, 4.8], fov: 43 }} dpr={[1, 1.65]}>
            <color attach="background" args={['#0b0c0b']} />
            <ambientLight intensity={0.48} />
            <spotLight position={[4, 5, 4]} intensity={1.7} penumbra={0.45} />
            <pointLight position={[-3, -2, -2]} intensity={1.1} color="#d69b63" />
            <Environment preset="warehouse" />
            <NetworkObject />
            <ContactShadows position={[0, -1.68, 0]} scale={6} blur={2.2} opacity={0.26} />
            <OrbitControls enablePan={false} enableZoom={false} autoRotate autoRotateSpeed={0.25} />
          </Canvas>
        </div>
      </div>
    </section>
  )
}
