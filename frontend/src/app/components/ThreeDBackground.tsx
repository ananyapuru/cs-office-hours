// src/app/components/ThreeDBackground.tsx
'use client';
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';

export default function ThreeDBackground() {
  return (
    <Canvas
      className="absolute inset-0 z-[-1]"
      camera={{ position: [0, 0, 5], fov: 60 }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} />
      <Stars radius={100} depth={50} count={5000} factor={4} fade />
      <Suspense fallback={null}>
        <mesh rotation={[10, 10, 0]}>
          <icoSphereBufferGeometry args={[1.5, 4]} />
          <meshStandardMaterial color="#7ec8e3" wireframe opacity={0.2} transparent />
        </mesh>
      </Suspense>
      <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.2} />
    </Canvas>
  );
}
