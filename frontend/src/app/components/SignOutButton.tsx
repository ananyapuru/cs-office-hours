// frontend/src/app/components/SignOutButton.tsx
'use client';

import React from 'react';
import Button from '@mui/material/Button';
import { API_ENDPOINTS } from '../constants';

const SignOutButton: React.FC = () => {
  const handleSignOut = () => {
    // Full page redirect to the custom /logout route on your backend
    window.location.href = `${API_ENDPOINTS.BACKEND_URL}/logout`;
  };

  return (
    <Button variant="contained" color="error" onClick={handleSignOut}>
      Sign Out
    </Button>
  );
};

export default SignOutButton;
