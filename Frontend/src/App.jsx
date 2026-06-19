import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function App() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  // --- 1. HEALTH BAR LOGIC ---
  const [isBackendAlive, setIsBackendAlive] = useState(false)

  useEffect(() => {
    // Ping the backend health endpoint every 10 seconds
    const checkHealth = async () => {
      try {
        const res = await fetch('/health')
        if (res.ok) {
          setIsBackendAlive(true)
        } else {
          setIsBackendAlive(false)
        }
      } catch (error) {
        setIsBackendAlive(false)
      }
    }
    
    // Check immediately, then start interval
    checkHealth()
    const interval = setInterval(checkHealth, 10000)
    return () => clearInterval(interval)
  }, [])


  // --- 2. FORM STATE ---
  const [formData, setFormData] = useState({
    member_id: 'OPT-188646',
    date_of_birth: '1972-07-03',
    provider_npi: '1234567890',
    date_of_service: new Date().toISOString().split('T')[0],
    cpt_code: '99213, 71046'
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  // --- 3. SUBMIT LOGIC ---
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    // Format the payload exactly how the backend expects it
    const payload = {
      transaction_id: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2),
      member_id: formData.member_id,
      date_of_birth: formData.date_of_birth,
      provider_npi: formData.provider_npi,
      date_of_service: formData.date_of_service,
      proposed_cpt_codes: formData.cpt_code.split(',').map(c => c.trim()).filter(c => c.length > 0),
      diagnosis_codes: []
    }

    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/v1/eligibility', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      if (res.status === 401) {
        localStorage.removeItem('token')
        navigate('/login')
        return
      }

      const data = await res.json()

      if (!res.ok) {
        // Validation error from backend
        throw new Error(JSON.stringify(data.detail) || 'Failed to fetch')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }


  // --- 4. RENDER UI ---
  return (
    <div className="app-container">
      
      {/* HEADER & HEALTH BAR */}
      <header className="header">
        <div>
          <h2>Optum RTE Engine</h2>
          <div style={{fontSize: '0.8rem', color: '#a1a1aa'}}>Real-Time Eligibility Pre-Check</div>
        </div>
        
        <div style={{display: 'flex', alignItems: 'center', gap: '1.5rem'}}>
          <div className="health-status">
            <div className={`status-dot ${isBackendAlive ? 'active' : 'inactive'}`}></div>
            <span style={{color: isBackendAlive ? '#34d399' : '#f87171'}}>
              {isBackendAlive ? 'Backend Connected' : 'Backend Offline'}
            </span>
          </div>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <main className="main-grid">
        
        {/* LEFT: THE FORM */}
        <section className="glass-card">
          <h3 className="card-title">Patient Check-In</h3>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Member ID</label>
              <input 
                type="text" 
                name="member_id" 
                value={formData.member_id} 
                onChange={handleChange} 
                required 
              />
            </div>

            <div className="form-group">
              <label>Date of Birth</label>
              <input 
                type="date" 
                name="date_of_birth" 
                value={formData.date_of_birth} 
                onChange={handleChange} 
                required 
              />
            </div>

            <div className="form-group">
              <label>Provider NPI (10 digits)</label>
              <input 
                type="text" 
                name="provider_npi" 
                value={formData.provider_npi} 
                onChange={handleChange} 
                required 
              />
            </div>

            <div className="form-group">
              <label>Date of Service</label>
              <input 
                type="date" 
                name="date_of_service" 
                value={formData.date_of_service} 
                onChange={handleChange} 
                required 
              />
            </div>

            <div className="form-group">
              <label>Proposed CPT Codes (comma separated)</label>
              <input 
                type="text" 
                name="cpt_code" 
                value={formData.cpt_code} 
                onChange={handleChange} 
                required 
              />
            </div>

            <button type="submit" className="submit-btn" disabled={loading || !isBackendAlive}>
              {loading ? 'Running Engine...' : 'Check Eligibility'}
            </button>
            
            {error && <div className="error-text">Error: {error}</div>}
          </form>
        </section>

        {/* RIGHT: THE RESULTS */}
        <section className="glass-card">
          <h3 className="card-title">Pre-Check Results</h3>
          
          {!result && !loading && (
            <div style={{color: '#a1a1aa', textAlign: 'center', marginTop: '3rem'}}>
              Submit patient details to run a real-time eligibility scrub.
            </div>
          )}

          {loading && (
            <div style={{color: '#3b82f6', textAlign: 'center', marginTop: '3rem'}}>
              Checking databases...
            </div>
          )}

          {result && (
            <div style={{ animation: 'slideIn 0.4s ease-out' }}>
              
              {/* STATUS BANNER */}
              <div className={`banner ${result.status === 'ACTIVE' ? 'active' : 'inactive'}`}>
                {result.status === 'ACTIVE' ? '✓ COVERAGE ACTIVE' : '✗ ' + result.status}
              </div>

              {/* COVERAGE DETAILS (Only show if we have them) */}
              {result.coverage_details && (
                <div className="details-grid">
                  <div className="detail-item">
                    <div className="detail-label">Plan Name</div>
                    <div className="detail-val">{result.coverage_details.plan_name}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">Copay</div>
                    <div className="detail-val" style={{color: '#34d399'}}>${result.coverage_details.copay_amount}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">Deductible</div>
                    <div className="detail-val">${result.coverage_details.deductible_remaining}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">Out of Pocket Max</div>
                    <div className="detail-val">${result.coverage_details.out_of_pocket_max}</div>
                  </div>
                </div>
              )}

              {/* CPT SCRUBBING RESULTS */}
              {result.scrubbing_results && result.scrubbing_results.length > 0 && (
                <div style={{marginTop: '2rem'}}>
                  <h4 style={{marginBottom: '1rem', color: '#a1a1aa'}}>Scrubbing Results</h4>
                  
                  {result.scrubbing_results.map((item, index) => (
                    <div key={index} className="scrub-item">
                      <span className="scrub-code">CPT {item.cpt_code}</span>
                      
                      {/* COLOR CODED STATUS */}
                      <span className={`scrub-status ${item.result.toLowerCase()}`}>
                        {item.result === 'APPROVED' && '✓ APPROVED'}
                        {item.result === 'WARNING' && '⚠ WARNING'}
                        {item.result === 'DENIED' && '✗ DENIED'}
                      </span>
                    </div>
                  ))}
                  
                  {result.scrubbing_results[0].message && (
                    <div className="scrub-message">{result.scrubbing_results[0].message}</div>
                  )}
                </div>
              )}

            </div>
          )}
        </section>

      </main>
    </div>
  )
}

export default App
