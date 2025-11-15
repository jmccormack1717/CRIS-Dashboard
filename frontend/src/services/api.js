import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const fetchVisualizationData = async (filters) => {
  try {
    const response = await api.post('/api/data', filters)
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw new Error(error.response?.data?.detail || 'Failed to fetch data')
  }
}

export const getAvailableMeasures = async () => {
  try {
    const response = await api.get('/api/filters/measures')
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

export const getAvailablePeriods = async () => {
  try {
    const response = await api.get('/api/filters/periods')
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

