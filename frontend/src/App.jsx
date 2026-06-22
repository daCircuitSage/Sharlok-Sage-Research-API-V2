import { useEffect, useState } from 'react'
import { GoogleLogin } from '@react-oauth/google'
import './App.css'
import { createResearch, getStoredUser, loginWithGoogle, logoutUser, saveAuthData } from './api'

function App() {
  const [user, setUser] = useState(getStoredUser())
  const [topic, setTopic] = useState('')
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const storedHistory = localStorage.getItem('researchHistory')
    if (storedHistory) {
      setHistory(JSON.parse(storedHistory))
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('researchHistory', JSON.stringify(history))
  }, [history])

  const handleGoogleSuccess = async (response) => {
    try {
      setError('')
      const data = await loginWithGoogle(response.credential)
      saveAuthData(data)
      setUser(data.user)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Google authentication failed.')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!topic.trim()) {
      setError('Please enter a research topic.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await createResearch(topic.trim())
      const latestResult = {
        topic: response.topic,
        report: response.report,
        confidence: response.confidence
      }
      setResult(latestResult)
      setHistory((prev) => [latestResult, ...prev].slice(0, 6))
      setTopic('')
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.topic ||
          'Unable to generate research report right now.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logoutUser()
    setUser(null)
    setResult(null)
  }

  return (
    <div className="app-shell">
      <header className="top-nav">
        <div>
          <p className="eyebrow">Sharlok Sage</p>
          <h1>Research Hub</h1>
        </div>
        {user ? (
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        ) : null}
      </header>

      {!user ? (
        <section className="auth-panel">
          <div>
            <p className="eyebrow">Welcome</p>
            <h2>Sign in to start deep research</h2>
            <p className="auth-subtitle">
              Use your Google account to access the research workflow.
            </p>
          </div>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError('Google sign-in failed.')}
          />
          {error ? <p className="error-message">{error}</p> : null}
        </section>
      ) : (
        <main className="dashboard">
          <section className="input-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Research prompt</p>
                <h2>Hello, {user.first_name || user.email}</h2>
              </div>
            </div>
            <form onSubmit={handleSubmit}>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Ask anything you want researched..."
                rows="6"
              />
              <div className="form-actions">
                <button type="submit" disabled={loading}>
                  {loading ? 'Generating...' : 'Generate Research'}
                </button>
              </div>
            </form>
            {error ? <p className="error-message">{error}</p> : null}
          </section>

          <section className="results-panel">
            {result ? (
              <article className="report-card">
                <div className="report-card__header">
                  <div>
                    <p className="eyebrow">Latest report</p>
                    <h3>{result.topic}</h3>
                  </div>
                  <span className="confidence-pill">Confidence {result.confidence}</span>
                </div>
                <p className="report-text">{result.report}</p>
              </article>
            ) : (
              <div className="empty-state">
                <p className="eyebrow">Ready</p>
                <h3>Your report will appear here</h3>
              </div>
            )}

            {history.length > 0 ? (
              <div className="history-panel">
                <p className="eyebrow">Recent requests</p>
                <ul>
                  {history.map((item, index) => (
                    <li key={`${item.topic}-${index}`}>
                      <button onClick={() => setResult(item)}>
                        <span>{item.topic}</span>
                        <strong>{item.confidence}</strong>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </section>
        </main>
      )}
    </div>
  )
}

export default App
