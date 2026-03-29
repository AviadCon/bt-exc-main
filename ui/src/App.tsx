import { useState } from 'react'
import Uploader from './components/Uploader'
import JobStatus from './components/JobStatus'

export default function App() {
  const [jobId, setJobId] = useState<string | null>(null)

  return (
    <div className="app">
      <h1>Media Pipeline</h1>
      <Uploader onJobCreated={setJobId} />
      {jobId && <JobStatus jobId={jobId} />}
    </div>
  )
}