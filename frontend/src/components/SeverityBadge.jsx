export const SEVERITY_CONFIG = {
  CRITICAL: { label: 'CRITICAL', cls: 'badge-critical', dot: 'bg-red-400',    glow: 'shadow-cyber-red' },
  HIGH:     { label: 'HIGH',     cls: 'badge-high',     dot: 'bg-orange-400', glow: '' },
  MEDIUM:   { label: 'MEDIUM',   cls: 'badge-medium',   dot: 'bg-yellow-400', glow: '' },
  LOW:      { label: 'LOW',      cls: 'badge-low',      dot: 'bg-green-400',  glow: '' },
  INFO:     { label: 'INFO',     cls: 'badge-info',     dot: 'bg-blue-400',   glow: '' },
}

export default function SeverityBadge({ severity, pulse = false }) {
  const cfg = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.INFO
  return (
    <span className={`${cfg.cls} inline-flex items-center gap-1.5`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} ${pulse && severity === 'CRITICAL' ? 'animate-pulse' : ''}`} />
      {cfg.label}
    </span>
  )
}
