
import "./App.css";
import { useEffect, useState } from "react";
import axios from "axios";

const API = "https://emailspamdetection-now6.onrender.com";

function App() {
  const [token, setToken] = useState(localStorage.getItem("spam_token") || "");
  const [username, setUsername] = useState(localStorage.getItem("spam_username") || "");
  const [authMode, setAuthMode] = useState("login");
  const [form, setForm] = useState({ username: "", password: "" });

  const [email, setEmail] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const authHeaders = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const loadDashboard = async () => {
    try {
      const [historyResponse, statsResponse] = await Promise.all([
        axios.get(`${API}/history`, authHeaders),
        axios.get(`${API}/stats`, authHeaders)
      ]);

      setHistory(historyResponse.data);
      setStats(statsResponse.data);
    } catch (error) {
      setMessage(error.response?.data?.error || "Unable to load dashboard.");
    }
  };

  useEffect(() => {
    if (token) {
      loadDashboard();
    }
  }, [token]);

  const handleAuth = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      if (authMode === "register") {
        await axios.post(`${API}/register`, form);
        setMessage("Account created! Please login.");
        setAuthMode("login");
      } else {
        const response = await axios.post(`${API}/login`, form);

        localStorage.setItem("spam_token", response.data.token);
        localStorage.setItem("spam_username", response.data.username);

        setToken(response.data.token);
        setUsername(response.data.username);
        setForm({ username: "", password: "" });
        setMessage("");
      }
    } catch (error) {
      setMessage(error.response?.data?.error || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  const detectSpam = async () => {
    if (!email.trim()) {
      setMessage("Please enter an email message first.");
      return;
    }

    setLoading(true);
    setMessage("");
    setResult(null);

    try {
      const response = await axios.post(
        `${API}/predict`,
        { email },
        authHeaders
      );

      setResult(response.data);
      setEmail("");
      await loadDashboard();
    } catch (error) {
      setMessage(error.response?.data?.error || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/logout`, {}, authHeaders);
    } catch (error) {
      console.log("Logout request failed", error);
    }

    localStorage.removeItem("spam_token");
    localStorage.removeItem("spam_username");

    setToken("");
    setUsername("");
    setResult(null);
    setHistory([]);
    setStats(null);
    setMessage("You have logged out.");
  };

  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="brand-icon">✉</div>
          <h1>EmailGuard AI</h1>
          <p className="subtitle">
            Intelligent Email Spam Detection System
          </p>

          <div className="auth-tabs">
            <button
              className={authMode === "login" ? "active" : ""}
              onClick={() => setAuthMode("login")}
            >
              Login
            </button>

            <button
              className={authMode === "register" ? "active" : ""}
              onClick={() => setAuthMode("register")}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleAuth}>
            <label>Username</label>
            <input
              type="text"
              placeholder="Enter username"
              value={form.username}
              onChange={(e) =>
                setForm({ ...form, username: e.target.value })
              }
              required
            />

            <label>Password</label>
            <input
              type="password"
              placeholder="Enter password (minimum 6 characters)"
              value={form.password}
              onChange={(e) =>
                setForm({ ...form, password: e.target.value })
              }
              required
            />

            <button
              className="primary-btn"
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Please wait..."
                : authMode === "login"
                ? "Login to Dashboard"
                : "Create Account"}
            </button>
          </form>

          {message && <p className="message">{message}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="topbar">
        <div>
          <h1>✉ EmailGuard AI</h1>
          <p>Machine Learning Email Security Dashboard</p>
        </div>

        <div className="user-area">
          <span>Welcome, {username}</span>
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <main className="main-content">
        <section className="welcome-section">
          <div>
            <h2>Email Spam Detection</h2>
            <p>Analyze suspicious emails using Machine Learning.</p>
          </div>

          <span className="model-tag">Random Forest Model</span>
        </section>

        {message && <div className="message">{message}</div>}

        <section className="stats-grid">
          <div className="stat-card">
            <span>Total Analyzed</span>
            <h2>{stats?.total ?? 0}</h2>
          </div>

          <div className="stat-card spam-card">
            <span>Spam Emails</span>
            <h2>{stats?.spam ?? 0}</h2>
          </div>

          <div className="stat-card safe-card">
            <span>Not Spam Emails</span>
            <h2>{stats?.not_spam ?? 0}</h2>
          </div>
        </section>

        <section className="panel detector-panel">
          <h2>Analyze an Email</h2>
          <p>
            Paste the email content below to check whether it is spam.
          </p>

          <textarea
            rows="7"
            placeholder="Paste your email message here..."
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <button
            className="primary-btn detect-btn"
            onClick={detectSpam}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Detect Spam"}
          </button>
        </section>

        {result && (
          <section className="panel result-panel">
            <h2>Prediction Result</h2>

            <div
              className={`result-label ${
                result.result === "Spam" ? "spam-text" : "safe-text"
              }`}
            >
              {result.result === "Spam"
                ? "⚠ SPAM EMAIL"
                : "✓ NOT SPAM"}
            </div>

            <p>
              <strong>Model confidence:</strong>{" "}
              {result.confidence_percent !== null
                ? `${result.confidence_percent}%`
                : "Not available"}
            </p>

            <p>{result.explanation}</p>

            <h3>Suspicious Indicators</h3>

            {result.indicators?.length > 0 ? (
              result.indicators.map((item, index) => (
                <div className="indicator" key={index}>
                  <strong>{item.category}</strong>
                  <p>{item.examples.join(", ")}</p>
                </div>
              ))
            ) : (
              <p>No matching suspicious text indicators found.</p>
            )}

            <p className="disclaimer">
              Indicators are text-based clues, not proof of the model's reasoning.
            </p>
          </section>
        )}

        <section className="charts-grid">
          <div className="panel">
            <h2>Your Prediction Statistics</h2>

            {stats?.prediction_chart ? (
              <img
                className="chart-image"
                src={`data:image/png;base64,${stats.prediction_chart}`}
                alt="Prediction statistics chart"
              />
            ) : (
              <p>No prediction data yet.</p>
            )}
          </div>

          <div className="panel">
            <h2>Model Comparison</h2>

            {stats?.model_comparison_chart ? (
              <img
                className="chart-image"
                src={`data:image/png;base64,${stats.model_comparison_chart}`}
                alt="Model comparison chart"
              />
            ) : (
              <p>Model comparison chart unavailable.</p>
            )}
          </div>
        </section>

        <section className="panel">
          <h2>Confusion Matrix</h2>

          {stats?.confusion_matrix ? (
            <img
              className="chart-image confusion-image"
              src={`data:image/png;base64,${stats.confusion_matrix}`}
              alt="Confusion matrix"
            />
          ) : (
            <p>Confusion matrix unavailable.</p>
          )}
        </section>

        <section className="panel">
          <h2>Prediction History</h2>

          {history.length === 0 ? (
            <p>No predictions yet. Analyze your first email!</p>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>Prediction</th>
                    <th>Confidence</th>
                    <th>Date</th>
                  </tr>
                </thead>

                <tbody>
                  {history.map((item) => (
                    <tr key={item.id}>
                      <td className="email-cell">{item.email}</td>

                      <td>
                        <span
                          className={
                            item.prediction === "Spam"
                              ? "spam-text"
                              : "safe-text"
                          }
                        >
                          {item.prediction}
                        </span>
                      </td>

                      <td>
                        {item.confidence === null
                          ? "N/A"
                          : `${item.confidence}%`}
                      </td>

                      <td>{item.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <footer>
          EmailGuard AI | Powered by Python, Flask, React and Machine Learning
        </footer>
      </main>
    </div>
  );
}

export default App;
