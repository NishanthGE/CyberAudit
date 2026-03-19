export default function RiskScoreBar({ score }) {
  const pct = Math.min(Math.max(score, 0), 100)
  const color =
    pct >= 85 ? '#ff003c' :
    pct >= 65 ? '#ff6b00' :
    pct >= 40 ? '#ffd700' :
    pct >= 15 ? '#00ff87' :
               '#60a5fa'

  const glow =
    pct >= 85 ? 'rgba(255,0,60,0.6)' :
    pct >= 65 ? 'rgba(255,107,0,0.5)' :
    pct >= 40 ? 'rgba(255,215,0,0.4)' :
               'rgba(0,255,135,0.3)'

  return (
    <div className="flex items-center gap-2 min-w-0">
      <div className="flex-1 h-1.5 rounded-full bg-cyber-border overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, background: color, boxShadow: `0 0 6px ${glow}` }}
        />
      </div>
      <span className="font-mono text-xs font-semibold w-7 text-right" style={{ color }}>
        {score}
      </span>
    </div>
  )
}
