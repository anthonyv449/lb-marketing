/**
 * @fileoverview Reusable form primitives shared across all Demo Toolkit components.
 * Every field is a controlled component. No duplicated input markup across the suite.
 */

import React, { useState, useCallback } from 'react';
import { COLORS, FONTS, baseStyles } from './styles';

export function Label({ children, htmlFor }) {
  return (
    <label htmlFor={htmlFor} style={baseStyles.label}>
      {children}
    </label>
  );
}

export function Input({ value, onChange, placeholder, type = 'text', style: extra, id, ...rest }) {
  const [focused, setFocused] = useState(false);
  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        ...baseStyles.input,
        borderColor: focused ? COLORS.accent : COLORS.border,
        ...extra,
      }}
      {...rest}
    />
  );
}

export function Textarea({ value, onChange, placeholder, rows = 4, style: extra, id }) {
  const [focused, setFocused] = useState(false);
  return (
    <textarea
      id={id}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      rows={rows}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        ...baseStyles.input,
        resize: 'vertical',
        borderColor: focused ? COLORS.accent : COLORS.border,
        ...extra,
      }}
    />
  );
}

export function Select({ value, onChange, options, placeholder, style: extra, id }) {
  const [focused, setFocused] = useState(false);
  return (
    <select
      id={id}
      value={value}
      onChange={onChange}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        ...baseStyles.input,
        borderColor: focused ? COLORS.accent : COLORS.border,
        appearance: 'none',
        ...extra,
      }}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

export function Field({ label, children, span, htmlFor }) {
  return (
    <div style={span ? { gridColumn: span } : undefined}>
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
    </div>
  );
}

export function Divider() {
  return <hr style={baseStyles.divider} />;
}

export function CopyBtn({ text, label = 'Copy' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [text]);

  return (
    <button
      type="button"
      onClick={handleCopy}
      style={{
        ...baseStyles.btn,
        ...(copied ? baseStyles.btnCopied : baseStyles.btnPrimary),
      }}
    >
      {copied ? '✓ Copied' : label}
    </button>
  );
}

export function PreviewBox({ text, label = 'Preview' }) {
  return (
    <div>
      <Label>{label}</Label>
      <div style={baseStyles.preview}>
        <pre style={baseStyles.previewText}>{text}</pre>
      </div>
    </div>
  );
}
