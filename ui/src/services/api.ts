import type { Job, JobListResponse, HealthResponse, UploadResponse } from '../types'

const API_BASE = '/api'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new ApiError(response.status, body.detail ?? `HTTP ${response.status}`)
  }
  return response.json()
}

export const api = {
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    })

    return handleResponse<UploadResponse>(response)
  },

  async getJobs(page: number = 1, pageSize: number = 10): Promise<JobListResponse> {
    const response = await fetch(`${API_BASE}/jobs?page=${page}&page_size=${pageSize}`)
    return handleResponse<JobListResponse>(response)
  },

  async getJob(jobId: string): Promise<Job> {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`)
    return handleResponse<Job>(response)
  },

  async getMongoHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE}/health/mongodb`)
    return handleResponse<HealthResponse>(response)
  },

  async getRabbitHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE}/health/rabbitmq`)
    return handleResponse<HealthResponse>(response)
  },
}
