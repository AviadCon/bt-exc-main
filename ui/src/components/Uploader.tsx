import { useState, useRef, useEffect } from 'react'
import { api } from '../services/api'

interface Props {
  onUploadComplete?: () => void
}

interface QueueItem {
  id: string
  file: File
  status: 'pending' | 'uploading' | 'completed' | 'failed'
  error?: string
  fadeOut?: boolean
}

export default function Uploader({ onUploadComplete }: Props) {
  const [queue, setQueue] = useState<QueueItem[]>([])
  const [uploading, setUploading] = useState(false)
  const [queuePage, setQueuePage] = useState(1)
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const itemsPerPage = 3

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return

    const newItems: QueueItem[] = files.map((file) => ({
      id: crypto.randomUUID(),
      file,
      status: 'pending',
    }))

    setQueue((prev) => [...prev, ...newItems])

    // Clear input
    if (inputRef.current) inputRef.current.value = ''
  }

  function handleDrag(e: React.DragEvent) {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = Array.from(e.dataTransfer.files).filter((file) =>
      file.type.startsWith('audio/') || file.type.startsWith('video/')
    )

    if (files.length === 0) return

    const newItems: QueueItem[] = files.map((file) => ({
      id: crypto.randomUUID(),
      file,
      status: 'pending',
    }))

    setQueue((prev) => [...prev, ...newItems])
  }

  function removeFromQueue(id: string) {
    setQueue((prev) => prev.filter((item) => item.id !== id))
  }

  async function processQueue() {
    if (uploading || queue.length === 0) return

    setUploading(true)

    const itemsToProcess = queue.filter((item) => item.status === 'pending')

    for (const item of itemsToProcess) {
      // Mark as uploading
      setQueue((prev) =>
        prev.map((q) => (q.id === item.id ? { ...q, status: 'uploading' as const } : q))
      )

      try {
        await api.uploadFile(item.file)

        // Mark as completed
        setQueue((prev) =>
          prev.map((q) => (q.id === item.id ? { ...q, status: 'completed' as const } : q))
        )

        // Notify parent
        if (onUploadComplete) {
          onUploadComplete()
        }

        // Trigger fadeout after 5 seconds
        setTimeout(() => {
          setQueue((prev) =>
            prev.map((q) => (q.id === item.id ? { ...q, fadeOut: true } : q))
          )

          // Remove after fadeout animation completes (0.5s)
          setTimeout(() => {
            setQueue((prev) => prev.filter((q) => q.id !== item.id))
          }, 500)
        }, 5000)
      } catch (error) {
        // Mark as failed
        setQueue((prev) =>
          prev.map((q) =>
            q.id === item.id
              ? {
                  ...q,
                  status: 'failed' as const,
                  error: error instanceof Error ? error.message : 'Upload failed',
                }
              : q
          )
        )
      }
    }

    setUploading(false)
  }

  function clearCompleted() {
    setQueue((prev) => prev.filter((item) => item.status !== 'completed'))
  }

  const pendingCount = queue.filter((item) => item.status === 'pending').length
  const hasCompleted = queue.some((item) => item.status === 'completed')

  const startIdx = (queuePage - 1) * itemsPerPage
  const paginatedQueue = queue.slice(startIdx, startIdx + itemsPerPage)
  const totalQueuePages = Math.ceil(queue.length / itemsPerPage)

  return (
    <div className="card uploader-card">
      <h2>Upload Media Files</h2>

      <div className="upload-controls">
        <div
          className={`dropzone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <div className="dropzone-content">
            <span className="dropzone-icon">📁</span>
            <p className="dropzone-text">
              {dragActive ? 'Drop files here' : 'Drag & drop files or click to browse'}
            </p>
            <p className="dropzone-hint">Audio and video files only</p>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept="audio/*,video/*"
            multiple
            onChange={handleFileSelect}
            disabled={uploading}
            style={{ display: 'none' }}
          />
        </div>

        {queue.length > 0 && (
          <div className="upload-actions">
            <button
              onClick={processQueue}
              disabled={uploading || pendingCount === 0}
              className="upload-btn"
            >
              {uploading ? 'Uploading...' : `Upload ${pendingCount} file(s)`}
            </button>
            {hasCompleted && (
              <button onClick={clearCompleted} className="clear-btn">
                Clear Completed
              </button>
            )}
          </div>
        )}
      </div>

      {queue.length > 0 && (
        <div className="upload-queue">
          <h3>Queue ({queue.length})</h3>
          {paginatedQueue.map((item) => (
            <div
              key={item.id}
              className={`queue-item status-${item.status}${item.fadeOut ? ' fade-out' : ''}`}
            >
              <div className="queue-item-info">
                <span className="queue-filename">{item.file.name}</span>
                <span className="queue-size">
                  {(item.file.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>

              <div className="queue-item-status">
                {item.status === 'pending' && <span className="status-badge">Waiting for upload</span>}
                {item.status === 'uploading' && (
                  <span className="status-badge uploading">Uploading...</span>
                )}
                {item.status === 'completed' && (
                  <span className="status-badge completed">✓ Done</span>
                )}
                {item.status === 'failed' && (
                  <span className="status-badge failed">✕ Failed</span>
                )}

                {item.status === 'pending' && (
                  <button
                    onClick={() => removeFromQueue(item.id)}
                    className="remove-btn"
                    aria-label="Remove"
                  >
                    ✕
                  </button>
                )}
              </div>

              {item.error && <div className="queue-error">{item.error}</div>}
            </div>
          ))}

          {totalQueuePages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setQueuePage((prev) => Math.max(1, prev - 1))}
                disabled={queuePage === 1}
                className="pagination-btn"
              >
                ← Previous
              </button>
              <span className="pagination-info">
                Page {queuePage} of {totalQueuePages}
              </span>
              <button
                onClick={() => setQueuePage((prev) => Math.min(totalQueuePages, prev + 1))}
                disabled={queuePage === totalQueuePages}
                className="pagination-btn"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
