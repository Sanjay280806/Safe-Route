import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import type { LoginResponse, User } from "./types";

const SESSION_KEY = "saferoute-demo-session";

interface StoredSession { user: User; token: string; }

function readSession(): StoredSession | null {
  try {
    const raw = window.localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) as StoredSession : null;
  } catch {
    return null;
  }
}

export default function App() {
  const [session, setSession] = useState<StoredSession | null>(() => readSession());

  useEffect(() => {
    if (session) window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    else window.localStorage.removeItem(SESSION_KEY);
  }, [session]);

  const handleLogin = (response: LoginResponse) => setSession({ user: response.user, token: response.access_token });

  return (
    <Routes>
      <Route path="/" element={<DashboardPage user={session?.user ?? null} token={session?.token ?? null} onLogout={() => setSession(null)} />} />
      <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
