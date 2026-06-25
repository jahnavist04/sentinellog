import { useState, useEffect } from "react"
import axios from "axios"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import "./App.css"

const API = "http://localhost:5000"

function App() {
  const [logs, setLogs] = useState([])
  const [stats, setStats] = useState({ total: 0, errors: 0, warnings: 0, info: 0, by_service: [] })
  const [search, setSearch] = useState("")
  const [levelFilter, setLevelFilter] = useState("")
  const [serviceFilter, setServiceFilter] = useState("")
  const [alert, setAlert] = useState(false)

  const fetchLogs = async () => {
    try {
      const res = search || levelFilter || serviceFilter
        ? await axios.get(`${API}/api/search`, { params: { q: search, level: levelFilter, service: serviceFilter } })
        : await axios.get(`${API}/api/logs`)
      setLogs(res.data)
    } catch (e) { console.error(e) }
  }

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API}/api/stats`)
      setStats(res.data)
      setAlert(res.data.errors > 10)
    } catch (e) { console.error(e) }
  }

  const exportLogs = () => {
    window.open(`${API}/api/export`, '_blank')
  }

  useEffect(() => {
    fetchLogs()
    fetchStats()
    const interval = setInterval(() => {
      fetchLogs()
      fetchStats()
    }, 2000)
    return () => clearInterval(interval)
  }, [search, levelFilter, serviceFilter])

  return (
    <div className="app">
      {alert && <div className="alert-bar">⚠ ALERT: High error rate detected across services</div>}

      <header>
        <div className="logo">SENTINEL<span>LOG</span></div>
        <div className="header-right">
          <span className="live">● LIVE</span>
          <button className="export-btn" onClick={exportLogs}>Export CSV</button>
        </div>
      </header>

      <div className="stats">
        <div className="stat-card total"><h2>{stats.total}</h2><p>TOTAL LOGS</p></div>
        <div className="stat-card info"><h2>{stats.info}</h2><p>INFO</p></div>
        <div className="stat-card warning"><h2>{stats.warnings}</h2><p>WARNINGS</p></div>
        <div className="stat-card error"><h2>{stats.errors}</h2><p>ERRORS</p></div>
      </div>

      <div className="chart-section">
        <h3>Logs by Service</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={stats.by_service.map(s => ({ name: s.service, count: s.count }))}>
            <XAxis dataKey="name" stroke="#666" />
            <YAxis stroke="#666" />
            <Tooltip contentStyle={{ background: '#111', border: '1px solid #333' }} />
            <Bar dataKey="count" fill="#00ff88" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="filters">
        <input
          placeholder="Search logs..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select value={levelFilter} onChange={e => setLevelFilter(e.target.value)}>
          <option value="">All Levels</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
        </select>
        <select value={serviceFilter} onChange={e => setServiceFilter(e.target.value)}>
          <option value="">All Services</option>
          <option value="ServiceA">ServiceA</option>
          <option value="ServiceB">ServiceB</option>
          <option value="ServiceC">ServiceC</option>
        </select>
      </div>

      <div className="logs-section">
        <h3>LIVE LOG FEED</h3>
        <div className="log-header">
          <span>Timestamp</span>
          <span>Level</span>
          <span>Service</span>
          <span>Message</span>
        </div>
        {logs.map(log => (
          <div key={log.id} className="log-entry">
            <span className="timestamp">{log.timestamp}</span>
            <span className={`level ${log.level}`}>{log.level}</span>
            <span className="service">{log.service}</span>
            <span className="message">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App