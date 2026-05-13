import axios, { AxiosHeaders, type InternalAxiosRequestConfig } from 'axios';
import { auth } from '@/firebase';

type AuthRetryConfig = InternalAxiosRequestConfig & {
    _retryAuth?: boolean;
}

declare module 'axios' {
    interface AxiosError {
        rateLimited?: boolean;
        rateLimitMessage?: string;
    }
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
        const headers = AxiosHeaders.from(config.headers);
        if (user) {
            if (!headers.has('Authorization')) {
                const token = await user.getIdToken();
                headers.set('Authorization', `Bearer ${token}`);
            }
        }
        config.headers = headers;

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

        if (status === 429) {
            const retryAfter = error.response?.headers?.['retry-after'];
            const waitSec = retryAfter ? parseInt(retryAfter, 10) : 60;
            error.rateLimited = true;
            error.rateLimitMessage = waitSec <= 60
                ? `Too many requests. Please wait ${waitSec} seconds before trying again.`
                : `Too many requests. Please wait about ${Math.ceil(waitSec / 60)} minutes before trying again.`;
        }

        return Promise.reject(error);
    }
)

export default api;
