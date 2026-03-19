import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { User, Clock, AlertTriangle, Activity, Globe, Shield, ChevronDown } from 'lucide-react'
import { getUsers, getProfile } from '../api/client'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function DeviationMeter({ score }) {
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? '#ff003c' : pct >= 40 ? '#ff6b00' : pct >= 15 ? '#ffd700' : '#00ff87'
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs text-cyber-textDim">
        <span>Behavioral Deviation Score</span>
        <span className="font-mono font-bold" style={{ color }}>{pct}%</span>
      </div>
      <div className="h-3 bg-cyber-border rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ background: `linear-gradient(90deg, #00ff87, ${color})`, boxShadow: `0 0 10px ${color}60` }}
        />
      </div>
    </div>
  )
}

function FlagItem({ flag, index }) {
  const flagText = typeof flag === 'string' ? flag : flag.flag || ''
  const ts = typeof flag === 'object' ? flag.timestamp : null
  const isHigh = flagText.toLowerCase().includes('new ip') ||
                 flagText.toLowerCase().includes('unusual') ||
                 flagText.toLowerCase().includes('high-risk')
  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`flex items-start gap-3 p-3 rounded-xl text-sm border ${
        isHigh ? 'border-red-500/30 bg-red-500/05' : 'border-yellow-500/20 bg-yellow-500/04'
      }`}
    >
      <AlertTriangle size={14} className={`mt-0.5 flex-shrink-0 ${isHigh ? 'text-red-400' : 'text-yellow-400'}`} />
      <div className="min-w-0">
        <p className="text-cyber-text">{flagText}</p>
        {ts && <p className="text-cyber-textDim text-xs mt-1 font-mono">{new Date(ts).toLocaleString()}</p>}
      </div>
    </motion.div>
  )
}

