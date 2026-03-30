import { useState, useEffect } from 'react'
import { api } from '../services/api'
import type { HealthResponse } from '../types'

export default function HealthStatus() {
  const [mongo, setMongo] = useState<HealthResponse | null>(null)
  const [rabbit, setRabbit] = useState<HealthResponse | null>(null)

  async function fetchHealth() {
    try {
      const [mongoData, rabbitData] = await Promise.all([
        api.getMongoHealth(),
        api.getRabbitHealth(),
      ])
      setMongo(mongoData)
      setRabbit(rabbitData)
    } catch (error) {
      console.error('Failed to fetch health status:', error)
    }
  }

  useEffect(() => {
    fetchHealth()
    const interval = setInterval(fetchHealth, 10000) // Poll every 10s
    return () => clearInterval(interval)
  }, [])

  function renderService(name: string, health: HealthResponse | null) {
    if (!health) {
      return (
        <div className="health-service">
          <div className="health-name">{name}</div>
          <div className="health-status loading">Loading...</div>
        </div>
      )
    }

    const isHealthy = health.status === 'healthy'

    return (
      <div className="health-service">
        <div className="health-header">
          <div className="health-name">{name}</div>
          <div className={`health-indicator ${isHealthy ? 'healthy' : 'unhealthy'}`}>
            {isHealthy ? '●' : '✕'}
          </div>
          <div className={`health-status ${health.status}`}>{health.status}</div>
        </div>
        {health.error && (
          <div className="health-error">{health.error}</div>
        )}
        {health.collections && health.collections.length > 0 && (
          <div className="health-detail">
            Collections: {health.collections.join(', ')}
          </div>
        )}
        {health.queues && health.queues.length > 0 && (
          <div className="health-detail">
            Queues: {health.queues.join(', ')}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="card health-card">
      <h2>System Health</h2>
      <div className="health-grid">
        {renderService('MongoDB', mongo)}
        {renderService('RabbitMQ', rabbit)}
      </div>
    </div>
  )
}
