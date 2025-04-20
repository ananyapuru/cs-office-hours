// src/app/components/WaveFooter.tsx
'use client';
import React from 'react';
import Wave from 'react-wavify';

export default function WaveFooter() {
  return (
    <div className="absolute bottom-0 left-0 w-full overflow-hidden z-0 leading-[0]">
      <Wave
        fill="#ffffff"
        paused={false}
        options={{ height: 20, amplitude: 30, speed: 0.2, points: 3 }}
      />
    </div>
  );
}
