/**
 * @fileoverview Demo task checklist organised by week. Shows overall and per-week
 * progress, critical-task badges, and optional vertical-specific extras.
 */

import React, { useState, useMemo } from 'react';
import { COLORS, FONTS, baseStyles } from '../shared/styles';
import { WEEKS, VERTICAL_EXTRAS } from './TaskTracker.data';
import useTaskState from '../hooks/useTaskState';

function pct(done, total) {
  return total === 0 ? 0 : Math.round((done / total) * 100);
}

function ProgressBar({ value, height = 6, color = COLORS.accent }) {
  return (
    <div style={{ width: '100%', background: COLORS.bgLight, borderRadius: height / 2, overflow: 'hidden', height }}>
      <div style={{ width: `${value}%`, height: '100%', background: color, borderRadius: height / 2, transition: 'width 0.4s ease' }} />
    </div>
  );
}

export default function TaskTracker({ vertical, clientId }) {
  const { checked, toggle, reset } = useTaskState(clientId);
  const [activeWeek, setActiveWeek] = useState(1);

  const extras = vertical && VERTICAL_EXTRAS[vertical] ? VERTICAL_EXTRAS[vertical] : null;

  const allIds = useMemo(() => {
    const ids = WEEKS.flatMap((w) => w.tasks.map((t) => t.id));
    if (extras) ids.push(...extras.items.map((i) => i.id));
    return ids;
  }, [extras]);

  const overallDone = allIds.filter((id) => checked[id]).length;
  const overallPct = pct(overallDone, allIds.length);

  const weekStats = useMemo(() => {
    return WEEKS.map((w) => {
      let ids = w.tasks.map((t) => t.id);
      if (extras && extras.weeks.includes(w.week)) {
        ids = ids.concat(extras.items.map((i) => i.id));
      }
      const done = ids.filter((id) => checked[id]).length;
      return { week: w.week, done, total: ids.length, pct: pct(done, ids.length) };
    });
  }, [checked, extras]);

  const activeData = WEEKS.find((w) => w.week === activeWeek);
  const activeStat = weekStats.find((s) => s.week === activeWeek);
  const showExtras = extras && extras.weeks.includes(activeWeek);

  const tabBase = {
    ...baseStyles.btn,
    flex: 1,
    textAlign: 'center',
    padding: '10px 6px',
    fontSize: '0.68rem',
  };

  return (
    <div style={baseStyles.sectionBox}>
      <h2 style={{ fontFamily: FONTS.heading, color: COLORS.cream, fontSize: '1.6rem', marginTop: 0, marginBottom: 4 }}>
        Demo Task Tracker
      </h2>
      <p style={{ fontFamily: FONTS.body, color: COLORS.muted, fontSize: '1rem', marginTop: 0, marginBottom: 20 }}>
        Track every deliverable across the four-week engagement.
      </p>

      {/* Overall progress */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 8 }}>
        <span style={{ fontFamily: FONTS.heading, fontSize: '2.8rem', color: COLORS.accent, lineHeight: 1 }}>
          {overallPct}%
        </span>
        <span style={{ fontFamily: FONTS.mono, fontSize: '0.72rem', color: COLORS.muted, letterSpacing: '0.06em' }}>
          {overallDone} / {allIds.length} tasks complete
        </span>
      </div>
      <ProgressBar value={overallPct} height={8} />

      {/* Week tabs */}
      <div style={{ display: 'flex', gap: 8, marginTop: 24, marginBottom: 20 }}>
        {WEEKS.map((w) => {
          const s = weekStats.find((st) => st.week === w.week);
          const active = w.week === activeWeek;
          return (
            <button
              key={w.week}
              type="button"
              onClick={() => setActiveWeek(w.week)}
              style={{
                ...tabBase,
                borderColor: active ? COLORS.accent : COLORS.border,
                color: active ? COLORS.accent : COLORS.muted,
                background: active ? `${COLORS.accent}12` : 'transparent',
              }}
            >
              {w.label} — {s.pct}%
            </button>
          );
        })}
      </div>

      {/* Active week panel */}
      {activeData && (
        <div style={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 6, padding: 20 }}>
          <div style={{ fontFamily: FONTS.mono, fontSize: '0.68rem', color: COLORS.muted, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>
            {activeData.theme}
          </div>
          <div style={{ fontFamily: FONTS.body, fontSize: '1rem', color: COLORS.accent, fontStyle: 'italic', marginBottom: 14 }}>
            Deliverable: {activeData.deliverable}
          </div>
          <ProgressBar value={activeStat.pct} height={5} />

          <div style={{ marginTop: 16 }}>
            {activeData.tasks.map((task) => (
              <TaskRow key={task.id} task={task} done={!!checked[task.id]} onToggle={() => toggle(task.id)} />
            ))}
          </div>

          {showExtras && (
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: `1px solid ${COLORS.border}` }}>
              <span style={{
                fontFamily: FONTS.mono, fontSize: '0.65rem', textTransform: 'uppercase',
                letterSpacing: '0.1em', color: COLORS.blue, background: `${COLORS.blue}18`,
                padding: '3px 10px', borderRadius: 3,
              }}>
                {extras.label}
              </span>
              <div style={{ marginTop: 12 }}>
                {extras.items.map((item) => (
                  <TaskRow key={item.id} task={item} done={!!checked[item.id]} onToggle={() => toggle(item.id)} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
        <button type="button" onClick={reset} style={{ ...baseStyles.btn, ...baseStyles.btnSecondary, fontSize: '0.68rem' }}>
          Reset All
        </button>
      </div>
    </div>
  );
}

function TaskRow({ task, done, onToggle }) {
  return (
    <label
      style={{
        display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0',
        cursor: 'pointer', fontFamily: FONTS.body, fontSize: '0.95rem',
        color: done ? COLORS.muted : COLORS.cream,
        textDecoration: done ? 'line-through' : 'none',
      }}
    >
      <input
        type="checkbox"
        checked={done}
        onChange={onToggle}
        style={{ accentColor: COLORS.accent, width: 16, height: 16, cursor: 'pointer' }}
      />
      <span style={{ flex: 1 }}>{task.text}</span>
      {task.critical && !done && (
        <span style={{
          fontFamily: FONTS.mono, fontSize: '0.6rem', color: COLORS.gold,
          border: `1px solid ${COLORS.gold}`, borderRadius: 3, padding: '2px 7px',
          letterSpacing: '0.06em', textTransform: 'uppercase',
        }}>
          key
        </span>
      )}
    </label>
  );
}
