/**
 * @fileoverview Design tokens and reusable style fragments for the Demo Delivery Toolkit.
 * All components import from here to maintain a consistent luxury editorial aesthetic.
 */

export const COLORS = {
  bg:          '#16100c',
  bgMid:       '#1f1610',
  bgLight:     '#2a1e16',
  accent:      '#c9956a',
  cream:       '#f0e8dc',
  muted:       '#7a6558',
  green:       '#7ec8a0',
  red:         '#e07070',
  gold:        '#e8c87a',
  border:      '#3d2d22',
  blue:        '#7aacd4',
};

export const FONTS = {
  heading: "'Playfair Display', serif",
  body:    "'Cormorant Garamond', serif",
  mono:    "'DM Mono', monospace",
};

export const baseStyles = {
  input: {
    fontFamily: FONTS.body,
    fontSize: '1rem',
    color: COLORS.cream,
    background: COLORS.bgLight,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 4,
    padding: '10px 14px',
    outline: 'none',
    width: '100%',
    boxSizing: 'border-box',
    transition: 'border-color 0.25s ease',
  },

  label: {
    fontFamily: FONTS.mono,
    fontSize: '0.7rem',
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
    color: COLORS.muted,
    marginBottom: 6,
  },

  btn: {
    fontFamily: FONTS.mono,
    fontSize: '0.75rem',
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    background: 'transparent',
    color: COLORS.cream,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 4,
    padding: '10px 22px',
    cursor: 'pointer',
    transition: 'all 0.25s ease',
  },

  btnPrimary: {
    borderColor: COLORS.accent,
    color: COLORS.accent,
  },

  btnSecondary: {
    borderColor: COLORS.muted,
    color: COLORS.muted,
  },

  btnSaved: {
    borderColor: COLORS.green,
    color: COLORS.green,
  },

  btnCopied: {
    borderColor: COLORS.green,
    color: COLORS.green,
  },

  preview: {
    background: COLORS.bg,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 4,
    padding: 20,
    marginTop: 8,
  },

  previewText: {
    fontFamily: FONTS.mono,
    fontSize: '0.8rem',
    lineHeight: 1.7,
    color: COLORS.cream,
    whiteSpace: 'pre-wrap',
    margin: 0,
  },

  grid2col: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 20,
  },

  divider: {
    gridColumn: '1 / -1',
    border: 'none',
    borderTop: `1px solid ${COLORS.border}`,
    margin: '8px 0',
  },

  sectionBox: {
    background: COLORS.bgMid,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 6,
    padding: 24,
    marginBottom: 24,
  },
};
