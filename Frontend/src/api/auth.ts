import api from './axios';
import type { User, UserRole } from '@/types';

type RegisterProfileOptions = {
    idToken?: string;
}

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
}): Promise<User> => {
    const res = await api.patch('/api/v1/users/me', data);
    return res.data;
}

export const registerProfile = async (data: {
    display_name: string;
    role: UserRole;
}, options: RegisterProfileOptions = {}): Promise<User> => {
    const res = await api.post('/api/v1/auth/register', data, {
        headers: options.idToken
            ? { Authorization: `Bearer ${options.idToken}` }
            : undefined,
    });
    return res.data;
}
