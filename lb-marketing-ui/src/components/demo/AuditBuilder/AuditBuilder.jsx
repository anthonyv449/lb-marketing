/**
 * @fileoverview Audit report builder. Collects GBP data, rankings, issues, and quick wins,
 * then generates a live preview and supports copy-to-clipboard.
 */

import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { COLORS, FONTS, baseStyles } from '../shared/styles';
import { Field, Input, Textarea, Select, Divider, CopyBtn, PreviewBox } from '../shared/FormFields';
import { generateAuditReport } from './AuditBuilder.preview';
import { fetchAuditReport, saveAuditReport } from '../api/client';

const GBP_STATUS_OPTIONS = [
  { value: 'claimed_complete',   label: 'Claimed — Complete' },
  { value: 'claimed_incomplete', label: 'Claimed — Incomplete' },
  { value: 'unclaimed',          label: 'Unclaimed' },
  { value: 'does_not_exist',     label: 'Does Not Exist' },
];

const EMPTY = {
  businessName: '', auditedBy: '', dateDelivered: '',
  gbpStatus: '', gbpPhotos: '', starRating: '', reviewCount: '',
  websiteScore: '', citationConsistency: '',
  keyword1: '', position1: '', keyword2: '', position2: '',
  issue1: '', issue2: '', issue3: '',
  quickWin1: '', quickWin2: '',
  notes: '',
};

