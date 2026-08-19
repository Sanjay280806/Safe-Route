import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login, useMocks } from "../api/client";
import type { LoginResponse } from "../types";

export function LoginPage({ onLogin }: { onLogin: (response: LoginResponse) => void }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("reporter");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const response = await login(username, password);
      onLogin(response);
      navigate("/");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to sign in.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-intro">
        <Link className="brand brand-on-dark" to="/"><span className="brand-mark">⌁</span><span>SafeRoute<small>Velachery</small></span></Link>
        <div>
          <p className="eyebrow light">Flood-aware navigation</p>
          <h1>Give field teams a safer route through uncertainty.</h1>
          <p>Use the benchmark dashboard to inspect road risk, report flooding and demonstrate automatic rerouting.</p>
        </div>
        <div className="login-feature-list">
          <span>● Risk-layered roads</span><span>● Verified field reports</span><span>● Time-to-risk route warnings</span>
        </div>
      </section>
      <section className="login-form-area">
        <form className="login-card" onSubmit={submit}>
          <Link className="back-link" to="/">← Back to dashboard</Link>
          <p className="eyebrow">Access dashboard tools</p>
          <h2>Sign in</h2>
          <p className="muted">Reporter and control-room access is only for verified demo roles.</p>
          {useMocks ? <p className="mock-credentials">Mock credentials: <strong>reporter/password</strong> or <strong>admin/password</strong></p> : null}
          {error ? <p className="form-error" role="alert">{error}</p> : null}
          <label className="field-label" htmlFor="username">Username</label>
          <input id="username" value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" />
          <label className="field-label" htmlFor="password">Password</label>
          <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" />
          <button type="submit" className="primary-button login-submit" disabled={submitting}>{submitting ? "Signing in…" : "Sign in"}</button>
          <p className="login-disclaimer">This benchmark login is not production authentication.</p>
        </form>
      </section>
    </main>
  );
}
