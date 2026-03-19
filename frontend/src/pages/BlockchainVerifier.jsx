import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Lock, Search, CheckCircle, XCircle, AlertCircle, Loader, Hash, Clock, Shield } from 'lucide-react'
import { verifyLog } from '../api/client'

function VerifyResult({ result }) {
  const isVerified = result.status === 'VERIFIED'
  const isTampered = result.status === 'TAMPERED'
  const isUnavailable = !isVerified && !isTampered

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 200, damping: 20 }}
        className={`glass-card p-8 text-center ${
          isVerified ? 'border-glow-cyan' : isTampered ? 'border-glow-red' : ''
        }`}
      >
        {/* Main status icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.15, type: 'spring', stiffness: 300 }}
          className="flex justify-center mb-4"
        >
          {isVerified ? (
            <div className="relative">
              <motion.div
                className="absolute inset-0 rounded-full"
                animate={{ scale: [1, 1.5, 1], opacity: [0.6, 0, 0.6] }}
                transition={{ duration: 2, repeat: Infinity }}
                style={{ background: 'rgba(0,245,255,0.2)' }}
              />
              <CheckCircle size={72} className="text-cyber-cyan relative z-10" strokeWidth={1.5} />
            </div>
          ) : isTampered ? (
            <div className="relative">
              <motion.div
                className="absolute inset-0 rounded-full"
                animate={{ scale: [1, 1.4, 1], opacity: [0.7, 0, 0.7] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                style={{ background: 'rgba(255,0,60,0.25)' }}
              />
              <XCircle size={72} className="text-cyber-red relative z-10" strokeWidth={1.5} />
            </div>
          ) : (
            <AlertCircle size={72} className="text-yellow-400" strokeWidth={1.5} />
          )}
        </motion.div>

        {/* Status text */}
        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className={`text-4xl font-bold font-mono mb-2 ${
            isVerified ? 'text-glow-cyan' : isTampered ? 'text-glow-red' : 'text-yellow-400'
          }`}
        >
          {isVerified ? '✅ VERIFIED' : isTampered ? '❌ TAMPERED' : `⚠ ${result.status}`}
        </motion.h2>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35 }}
          className="text-cyber-textDim text-sm mb-6"
        >
          {isVerified
            ? 'Log integrity confirmed — on-chain hash matches computed hash'
            : isTampered
            ? 'ALERT: Log has been modified since blockchain storage!'
            : result.message || 'Could not verify this log entry'}
        </motion.p>

        {/* Hash comparison */}
        {(result.recomputed_hash || result.stored_hash) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            className="text-left space-y-3 mt-4"
          >
            <div className="cyber-divider mb-4" />
            <HashRow label="Computed Hash (SHA-256)" value={result.recomputed_hash} color="#00f5ff" />
            <HashRow label="On-Chain Hash" value={result.stored_hash} color={isVerified ? '#00ff87' : '#ff003c'} />
            {result.tx_hash && <HashRow label="Transaction Hash" value={result.tx_hash} color="#8b5cf6" />}
            <div className="grid grid-cols-2 gap-3 mt-4">
              {result.risk_score != null && (
                <InfoPill icon={Shield} label="Risk Score" value={result.risk_score} />
              )}
              {result.threat_label && (
                <InfoPill icon={AlertCircle} label="Threat" value={result.threat_label} />
              )}
              {result.event_type && (
                <InfoPill icon={Lock} label="Event Type" value={result.event_type} />
              )}
              {result.user_id && (
                <InfoPill icon={Clock} label="User" value={result.user_id} />
              )}
            </div>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}

function HashRow({ label, value, color }) {
  return (
    <div className="bg-cyber-surface/60 rounded-xl p-3 border border-cyber-border">
      <p className="text-cyber-textDim text-xs mb-1">{label}</p>
      <p className="font-mono text-xs break-all" style={{ color }}>{value}</p>
    </div>
  )
}

function InfoPill({ icon: Icon, label, value }) {
  return (
    <div className="bg-cyber-surface/40 rounded-xl p-3 border border-cyber-border flex items-center gap-2">
      <Icon size={14} className="text-cyber-purple flex-shrink-0" />
      <div>
        <p className="text-cyber-textDim text-xs">{label}</p>
        <p className="text-cyber-text text-sm font-mono font-semibold">{value}</p>
      </div>
    </div>
  )
}

export default function BlockchainVerifier() {
  const [logId, setLogId] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const verify = async () => {
    const id = logId.trim()
    if (!id) return
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await verifyLog(id)
      setResult(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Verification failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold gradient-text-cyan">Blockchain Verifier</h1>
        <p className="text-cyber-textDim text-sm mt-1">
          Verify log integrity — compare off-chain hash vs on-chain proof
        </p>
      </div>

      {/* How it works */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card border-glow-purple p-5"
      >
        <h3 className="text-cyber-purple font-semibold mb-3 text-sm uppercase tracking-wider">How It Works</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          {[
            { step: '01', label: 'Enter Log ID', desc: 'Paste any log ObjectId from MongoDB' },
            { step: '02', label: 'Hash Recomputed', desc: 'SHA-256 computed from current log data' },
            { step: '03', label: 'Chain Compared', desc: 'On-chain hash fetched and compared' },
          ].map(s => (
            <div key={s.step} className="space-y-1">
              <div className="text-2xl font-bold font-mono text-cyber-cyan/40">{s.step}</div>
              <p className="text-cyber-text text-sm font-semibold">{s.label}</p>
              <p className="text-cyber-textDim text-xs">{s.desc}</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Input area */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card border-glow-cyan p-6 space-y-4"
      >
        <label className="block">
          <span className="text-cyber-textDim text-xs font-mono uppercase tracking-wider mb-2 block">
            Log ID (MongoDB ObjectId)
          </span>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Hash size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-cyber-textDim" />
              <input
                value={logId}
                onChange={e => setLogId(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && verify()}
                placeholder="e.g. 65f3a2c8e4b0123456789abc"
                className="input-cyber pl-9 font-mono"
              />
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={verify}
              disabled={loading || !logId.trim()}
              className="btn-cyber flex items-center gap-2 px-6 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? <Loader size={14} className="animate-spin" /> : <Search size={14} />}
              Verify
            </motion.button>
          </div>
        </label>

        {error && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-red-400 text-sm font-mono border border-red-500/20 rounded-lg p-3 bg-red-500/05"
          >
            ❌ {error}
          </motion.p>
        )}
      </motion.div>

      {/* Result */}
      {result && <VerifyResult result={result} />}
    </div>
  )
}
