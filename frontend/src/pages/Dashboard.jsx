import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, AlertTriangle, Shield, Zap, TrendingUp, Server, RefreshCw, Brain } from 'lucide-react'
import SeverityBadge from '../components/SeverityBadge'
import RiskScoreBar from '../components/RiskScoreBar'
import ExplainModal from '../components/ExplainModal'
import { getLogs } from '../api/client'
import { formatDistanceToNow } from 'date-fns'

const THREAT_COLORS = {
  Normal: '#60a5fa', Probe: '#ffd700', DoS: '#ff6b00', R2L: '#ff003c', U2R: '#8b5cf6',
}

function StatCard({ icon: Icon, label, value, color, sublabel }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="stat-card border-glow-cyan"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-cyber-textDim text-xs font-medium uppercase tracking-wider">{label}</p>
          <p className="text-3xl font-bold mt-1" style={{ color }}>{value}</p>
          {sublabel && <p className="text-cyber-textDim text-xs mt-1">{sublabel}</p>}
        </div>
        <div className="p-2.5 rounded-xl" style={{ background: color + '18', border: `1px solid ${color}30` }}>
          <Icon size={20} style={{ color }} />
        </div>
      </div>
    </motion.div>
  )
}

function LogEntry({ log, index, onExplain }) {
  const ts = log.created_at ? new Date(log.created_at) : new Date()
  const timeAgo = isNaN(ts) ? '' : (() => { try { return formatDistanceToNow(ts, { addSuffix: true }) } catch { return '' } })()
  const canExplain = ['HIGH', 'CRITICAL'].includes(log.severity)

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.3, delay: index * 0.03 }}
      className="log-entry"
      style={{
        borderLeft: `3px solid ${
          log.severity === 'CRITICAL' ? '#ff003c' :
          log.severity === 'HIGH' ? '#ff6b00' :
          log.severity === 'MEDIUM' ? '#ffd700' :
          log.severity === 'LOW' ? '#00ff87' : '#60a5fa'
        }`,
      }}
    >
      <div className="flex flex-wrap items-start gap-3">
        {/* Severity + Threat label */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <SeverityBadge severity={log.severity} pulse />
          <span
            className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold border"
            style={{
              color: THREAT_COLORS[log.threat_label] || '#60a5fa',
              borderColor: (THREAT_COLORS[log.threat_label] || '#60a5fa') + '40',
              background: (THREAT_COLORS[log.threat_label] || '#60a5fa') + '12',
            }}
          >
            {log.threat_label || 'Normal'}
          </span>
          {log.is_anomaly && (
            <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold border border-red-500/40 bg-red-500/10 text-red-400">
              ⚠ ANOMALY
            </span>
          )}
        </div>

        {/* Core details */}
        <div className="flex-1 min-w-0">
          <p className="text-cyber-text text-sm font-medium truncate">{log.description}</p>
          <div className="flex flex-wrap gap-3 mt-1 text-xs text-cyber-textDim font-mono">
            <span>👤 {log.user_id}</span>
            <span>🌐 {log.source_ip}</span>
            <span>⚡ {log.event_type?.replace(/_/g, ' ')}</span>
            <span className="text-cyber-textDim">🕐 {timeAgo}</span>
          </div>
        </div>

        {/* Risk score */}
        <div className="w-32 flex-shrink-0">
          <p className="text-cyber-textDim text-xs mb-1">Risk Score</p>
          <RiskScoreBar score={log.risk_score || 0} />
        </div>

        {/* TX Hash pill */}
        {log.tx_hash && (
          <div className="flex-shrink-0">
            <span
              className="px-2 py-1 rounded-lg text-xs font-mono border cursor-pointer hover:border-cyber-cyan/50 transition-colors"
              style={{ borderColor: 'rgba(0,245,255,0.2)', color: '#00f5ff80', background: 'rgba(0,245,255,0.04)' }}
              title={log.tx_hash}
            >
              ⛓ {log.tx_hash.slice(0, 8)}…
            </span>
          </div>
        )}

        {/* AI Explain button — HIGH and CRITICAL only */}
        {canExplain && log._id && (
          <button
            onClick={() => onExplain(log._id)}
            style={{
              display: 'flex', alignItems: 'center', gap: 5,
              padding: '4px 10px', borderRadius: 6, fontSize: 11,
              fontWeight: 700, cursor: 'pointer', border: '1px solid rgba(139,92,246,0.4)',
              background: 'rgba(139,92,246,0.1)', color: '#a78bfa',
              transition: 'all .15s', flexShrink: 0,
            }}
            onMouseEnter={e => { e.currentTarget.style.background='rgba(139,92,246,0.2)'; e.currentTarget.style.borderColor='rgba(139,92,246,0.7)' }}
            onMouseLeave={e => { e.currentTarget.style.background='rgba(139,92,246,0.1)'; e.currentTarget.style.borderColor='rgba(139,92,246,0.4)' }}
          >
            <Brain size={11} />
            Explain
          </button>
        )}
      </div>
    </motion.div>
  )
}

