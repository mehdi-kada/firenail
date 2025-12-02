import axios from 'axios';
import { createClient } from '../supabase/client';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
    // baseURL: "http://localhost:8000",
    timeout: 60000, // 60 second timeout    
});

api.interceptors.request.use(async (config) =>{
    const supabase = createClient();
    const {data: {session}} = await supabase.auth.getSession()

    if(session?.access_token){
        config.headers.Authorization = `Bearer ${session.access_token}`;
    }

    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            if (typeof window !== 'undefined') {
                window.location.href = '/auth/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;