/**
 * @fileoverview Shared hook managing task-checkbox state with optional backend persistence.
 * Debounces saves by 800ms to avoid excessive API calls while the user clicks through tasks.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { fetchTaskState, saveTaskState } from '../api/client';

export default function useTaskState(clientId) {
  const [checked, setChecked] = useState({});
  const timerRef = useRef(null);

  useEffect(() => {
    if (!clientId) return;
    fetchTaskState(clientId).then((data) => {
      if (data && Object.keys(data).length) setChecked(data);
    });
  }, [clientId]);

  const persistDebounced = useCallback(
    (next) => {
      if (!clientId) return;
      clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        saveTaskState(clientId, next);
      }, 800);
    },
    [clientId],
  );

  const toggle = useCallback(
    (taskId) => {
      setChecked((prev) => {
        const next = { ...prev, [taskId]: !prev[taskId] };
        persistDebounced(next);
        return next;
      });
    },
    [persistDebounced],
  );

  const reset = useCallback(() => {
    setChecked({});
    if (clientId) saveTaskState(clientId, {});
  }, [clientId]);

  useEffect(() => () => clearTimeout(timerRef.current), []);

  return { checked, toggle, reset };
}
