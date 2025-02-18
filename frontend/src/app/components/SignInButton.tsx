// frontend/src/app/components/SignInButton.tsx
'use client';

import React from 'react';
import Button from '@mui/material/Button';
import { API_ENDPOINTS } from '../constants';

const SignInButton: React.FC = () => {
  const loginUrl = `${API_ENDPOINTS.BACKEND_URL}/cas/login?redirect=${API_ENDPOINTS.FRONTEND_URL}`;

  return (
    <Button variant="contained" href={loginUrl}>
      Sign in With Yale CAS
    </Button>
  );
};

export default SignInButton;
