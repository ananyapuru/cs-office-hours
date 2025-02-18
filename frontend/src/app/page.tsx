// app/page.jsx
'use client'; // we do this to ensure client side rendering

import { useState, useEffect } from 'react';
import { API_ENDPOINTS } from './constants';

export default function Home() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch(API_ENDPOINTS.BASE_URL)
      .then((response) => response.text())
      .then((data) => setMessage(data))
      .catch((error) => console.error('Error fetching data:', error));
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>CS Office Hours</h1>
      <p>{message || 'Loading...'}</p>
    </div>
  );
}
