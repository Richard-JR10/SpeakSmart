import api from './axios';
import type { User } from '@/types';

export const getMe = async (): Promise<User> => {
    const res = await api.get('/api/v1/auth/me');
    return res.data;
}

export const verifyToken = async (): Promise<{ valid: boolean; uid: string; role: string;}> => {
    const res = await api.get('/api/v1/auth/verify');
    return res.data;
}

export const updateProfile = async (data: {
    display_name?: string;
    class_id?: string
}): Promise<User> => {
    const res = await api.patch('/api/v1/auth/users/me', data);
    return res.data;
}