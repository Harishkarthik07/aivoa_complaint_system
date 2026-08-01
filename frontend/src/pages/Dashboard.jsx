import { useEffect, useMemo, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchComplaints } from '../redux/complaintsSlice'
import SeverityBadge from '../components/SeverityBadge'

export default function Dashboard() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { items, total, status } = useSelector((s) => s.complaints)
  const [statusFilter, setStatusFilter] = useState('')
  const [severityFilter, setSeverityFilter] = useState('')

  useEffect(() => {
    dispatch(fetchComplaints({ status: statusFilter, severity: severityFilter }))
  }, [dispatch, statusFilter, severityFilter])

  const stats = useMemo(() => {
    const critical = items.filter((c) => c.severity === 'Critical').length
    const open = items.filter((c) => c.status !== 'Closed').length
    const duplicates = items.filter((c) => c.ai_duplicate_of).length
    return { critical, open, duplicates }
  }, [items])

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <span className="eyebrow">Overview</span>
          <h2>Complaints</h2>
          <p>AI-triaged, sorted by what needs attention first.</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <select className="select-pill" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All statuses</option>
            <option value="New">New</option>
            <option value="Under Investigation">Under Investigation</option>
            <option value="CAPA Initiated">CAPA Initiated</option>
            <option value="Closed">Closed</option>
          </select>
          <select className="select-pill" value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="">All severities</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-value">{total}</div>
          <div className="stat-label">Total complaints</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--critical)' }}>{stats.critical}</div>
          <div className="stat-label">Critical, this view</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.open}</div>
          <div className="stat-label">Open, this view</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.duplicates}</div>
          <div className="stat-label">Flagged duplicates</div>
        </div>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {status === 'loading' && (
          <div style={{ padding: 22 }}>
            {[0, 1, 2].map((i) => (
              <div key={i} className="skeleton" style={{ height: 18, marginBottom: 12, width: `${90 - i * 12}%` }} />
            ))}
          </div>
        )}

        {status === 'succeeded' && items.length === 0 && (
          <div className="empty-state">
            <span className="eyebrow">Nothing here</span>
            <p style={{ margin: 0 }}>No complaints match these filters yet.</p>
          </div>
        )}

        {items.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Complaint #</th>
                  <th>Product</th>
                  <th>Batch</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {items.map((c) => (
                  <tr key={c.id} className="row-link" onClick={() => navigate(`/complaints/${c.id}`)}>
                    <td className="mono">{c.complaint_number}</td>
                    <td>{c.product_name}</td>
                    <td className="mono">{c.batch_number}</td>
                    <td>{c.complaint_type}</td>
                    <td><SeverityBadge severity={c.severity} /></td>
                    <td><span className="status-pill">{c.status}</span></td>
                    <td className="mono">{new Date(c.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
