export interface Job {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  file_name: string
  result: Record<string, unknown> | null
  error: string | null
}

export interface JobListResponse {
  jobs: Job[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy'
  error?: string
  collections?: string[]
  queues?: string[]
}

export interface UploadResponse {
  job_id: string
}
