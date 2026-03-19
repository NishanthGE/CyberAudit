import { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Mail, MessageSquare, Bell, Shield,
         Save, CheckCircle, AlertTriangle, Clock, Zap } from 'lucide-react'
import { getSettings, saveSettings, getAlertHistory } from '../api/client'

const SEVERITY_LEVELS = ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

const SEV_COLOR = {
  CRITICAL: '#ff003c', HIGH: '#ff6b00', MEDIUM: '#ffd700', LOW: '#00ff87', INFO: '#60a5fa'
}

const CHANNEL_ICONS = { email: Mail, slack: MessageSquare }

export default function Settings() {
  const [config,  setConfig]  = useState(null)
  const [history, setHistory] = useState([])
  const [saving,  setSaving]  = useState(false)
  const [saved,   setSaved]   = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getSettings(), getAlertHistory(20)])
      .then(([sRes, hRes]) => {
        setConfig(sRes.data)
        setHistory(hRes.data.alerts || [])
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await saveSettings(config)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (e) {
      alert('Save failed: ' + (e?.response?.data?.detail || e.message))
    } finally {
      setSaving(false)
    }
  }

  const set = (key, val) => setConfig(prev => ({ ...prev, [key]: val }))

  if (loading || !config) return (
    <div style={pageStyle}>
      <p style={{ color: '#334155', textAlign: 'center', paddingTop: 80 }}>Loading settings…</p>
    </div>
  )

  return (
    <div style={pageStyle}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={iconBubble('#8b5cf6')}><SettingsIcon size={18} color="#8b5cf6" /></div>
          <div>
            <h1 style={{ margin: 0, color: '#f1f5f9', fontSize: 22, fontWeight: 700 }}>Alert Settings</h1>
            <p style={{ margin: '2px 0 0', color: '#475569', fontSize: 13 }}>
              Configure real-time email and Slack security alerts
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>

        {/* ── Thresholds ─────────────────────────────────────────── */}
        <Card title="Alert Thresholds" icon={<Shield size={16} color="#00c8ff" />}>
          <Label>Minimum Severity to Alert</Label>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 20 }}>
            {SEVERITY_LEVELS.map(s => (
              <button key={s} onClick={() => set('min_severity', s)} style={{
                padding: '6px 14px', borderRadius: 6, fontSize: 11, fontWeight: 700,
                cursor: 'pointer', transition: 'all .15s',
                border: `1px solid ${config.min_severity === s ? SEV_COLOR[s] : '#1e293b'}`,
                background: config.min_severity === s ? `${SEV_COLOR[s]}20` : 'transparent',
                color: config.min_severity === s ? SEV_COLOR[s] : '#64748b',
              }}>{s}</button>
            ))}
          </div>

          <Label>Risk Score Threshold: <span style={{ color: '#ffd700' }}>{config.risk_threshold}</span></Label>
          <input
            type="range" min={0} max={100} value={config.risk_threshold}
            onChange={e => set('risk_threshold', Number(e.target.value))}
            style={{ width: '100%', accentColor: '#00c8ff', marginBottom: 8 }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#334155', fontSize: 10 }}>
            <span>0 — Alert everything</span><span>100 — Never alert</span>
          </div>

          <div style={{ marginTop: 20 }}>
            <p style={{ color: '#475569', fontSize: 11, lineHeight: 1.7, margin: 0 }}>
              Alerts fire when: <strong style={{ color: '#ffffff' }}>severity ≥ {config.min_severity}</strong>,
              or <strong style={{ color: '#ffd700' }}>risk score &gt; {config.risk_threshold}</strong>,
              or AI anomaly on MEDIUM+ event, or same IP fires 5+ events/min,
              or same user fires 3+ HIGH in 5 min.
              <br />10-minute cooldown prevents duplicate alerts.
            </p>
          </div>
        </Card>

        {/* ── Email ──────────────────────────────────────────────── */}
        <Card title="Email Alerts" icon={<Mail size={16} color="#00c8ff" />}>
          <Toggle
            label="Enable Email Alerts"
            value={config.email_enabled}
            onChange={v => set('email_enabled', v)}
          />
          <Label>Your Email Address (recipient)</Label>
          <Input
            placeholder="you@gmail.com"
            value={config.smtp_user || ''}
            onChange={e => set('smtp_user', e.target.value)}
            disabled={!config.email_enabled}
          />
          <div style={noteBox}>
            <p style={{ margin: 0, color: '#64748b', fontSize: 11, lineHeight: 1.8 }}>
              Uses Gmail SMTP. Required in <code style={code}>backend/.env</code>:
            </p>
            <pre style={{ ...code, display: 'block', marginTop: 6, padding: '8px 10px',
                          background: '#0d0d18', borderRadius: 6, fontSize: 10 }}>{
`SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx`}</pre>
            <p style={{ margin: '6px 0 0', color: '#475569', fontSize: 10 }}>
              Get App Password: Google Account → Security → 2-Step Verification → App passwords → Select app: Mail
            </p>
          </div>
        </Card>

        {/* ── Slack ──────────────────────────────────────────────── */}
        <Card title="Slack Alerts" icon={<MessageSquare size={16} color="#00c8ff" />}>
          <Toggle
            label="Enable Slack Alerts"
            value={config.slack_enabled}
            onChange={v => set('slack_enabled', v)}
          />
          <Label>Slack Webhook URL</Label>
          <Input
            placeholder="https://hooks.slack.com/services/T.../B.../..."
            value={config.slack_webhook_url || ''}
            onChange={e => set('slack_webhook_url', e.target.value)}
            disabled={!config.slack_enabled}
          />
          <div style={noteBox}>
            <p style={{ margin: 0, color: '#64748b', fontSize: 11, lineHeight: 1.8 }}>
              Get Webhook URL: Slack → Apps → Incoming Webhooks → Add to Slack → 
              Choose channel → Copy Webhook URL
            </p>
            <p style={{ margin: '6px 0 0', color: '#475569', fontSize: 10 }}>
              Messages include Block Kit with severity color, event details, and dashboard link.
            </p>
          </div>
        </Card>

        {/* ── Trigger Rules Summary ──────────────────────────────── */}
        <Card title="Trigger Rules" icon={<Bell size={16} color="#00c8ff" />}>
          {[
            ['Severity Alert',     `Severity ≥ ${config.min_severity} → always alert`],
            ['Risk Score Alert',   `Risk score > ${config.risk_threshold} → alert`],
            ['Anomaly Alert',      'AI anomaly + MEDIUM/HIGH/CRITICAL → alert'],
            ['Rate Alert',         '5+ events from same IP in 60 seconds'],
            ['User Alert',         '3+ HIGH events from same user in 5 minutes'],
            ['Cooldown',           '10 minutes per (IP + event type) pair'],
          ].map(([name, desc]) => (
            <div key={name} style={{
              display: 'flex', gap: 10, alignItems: 'flex-start',
              marginBottom: 10, padding: '8px 12px',
              background: 'rgba(0,200,255,0.04)', borderRadius: 8,
              border: '1px solid rgba(0,200,255,0.1)',
            }}>
              <Zap size={12} color="#00c8ff" style={{ marginTop: 3, flexShrink: 0 }} />
              <div>
                <p style={{ margin: 0, color: '#e2e8f0', fontSize: 12, fontWeight: 600 }}>{name}</p>
                <p style={{ margin: 0, color: '#64748b', fontSize: 11 }}>{desc}</p>
              </div>
            </div>
          ))}
        </Card>
      </div>

      {/* Save Button */}
      <div style={{ marginTop: 20, display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
        {saved && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#00ff87', fontSize: 13 }}>
            <CheckCircle size={15} /> Settings saved!
          </div>
        )}
        <button onClick={handleSave} disabled={saving} style={{
          padding: '10px 28px', borderRadius: 8, fontWeight: 700, fontSize: 13,
          cursor: saving ? 'default' : 'pointer', transition: 'all .15s',
          background: saving ? '#1e293b' : 'linear-gradient(135deg,#00c8ff,#8b5cf6)',
          color: 'white', border: 'none',
        }}>
          <Save size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
          {saving ? 'Saving…' : 'Save Settings'}
        </button>
      </div>

      {/* ── Alert History ─────────────────────────────────────────── */}
      <div style={{ marginTop: 32 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <Clock size={16} color="#00c8ff" />
          <h2 style={{ margin: 0, color: '#f1f5f9', fontSize: 16, fontWeight: 700 }}>
            Alert History
          </h2>
          <span style={{
            background: 'rgba(0,200,255,0.1)', border: '1px solid rgba(0,200,255,0.3)',
            borderRadius: 12, padding: '2px 10px', fontSize: 11, color: '#00c8ff',
          }}>Last 20</span>
        </div>

        {history.length === 0 ? (
          <div style={{
            background: 'rgba(255,255,255,0.02)', border: '1px solid #1e293b',
            borderRadius: 12, padding: '40px 24px', textAlign: 'center',
          }}>
            <Bell size={32} color="#1e293b" style={{ marginBottom: 12 }} />
            <p style={{ color: '#334155', margin: 0, fontSize: 13 }}>
              No alerts fired yet. Configure email or Slack above and run the simulation.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {history.map((alert, i) => {
              const color = SEV_COLOR[alert.severity] || '#60a5fa'
              return (
                <div key={i} style={{
                  background: 'rgba(255,255,255,0.02)',
                  border: `1px solid ${color}30`,
                  borderLeft: `3px solid ${color}`,
                  borderRadius: 10, padding: '12px 16px',
                  display: 'grid', gridTemplateColumns: '1fr auto', gap: 12, alignItems: 'start',
                }}>
                  <div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
                      <span style={{
                        background: `${color}20`, color, border: `1px solid ${color}50`,
                        borderRadius: 4, padding: '2px 8px', fontSize: 10, fontWeight: 700,
                      }}>{alert.severity}</span>
                      <span style={{ color: '#e2e8f0', fontSize: 12, fontWeight: 600 }}>
                        {(alert.event_type || '').replace(/_/g, ' ').toUpperCase()}
                      </span>
                    </div>
                    <p style={{ margin: 0, color: '#64748b', fontSize: 11 }}>
                      <strong style={{ color: '#94a3b8' }}>{alert.user_id}</strong>
                      {' '} from {' '}
                      <code style={{ color: '#00c8ff', fontSize: 10 }}>{alert.source_ip}</code>
                      {' '} · Risk: <strong style={{ color: '#ffd700' }}>{alert.risk_score}</strong>
                    </p>
                    {(alert.reasons || []).map((r, ri) => (
                      <p key={ri} style={{ margin: '4px 0 0', color: '#475569', fontSize: 10 }}>↳ {r}</p>
                    ))}
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ margin: 0, color: '#334155', fontSize: 10 }}>
                      {alert.fired_at ? new Date(alert.fired_at).toLocaleTimeString() : ''}
                    </p>
                    <div style={{ display: 'flex', gap: 4, marginTop: 6, justifyContent: 'flex-end' }}>
                      {(alert.channels || []).map(ch => {
                        const Icon = CHANNEL_ICONS[ch] || Bell
                        return (
                          <span key={ch} style={{
                            background: 'rgba(0,200,255,0.1)',
                            border: '1px solid rgba(0,200,255,0.2)',
                            borderRadius: 4, padding: '2px 6px',
                            display: 'flex', alignItems: 'center', gap: 3,
                          }}>
                            <Icon size={9} color="#00c8ff" />
                            <span style={{ color: '#00c8ff', fontSize: 9, textTransform: 'capitalize' }}>{ch}</span>
                          </span>
                        )
                      })}
                    </div>
                    {alert.is_anomaly && (
                      <div style={{ display: 'flex', gap: 4, alignItems: 'center', marginTop: 4, justifyContent: 'flex-end' }}>
                        <AlertTriangle size={10} color="#ffd700" />
                        <span style={{ color: '#ffd700', fontSize: 9 }}>ANOMALY</span>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Shared sub-components ──────────────────────────────────────────────────────

function Card({ title, icon, children }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.02)',
      border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 14, padding: '20px 20px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 18 }}>
        {icon}
        <h3 style={{ margin: 0, color: '#f1f5f9', fontSize: 13, fontWeight: 700 }}>{title}</h3>
      </div>
      {children}
    </div>
  )
}

function Toggle({ label, value, onChange }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      marginBottom: 16, padding: '10px 14px',
      background: 'rgba(0,200,255,0.04)', borderRadius: 8,
      border: '1px solid rgba(0,200,255,0.1)',
    }}>
      <span style={{ color: '#e2e8f0', fontSize: 13 }}>{label}</span>
      <button onClick={() => onChange(!value)} style={{
        width: 44, height: 24, borderRadius: 12, border: 'none', cursor: 'pointer',
        background: value ? 'linear-gradient(135deg,#00c8ff,#8b5cf6)' : '#1e293b',
        position: 'relative', transition: 'all .2s',
      }}>
        <span style={{
          position: 'absolute', top: 3, left: value ? 22 : 3,
          width: 18, height: 18, borderRadius: '50%',
          background: 'white', transition: 'left .2s',
        }} />
      </button>
    </div>
  )
}

function Label({ children }) {
  return <p style={{ margin: '0 0 6px', color: '#64748b', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{children}</p>
}

function Input({ disabled, ...props }) {
  return (
    <input {...props} style={{
      width: '100%', padding: '9px 12px', borderRadius: 8, fontSize: 12, marginBottom: 14,
      background: disabled ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.4)',
      border: '1px solid #1e293b', color: disabled ? '#334155' : '#e2e8f0',
      outline: 'none', boxSizing: 'border-box', fontFamily: 'monospace',
      cursor: disabled ? 'not-allowed' : 'text',
    }} />
  )
}

const pageStyle  = { padding: '24px', maxWidth: 1100, margin: '0 auto' }
const noteBox    = { background: 'rgba(0,0,0,0.3)', border: '1px solid #1e293b', borderRadius: 8, padding: '10px 12px', marginTop: 4 }
const code       = { fontFamily: 'monospace', fontSize: 11, color: '#94a3b8' }
const iconBubble = (c) => ({
  width: 38, height: 38, borderRadius: '50%',
  background: `${c}15`, border: `1px solid ${c}40`,
  display: 'flex', alignItems: 'center', justifyContent: 'center',
})
