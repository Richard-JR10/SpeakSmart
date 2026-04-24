import axios, { AxiosHeaders, type InternalAxiosRequestConfig } from 'axios';
import { auth } from '@/firebase';

type AuthRetryConfig = InternalAxiosRequestConfig & {
    _retryAuth?: boolean;
}

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    }
})

api.interceptors.request.use(
    async (config) => {
        const user = auth.currentUser;
        if (user) {
            const token = await user.getIdToken();
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
)

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const status = error.response?.status;
        const retryConfig = error.config as AuthRetryConfig | undefined;

        if (status === 401 && auth.currentUser && retryConfig && !retryConfig._retryAuth) {
            retryConfig._retryAuth = true;

            try {
                const token = await auth.currentUser.getIdToken(true);
                retryConfig.headers = AxiosHeaders.from(retryConfig.headers);
                retryConfig.headers.set('Authorization', `Bearer ${token}`);
                return api(retryConfig);
            } catch {
                await auth.signOut();
            }
        } else if (status === 401) {
            await auth.signOut();
        }

        if (status === 401 && window.location.pathname !== '/login') {
            window.location.assign('/login');
        }

        if (status === 403) {
            console.error("Access denied — insufficient permissions");
        }

        return Promise.reject(error);
    }
)

export default api;
