import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) {
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        return Promise.reject(error)
      }

      originalRequest._retry = true
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken
        })
        const newAccessToken = response.data.access
        localStorage.setItem('accessToken', newAccessToken)
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export const loginWithGoogle = async (idToken) => {
  const response = await api.post('/auth/google/', { id_token: idToken })
  return response.data
}

export const createResearch = async (topic) => {
  const response = await api.post('/research/', { topic })
  return response.data
}

export const logoutUser = () => {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('user')
}

export const saveAuthData = (data) => {
  localStorage.setItem('accessToken', data.access)
  localStorage.setItem('refreshToken', data.refresh)
  localStorage.setItem('user', JSON.stringify(data.user))
}

export const getStoredUser = () => {
  const raw = localStorage.getItem('user')
  return raw ? JSON.parse(raw) : null
}

export default api
