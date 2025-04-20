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
                    number: { value: 75, density: { enable: true, area: 700 } },
                    color: { value: '#ffffff' },

                    shape: { type: 'circle' },
                    opacity: { value: 1, random: { enable: true, minimumValue: 0.3 } },

                    size: { value: { min: 1, max: 3 } },
                    move: { enable: true, speed: 0.6, outModes: 'bounce' },
                    links: {
                        enable: true,
                        distance: 100,
                        color: '#ffffff',
                        opacity: 0.5,
                        width: 2,
                      },
                      
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
