// frontend/src/app/components/SignOutButton.tsx
'use client';

import Button from '@mui/material/Button';
import axios from '../utils/axios';
import { useContext } from 'react';
import UserContext from '../contexts/UserContext';

const SignOutButton: React.FC = () => {
  const { checkContext } = useContext(UserContext);

  const handleSignOut = async () => {
    try {
      // Calling the backend logout endpoint TODO: fix this
      const { data } = await axios.get<{ success: boolean }>('/cas/logout', {
        withCredentials: true,
      });
      if (data.success) {
        checkContext();
      }
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <Button variant="contained" color="error" onClick={handleSignOut}>
      Sign Out
    </Button>
  );
};

export default SignOutButton;
