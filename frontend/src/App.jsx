import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster, toast } from 'react-hot-toast'
import Navbar from './components/Navbar'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AIAnalytics from './pages/AIAnalytics'
import BlockchainVerifier from './pages/BlockchainVerifier'
import BehavioralProfiler from './pages/BehavioralProfiler'
import ForensicReport from './pages/ForensicReport'
import Settings from './pages/Settings'

/** Wait up to `ms` milliseconds for MetaMask to inject window.ethereum */
async function waitForEthereum(ms = 1500) {
  if (window.ethereum) return window.ethereum
  return new Promise((resolve) => {
    const t = setTimeout(() => resolve(null), ms)
    window.addEventListener('ethereum#initialized', () => {
      clearTimeout(t)
      resolve(window.ethereum)
    }, { once: true })
  })
}

export default function App() {
  const [wallet, setWallet] = useState(null)

  // Restore wallet if already connected
  useEffect(() => {
    waitForEthereum(800).then(eth => {
      if (!eth) return
      eth.request({ method: 'eth_accounts' }).then(accounts => {
        if (accounts?.length) setWallet(accounts[0])
      })
      eth.on('accountsChanged', (accounts) => {
        setWallet(accounts[0] || null)
        if (!accounts[0]) toast('Wallet disconnected', { icon: '🔌' })
      })
    })
  }, [])

  const connectWallet = async () => {
    const eth = await waitForEthereum(1500)
    if (!eth) {
      toast.error('MetaMask not detected — please install the MetaMask extension and refresh.', { duration: 5000 })
      return
    }
    try {
      // Ask MetaMask to switch to / add the Hardhat local network
      try {
        await eth.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: '0x7A69' }], // 31337 in hex
        })
      } catch (switchErr) {
        // Chain not yet added — add it
        if (switchErr.code === 4902) {
          await eth.request({
            method: 'wallet_addEthereumChain',
            params: [{
              chainId: '0x7A69',
              chainName: 'Hardhat Local',
              rpcUrls: ['http://127.0.0.1:8545'],
              nativeCurrency: { name: 'Ether', symbol: 'ETH', decimals: 18 },
            }],
          })
        }
      }
      const accounts = await eth.request({ method: 'eth_requestAccounts' })
      setWallet(accounts[0])
      toast.success(`Connected: ${accounts[0].slice(0,6)}…${accounts[0].slice(-4)}`)
    } catch (e) {
      if (e.code === 4001) {
        toast.error('Connection rejected by user')
      } else {
        console.error('Wallet connect failed:', e)
        toast.error('Connection failed: ' + e.message)
      }
    }
  }

  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(17,17,40,0.95)',
            border: '1px solid rgba(0,245,255,0.2)',
            color: '#e2e8f0',
            fontFamily: 'Inter, sans-serif',
            fontSize: '13px',
            backdropFilter: 'blur(16px)',
          },
        }}
      />
      <Navbar wallet={wallet} onConnect={connectWallet} />
      <Layout>
        <Routes>
          <Route path="/"           element={<Dashboard />} />
          <Route path="/analytics"  element={<AIAnalytics />} />
          <Route path="/verify"     element={<BlockchainVerifier />} />
          <Route path="/profile"    element={<BehavioralProfiler />} />
          <Route path="/forensics"  element={<ForensicReport />} />
          <Route path="/settings"   element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
