/**
 * @fileoverview Client onboarding intake form. Collects business details, GBP info,
 * and client goals. Supports persistence via api/client.js and .txt export.
 */

import React, { useState, useCallback } from 'react';
import { COLORS, FONTS, baseStyles } from '../shared/styles';
import { Field, Input, Textarea, Select, Divider } from '../shared/FormFields';
import { INDUSTRY_OPTIONS, GBP_ACCESS_OPTIONS, START_TYPE_OPTIONS } from './ClientIntake.config';
import { saveClientIntake, createNewEngagement } from '../api/client';

const EMPTY = {
  businessName: '',
  contactName: '',
  industry: '',
  cityArea: '',
  phone: '',
  email: '',
  website: '',
  gbpAccountId: '',
  gbpLocationId: '',
  gbpAccessStatus: '',
  startingPoint: '',
  currentRating: '',
  currentReviewCount: '',
  topGoal: '',
  notes: '',
};

function generateTxt(d) {
  return [
    `CLIENT INTAKE — ${d.businessName || '(no name)'}`,
    '='.repeat(50),
    '',
    `Contact:         ${d.contactName}`,
    `Industry:        ${d.industry}`,
    `City / Area:     ${d.cityArea}`,
    `Phone:           ${d.phone}`,
    `Email:           ${d.email}`,
    `Website:         ${d.website}`,
    '',
    `GBP Account ID:  ${d.gbpAccountId}`,
    `GBP Location ID: ${d.gbpLocationId}`,
    `GBP Access:      ${d.gbpAccessStatus}`,
    `Starting Point:  ${d.startingPoint}`,
    '',
    `Star Rating:     ${d.currentRating}`,
    `Review Count:    ${d.currentReviewCount}`,
    '',
    `#1 Goal:         ${d.topGoal}`,
    '',
    'Notes:',
    d.notes || '(none)',
  ].join('\n');
}

