import { useEffect, useState } from 'react'
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2>Complaints ({total})</h2>
        <div style={{ display: 'flex', gap: 12 }}>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="New">New</option>
            <option value="Under Investigation">Under Investigation</option>
            <option value="CAPA Initiated">CAPA Initiated</option>
            <option value="Closed">Closed</option>
          </select>
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="">All Severities</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
        </div>
      </div>

      <div className="card">
        {status === 'loading' && <p>Loading...</p>}
        {status === 'succeeded' && items.length === 0 && <p>No complaints found.</p>}
        {items.length > 0 && (
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
                  <td>{c.complaint_number}</td>
                  <td>{c.product_name}</td>
                  <td>{c.batch_number}</td>
                  <td>{c.complaint_type}</td>
                  <td><SeverityBadge severity={c.severity} /></td>
                  <td>{c.status}</td>
                  <td>{new Date(c.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
