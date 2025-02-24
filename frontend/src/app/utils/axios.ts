// frontend/src/app/utils/axios.ts
import axios from 'axios';
import { API_ENDPOINTS } from '../constants';

const instance = axios.create({
  baseURL: API_ENDPOINTS.BACKEND_URL,
  withCredentials: true, // to include cookies, which we likely need to do.
});

export default instance;
