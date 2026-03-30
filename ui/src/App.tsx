import { useState } from 'react'
import Uploader from './components/Uploader'
import JobList from './components/JobList'
import HealthStatus from './components/HealthStatus'

type TabType = 'jobs' | 'admin'

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('jobs')
  const [refreshKey, setRefreshKey] = useState(0)

  function handleUploadComplete() {
    // Trigger refresh of job list
    setRefreshKey((prev) => prev + 1)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Media Processing Pipeline</h1>
        <p className="app-subtitle">Upload, process, and transcribe media files</p>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'jobs' ? 'active' : ''}`}
          onClick={() => setActiveTab('jobs')}
        >
          Jobs
        </button>
        <button
          className={`tab ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin')}
        >
          Admin
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'jobs' && (
          <>
            <Uploader onUploadComplete={handleUploadComplete} />
            <JobList key={refreshKey} />
          </>
        )}

        {activeTab === 'admin' && (
          <HealthStatus />
        )}
      </main>
    </div>
  )
}
