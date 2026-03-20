/**
 * @fileoverview Table of client engagements. Displays business name, contact info,
 * website. Row click navigates to client detail (Task Tracker, etc.).
 */

import React, { useState, useEffect } from 'react';
import { COLORS, FONTS, baseStyles } from '../shared/styles';
import { fetchEngagements } from '../api/client';

function formatDate(isoStr) {
  if (!isoStr) return '—';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  } catch {
    return '—';
  }
}

function formatContact(engagement) {
  if (engagement.email) return engagement.email;
  if (engagement.phone) return engagement.phone;
  return '—';
}

export default function ClientEngagementsTable({ onSelectClient, refreshTrigger }) {
  const [engagements, setEngagements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hoveredId, setHoveredId] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchEngagements()
      .then((data) => {
        if (!cancelled) setEngagements(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || 'Failed to load');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [refreshTrigger]);

  const handleRowClick = (row) => {
    onSelectClient?.(row);
  };

  if (loading) {
    return (
      <div style={baseStyles.sectionBox}>
        <h2 style={{ fontFamily: FONTS.heading, color: COLORS.cream, fontSize: '1.6rem', marginTop: 0, marginBottom: 4 }}>
          Client Engagements
        </h2>
        <p style={{ fontFamily: FONTS.body, color: COLORS.muted, fontSize: '1rem', marginTop: 0, marginBottom: 24 }}>
          Loading engagements…
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={baseStyles.sectionBox}>
        <h2 style={{ fontFamily: FONTS.heading, color: COLORS.cream, fontSize: '1.6rem', marginTop: 0, marginBottom: 4 }}>
          Client Engagements
        </h2>
        <p style={{ fontFamily: FONTS.body, color: COLORS.red, fontSize: '1rem', marginTop: 0, marginBottom: 24 }}>
          {error}
        </p>
      </div>
    );
  }

  return (
    <div style={baseStyles.sectionBox}>
      <h2 style={{ fontFamily: FONTS.heading, color: COLORS.cream, fontSize: '1.6rem', marginTop: 0, marginBottom: 4 }}>
        Client Engagements
      </h2>
      <p style={{ fontFamily: FONTS.body, color: COLORS.muted, fontSize: '1rem', marginTop: 0, marginBottom: 24 }}>
        Select a client to view their task tracker and delivery tools.
      </p>

      {engagements.length === 0 ? (
        <p style={{ fontFamily: FONTS.body, color: COLORS.muted, fontSize: '1rem' }}>
          No client engagements yet. Add clients via the Business API or Client Intake.
        </p>
      ) : (
        <div style={{ overflowX: 'auto', border: `1px solid ${COLORS.border}`, borderRadius: 6 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: FONTS.body, fontSize: '0.95rem' }}>
            <thead>
              <tr style={{ background: COLORS.bg, borderBottom: `1px solid ${COLORS.border}` }}>
                <th style={thStyle}>Business Name</th>
                <th style={thStyle}>Contact</th>
                <th style={thStyle}>Website</th>
                <th style={thStyle}>Created</th>
              </tr>
            </thead>
            <tbody>
              {engagements.map((row) => (
                <tr
                  key={row.id}
                  onClick={() => handleRowClick(row)}
                  onMouseEnter={() => setHoveredId(row.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  style={{
                    ...rowStyle,
                    cursor: onSelectClient ? 'pointer' : 'default',
                    background: hoveredId === row.id ? `${COLORS.accent}14` : 'transparent',
                  }}
                >
                  <td style={tdStyle}>{row.business_name || '—'}</td>
                  <td style={tdStyle}>{formatContact(row)}</td>
                  <td style={tdStyle}>
                    {row.website ? (
                      <a
                        href={row.website.startsWith('http') ? row.website : `https://${row.website}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        style={{ color: COLORS.blue, textDecoration: 'none' }}
                      >
                        {row.website}
                      </a>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td style={tdStyle}>{formatDate(row.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const thStyle = {
  fontFamily: "'DM Mono', monospace",
  fontSize: '0.68rem',
  letterSpacing: '0.08em',
  textTransform: 'uppercase',
  color: COLORS.muted,
  textAlign: 'left',
  padding: '12px 16px',
  fontWeight: 500,
};

const rowStyle = {
  borderBottom: `1px solid ${COLORS.border}`,
  transition: 'background 0.2s ease',
};

const tdStyle = {
  padding: '12px 16px',
  color: COLORS.cream,
};