export default function AuditBuilder({ businessName = '', clientId }) {
  const [form, setForm] = useState({ ...EMPTY, businessName });
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState('');

  useEffect(() => {
    if (!businessName) return;
    setForm((prev) => ({ ...prev, businessName }));
  }, [businessName]);

  useEffect(() => {
    if (!clientId) return;
    fetchAuditReport(clientId).then((data) => {
      if (data) {
        setForm((prev) => ({ ...prev, ...data, businessName: prev.businessName }));
      }
    }).catch(() => {
      // Non-blocking: keep the form usable even when fetch fails.
    });
  }, [clientId]);

  const set = useCallback((key) => (e) => {
    setForm((prev) => ({ ...prev, [key]: e.target.value }));
  }, []);

  const report = useMemo(() => generateAuditReport(form), [form]);

  const handleSave = async () => {
    if (!clientId) {
      setSaveError('Set an engagement ID to persist this report.');
      return;
    }
    setSaveError('');
    try {
      const savedReport = await saveAuditReport(clientId, form);
      setForm((prev) => ({ ...prev, ...savedReport, businessName: prev.businessName }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (error) {
      setSaveError(error.message || 'Failed to save audit report.');
    }
  };

  return (
    <div style={baseStyles.sectionBox}>
      <h2 style={{ fontFamily: FONTS.heading, color: COLORS.cream, fontSize: '1.6rem', marginTop: 0, marginBottom: 4 }}>
        Audit Builder
      </h2>
      <p style={{ fontFamily: FONTS.body, color: COLORS.muted, fontSize: '1rem', marginTop: 0, marginBottom: 24 }}>
        Fill in audit findings to generate a client-ready report. The preview updates in real time.
      </p>

      <div style={baseStyles.grid2col}>
        <Field label="Business Name" span="1 / -1" htmlFor="ab-biz">
          <Input id="ab-biz" value={form.businessName} onChange={set('businessName')} placeholder="Client business name" />
        </Field>

        <Field label="Audited By" htmlFor="ab-auditor">
          <Input id="ab-auditor" value={form.auditedBy} onChange={set('auditedBy')} placeholder="Your name" />
        </Field>

        <Field label="Date Delivered" htmlFor="ab-date">
          <Input id="ab-date" value={form.dateDelivered} onChange={set('dateDelivered')} type="date" />
        </Field>

        <Divider />

        <Field label="GBP Status" htmlFor="ab-gbp-status">
          <Select id="ab-gbp-status" value={form.gbpStatus} onChange={set('gbpStatus')} options={GBP_STATUS_OPTIONS} placeholder="Select status" />
        </Field>

        <Field label="GBP Photos" htmlFor="ab-photos">
          <Input id="ab-photos" value={form.gbpPhotos} onChange={set('gbpPhotos')} placeholder="e.g. 4 photos" />
        </Field>

        <Field label="Star Rating" htmlFor="ab-rating">
          <Input id="ab-rating" value={form.starRating} onChange={set('starRating')} placeholder="e.g. 3.8" />
        </Field>

        <Field label="Review Count" htmlFor="ab-reviews">
          <Input id="ab-reviews" value={form.reviewCount} onChange={set('reviewCount')} placeholder="e.g. 22" />
        </Field>

        <Field label="Website Health Score" htmlFor="ab-web">
          <Input id="ab-web" value={form.websiteScore} onChange={set('websiteScore')} placeholder="e.g. 62/100" />
        </Field>

        <Field label="Citation Consistency" htmlFor="ab-citation">
          <Input id="ab-citation" value={form.citationConsistency} onChange={set('citationConsistency')} placeholder="e.g. 70% consistent" />
        </Field>

        <Divider />

        <Field label="Keyword 1" htmlFor="ab-kw1">
          <Input id="ab-kw1" value={form.keyword1} onChange={set('keyword1')} placeholder="e.g. plumber near me" />
        </Field>

        <Field label="Position" htmlFor="ab-pos1">
          <Input id="ab-pos1" value={form.position1} onChange={set('position1')} placeholder="e.g. 14" />
        </Field>

        <Field label="Keyword 2" htmlFor="ab-kw2">
          <Input id="ab-kw2" value={form.keyword2} onChange={set('keyword2')} placeholder="e.g. emergency plumber LA" />
        </Field>

        <Field label="Position" htmlFor="ab-pos2">
          <Input id="ab-pos2" value={form.position2} onChange={set('position2')} placeholder="e.g. 23" />
        </Field>

        <Divider />

        <Field label="Priority Issue 1" span="1 / -1" htmlFor="ab-i1">
          <Input id="ab-i1" value={form.issue1} onChange={set('issue1')} placeholder="Most important finding" />
        </Field>

        <Field label="Priority Issue 2" span="1 / -1" htmlFor="ab-i2">
          <Input id="ab-i2" value={form.issue2} onChange={set('issue2')} />
        </Field>

        <Field label="Priority Issue 3" span="1 / -1" htmlFor="ab-i3">
          <Input id="ab-i3" value={form.issue3} onChange={set('issue3')} />
        </Field>

        <Field label="Quick Win 1" span="1 / -1" htmlFor="ab-qw1">
          <Input id="ab-qw1" value={form.quickWin1} onChange={set('quickWin1')} placeholder="Low-effort, high-impact action" />
        </Field>

        <Field label="Quick Win 2" span="1 / -1" htmlFor="ab-qw2">
          <Input id="ab-qw2" value={form.quickWin2} onChange={set('quickWin2')} />
        </Field>

        <Field label="Notes" span="1 / -1" htmlFor="ab-notes">
          <Textarea id="ab-notes" value={form.notes} onChange={set('notes')} placeholder="Additional context or observations…" rows={4} />
        </Field>
      </div>

      <div style={{ marginTop: 24 }}>
        <PreviewBox text={report} label="Audit Report Preview" />
      </div>

      <div style={{ marginTop: 16 }}>
        <CopyBtn text={report} label="Copy Report" />
      </div>

      <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
        <button
          type="button"
          onClick={handleSave}
          style={{
            ...baseStyles.btn,
            ...(saved ? baseStyles.btnSaved : baseStyles.btnPrimary),
          }}
        >
          {saved ? '✓ Saved' : 'Save Audit'}
        </button>
      </div>

      {saveError && (
        <div style={{ fontFamily: FONTS.mono, fontSize: '0.7rem', color: COLORS.red, marginTop: 8 }}>
          {saveError}
        </div>
      )}
    </div>
  );
}
