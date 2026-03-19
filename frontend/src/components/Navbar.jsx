import { NavLink, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Activity, BarChart2, Lock, User, FileText, Wallet, Settings } from 'lucide-react'
import { useState, useEffect } from 'react'

const NAV_ITEMS = [
  { path: '/',            label: 'Live Feed',   icon: Activity },
  { path: '/analytics',  label: 'AI Analytics',icon: BarChart2 },
  { path: '/verify',     label: 'Verifier',    icon: Lock },
  { path: '/profile',    label: 'Profiler',    icon: User },
  { path: '/forensics',  label: 'Forensics',   icon: FileText },
  { path: '/settings',   label: 'Settings',    icon: Settings },
]

export default function Navbar({ wallet, onConnect }) {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  const timeStr = time.toLocaleTimeString('en-US', { hour12: false })
  const dateStr = time.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-16">
      {/* Glassy bar */}
      <div
        className="h-full flex items-center px-6 gap-4"
        style={{
          background: 'rgba(10,10,15,0.85)',
          borderBottom: '1px solid rgba(0,245,255,0.12)',
          backdropFilter: 'blur(20px)',
        }}
      >
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-2.5 mr-4 flex-shrink-0">
          <motion.div
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #00f5ff30, #8b5cf630)', border: '1px solid #00f5ff40' }}
          >
            <Shield size={16} className="text-cyber-cyan" />
          </motion.div>
          <span className="font-bold text-base gradient-text-cyan tracking-wide hidden sm:block">
            CyberAudit
          </span>
        </NavLink>

        {/* Nav links */}
        <div className="flex items-center gap-1 flex-1 overflow-x-auto no-scrollbar">
          {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 whitespace-nowrap
                ${isActive
                  ? 'text-cyber-cyan bg-cyber-cyan/10 border border-cyber-cyan/30'
                  : 'text-cyber-textDim hover:text-cyber-text hover:bg-white/5'
                }`
              }
            >
              <Icon size={14} />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>

        {/* Live clock */}
        <div className="hidden lg:flex flex-col items-end mr-3 flex-shrink-0">
          <span className="font-mono text-cyber-cyan text-sm font-semibold tracking-widest">{timeStr}</span>
          <span className="font-mono text-cyber-textDim text-xs">{dateStr}</span>
        </div>

        {/* Wallet button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onConnect}
          className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold flex-shrink-0 transition-all duration-200"
          style={{
            background: wallet ? 'rgba(0,255,135,0.08)' : 'rgba(0,245,255,0.08)',
            border: wallet ? '1px solid rgba(0,255,135,0.3)' : '1px solid rgba(0,245,255,0.3)',
            color: wallet ? '#00ff87' : '#00f5ff',
          }}
        >
          <Wallet size={14} />
          <span className="hidden md:block">
            {wallet ? `${wallet.slice(0, 6)}…${wallet.slice(-4)}` : 'Connect'}
          </span>
          {wallet && (
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          )}
        </motion.button>
      </div>

      {/* Animated scan line under navbar */}
      <motion.div
        className="h-px"
        style={{ background: 'linear-gradient(90deg, transparent, #00f5ff, #8b5cf6, transparent)' }}
        animate={{ opacity: [0.3, 0.8, 0.3] }}
        transition={{ duration: 3, repeat: Infinity }}
      />
    </nav>
  )
}
