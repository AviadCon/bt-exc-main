interface Props {
  result: Record<string, unknown>
}

function formatValue(value: unknown): string {
  if (typeof value === 'number') return value.toFixed(2)
  if (value === null || value === undefined) return '—'
  return String(value)
}

export default function ResultCard({ result }: Props) {
  const { transcription, ...metadata } = result

  return (
    <div className="card">
      <h2>Result</h2>
      {Object.entries(metadata).map(([key, value]) => (
        <div className="result-row" key={key}>
          <span>{key.replace(/_/g, ' ')}</span>
          <span>{formatValue(value)}</span>
        </div>
      ))}
      {transcription && (
        <>
          <div className="result-row" style={{ marginTop: 12 }}>
            <span>transcription</span>
          </div>
          <div className="transcription">{String(transcription)}</div>
        </>
      )}
    </div>
  )
}
