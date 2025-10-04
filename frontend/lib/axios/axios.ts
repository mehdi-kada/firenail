import axios from 'axios';
import { createClient } from '../supabase/client';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL!,
    timeout: 30000, // 30 second timeout
});

api.interceptors.request.use(async (config) =>{
    const supabase = createClient();
    const {data: {session}} = await supabase.auth.getSession()

    if(session?.access_token){
        config.headers.Authorization = `Bearer ${session.access_token}`;
    }

    return config;
});

export default api;