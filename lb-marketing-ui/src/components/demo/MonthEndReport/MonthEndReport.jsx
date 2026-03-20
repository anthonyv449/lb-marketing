/**
 * @fileoverview Month-end performance report builder. Captures before/after metrics,
 * computes deltas with colour coding, and generates a copyable report.
 */

import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { COLORS, FONTS, baseStyles } from '../shared/styles';
import { Field, Input, Textarea, Divider, CopyBtn, PreviewBox, Label } from '../shared/FormFields';
import { calcDelta, formatReportText } from './MonthEndReport.utils';
import { fetchMonthEndReport, saveMonthEndReport, fetchAuditReport } from '../api/client';

const EMPTY = {
  businessName: '', reportPeriod: '',
  keyword1: '', kw1Before: '', kw1After: '',
  keyword2: '', kw2Before: '', kw2After: '',
  reviewsBefore: '', reviewsAfter: '',
  ratingBefore: '', ratingAfter: '',
  viewsBefore: '', viewsAfter: '',
  changesMade: '', highlights: '', month2Plan: '',
};

function MetricRow({ label, beforeKey, afterKey, form, set, invert = false }) {
  const delta = useMemo(
    () => calcDelta(form[beforeKey], form[afterKey], invert),
    [form[beforeKey], form[afterKey], invert],
  );

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, alignItems: 'end' }}>
      <Field label={`${label} — Before`} htmlFor={`me-${beforeKey}`}>
        <Input id={`me-${beforeKey}`} value={form[beforeKey]} onChange={set(beforeKey)} placeholder="Before" />
      </Field>
      <Field label={`${label} — After`} htmlFor={`me-${afterKey}`}>
        <Input id={`me-${afterKey}`} value={form[afterKey]} onChange={set(afterKey)} placeholder="After" />
      </Field>
      <div>
        <Label>Delta</Label>
        <div style={{
          fontFamily: FONTS.heading, fontSize: '1.1rem', color: delta.color,
          background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 4,
          padding: '10px 14px', textAlign: 'center', minHeight: 20,
        }}>
          {delta.label}
        </div>
      </div>
    </div>
  );
}

export default function MonthEndReport({ clientId, businessName = '' }) {
  const [form, setForm] = useState({ ...EMPTY });
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState('');

  useEffect(() => {
    if (!clientId) return;
    Promise.all([
      fetchMonthEndReport(clientId),
      fetchAuditReport(clientId),
    ]).then(([reportData, auditData]) => {
      if (reportData) {
        // Saved report — use it; businessName comes from prop (not stored in report)
        setForm({ ...EMPTY, businessName, ...reportData });
      } else if (auditData) {
        // No saved report — seed "before" values from audit
        setForm({
          ...EMPTY,
          businessName,
          keyword1: auditData.keyword1 || '',
          kw1Before: auditData.position1 || '',
          keyword2: auditData.keyword2 || '',
          kw2Before: auditData.position2 || '',
          reviewsBefore: auditData.reviewCount || '',
          ratingBefore: auditData.starRating || '',
        });
      } else {
        setForm((prev) => ({ ...prev, businessName }));
      }
    }).catch(() => {
      setForm((prev) => ({ ...prev, businessName }));
    });
  }, [clientId, businessName]);

  const set = useCallback((key) => (e) => {
    setForm((prev) => ({ ...prev, [key]: e.target.value }));
  }, []);

  const report = useMemo(() => formatReportText(form), [form]);

  const handleSave = async () => {
    if (!clientId) {
      setSaveError('Set an engagement ID to persist this report.');
      return;
    }
    setSaveError('');
    try {
      const savedReport = await saveMonthEndReport(clientId, form);
      setForm((prev) => ({ ...prev, ...savedReport }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (error) {
      setSaveError(error.message || 'Failed to save month-end report.');
    }
  };

  return (
    <div style={baseStyles.sectionBox}>
      <h2 style={{ fontFamily: FONTS.heading, color: COLORS.cream, fontSize: '1.6rem', marginTop: 0, marginBottom: 4 }}>
        Month-End Report
      </h2>
      <p style={{ fontFamily: FONTS.body, color: COLORS.muted, fontSize: '1rem', marginTop: 0, marginBottom: 24 }}>
        Compare before-and-after metrics and generate the client performance report.
      </p>

      {/* Header */}
      <div style={baseStyles.grid2col}>
        <Field label="Business Name" htmlFor="me-biz">
          <Input id="me-biz" value={form.businessName} onChange={set('businessName')} placeholder="Client business name" />
        </Field>
        <Field label="Report Period" htmlFor="me-period">
          <Input id="me-period" value={form.reportPeriod} onChange={set('reportPeriod')} placeholder="e.g. Feb 1 – Feb 28, 2026" />
        </Field>
      </div>

      {/* Rankings */}
      <div style={{ ...baseStyles.sectionBox, marginTop: 24 }}>
        <div style={{ ...baseStyles.label, marginBottom: 16 }}>Search Rankings</div>

        <Field label="Keyword 1" span="1 / -1" htmlFor="me-kw1">
          <Input id="me-kw1" value={form.keyword1} onChange={set('keyword1')} placeholder="e.g. plumber near me" />
        </Field>
        <div style={{ marginTop: 12 }}>
          <MetricRow label="Position" beforeKey="kw1Before" afterKey="kw1After" form={form} set={set} invert />
        </div>

        <div style={{ margin: '16px 0' }}>
          <Divider />
        </div>

        <Field label="Keyword 2" span="1 / -1" htmlFor="me-kw2">
          <Input id="me-kw2" value={form.keyword2} onChange={set('keyword2')} placeholder="e.g. emergency plumber LA" />
        </Field>
        <div style={{ marginTop: 12 }}>
          <MetricRow label="Position" beforeKey="kw2Before" afterKey="kw2After" form={form} set={set} invert />
        </div>
      </div>

      {/* Reviews & Visibility */}
      <div style={baseStyles.sectionBox}>
        <div style={{ ...baseStyles.label, marginBottom: 16 }}>Reviews & Visibility</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <MetricRow label="Review Count" beforeKey="reviewsBefore" afterKey="reviewsAfter" form={form} set={set} />
          <MetricRow label="Star Rating" beforeKey="ratingBefore" afterKey="ratingAfter" form={form} set={set} />
          <MetricRow label="Profile Views" beforeKey="viewsBefore" afterKey="viewsAfter" form={form} set={set} />
        </div>
      </div>

      {/* Freetext */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        <Field label="Changes Made" span="1 / -1" htmlFor="me-changes">
          <Textarea id="me-changes" value={form.changesMade} onChange={set('changesMade')} placeholder="What was done this month…" rows={4} />
        </Field>
        <Field label="Highlights" span="1 / -1" htmlFor="me-highlights">
          <Textarea id="me-highlights" value={form.highlights} onChange={set('highlights')} placeholder="Key wins and milestones…" rows={3} />
        </Field>
        <Field label="Month 2 Plan" span="1 / -1" htmlFor="me-m2">
          <Textarea id="me-m2" value={form.month2Plan} onChange={set('month2Plan')} placeholder="What's planned for next month…" rows={3} />
        </Field>
      </div>

      <div style={{ marginTop: 24 }}>
        <PreviewBox text={report} label="Report Preview" />
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
          {saved ? '✓ Saved' : 'Save Report'}
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
