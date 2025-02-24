// src/app/theme.ts
import { createTheme } from '@mui/material/styles';

const yaleBlue = '#0E1C2C'; // Yale Blue
const yaleGold = '#FFC20E'; // Yale Gold

const theme = createTheme({
  palette: {
    primary: {
      main: yaleBlue,
    },
    secondary: {
      main: yaleGold,
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

export default theme;
