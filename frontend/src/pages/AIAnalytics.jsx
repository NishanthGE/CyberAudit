import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  BarChart, Bar,
} from 'recharts'
import { BarChart2, Cpu, AlertTriangle, Globe } from 'lucide-react'
import { getAnalytics } from '../api/client'

const THREAT_PALETTE = {
  Normal: '#60a5fa', Probe: '#ffd700', DoS: '#ff6b00', R2L: '#ff003c', U2R: '#8b5cf6',
}
const SEVERITY_PALETTE = {
  CRITICAL: '#ff003c', HIGH: '#ff6b00', MEDIUM: '#ffd700', LOW: '#00ff87', INFO: '#60a5fa',
}

const DOW = ['', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function ChartCard({ title, icon: Icon, children, className = '' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-card border-glow-purple p-5 ${className}`}
    >
      <h3 className="text-cyber-text font-semibold flex items-center gap-2 mb-5">
        <Icon size={16} className="text-cyber-purple" />
        {title}
      </h3>
      {children}
    </motion.div>
  )
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card p-3 border-glow-cyan text-xs">
      <p className="text-cyber-cyan font-mono mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }} className="font-semibold">
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}
        </p>
      ))}
    </div>
  )
}

// Heatmap cell
function HeatCell({ value, maxVal }) {
  const intensity = maxVal > 0 ? value / maxVal : 0
  const alpha = Math.round(intensity * 220 + 20)
  const color = intensity > 0.7 ? '#ff003c' : intensity > 0.4 ? '#ff6b00' : intensity > 0.1 ? '#ffd700' : '#1e2040'
  return (
    <div
      className="rounded-sm transition-all duration-300 hover:scale-110 cursor-default"
      style={{ background: color, opacity: 0.15 + intensity * 0.85, width: '100%', paddingTop: '100%', position: 'relative' }}
      title={`Count: ${value}`}
    />
  )
}

export default function AIAnalytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAnalytics()
      .then(r => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-cyber-textDim">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyber-purple mr-3" />
        Loading AI analytics…
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center text-cyber-textDim py-24">
        <Cpu size={40} className="mx-auto mb-4 opacity-30" />
        <p>No analytics data available. Run the simulation first.</p>
      </div>
    )
  }

  // Build heatmap matrix [dow 1-7][hour 0-23]
  const heatMatrix = Array.from({ length: 7 }, () => Array(24).fill(0))
  const maxHeat = Math.max(1, ...(data.hourly_heatmap || []).map(d => d.count))
  ;(data.hourly_heatmap || []).forEach(d => {
    const dow = (d._id?.dow || 1) - 1
    const hour = d._id?.hour || 0
    if (dow >= 0 && dow < 7 && hour >= 0 && hour < 24) heatMatrix[dow][hour] = d.count
  })

  const threatData = (data.threat_distribution || []).map(d => ({
    ...d, color: THREAT_PALETTE[d.label] || '#60a5fa',
  }))

  const riskTimeline = (data.risk_over_time || []).map((d, i) => ({
    i, risk: d.risk,
    time: d.time ? new Date(d.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : `T${i}`,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text-cyan">AI Analytics</h1>
        <p className="text-cyber-textDim text-sm mt-1">Machine learning insights from your audit log data</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Distribution Donut */}
        <ChartCard title="Threat Type Distribution" icon={AlertTriangle}>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={threatData} dataKey="count" nameKey="label" cx="50%" cy="50%"
                innerRadius={60} outerRadius={90} paddingAngle={4}>
                {threatData.map((d, i) => (
                  <Cell key={i} fill={d.color} stroke={d.color + '60'} strokeWidth={1} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{v}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Severity Distribution Bar */}
        <ChartCard title="Severity Distribution" icon={BarChart2}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.severity_distribution || []} barSize={28}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fill: '#64748b', fontSize: 11, fontFamily: 'JetBrains Mono' }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {(data.severity_distribution || []).map((d, i) => (
                  <Cell key={i} fill={SEVERITY_PALETTE[d.label] || '#60a5fa'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Risk Score Over Time */}
        <ChartCard title="Risk Score Timeline (Last 100 Events)" icon={Cpu} className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={riskTimeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'JetBrains Mono' }} interval={Math.floor(riskTimeline.length / 10)} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="risk" stroke="#00f5ff" strokeWidth={2}
                dot={false} activeDot={{ r: 5, fill: '#00f5ff', stroke: '#0a0a0f', strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Anomaly Heatmap */}
        <ChartCard title="Activity Heatmap (Day × Hour)" icon={Globe} className="lg:col-span-2">
          <div className="overflow-x-auto">
            <div style={{ minWidth: 640 }}>
              {/* Hour labels */}
              <div className="flex mb-1 pl-10">
                {Array.from({ length: 24 }, (_, h) => (
                  <div key={h} className="flex-1 text-center text-cyber-textDim font-mono" style={{ fontSize: 9 }}>
                    {h % 4 === 0 ? `${h}h` : ''}
                  </div>
                ))}
              </div>
              {heatMatrix.map((row, dow) => (
                <div key={dow} className="flex items-center gap-1 mb-1">
                  <span className="w-9 text-xs text-cyber-textDim font-mono text-right pr-1">{DOW[dow + 1]}</span>
                  {row.map((val, hour) => (
                    <div key={hour} className="flex-1" style={{ aspectRatio: '1.5 / 1' }}>
                      <HeatCell value={val} maxVal={maxHeat} />
                    </div>
                  ))}
                </div>
              ))}
              <div className="flex items-center gap-3 mt-3 justify-end text-xs text-cyber-textDim">
                <span>Low</span>
                {['#1e2040', '#ffd700', '#ff6b00', '#ff003c'].map((c, i) => (
                  <div key={i} className="w-4 h-3 rounded-sm" style={{ background: c }} />
                ))}
                <span>High</span>
              </div>
            </div>
          </div>
        </ChartCard>

        {/* Top IPs */}
        <ChartCard title="Top Risky IPs" icon={Globe}>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.top_ips || []} layout="vertical" barSize={14}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
              <YAxis type="category" dataKey="ip" width={120} tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'monospace' }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="avg_risk" name="Avg Risk" fill="#ff6b00" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Top Users */}
        <ChartCard title="Top Risky Users" icon={BarChart2}>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.top_users || []} layout="vertical" barSize={14}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
              <YAxis type="category" dataKey="user" width={100} tick={{ fill: '#64748b', fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="avg_risk" name="Avg Risk" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}