function EventRow({ event, index }) {
  const isRisky = event.risk_score >= 65
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: index * 0.03 }}
      className={`flex items-center gap-3 p-2.5 rounded-lg border text-xs font-mono ${
        isRisky ? 'border-red-500/20 bg-red-500/04' : 'border-cyber-border bg-cyber-surface/30'
      }`}
    >
      <span className="text-cyber-textDim w-10 flex-shrink-0">{event.hour}:00</span>
      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold flex-shrink-0 ${
        isRisky ? 'bg-red-500/15 text-red-400 border border-red-500/30' : 'bg-cyber-surface text-cyber-textDim border border-cyber-border'
      }`}>
        {(event.event_type || '').replace(/_/g, ' ')}
      </span>
      <span className="text-cyber-textDim truncate">{event.ip}</span>
      <span className="ml-auto font-bold" style={{ color: event.risk_score >= 65 ? '#ff003c' : event.risk_score >= 40 ? '#ffd700' : '#00ff87' }}>
        {event.risk_score}
      </span>
    </motion.div>
  )
}

export default function BehavioralProfiler() {
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState('')
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingUsers, setLoadingUsers] = useState(true)

  useEffect(() => {
    getUsers().then(r => {
      setUsers(r.data.users || [])
      if (r.data.users?.length > 0) setSelectedUser(r.data.users[0])
    }).catch(console.error).finally(() => setLoadingUsers(false))
  }, [])

  useEffect(() => {
    if (!selectedUser) return
    setLoading(true); setProfile(null)
    getProfile(selectedUser)
      .then(r => setProfile(r.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [selectedUser])

  // Build timeline for chart
  const timelineData = (profile?.recent_events || []).map((e, i) => ({
    i, risk: e.risk_score, hour: e.hour,
    label: `${(e.event_type || '').replace(/_/g, ' ')} @ ${e.hour}:00`,
  }))

  const deviationScore = profile?.recent_flags?.length
    ? Math.min((profile.recent_flags.length / 10), 1)
    : 0.05

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text-cyan">Behavioral Profiler</h1>
          <p className="text-cyber-textDim text-sm mt-1">Per-user baseline analysis and deviation detection</p>
        </div>

        {/* User selector */}
        <div className="relative">
          <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-cyber-textDim" />
          <select
            value={selectedUser}
            onChange={e => setSelectedUser(e.target.value)}
            className="input-cyber pl-9 pr-8 appearance-none cursor-pointer"
            style={{ minWidth: 200 }}
          >
            {loadingUsers ? (
              <option>Loading…</option>
            ) : users.length === 0 ? (
              <option>No users yet</option>
            ) : (
              users.map(u => <option key={u} value={u}>{u}</option>)
            )}
          </select>
          <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-cyber-textDim pointer-events-none" />
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-48 text-cyber-textDim">
          <div className="animate-spin h-8 w-8 rounded-full border-b-2 border-cyber-purple mr-3" />
          Loading profile…
        </div>
      )}

      {profile && (
        <div className="space-y-5">
          {/* Stats row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Total Events', value: profile.total_events, color: '#00f5ff', icon: Activity },
              { label: 'Avg Risk Score', value: profile.avg_risk_score, color: '#ffd700', icon: Shield },
              { label: 'Known IPs', value: profile.known_ips?.length ?? 0, color: '#8b5cf6', icon: Globe },
              { label: 'Flags Raised', value: profile.recent_flags?.length ?? 0, color: '#ff003c', icon: AlertTriangle },
            ].map(s => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="stat-card"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-cyber-textDim text-xs uppercase tracking-wider">{s.label}</p>
                    <p className="text-3xl font-bold mt-1" style={{ color: s.color }}>{s.value}</p>
                  </div>
                  <div className="p-2 rounded-xl" style={{ background: s.color + '18', border: `1px solid ${s.color}30` }}>
                    <s.icon size={18} style={{ color: s.color }} />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Deviation meter */}
          <div className="glass-card border-glow-purple p-5">
            <DeviationMeter score={deviationScore} />
            <div className="mt-4 flex flex-wrap gap-2">
              {profile.known_ips?.map((ip, i) => (
                <span key={i} className="px-2.5 py-1 rounded-lg text-xs font-mono border border-cyber-border text-cyber-textDim bg-cyber-surface/40">
                  🌐 {ip}
                </span>
              ))}
            </div>
          </div>

          {/* Activity timeline chart */}
          {timelineData.length > 0 && (
            <div className="glass-card border-glow-cyan p-5">
              <h3 className="text-cyber-text font-semibold flex items-center gap-2 mb-4">
                <Clock size={16} className="text-cyber-cyan" />
                Risk Score Timeline (Last {timelineData.length} Events)
              </h3>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="i" tick={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (!active || !payload?.length) return null
                      const d = payload[0].payload
                      return (
                        <div className="glass-card p-3 text-xs border-glow-cyan">
                          <p className="text-cyber-cyan font-mono">{d.label}</p>
                          <p className="text-cyber-text font-bold mt-1">Risk: {d.risk}</p>
                        </div>
                      )
                    }}
                  />
                  <Line type="monotone" dataKey="risk" stroke="#8b5cf6" strokeWidth={2}
                    dot={(p) => p.payload.risk >= 65
                      ? <circle cx={p.cx} cy={p.cy} r={4} fill="#ff003c" stroke="#0a0a0f" strokeWidth={2} />
                      : <circle cx={p.cx} cy={p.cy} r={2} fill="#8b5cf6" />
                    }
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Recent events + flags side by side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="glass-card p-5">
              <h3 className="text-cyber-text font-semibold mb-3 flex items-center gap-2">
                <Activity size={16} className="text-cyber-cyan" /> Recent Events
              </h3>
              <div className="space-y-1.5 max-h-72 overflow-y-auto">
                {profile.recent_events?.length === 0
                  ? <p className="text-cyber-textDim text-sm">No events recorded</p>
                  : profile.recent_events.map((e, i) => <EventRow key={i} event={e} index={i} />)
                }
              </div>
            </div>
            <div className="glass-card p-5">
              <h3 className="text-cyber-text font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle size={16} className="text-cyber-red" /> Behavioral Flags
              </h3>
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {profile.recent_flags?.length === 0
                  ? <p className="text-green-400 text-sm flex items-center gap-2"><span>✅</span> No anomalies detected</p>
                  : profile.recent_flags.map((f, i) => <FlagItem key={i} flag={f} index={i} />)
                }
              </div>
            </div>
          </div>
        </div>
      )}

      {!loading && !profile && users.length === 0 && (
        <div className="text-center py-24 text-cyber-textDim">
          <User size={48} className="mx-auto mb-4 opacity-20" />
          <p>No user profiles yet. Run the simulation to generate data.</p>
        </div>
      )}
    </div>
  )
}
