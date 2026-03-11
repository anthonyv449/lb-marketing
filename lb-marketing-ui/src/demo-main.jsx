/**
 * @fileoverview Dev entry point for the Demo Delivery Toolkit.
 * Renders all five components in a scrollable layout for development and review.
 */

import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ClientIntake,
  TaskTracker,
  AuditBuilder,
  ReviewRequestComposer,
  MonthEndReport,
} from './components/demo';

const COLORS = {
  bg: '#16100c',
  cream: '#f0e8dc',
  accent: '#c9956a',
  muted: '#7a6558',
  border: '#3d2d22',
};

const TABS = [
  { key: 'intake',   label: 'Client Intake' },
  { key: 'tasks',    label: 'Task Tracker' },
  { key: 'audit',    label: 'Audit Builder' },
  { key: 'review',   label: 'Review Composer' },
  { key: 'report',   label: 'Month-End Report' },
];

function DemoToolkit() {
  const [active, setActive] = useState('intake');
  const [intakeData, setIntakeData] = useState({});

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
        <p style={{
          fontFamily: "'Cormorant Garamond', serif",
          fontSize: '1.1rem',
          color: COLORS.muted,
          marginTop: 0,
          marginBottom: 32,
        }}>
          Internal tools for managing client onboarding and delivery.
        </p>

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
        {active === 'intake' && (
          <ClientIntake
            onSave={(data) => {
              setIntakeData(data);
              console.log('Intake saved:', data);
            }}
          />
        )}
        {active === 'tasks' && (
          <TaskTracker
            vertical={intakeData.industry || 'salons_spas'}
          />
        )}
        {active === 'audit' && (
          <AuditBuilder businessName={intakeData.businessName || ''} />
        )}
        {active === 'review' && (
          <ReviewRequestComposer />
        )}
        {active === 'report' && (
          <MonthEndReport />
        )}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <DemoToolkit />
  </React.StrictMode>
);
