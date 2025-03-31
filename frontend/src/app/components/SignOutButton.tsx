'use client';

import React from 'react';
import Button from '@mui/material/Button';
import { API_ENDPOINTS } from '../constants';

const SignOutButton: React.FC = () => {
  const handleSignOut = () => {
    window.location.href = `${API_ENDPOINTS.BACKEND_URL}/logout`;
  };

  return (
    <Button
      variant="contained"
      color="error"
      onClick={handleSignOut}
      style={{
        padding: '0.75rem 2rem',
        borderRadius: '0.75rem',
        textTransform: 'none',
        fontSize: '0.85rem',
        fontWeight: 500,
      }}
    >
      Sign Out
    </Button>
  );
};

export default SignOutButton;
