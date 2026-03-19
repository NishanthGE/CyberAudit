import { useState, useEffect, useRef } from 'react'
import { X, Brain, AlertTriangle, Shield, Zap, Target, ChevronRight } from 'lucide-react'
import { explainLog } from '../api/client'

const SECTIONS = [
  { key: 'summary',              icon: Brain,         label: 'Summary',               color: '#00c8ff' },
  { key: 'why_flagged',          icon: AlertTriangle,  label: 'Why It Was Flagged',    color: '#ffd700' },
  { key: 'attack_pattern',       icon: Target,         label: 'Attack Pattern',        color: '#f97316' },
  { key: 'mitre_technique',      icon: Shield,         label: 'MITRE ATT&CK Technique',color: '#8b5cf6' },
  { key: 'recommended_action',   icon: Zap,            label: 'Recommended Action',    color: '#00ff87' },
  { key: 'confidence_reasoning', icon: ChevronRight,   label: 'Confidence Reasoning',  color: '#64748b' },
]

export default function ExplainModal({ logId, onClose }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  const [typed,   setTyped]   = useState({})   // key -> displayed chars count
  const intervalRefs = useRef({})

  // Fetch on mount
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const res = await explainLog(logId)
        if (!cancelled) {
          setData(res.data)
          setLoading(false)
          // Start typing animations
          SECTIONS.forEach(({ key }) => {
            const text = res.data[key] || ''
            let i = 0
            intervalRefs.current[key] = setInterval(() => {
              i = Math.min(i + 3, text.length)
              setTyped(prev => ({ ...prev, [key]: i }))
              if (i >= text.length) clearInterval(intervalRefs.current[key])
            }, 12)
          })
        }
      } catch (e) {
        if (!cancelled) {
          setError(e?.response?.data?.detail || 'Failed to get explanation')
          setLoading(false)
        }
      }
    })()
    return () => {
      cancelled = true
      Object.values(intervalRefs.current).forEach(clearInterval)
    }
  }, [logId])

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(0,0,0,0.75)',
        backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '24px',
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          width: '100%', maxWidth: '720px', maxHeight: '85vh',
          background: 'rgba(13,13,24,0.97)',
          border: '1px solid rgba(0,200,255,0.3)',
          borderRadius: '16px',
          boxShadow: '0 0 60px rgba(0,200,255,0.15)',
          display: 'flex', flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid rgba(0,200,255,0.15)',
          display: 'flex', alignItems: 'center', gap: '12px',
          background: 'rgba(0,200,255,0.05)',
        }}>
          <div style={{
            width: 36, height: 36, borderRadius: '50%',
            background: 'rgba(0,200,255,0.15)',
            border: '1px solid rgba(0,200,255,0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Brain size={18} color="#00c8ff" />
          </div>
          <div>
            <h2 style={{ margin: 0, color: '#00c8ff', fontSize: '16px', fontWeight: 700 }}>
              AI Threat Explanation
            </h2>
            <p style={{ margin: 0, color: '#64748b', fontSize: '11px', fontFamily: 'monospace' }}>
              Powered by Claude claude-sonnet-4-20250514 &nbsp;|&nbsp; Log ID: {logId?.slice(-12)}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              marginLeft: 'auto', background: 'transparent', border: 'none',
              cursor: 'pointer', color: '#64748b', padding: '4px',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div style={{ overflowY: 'auto', padding: '20px 24px', flex: 1 }}>

          {loading && (
            <div style={{ textAlign: 'center', padding: '48px 0' }}>
              <div style={{
                display: 'inline-flex', gap: '8px', alignItems: 'center',
                color: '#00c8ff', fontSize: '14px',
              }}>
                <TypingDots />
                Analyzing with Claude AI...
              </div>
              <p style={{ color: '#334155', fontSize: '12px', marginTop: '12px' }}>
                This may take 5-10 seconds on first request. Cached for future views.
              </p>
            </div>
          )}

          {error && (
            <div style={{
              background: 'rgba(255,0,60,0.08)', border: '1px solid rgba(255,0,60,0.3)',
              borderRadius: '10px', padding: '16px 20px', color: '#ff6b6b', fontSize: '13px',
            }}>
              <strong>Error:</strong> {error}
            </div>
          )}

          {data && !loading && SECTIONS.map(({ key, icon: Icon, label, color }) => {
            const fullText = data[key] || 'N/A'
            const displayText = fullText.slice(0, typed[key] ?? fullText.length)
            const isTyping = (typed[key] ?? fullText.length) < fullText.length

            return (
              <div key={key} style={{
                marginBottom: '16px',
                background: 'rgba(255,255,255,0.02)',
                border: `1px solid ${color}25`,
                borderRadius: '10px',
                overflow: 'hidden',
              }}>
                <div style={{
                  padding: '10px 16px',
                  background: `${color}10`,
                  borderBottom: `1px solid ${color}20`,
                  display: 'flex', alignItems: 'center', gap: '8px',
                }}>
                  <Icon size={14} color={color} />
                  <span style={{ color, fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px' }}>
                    {label}
                  </span>
                  {key === 'mitre_technique' && fullText !== 'N/A' && (
                    <span style={{
                      marginLeft: 'auto', background: `${color}20`,
                      border: `1px solid ${color}40`, borderRadius: '4px',
                      padding: '2px 8px', fontSize: '10px', color,
                      fontFamily: 'monospace',
                    }}>
                      MITRE ATT&CK
                    </span>
                  )}
                </div>
                <div style={{
                  padding: '14px 16px', color: '#cbd5e1', fontSize: '13px',
                  lineHeight: '1.7', minHeight: '40px', fontFamily: key === 'mitre_technique' ? 'monospace' : 'inherit',
                }}>
                  {displayText}
                  {isTyping && <span style={{ color, opacity: 0.8 }}>▋</span>}
                </div>
              </div>
            )
          })}

          {data?.cached && (
            <p style={{ color: '#334155', fontSize: '11px', textAlign: 'center', marginTop: '8px' }}>
              ⚡ Served from cache — no API call made
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function TypingDots() {
  return (
    <span style={{ display: 'inline-flex', gap: '4px' }}>
      {[0, 1, 2].map(i => (
        <span
          key={i}
          style={{
            width: 6, height: 6, borderRadius: '50%',
            background: '#00c8ff',
            animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
      <style>{`@keyframes pulse{0%,80%,100%{opacity:.3}40%{opacity:1}}`}</style>
    </span>
  )
}
