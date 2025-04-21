'use client';
import React from 'react';
import Particles from 'react-tsparticles';
import { loadSlim } from 'tsparticles-slim';

export default function ParticlesBackground() {
  const particlesInit = async (engine: any) => {
    await loadSlim(engine);
  };

  return (
    <Particles
      init={particlesInit}
      options={{
        fullScreen: { enable: true, zIndex: -1 },
        fpsLimit: 60,
        particles: {
          number: { value: 50, density: { enable: true, area: 800 } },        // more particles
          color: { value: '#7ec8e3' },
          shape: { type: 'circle' },
          opacity: { value: 0.5 },                                             // higher opacity
          size: { value: { min: 2, max: 5 } },                                  // larger sizes
          move: { enable: true, speed: 1, outModes: 'bounce' },
          links: {
            enable: true,
            distance: 150,
            color: '#7ec8e3',
            opacity: 0.3,
            width: 1,
          },
        },
        interactivity: {
          events: {
            onHover: { enable: true, mode: 'grab' },
            onClick: { enable: true, mode: 'push' },
          },
          modes: {
            grab: { distance: 200, links: { opacity: 0.5 } },
            push: { quantity: 4 },
          },
        },
        detectRetina: true,
      }}
    />
  );
}
