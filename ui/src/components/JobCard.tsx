import { useState } from 'react'
import type { Job } from '../types'
import ResultCard from './ResultCard'

interface Props {
  job: Job
}

export default function JobCard({ job }: Props) {
  const [expanded, setExpanded] = useState(false)

  const statusColors = {
    pending: 'status-pending',
    processing: 'status-processing',
    completed: 'status-completed',
    failed: 'status-failed',
  }

  return (
    <div className="job-card">
      <div className="job-card-header" onClick={() => setExpanded(!expanded)}>
        <div className="job-card-main">
          <span className={`badge ${statusColors[job.status]}`}>
            {job.status}
          </span>
          <span className="job-filename">{job.file_name}</span>
        </div>
        <button className="expand-btn" aria-label={expanded ? 'Collapse' : 'Expand'}>
          {expanded ? '▼' : '▶'}
        </button>
      </div>

      {expanded && (
        <div className="job-card-details">
          <div className="job-id-small">ID: {job.job_id}</div>

          {job.error && (
            <div className="error-msg">{job.error}</div>
          )}

          {job.status === 'completed' && job.result && (
            <ResultCard result={job.result} />
          )}

          {(job.status === 'pending' || job.status === 'processing') && (
            <div className="job-progress">Processing...</div>
          )}
        </div>
      )}
    </div>
  )
}
