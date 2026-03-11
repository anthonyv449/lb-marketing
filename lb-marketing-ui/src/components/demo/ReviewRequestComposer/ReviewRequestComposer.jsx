/**
 * @fileoverview Self-contained review request message composer.
 * Users fill in details, pick a tone, and get a ready-to-send message they can copy.
 */

import React, { useState, useMemo, useCallback } from 'react';
import { COLORS, FONTS, baseStyles } from '../shared/styles';
import { Field, Input, CopyBtn } from '../shared/FormFields';
import { TEMPLATES } from './ReviewRequestComposer.templates';

const TONES = [
  { key: 'warm',         label: 'Warm' },
  { key: 'concise',      label: 'Concise' },
  { key: 'professional', label: 'Professional' },
];

export default function ReviewRequestComposer() {
  const [form, setForm] = useState({
    businessName: '',
    customerName: '',
    service: '',
    reviewLink: '',
  });
  const [tone, setTone] = useState('warm');

  const set = useCallback((key) => (e) => {
    setForm((prev) => ({ ...prev, [key]: e.target.value }));
  }, []);

  const message = useMemo(() => {
    const fn = TEMPLATES[tone];
    return fn(
      form.businessName || '[Business Name]',
      form.customerName || '[Customer]',
      form.service,
      form.reviewLink || '[review link]',
    );
  }, [form, tone]);

  const toneBtn = (t) => {
    const active = tone === t.key;
    return (
      <button
        key={t.key}
        type="button"
        onClick={() => setTone(t.key)}
        style={{
          ...baseStyles.btn,
          borderColor: active ? COLORS.accent : COLORS.border,
          color: active ? COLORS.accent : COLORS.muted,
          background: active ? `${COLORS.accent}14` : 'transparent',
        }}
      >
        {t.label}
      </button>
    );
  };

  return (
    <div style={baseStyles.sectionBox}>
      <h2 style={{ fontFamily: FONTS.heading, color: COLORS.cream, fontSize: '1.6rem', marginTop: 0, marginBottom: 4 }}>
        Review Request Composer
      </h2>
      <p style={{ fontFamily: FONTS.body, color: COLORS.muted, fontSize: '1rem', marginTop: 0, marginBottom: 24 }}>
        Generate a personalised review request message ready to send via text or email.
      </p>

      <div style={baseStyles.grid2col}>
        <Field label="Business Name" htmlFor="rr-biz">
          <Input id="rr-biz" value={form.businessName} onChange={set('businessName')} placeholder="e.g. Bloom Beauty Studio" />
        </Field>

        <Field label="Customer First Name" htmlFor="rr-customer">
          <Input id="rr-customer" value={form.customerName} onChange={set('customerName')} placeholder="e.g. Maria" />
        </Field>

        <Field label="Service Provided" htmlFor="rr-service">
          <Input id="rr-service" value={form.service} onChange={set('service')} placeholder="e.g. balayage highlight" />
        </Field>

        <Field label="Google Review Link" htmlFor="rr-link">
          <Input id="rr-link" value={form.reviewLink} onChange={set('reviewLink')} placeholder="https://g.page/r/..." />
        </Field>
      </div>

      {/* Tone selector */}
      <div style={{ marginTop: 20, marginBottom: 20 }}>
        <div style={{ ...baseStyles.label, marginBottom: 10 }}>Tone</div>
        <div style={{ display: 'flex', gap: 10 }}>
          {TONES.map(toneBtn)}
        </div>
      </div>

      {/* Message preview — body font, not monospace */}
      <div>
        <div style={{ ...baseStyles.label, marginBottom: 6 }}>Message Preview</div>
        <div style={baseStyles.preview}>
          <div style={{ fontFamily: FONTS.body, fontSize: '1rem', lineHeight: 1.7, color: COLORS.cream, whiteSpace: 'pre-wrap' }}>
            {message}
          </div>
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <CopyBtn text={message} label="Copy Message" />
      </div>
    </div>
  );
}
