/**
 * @fileoverview Dev entry point for the Demo Delivery Toolkit.
 * Renders client engagements table and client detail tools (intake, task tracker, etc.).
 */

import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ClientEngagementsTable,
  ClientIntake,
  TaskTracker,
  AuditBuilder,
  MonthEndReport,
} from './components/demo';

const COLORS = {
  bg: '#16100c',
  cream: '#f0e8dc',
  accent: '#c9956a',
  muted: '#7a6558',
  border: '#3d2d22',
};

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Login failed');
  }
  const data = await res.json();
  localStorage.setItem('auth_token', data.access_token);
  if (data.user) localStorage.setItem('user_data', JSON.stringify(data.user));
  return data;
}

const TABS = [
  { key: 'tasks',    label: 'Task Tracker' },
  { key: 'audit',    label: 'Audit Builder' },
  { key: 'report',   label: 'Month-End Report' },
];

function LoginScreen({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      onLoginSuccess();
    } catch (err) {
      setError(err?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: COLORS.bg,
      color: COLORS.cream,
      padding: 40,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: 320 }}>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: '1.8rem', marginBottom: 24 }}>
          Demo Delivery Toolkit
        </h1>
        <p style={{ fontFamily: "'Cormorant Garamond', serif", color: COLORS.muted, marginBottom: 24 }}>
          Sign in with test / test (dev seed user)
        </p>
        <div style={{ marginBottom: 16 }}>
          <input
            type="text"
            placeholder="Username (email)"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
            style={{
              width: '100%',
              background: '#2a1e16',
              color: COLORS.cream,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 4,
              padding: '12px 14px',
              fontFamily: "'Cormorant Garamond', serif",
              fontSize: '1rem',
            }}
          />
        </div>
        <div style={{ marginBottom: 16 }}>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            style={{
              width: '100%',
              background: '#2a1e16',
              color: COLORS.cream,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 4,
              padding: '12px 14px',
              fontFamily: "'Cormorant Garamond', serif",
              fontSize: '1rem',
            }}
          />
        </div>
        {error && (
          <p style={{ color: '#e07070', fontSize: '0.9rem', marginBottom: 12 }}>{error}</p>
        )}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            ...{ fontFamily: "'DM Mono', monospace", letterSpacing: '0.06em', padding: '12px 20px', background: 'transparent', color: COLORS.accent, border: `1px solid ${COLORS.accent}`, borderRadius: 4, cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 },
          }}
        >
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  );
}

async function checkAuth() {
  const token = localStorage.getItem('auth_token');
  const res = await fetch(`${BASE_URL}/auth/me`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  return res.ok;
}

function App() {
  const [authStatus, setAuthStatus] = useState('checking'); // 'checking' | 'authenticated' | 'unauthenticated'

  useEffect(() => {
    checkAuth()
      .then((ok) => setAuthStatus(ok ? 'authenticated' : 'unauthenticated'))
      .catch(() => setAuthStatus('unauthenticated'));
  }, []);

  const onLoginSuccess = () => {
    setAuthStatus('authenticated');
  };

  if (authStatus === 'checking') {
    return (
      <div style={{
        minHeight: '100vh',
        background: COLORS.bg,
        color: COLORS.cream,
        padding: 40,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <p style={{ fontFamily: "'Cormorant Garamond', serif", color: COLORS.muted }}>
          Checking authentication…
        </p>
      </div>
    );
  }

  if (authStatus === 'unauthenticated') {
    return <LoginScreen onLoginSuccess={onLoginSuccess} />;
  }

  return <DemoToolkit />;
}

function IntakeModal({ onSave, onCancel }) {
  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: 24,
      }}
      onClick={(e) => e.target === e.currentTarget && onCancel()}
    >
      <div
        style={{
          background: COLORS.bg,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 8,
          maxWidth: 640,
          width: '100%',
          maxHeight: '90vh',
          overflow: 'auto',
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 24px',
            borderBottom: `1px solid ${COLORS.border}`,
          }}
        >
          <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: '1.4rem', margin: 0, color: COLORS.cream }}>
            Create Client Engagement
          </h3>
          <button
            type="button"
            onClick={onCancel}
            aria-label="Close"
            style={{
              background: 'transparent',
              border: 'none',
              color: COLORS.muted,
              fontSize: '1.5rem',
              cursor: 'pointer',
              padding: '0 8px',
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>
        <div style={{ padding: 24 }}>
          <ClientIntake
            onSave={onSave}
            onCancel={onCancel}
          />
        </div>
      </div>
    </div>
  );
}

