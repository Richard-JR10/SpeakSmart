import api from './axios';
import type { Module, Phrase } from '@/types';

export const getModules = async (): Promise<Module[]> => {
    const res = await api.get('/api/v1/modules')
    return res.data;
}

export const getModule = async (moduleId: string): Promise<Module> => {
    const res = await api.get(`/api/v1/modules/${moduleId}`)
    return res.data;
}

export const getModulesPhrases = async (moduleId: string): Promise<Phrase[]> => {
    const res = await api.get(`/api/v1/modules/${moduleId}/phrases`)
    return res.data;
}

export const getPhrase = async (phraseId: string): Promise<Phrase> => {
    const res = await api.get(`/api/v1/phrases/${phraseId}`)
    return res.data;
}