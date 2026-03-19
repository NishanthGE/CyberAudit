import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import ParticleBackground from './ParticleBackground'

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } },
  exit:    { opacity: 0, y: -8, transition: { duration: 0.2 } },
}

export default function Layout({ children }) {
  const location = useLocation()

  return (
    <div className="relative min-h-screen bg-cyber-bg">
      <ParticleBackground />
      {/* Subtle radial glow behind content */}
      <div
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,245,255,0.06) 0%, transparent 60%), ' +
            'radial-gradient(ellipse 60% 40% at 80% 80%, rgba(139,92,246,0.05) 0%, transparent 50%)',
        }}
      />
      <AnimatePresence mode="wait">
        <motion.main
          key={location.pathname}
          variants={pageVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          className="relative z-10 pt-20 px-4 pb-10 max-w-screen-xl mx-auto"
        >
          {children}
        </motion.main>
      </AnimatePresence>
    </div>
  )
}
