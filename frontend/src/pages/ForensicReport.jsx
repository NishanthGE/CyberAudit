import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { FileText, Download, Filter, Loader, Shield, Hash, Clock } from 'lucide-react'
import { getLogs } from '../api/client'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import SeverityBadge from '../components/SeverityBadge'
import RiskScoreBar from '../components/RiskScoreBar'

const SEVERITY_OPTIONS = ['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
const THREAT_OPTIONS = ['', 'Normal', 'Probe', 'DoS', 'R2L', 'U2R']

const COL_STYLE = 'grid items-center gap-4'
const COLS = '2fr 110px 100px 90px 110px 70px'

function LogReportRow({ log, index }) {
  const ts = log.created_at ? new Date(log.created_at).toLocaleString() : '—'
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: index * 0.02 }}
      className={`${COL_STYLE} py-3 border-b border-cyber-border`}
      style={{ gridTemplateColumns: COLS }}
    >
      {/* EVENT */}
      <div className="min-w-0">
        <p className="text-cyber-text text-xs truncate font-medium">{log.description}</p>
        <p className="text-cyber-textDim text-xs font-mono mt-0.5">{log.user_id} · {log.source_ip}</p>
        <p className="text-cyber-textDim text-xs">{ts}</p>
      </div>
      {/* SEVERITY */}
      <div className="flex items-center">
        <SeverityBadge severity={log.severity} />
      </div>
      {/* RISK */}
      <div className="flex flex-col gap-1">
        <span className="text-xs font-mono text-cyber-text font-bold">{log.risk_score ?? 0}</span>
        <RiskScoreBar score={log.risk_score || 0} />
      </div>
      {/* THREAT */}
      <span className="text-xs font-mono text-cyber-textDim">{log.threat_label || '—'}</span>
      {/* TX HASH */}
      <span className="text-xs font-mono text-cyber-textDim truncate">
        {log.tx_hash ? `${log.tx_hash.slice(0, 10)}…` : '—'}
      </span>
      {/* ANOMALY */}
      <span className={`text-xs font-mono font-semibold ${log.is_anomaly ? 'text-red-400' : 'text-green-400'}`}>
        {log.is_anomaly ? '⚠ YES' : 'No'}
      </span>
    </motion.div>
  )
}

