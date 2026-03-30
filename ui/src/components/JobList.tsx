import { useState, useEffect } from 'react'
import { api } from '../services/api'
import type { Job } from '../types'
import JobCard from './JobCard'

export default function JobList() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const pageSize = 5

  async function fetchJobs() {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getJobs(page, pageSize)
      setJobs(data.jobs)
      setTotal(data.total)
      setTotalPages(data.total_pages)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()

    // Auto-refresh if any jobs are in progress
    const hasActiveJobs = jobs.some(
      (job) => job.status === 'pending' || job.status === 'processing'
    )

    if (hasActiveJobs) {
      const interval = setInterval(fetchJobs, 3000) // Poll every 3s
      return () => clearInterval(interval)
    }
  }, [page])

  // Separate effect for auto-refresh
  useEffect(() => {
    const hasActiveJobs = jobs.some(
      (job) => job.status === 'pending' || job.status === 'processing'
    )

    if (hasActiveJobs) {
      const interval = setInterval(fetchJobs, 3000)
      return () => clearInterval(interval)
    }
  }, [jobs])

  function handlePrevious() {
    if (page > 1) setPage(page - 1)
  }

  function handleNext() {
    if (page < totalPages) setPage(page + 1)
  }

  if (error) {
    return (
      <div className="card">
        <h2>All Jobs</h2>
        <div className="error-msg">{error}</div>
        <button onClick={fetchJobs} className="retry-btn">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="card jobs-card">
      <div className="jobs-list-header">
        <h2>All Jobs</h2>
        <div className="jobs-count">{total} total</div>
      </div>

      {loading && jobs.length === 0 ? (
        <div className="loading-msg">Loading jobs...</div>
      ) : jobs.length === 0 ? (
        <div className="empty-msg">No jobs yet. Upload a file to get started!</div>
      ) : (
        <>
          <div className="jobs-grid">
            {jobs.map((job) => (
              <JobCard key={job.job_id} job={job} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={handlePrevious}
                disabled={page === 1}
                className="pagination-btn"
              >
                ← Previous
              </button>
              <span className="pagination-info">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={handleNext}
                disabled={page === totalPages}
                className="pagination-btn"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
