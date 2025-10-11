import React, { useEffect, useState } from 'react';
import axios from 'axios';
import BASE_URL from '../config';

const CURRENCY = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

// define the table once so headers + cells always align
const COLUMNS = [
  { key: 'sales_rep',  label: 'Sales Rep',    align: 'left'  },
  { key: 'num_sales',  label: '# Sales',      align: 'right' },
  { key: 'total_units',label: 'Units',        align: 'right' },
  { key: 'total_sales',label: 'Revenue',      align: 'right', format: (v) => CURRENCY.format(Number(v || 0)) },
];

export default function TopRepsTable() {
  const [rows, setRows]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr]     = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await axios.get(`${BASE_URL}/api/top_reps`);
        if (!cancelled) {
          setRows(Array.isArray(res.data) ? res.data : []);
        }
      } catch (e) {
        if (!cancelled) setErr('Could not load top reps.');
        // optional: console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  if (loading) return <p className="awt-loading">Loading top sales reps…</p>;
  if (err)     return <p className="awt-error">{err}</p>;
  if (!rows.length) return <p className="awt-empty">No results yet.</p>;

  return (
    <div className="awt-table-wrap">
      <h3 className="awt-section-title">Top Sales Reps (YTD)</h3>

      <table className="awt-table" aria-label="Top Sales Representatives">
        <thead>
          <tr>
            {COLUMNS.map(col => (
              <th key={col.key} className={col.align === 'right' ? 'num' : ''}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {rows.map((row, i) => (
            <tr key={row.sales_rep ?? i}>
              {COLUMNS.map(col => {
                const raw = row[col.key];
                const val = col.format ? col.format(raw) : (raw ?? '—');
                return (
                  <td key={col.key} className={col.align === 'right' ? 'num' : ''}>
                    {val}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Optional: quick actions */}
      <div className="awt-table-actions">
        <button
          onClick={() => {
            const csv = [
              COLUMNS.map(c => c.label).join(','),
              ...rows.map(r => COLUMNS.map(c => ('' + (r[c.key] ?? '')).replaceAll(',', '')).join(',')),
            ].join('\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'top_reps.csv';
            a.click();
            URL.revokeObjectURL(url);
          }}
        >
          Export CSV
        </button>
      </div>
    </div>
  );
}