export default function Dashboard() {
  const [logs,      setLogs]      = useState([])
  const [stats,     setStats]     = useState({ total: 0, critical: 0, anomalies: 0, avgRisk: 0 })
  const [loading,   setLoading]   = useState(true)
  const [streaming, setStreaming] = useState(false)
  const [explainId, setExplainId] = useState(null)
  const sseRef = useRef(null)

  const fetchLogs = async () => {
    try {
      const res = await getLogs({ limit: 50 })
      setLogs(res.data.logs || [])
      const all = res.data.logs || []
      setStats({
        total: res.data.total || all.length,
        critical: all.filter(l => l.severity === 'CRITICAL' || l.severity === 'HIGH').length,
        anomalies: all.filter(l => l.is_anomaly).length,
        avgRisk: all.length ? Math.round(all.reduce((s, l) => s + (l.risk_score || 0), 0) / all.length) : 0,
      })
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const startSSE = () => {
    if (sseRef.current) return
    const es = new EventSource('/api/logs/stream')
    es.onmessage = (e) => {
      try {
        const log = JSON.parse(e.data)
        setLogs(prev => {
          const updated = [log, ...prev].slice(0, 100)
          const critical = updated.filter(l => l.severity === 'CRITICAL' || l.severity === 'HIGH').length
          const anomalies = updated.filter(l => l.is_anomaly).length
          const avgRisk = updated.length ? Math.round(updated.reduce((s, l) => s + (l.risk_score || 0), 0) / updated.length) : 0
          setStats(prev => ({ total: prev.total + 1, critical, anomalies, avgRisk }))
          return updated
        })
      } catch {}
    }
    es.onerror = () => { es.close(); sseRef.current = null; setStreaming(false) }
    sseRef.current = es
    setStreaming(true)
  }

  useEffect(() => {
    fetchLogs()
    startSSE()
    return () => { sseRef.current?.close(); sseRef.current = null }
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text-cyan">Live Threat Feed</h1>
          <p className="text-cyber-textDim text-sm mt-1">Real-time cybersecurity events with AI analysis</p>
        </div>
        <div className="flex items-center gap-3">
          {streaming && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-green-500/30 bg-green-500/08 text-green-400 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              LIVE
            </div>
          )}
          <button onClick={fetchLogs} className="btn-cyber flex items-center gap-2">
            <RefreshCw size={14} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Activity} label="Total Events"    value={stats.total}     color="#00f5ff" sublabel="All time" />
        <StatCard icon={AlertTriangle} label="High Severity" value={stats.critical}  color="#ff6b00" sublabel="CRITICAL + HIGH" />
        <StatCard icon={Zap}      label="Anomalies"      value={stats.anomalies} color="#8b5cf6" sublabel="ML detected" />
        <StatCard icon={TrendingUp} label="Avg Risk Score" value={stats.avgRisk}   color="#ffd700" sublabel="0-100 scale" />
      </div>

      {/* Log stream */}
      <div className="glass-card border-glow-cyan p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-cyber-text flex items-center gap-2">
            <Server size={18} className="text-cyber-cyan" />
            Event Stream
            <span className="text-cyber-textDim text-sm font-normal">({logs.length} events)</span>
          </h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-40 text-cyber-textDim">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-cyan mr-3" />
            Loading events...
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center h-40 flex flex-col items-center justify-center text-cyber-textDim">
            <Shield size={32} className="mb-3 opacity-30" />
            <p>No events yet. Run the simulation script to populate data.</p>
            <code className="mt-2 text-xs bg-cyber-surface px-3 py-1 rounded">
              python backend/simulate_events.py
            </code>
          </div>
        ) : (
          <div className="space-y-0 max-h-[600px] overflow-y-auto pr-1">
            <AnimatePresence initial={false}>
              {logs.map((log, i) => (
                <LogEntry key={log._id || i} log={log} index={i} onExplain={setExplainId} />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* LLM Explain Modal */}
      {explainId && (
        <ExplainModal logId={explainId} onClose={() => setExplainId(null)} />
      )}
    </div>
  )
}
