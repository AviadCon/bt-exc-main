import { useState, useRef } from 'react'

interface Props {
  onJobCreated: (jobId: string) => void
}

export default function Uploader({ onJobCreated }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleUpload() {
    if (!file) return
    setUploading(true)
    setError(null)

    const form = new FormData()
    form.append('file', file)

    try {
      const res = await fetch('/api/upload', { method: 'POST', body: form })
      if (!res.ok) {
        const body = await res.json()
        throw new Error(body.detail ?? `HTTP ${res.status}`)
      }
      const data = await res.json()
      onJobCreated(data.job_id)
      setFile(null)
      if (inputRef.current) inputRef.current.value = ''
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="card">
      <h2>Upload Media</h2>
      <label className="upload-label">
        Choose file
        <input
          ref={inputRef}
          type="file"
          accept="audio/*,video/*"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </label>
      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading…' : 'Upload'}
      </button>
      {file && <div className="filename">{file.name}</div>}
      {error && <div className="error-msg">{error}</div>}
    </div>
  )
}
