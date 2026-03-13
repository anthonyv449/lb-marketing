/**
 * @fileoverview Shared hook managing task-checkbox state with backend persistence.
 * On load: GET tasks. On select: PUT. On deselect: DELETE. Reset: batch DELETE.
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchTaskState, upsertTask, deleteTask, batchDeleteTasks } from '../api/client';

export default function useTaskState(clientId, allTaskIds = []) {
  const [checked, setChecked] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!clientId) {
      setLoading(false);
      return;
    }
    const abortController = new AbortController();
    setLoading(true);
    fetchTaskState(clientId, abortController.signal)
      .then((data) => {
        if (!abortController.signal.aborted) {
          setChecked(data && typeof data === 'object' ? data : {});
        }
      })
      .catch((err) => {
        if (!abortController.signal.aborted && err?.name !== 'AbortError') {
          setChecked({});
        }
      })
      .finally(() => {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      });
    return () => abortController.abort();
  }, [clientId]);

  const toggle = useCallback(
    (taskId) => {
      const nextValue = !checked[taskId];
      setChecked((prev) => ({ ...prev, [taskId]: nextValue }));
      if (!clientId) return;
      if (nextValue) {
        upsertTask(clientId, taskId, true).catch(console.error);
      } else {
        deleteTask(clientId, taskId).catch(console.error);
      }
    },
    [clientId, checked],
  );

  const reset = useCallback(() => {
    if (!clientId || !allTaskIds || allTaskIds.length === 0) {
      setChecked({});
      return;
    }
    batchDeleteTasks(clientId, allTaskIds)
      .then(() => setChecked({}))
      .catch(console.error);
  }, [clientId, allTaskIds]);

  return { checked, toggle, reset, loading };
}
