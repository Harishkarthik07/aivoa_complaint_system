import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { fetchComplaintById, updateComplaintStatus } from '../redux/complaintsSlice'
import SeverityBadge from '../components/SeverityBadge'
import { IconArrowLeft, IconAlert, IconSpark } from '../components/icons'

const STATUSES = ['New', 'Under Investigation', 'CAPA Initiated', 'Closed']

export default function ComplaintDetail() {
  const { id } = useParams()
  const dispatch = useDispatch()
  const complaint = useSelector((s) => s.complaints.selected)

  useEffect(() => {
    dispatch(fetchComplaintById(id))
  }, [dispatch, id])

  if (!complaint) {
    return (
      <div>
        <div className="skeleton" style={{ height: 24, width: 200, marginBottom: 20 }} />
        <div className="card"><div className="skeleton" style={{ height: 100 }} /></div>
      </div>
    )
  }

  const riskClass = (complaint.severity || 'neutral').toLowerCase()

  return (
    <div className="fade-in">
      <Link to="/" className="nav-link" style={{ display: 'inline-flex', padding: '0 0 14px', color: 'var(--ink-muted)' }}>
        <IconArrowLeft /> Back to dashboard
      </Link>

      <div className="page-header">
        <div>
          <span className="eyebrow">{complaint.complaint_type}</span>
          <h2 className="mono">{complaint.complaint_number}</h2>
        </div>
        <SeverityBadge severity={complaint.severity} />
      </div>

      {complaint.ai_duplicate_of && (
        <div
          className="card"
          style={{ background: 'var(--medium-bg)', border: '1px solid #fde5b8', color: 'var(--medium)', display: 'flex', gap: 10, alignItems: 'flex-start' }}
        >
          <IconAlert />
          <div>
            <strong>Possible duplicate.</strong> AI flagged this as a likely match for{' '}
            <span className="mono">{complaint.ai_duplicate_of}</span>.
          </div>
        </div>
      )}

      <div className={`card risk-strip ${riskClass}`}>
        <div className="card-title">Complaint details</div>
        <dl className="kv-grid">
          <dt>Product</dt>
          <dd>{complaint.product_name}</dd>
          <dt>Batch</dt>
          <dd className="mono">{complaint.batch_number}</dd>
          <dt>Customer</dt>
          <dd>{complaint.customer_name} {complaint.customer_email && <span style={{ color: 'var(--ink-muted)' }}>({complaint.customer_email})</span>}</dd>
          <dt>Description</dt>
          <dd>{complaint.description}</dd>
        </dl>

        <hr className="divider" />

        <div className="form-field" style={{ maxWidth: 280, marginBottom: 0 }}>
          <label>Status</label>
          <select
            className="select-pill"
            value={complaint.status}
            onChange={(e) => dispatch(updateComplaintStatus({ id: complaint.id, status: e.target.value }))}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        <div className="card-title"><IconSpark /> AI analysis</div>
        <dl className="kv-grid">
          <dt>Completeness</dt>
          <dd>{complaint.ai_completeness_score != null ? `${Math.round(complaint.ai_completeness_score * 100)}%` : 'N/A'}</dd>
          {complaint.ai_missing_fields && complaint.ai_missing_fields.length > 0 && (
            <>
              <dt>Missing info</dt>
              <dd>{complaint.ai_missing_fields.join(', ')}</dd>
            </>
          )}
          <dt>Risk</dt>
          <dd>{complaint.ai_risk_classification || 'N/A'} — {complaint.ai_risk_reasoning || 'no reasoning available'}</dd>
          <dt>Summary</dt>
          <dd>{complaint.ai_summary || 'N/A'}</dd>
        </dl>
      </div>

      <div className="card">
        <div className="card-title">Root cause & CAPA</div>
        <dl className="kv-grid">
          <dt>Root cause</dt>
          <dd>{complaint.ai_root_cause_suggestion || 'N/A'}</dd>
          <dt>CAPA</dt>
          <dd>{complaint.ai_capa_suggestion || 'N/A'}</dd>
        </dl>
      </div>
    </div>
  )
}
