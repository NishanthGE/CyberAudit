import { useEffect, useRef } from 'react'

export default function ParticleBackground() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    let animFrame
    let W, H, particles

    const PARTICLE_COUNT = 80
    const MAX_DISTANCE = 140
    const COLORS = ['#00f5ff', '#8b5cf6', '#ff003c', '#00ff87']

    function resize() {
      W = canvas.width = window.innerWidth
      H = canvas.height = window.innerHeight
    }

    function createParticles() {
      particles = Array.from({ length: PARTICLE_COUNT }, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 1.8 + 0.8,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        alpha: Math.random() * 0.5 + 0.3,
        pulse: Math.random() * Math.PI * 2,
      }))
    }

    function drawGlowCircle(x, y, r, color, alpha) {
      const grad = ctx.createRadialGradient(x, y, 0, x, y, r * 4)
      grad.addColorStop(0, color + Math.round(alpha * 255).toString(16).padStart(2, '0'))
      grad.addColorStop(1, 'transparent')
      ctx.beginPath()
      ctx.arc(x, y, r * 4, 0, Math.PI * 2)
      ctx.fillStyle = grad
      ctx.fill()

      ctx.beginPath()
      ctx.arc(x, y, r, 0, Math.PI * 2)
      ctx.fillStyle = color
      ctx.globalAlpha = alpha
      ctx.fill()
      ctx.globalAlpha = 1
    }

    function draw() {
      ctx.clearRect(0, 0, W, H)

      // Background grid
      ctx.strokeStyle = 'rgba(30,32,64,0.3)'
      ctx.lineWidth = 0.5
      const gridSize = 60
      for (let x = 0; x < W; x += gridSize) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke()
      }
      for (let y = 0; y < H; y += gridSize) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
      }

      // Update + draw particles
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy
        p.pulse += 0.02
        if (p.x < 0 || p.x > W) p.vx *= -1
        if (p.y < 0 || p.y > H) p.vy *= -1

        const pulsedAlpha = p.alpha * (0.8 + 0.2 * Math.sin(p.pulse))
        drawGlowCircle(p.x, p.y, p.r, p.color, pulsedAlpha)
      })

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i], b = particles[j]
          const dx = a.x - b.x, dy = a.y - b.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < MAX_DISTANCE) {
            const alpha = (1 - dist / MAX_DISTANCE) * 0.25
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            const gradient = ctx.createLinearGradient(a.x, a.y, b.x, b.y)
            gradient.addColorStop(0, a.color + Math.round(alpha * 255).toString(16).padStart(2, '0'))
            gradient.addColorStop(1, b.color + Math.round(alpha * 255).toString(16).padStart(2, '0'))
            ctx.strokeStyle = gradient
            ctx.lineWidth = 0.8
            ctx.stroke()
          }
        }
      }

      animFrame = requestAnimationFrame(draw)
    }

    resize()
    createParticles()
    draw()
    window.addEventListener('resize', () => { resize(); createParticles() })
    return () => {
      cancelAnimationFrame(animFrame)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.6 }}
    />
  )
}
