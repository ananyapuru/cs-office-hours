// frontend/src/app/contexts/UserContext.tsx
import { createContext } from 'react';

interface IUserContext {
  // Context Properties
  user?: {
    netId: string;
    // We can add other properties after having figured out CAS stuff
  };
  checkContext: () => void;
}

const UserContext = createContext<IUserContext>({
  user: undefined,
  checkContext: () => {},
});

export default UserContext;