function DemoToolkit() {
  const [selectedClient, setSelectedClient] = useState(null);
  const [active, setActive] = useState('tasks');
  const [intakeData, setIntakeData] = useState({});
  const [intakeModalOpen, setIntakeModalOpen] = useState(false);
  const [tableRefreshTrigger, setTableRefreshTrigger] = useState(0);

  const handleSelectClient = (client) => {
    setSelectedClient(client);
    setIntakeData((prev) => ({
      ...prev,
      businessName: client?.name || prev.businessName,
      contactName: prev.contactName,
      email: client?.email || prev.email,
      phone: client?.phone || prev.phone,
      website: client?.website || prev.website,
    }));
    setActive('tasks');
  };

  const handleBackToList = () => {
    setSelectedClient(null);
  };

  const handleIntakeSaved = (data) => {
    setIntakeData(data);
    setIntakeModalOpen(false);
    setTableRefreshTrigger((t) => t + 1);
  };

  const handleIntakeCancel = () => {
    setIntakeModalOpen(false);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: COLORS.bg,
      color: COLORS.cream,
      padding: '40px 24px',
    }}>
      <div style={{ maxWidth: 960, margin: '0 auto' }}>
        <h1 style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: '2.2rem',
          color: COLORS.cream,
          marginBottom: 4,
        }}>
          Demo Delivery Toolkit
        </h1>

        {!selectedClient ? (
          <>
            <div style={{ marginBottom: 20 }}>
              <button
                type="button"
                onClick={() => setIntakeModalOpen(true)}
                style={{
                  fontFamily: "'DM Mono', monospace",
                  fontSize: '0.72rem',
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  padding: '10px 20px',
                  background: `${COLORS.accent}14`,
                  color: COLORS.accent,
                  border: `1px solid ${COLORS.accent}`,
                  borderRadius: 4,
                  cursor: 'pointer',
                  transition: 'all 0.25s ease',
                }}
              >
                + Create client engagement
              </button>
            </div>
            <ClientEngagementsTable
              onSelectClient={handleSelectClient}
              refreshTrigger={tableRefreshTrigger}
            />
            {intakeModalOpen && (
              <IntakeModal
                onSave={handleIntakeSaved}
                onCancel={handleIntakeCancel}
              />
            )}
          </>
        ) : (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
              <button
                type="button"
                onClick={handleBackToList}
                style={{
                  fontFamily: "'DM Mono', monospace",
                  fontSize: '0.72rem',
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  padding: '8px 16px',
                  background: 'transparent',
                  color: COLORS.muted,
                  border: `1px solid ${COLORS.border}`,
                  borderRadius: 4,
                  cursor: 'pointer',
                  transition: 'all 0.25s ease',
                }}
              >
                ← Back to list
              </button>
              <span style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '1rem', color: COLORS.muted }}>
                {selectedClient.name}
              </span>
            </div>

            {/* Tab navigation */}
            <nav style={{ display: 'flex', gap: 6, marginBottom: 32, flexWrap: 'wrap' }}>
              {TABS.map((t) => (
                <button
                  key={t.key}
                  type="button"
                  onClick={() => setActive(t.key)}
                  style={{
                    fontFamily: "'DM Mono', monospace",
                    fontSize: '0.72rem',
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    padding: '10px 20px',
                    background: active === t.key ? `${COLORS.accent}14` : 'transparent',
                    color: active === t.key ? COLORS.accent : COLORS.muted,
                    border: `1px solid ${active === t.key ? COLORS.accent : COLORS.border}`,
                    borderRadius: 4,
                    cursor: 'pointer',
                    transition: 'all 0.25s ease',
                  }}
                >
                  {t.label}
                </button>
              ))}
            </nav>

            {/* Active panel */}
            {active === 'tasks' && (
              <TaskTracker
                clientId={selectedClient.id}
                vertical={intakeData.industry || 'salons_spas'}
              />
            )}
            {active === 'audit' && (
              <AuditBuilder businessName={intakeData.businessName || selectedClient.name || ''} />
            )}
            {active === 'report' && (
              <MonthEndReport />
            )}
          </>
        )}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
