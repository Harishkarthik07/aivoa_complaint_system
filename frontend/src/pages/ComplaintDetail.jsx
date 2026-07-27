import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { fetchComplaintById, updateComplaintStatus } from '../redux/complaintsSlice'
import SeverityBadge from '../components/SeverityBadge'

const STATUSES = ['New', 'Under Investigation', 'CAPA Initiated', 'Closed']

export default function ComplaintDetail() {
  const { id } = useParams()
  const dispatch = useDispatch()
  const complaint = useSelector((s) => s.complaints.selected)

  useEffect(() => {
    dispatch(fetchComplaintById(id))
  }, [dispatch, id])

  if (!complaint) return <p>Loading...</p>

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2>{complaint.complaint_number}</h2>
        <SeverityBadge severity={complaint.severity} />
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Complaint Details</h3>
        <p><strong>Product:</strong> {complaint.product_name} (Batch {complaint.batch_number})</p>
        <p><strong>Customer:</strong> {complaint.customer_name} {complaint.customer_email && `(${complaint.customer_email})`}</p>
        <p><strong>Type:</strong> {complaint.complaint_type}</p>
        <p><strong>Description:</strong> {complaint.description}</p>

        <div className="form-field" style={{ maxWidth: 300, marginTop: 16 }}>
          <label>Status</label>
          <select
            value={complaint.status}
            onChange={(e) => dispatch(updateComplaintStatus({ id: complaint.id, status: e.target.value }))}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3>AI Analysis</h3>
        <p><strong>Completeness Score:</strong> {complaint.ai_completeness_score != null ? `${Math.round(complaint.ai_completeness_score * 100)}%` : 'N/A'}</p>
        {complaint.ai_missing_fields && complaint.ai_missing_fields.length > 0 && (
          <p><strong>Missing Info:</strong> {complaint.ai_missing_fields.join(', ')}</p>
        )}
        <p><strong>Risk Classification:</strong> {complaint.ai_risk_classification || 'N/A'}</p>
        <p><strong>Risk Reasoning:</strong> {complaint.ai_risk_reasoning || 'N/A'}</p>
        <p><strong>Summary:</strong> {complaint.ai_summary || 'N/A'}</p>
        {complaint.ai_duplicate_of && (
          <p style={{ color: '#d92d20' }}>
            <strong>Possible Duplicate Of:</strong> {complaint.ai_duplicate_of}
          </p>
        )}
      </div>

      <div className="card">
        <h3>Root Cause & CAPA Suggestions</h3>
        <p><strong>Root Cause Hypothesis:</strong> {complaint.ai_root_cause_suggestion || 'N/A'}</p>
        <p><strong>CAPA Recommendation:</strong> {complaint.ai_capa_suggestion || 'N/A'}</p>
      </div>
    </div>
  )
}
