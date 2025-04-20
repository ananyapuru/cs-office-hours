// src/app/components/ParticlesBackground.tsx

'use client';
import React from 'react';
import Particles from 'react-tsparticles';
import { loadSlim } from 'tsparticles-slim';

export default function ParticlesBackground() {
  const particlesInit = async (engine: any) => {
    // load the slim bundle for a lighter build
    await loadSlim(engine);
  };

  return (
    <Particles
      init={particlesInit}
      options={{
        fullScreen: { enable: true, zIndex: -1 },
        fpsLimit: 60,
        particles: {
        number: { value: 50, density: { enable: true, area: 600 } }, // more particles
            color: { value: '#7ec8e3' },
          shape: { type: 'circle' },
        opacity: { value: 0.5, random: { enable: true, minimumValue: 0.3 } }, // brighter, varied

          size: { value: { min: 1, max: 3 } },
          move: { enable: true, speed: 0.6, outModes: 'bounce' },
          links: { enable: true, distance: 100, color: '#7ec8e3', opacity: 0.3, width: 1.2},
        },
        interactivity: {
          events: {
            onHover: { enable: true, mode: 'grab' },
            onClick: { enable: true, mode: 'push' },
          },
          modes: {
            grab: { distance: 150, links: { opacity: 0.4 } },
            push: { quantity: 2 },
          },
        },
        detectRetina: true,
      }}
    />
  );
}