export default function ForensicReport() {
  const [filters, setFilters] = useState({ severity: '', threat_label: '', user_id: '' })
  const [logs, setLogs] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  const reportRef = useRef(null)

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const params = { limit: 200, ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)) }
      const res = await getLogs(params)
      setLogs(res.data.logs || [])
      setTotal(res.data.total || 0)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const exportPDF = async () => {
    setExporting(true)
    try {
      const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
      const pageW = pdf.internal.pageSize.getWidth()
      const pageH = pdf.internal.pageSize.getHeight()

      // Header
      pdf.setFillColor(10, 10, 15)
      pdf.rect(0, 0, pageW, pageH, 'F')
      pdf.setTextColor(0, 245, 255)
      pdf.setFontSize(20)
      pdf.setFont('helvetica', 'bold')
      pdf.text('CyberAudit — Forensic Security Report', 15, 20)
      pdf.setFontSize(9)
      pdf.setTextColor(100, 116, 139)
      pdf.text(`Generated: ${new Date().toLocaleString()} | Events: ${logs.length} / ${total} total`, 15, 28)

      // Summary stats
      const critical = logs.filter(l => l.severity === 'CRITICAL').length
      const anomalies = logs.filter(l => l.is_anomaly).length
      const avgRisk = logs.length ? Math.round(logs.reduce((s, l) => s + (l.risk_score || 0), 0) / logs.length) : 0

      pdf.setTextColor(255, 255, 255)
      pdf.setFontSize(10)
      pdf.text(`Total Events: ${logs.length}`, 15, 38)
      pdf.setTextColor(255, 0, 60)
      pdf.text(`Critical: ${critical}`, 70, 38)
      pdf.setTextColor(139, 92, 246)
      pdf.text(`Anomalies: ${anomalies}`, 120, 38)
      pdf.setTextColor(255, 215, 0)
      pdf.text(`Avg Risk: ${avgRisk}`, 175, 38)

      // Table header
      pdf.setFillColor(17, 17, 40)
      pdf.rect(10, 44, pageW - 20, 8, 'F')
      pdf.setTextColor(0, 245, 255)
      pdf.setFontSize(8)
      pdf.setFont('helvetica', 'bold')
      const cols = ['#', 'Timestamp', 'User', 'IP', 'Event Type', 'Severity', 'Risk', 'Threat', 'TX Hash', 'Anomaly']
      const colX = [12, 22, 60, 95, 130, 165, 185, 200, 220, 258]
      cols.forEach((c, i) => pdf.text(c, colX[i], 50))

      // Rows
      pdf.setFont('helvetica', 'normal')
      let y = 57
      logs.forEach((log, idx) => {
        if (y > pageH - 15) { pdf.addPage(); pdf.setFillColor(10,10,15); pdf.rect(0,0,pageW,pageH,'F'); y = 15 }
        const bg = idx % 2 === 0 ? [13, 13, 24] : [17, 17, 40]
        pdf.setFillColor(...bg)
        pdf.rect(10, y - 4, pageW - 20, 7, 'F')

        const sevColor = { CRITICAL: [255,0,60], HIGH: [255,107,0], MEDIUM: [255,215,0], LOW: [0,255,135], INFO: [96,165,250] }
        pdf.setTextColor(148, 163, 184)
        pdf.setFontSize(7)

        const ts = log.created_at ? new Date(log.created_at).toLocaleString('en-US', { month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' }) : '—'
        pdf.text(String(idx + 1), colX[0], y)
        pdf.text(ts, colX[1], y)
        pdf.text((log.user_id || '').slice(0, 14), colX[2], y)
        pdf.text((log.source_ip || '').slice(0, 15), colX[3], y)
        pdf.text((log.event_type || '').replace(/_/g,' ').slice(0, 18), colX[4], y)

        const [r, g, b] = sevColor[log.severity] || [96,165,250]
        pdf.setTextColor(r, g, b)
        pdf.text(log.severity || '—', colX[5], y)

        pdf.setTextColor(255, 215, 0)
        pdf.text(String(log.risk_score || 0), colX[6], y)

        pdf.setTextColor(148, 163, 184)
        pdf.text(log.threat_label || '—', colX[7], y)
        pdf.text(log.tx_hash ? log.tx_hash.slice(0, 14) + '…' : '—', colX[8], y)
        pdf.setTextColor(log.is_anomaly ? 255 : 0, log.is_anomaly ? 0 : 200, 0)
        pdf.text(log.is_anomaly ? 'YES' : 'No', colX[9], y)

        y += 7
      })

      // Footer
      pdf.setTextColor(100, 116, 139)
      pdf.setFontSize(7)
      pdf.text('CyberAudit AI Blockchain System — Tamper-Proof Audit Log', 15, pageH - 8)

      pdf.save(`forensic_report_${Date.now()}.pdf`)
    } catch (e) {
      console.error('PDF export error:', e)
    } finally {
      setExporting(false)
    }
  }

  const criticalCount = logs.filter(l => l.severity === 'CRITICAL').length
  const anomalyCount = logs.filter(l => l.is_anomaly).length
  const avgRisk = logs.length ? Math.round(logs.reduce((s, l) => s + (l.risk_score || 0), 0) / logs.length) : 0

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text-cyan">Forensic Report</h1>
          <p className="text-cyber-textDim text-sm mt-1">Filter, analyze, and export blockchain-verified audit logs</p>
        </div>
        <div className="flex gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
            onClick={fetchLogs}
            disabled={loading}
            className="btn-cyber flex items-center gap-2 disabled:opacity-40"
          >
            {loading ? <Loader size={14} className="animate-spin" /> : <Filter size={14} />}
            Apply Filters
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
            onClick={exportPDF}
            disabled={exporting || logs.length === 0}
            className="btn-cyber-purple flex items-center gap-2 disabled:opacity-40"
          >
            {exporting ? <Loader size={14} className="animate-spin" /> : <Download size={14} />}
            Export PDF
          </motion.button>
        </div>
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card border-glow-purple p-5"
      >
        <h3 className="text-cyber-textDim text-xs uppercase tracking-wider mb-4 font-semibold">Filters</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-cyber-textDim block mb-1.5">Severity</label>
            <select
              className="input-cyber"
              value={filters.severity}
              onChange={e => setFilters(f => ({ ...f, severity: e.target.value }))}
            >
              {SEVERITY_OPTIONS.map(s => <option key={s} value={s}>{s || 'All Severities'}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-cyber-textDim block mb-1.5">Threat Label</label>
            <select
              className="input-cyber"
              value={filters.threat_label}
              onChange={e => setFilters(f => ({ ...f, threat_label: e.target.value }))}
            >
              {THREAT_OPTIONS.map(s => <option key={s} value={s}>{s || 'All Threats'}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-cyber-textDim block mb-1.5">User ID</label>
            <input
              className="input-cyber"
              placeholder="e.g. alice.smith"
              value={filters.user_id}
              onChange={e => setFilters(f => ({ ...f, user_id: e.target.value }))}
            />
          </div>
        </div>
      </motion.div>

      {/* Summary stats */}
      {logs.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Showing', value: logs.length, sublabel: `of ${total} total`, color: '#00f5ff', icon: FileText },
            { label: 'Critical', value: criticalCount, sublabel: 'severity', color: '#ff003c', icon: Shield },
            { label: 'Anomalies', value: anomalyCount, sublabel: 'ML detected', color: '#8b5cf6', icon: Hash },
            { label: 'Avg Risk', value: avgRisk, sublabel: '0-100 scale', color: '#ffd700', icon: Clock },
          ].map(s => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="stat-card"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-cyber-textDim text-xs uppercase tracking-wider">{s.label}</p>
                  <p className="text-3xl font-bold mt-1" style={{ color: s.color }}>{s.value}</p>
                  <p className="text-cyber-textDim text-xs mt-1">{s.sublabel}</p>
                </div>
                <div className="p-2 rounded-xl" style={{ background: s.color + '18', border: `1px solid ${s.color}30` }}>
                  <s.icon size={18} style={{ color: s.color }} />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Log table */}
      <div ref={reportRef} className="glass-card border-glow-cyan p-5">
        {/* Column headers */}
        {logs.length > 0 && (
          <div
            className="grid items-center gap-4 pb-2 mb-2 border-b border-cyber-border text-xs font-semibold text-cyber-textDim uppercase tracking-wider"
            style={{ gridTemplateColumns: COLS }}
          >
            <span>Event</span>
            <span>Severity</span>
            <span>Risk</span>
            <span>Threat</span>
            <span>TX Hash</span>
            <span>Anomaly</span>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-40 text-cyber-textDim">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-cyan mr-3" />
            Fetching logs…
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-16 text-cyber-textDim">
            <FileText size={40} className="mx-auto mb-3 opacity-20" />
            <p>Apply filters and click <strong>Apply Filters</strong> to load events</p>
          </div>
        ) : (
          <div className="max-h-[500px] overflow-y-auto">
            {logs.map((log, i) => <LogReportRow key={log._id || i} log={log} index={i} />)}
          </div>
        )}
      </div>
    </div>
  )
}
