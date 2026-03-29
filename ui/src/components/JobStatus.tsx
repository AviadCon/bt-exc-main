import { useState, useEffect } from 'react'
import ResultCard from './ResultCard'

interface Job {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  file_name: string
  result: Record<string, unknown> | null
  error: string | null
}

interface Props {
  jobId: string
}

export default function JobStatus({ jobId }: Props) {
  const [job, setJob] = useState<Job | null>(null)
  const [fetchError, setFetchError] = useState<string | null>(null)

  async function fetchJob() {
    try {
      const res = await fetch(`/api/jobs/${jobId}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setJob(await res.json())
    } catch (err) {
      setFetchError(err instanceof Error ? err.message : 'Failed to fetch job')
    }
  }

  useEffect(() => {
    fetchJob()
    const interval = setInterval(() => {
      if (job?.status === 'completed' || job?.status === 'failed') {
        clearInterval(interval)
        return
      }
      fetchJob()
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  if (fetchError) return (
    <div className="card">
      <h2>Job Status</h2>
      <div className="error-msg">{fetchError}</div>
    </div>
  )

  if (!job) return (
    <div className="card">
      <h2>Job Status</h2>
      <div className="job-id">{jobId}</div>
      <p style={{ marginTop: 8, fontSize: '0.9rem', color: '#666' }}>Loading…</p>
    </div>
  )

  return (
    <>
      <div className="card">
        <h2>Job Status</h2>
        <div className="status-row">
          <span className={`badge ${job.status}`}>{job.status}</span>
          <span style={{ fontSize: '0.9rem' }}>{job.file_name}</span>
        </div>
        <div className="job-id">{job.job_id}</div>
        {job.error && <div className="error-msg" style={{ marginTop: 8 }}>{job.error}</div>}
      </div>
      {job.status === 'completed' && job.result && (
        <ResultCard result={job.result} />
      )}
    </>
  )
}
