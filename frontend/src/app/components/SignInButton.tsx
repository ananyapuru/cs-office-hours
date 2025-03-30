'use client';

import React from 'react';
import Button from '@mui/material/Button';
import { API_ENDPOINTS } from '../constants';

const SignInButton: React.FC = () => {
  const loginUrl = `${API_ENDPOINTS.BACKEND_URL}/cas/login?redirect=${API_ENDPOINTS.FRONTEND_URL}`;

  return (
    <Button
      variant="contained"
      href={loginUrl}
      style={{
        backgroundColor: '#ffffff',
        color: '#0e1c2c',
        fontWeight: 600,
        padding: '0.75rem 2rem',
        borderRadius: '0.75rem',
        textTransform: 'none',
        fontSize: '1rem',
      }}
    >
      Sign in with Yale CAS
    </Button>
  );
};

export default SignInButton;