export default function ClientIntake({ onSave, onCancel, initialData = {}, clientId }) {
  const [form, setForm] = useState({ ...EMPTY, ...initialData });
  const [errors, setErrors] = useState({});
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [saveMessage, setSaveMessage] = useState('');

  const set = useCallback((key) => (e) => {
    setForm((prev) => ({ ...prev, [key]: e.target.value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  }, []);

  const handleSave = async () => {
    const next = {};
    if (!form.businessName.trim()) next.businessName = 'Business name is required';
    if (!form.contactName.trim()) next.contactName = 'Contact name is required';
    if (!form.industry?.trim()) next.industry = 'Industry is required';
    if (!form.email.trim()) next.email = 'Email is required';
    if (Object.keys(next).length) {
      setErrors(next);
      return;
    }
    setSaveError('');
    setSaveMessage('');
    try {
      let engagementId = clientId;
      if (!engagementId) {
        const eng = await createNewEngagement(form.businessName.trim() || 'New Client');
        engagementId = String(eng.id);
      }
      const savedForm = await saveClientIntake({ ...form, clientId: engagementId });
      const merged = { ...form, ...savedForm, clientId: engagementId };
      setForm(merged);
      onSave?.(merged);
      setSaveMessage('Saved to engagement and business profile.');
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (error) {
      setSaveError(error.message || 'Failed to save intake.');
    }
  };

  const handleExport = () => {
    const blob = new Blob([generateTxt(form)], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${(form.businessName || 'client').replace(/\s+/g, '_')}_intake.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const errStyle = { fontFamily: FONTS.mono, fontSize: '0.7rem', color: COLORS.red, marginTop: 4 };

  return (
    <div style={baseStyles.sectionBox}>
      <h2 style={{ fontFamily: FONTS.heading, color: COLORS.cream, fontSize: '1.6rem', marginTop: 0, marginBottom: 4 }}>
        Client Intake
      </h2>
      <p style={{ fontFamily: FONTS.body, color: COLORS.muted, fontSize: '1rem', marginTop: 0, marginBottom: 24 }}>
        Capture all essential onboarding details for the client engagement.
      </p>

      <div style={baseStyles.grid2col}>
        <Field label="Business Name" span="1 / -1" htmlFor="ci-biz">
          <Input id="ci-biz" value={form.businessName} onChange={set('businessName')} placeholder="e.g. Bloom Beauty Studio" />
          {errors.businessName && <div style={errStyle}>{errors.businessName}</div>}
        </Field>

        <Field label="Contact Name" htmlFor="ci-contact">
          <Input id="ci-contact" value={form.contactName} onChange={set('contactName')} placeholder="Full name" />
          {errors.contactName && <div style={errStyle}>{errors.contactName}</div>}
        </Field>

        <Field label="Industry" htmlFor="ci-industry">
          <Select id="ci-industry" value={form.industry} onChange={set('industry')} options={INDUSTRY_OPTIONS} placeholder="Select industry" />
        </Field>

        <Field label="City / Area" htmlFor="ci-city">
          <Input id="ci-city" value={form.cityArea} onChange={set('cityArea')} placeholder="e.g. East Los Angeles, CA" />
        </Field>

        <Field label="Phone" htmlFor="ci-phone">
          <Input id="ci-phone" value={form.phone} onChange={set('phone')} placeholder="(555) 123-4567" />
        </Field>

        <Field label="Email" htmlFor="ci-email">
          <Input id="ci-email" value={form.email} onChange={set('email')} type="email" placeholder="client@example.com" />
        </Field>

        <Field label="Website" span="1 / -1" htmlFor="ci-web">
          <Input id="ci-web" value={form.website} onChange={set('website')} placeholder="https://..." />
        </Field>

        <Divider />

        <Field label="GBP Account ID" span="1 / -1" htmlFor="ci-gbp-acct">
          <Input id="ci-gbp-acct" value={form.gbpAccountId} onChange={set('gbpAccountId')} placeholder="accounts/123456789 — auto-filled after GBP OAuth" />
        </Field>

        <Field label="GBP Location ID" span="1 / -1" htmlFor="ci-gbp-loc">
          <Input id="ci-gbp-loc" value={form.gbpLocationId} onChange={set('gbpLocationId')} placeholder="locations/987654321 — auto-filled after GBP OAuth" />
        </Field>

        <Field label="GBP Access Status" htmlFor="ci-gbp-status">
          <Select id="ci-gbp-status" value={form.gbpAccessStatus} onChange={set('gbpAccessStatus')} options={GBP_ACCESS_OPTIONS} placeholder="Select status" />
        </Field>

        <Field label="Starting Point" htmlFor="ci-start">
          <Select id="ci-start" value={form.startingPoint} onChange={set('startingPoint')} options={START_TYPE_OPTIONS} placeholder="Select starting point" />
        </Field>

        <Field label="Current Star Rating" htmlFor="ci-rating">
          <Input id="ci-rating" value={form.currentRating} onChange={set('currentRating')} placeholder="e.g. 4.2" />
        </Field>

        <Field label="Current Review Count" htmlFor="ci-reviews">
          <Input id="ci-reviews" value={form.currentReviewCount} onChange={set('currentReviewCount')} placeholder="e.g. 37" />
        </Field>

        <Divider />

        <Field label="Client's #1 Goal This Month" span="1 / -1" htmlFor="ci-goal">
          <Input id="ci-goal" value={form.topGoal} onChange={set('topGoal')} placeholder="What does the client want most from month 1?" />
        </Field>

        <Field label="Additional Notes" span="1 / -1" htmlFor="ci-notes">
          <Textarea id="ci-notes" value={form.notes} onChange={set('notes')} placeholder="Anything else relevant…" rows={4} />
        </Field>
      </div>

      {saveError && (
        <div style={{ ...errStyle, marginTop: 10 }}>
          {saveError}
        </div>
      )}
      {saveMessage && !saveError && (
        <div style={{ fontFamily: FONTS.mono, fontSize: '0.7rem', color: COLORS.green, marginTop: 10 }}>
          {saveMessage}
        </div>
      )}

      <div style={{ display: 'flex', gap: 12, marginTop: 24, flexWrap: 'wrap' }}>
        <button
          type="button"
          onClick={handleSave}
          style={{
            ...baseStyles.btn,
            ...(saved ? baseStyles.btnSaved : baseStyles.btnPrimary),
          }}
        >
          {saved ? '✓ Saved' : 'Save Intake'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            style={{ ...baseStyles.btn, ...baseStyles.btnSecondary }}
          >
            Cancel
          </button>
        )}
        <button
          type="button"
          onClick={handleExport}
          style={{ ...baseStyles.btn, ...baseStyles.btnSecondary }}
        >
          Export .txt
        </button>
      </div>
    </div>
  );
}
