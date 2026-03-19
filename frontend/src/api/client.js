import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// Logs
export const getLogs      = (params = {}) => api.get('/logs', { params })
export const ingestLog    = (data)        => api.post('/logs', data)
export const getAnalytics = ()            => api.get('/logs/analytics')

// Verification
export const verifyLog    = (logId)       => api.get(`/verify/${logId}`)

// Behavioral Profiles
export const getUsers     = ()            => api.get('/profile/users')
export const getProfile   = (userId)     => api.get(`/profile/${userId}`)

// LLM Explain (Feature 2)
export const explainLog   = (logId)      => api.get(`/logs/${logId}/explain`)

// Alert Settings (Feature 3)
export const getSettings      = ()       => api.get('/settings')
export const saveSettings     = (data)  => api.post('/settings', data)
export const getAlertHistory  = (limit = 20) => api.get('/alerts/history', { params: { limit } })

export default api
