import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { createComplaint } from '../redux/complaintsSlice'
import { IconSpark } from '../components/icons'

const initialForm = {
  customer_name: '',
  customer_email: '',
  customer_phone: '',
  product_name: '',
  batch_number: '',
  manufacturing_date: '',
  expiry_date: '',
  complaint_type: 'Quality',
  description: '',
  source_channel: 'Manual',
}

export default function NewComplaint() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { createStatus } = useSelector((s) => s.complaints)
  const [form, setForm] = useState(initialForm)
  const [file, setFile] = useState(null)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    const data = new FormData()
    Object.entries(form).forEach(([key, value]) => data.append(key, value))
    if (file) data.append('attachment', file)

    const result = await dispatch(createComplaint(data))
    if (createComplaint.fulfilled.match(result)) {
      navigate(`/complaints/${result.payload.id}`)
    }
  }

  const isSubmitting = createStatus === 'loading'

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <span className="eyebrow">Intake</span>
          <h2>New complaint</h2>
          <p>Submitted complaints run through five AI checks before landing on the dashboard.</p>
        </div>
      </div>

      <form className="card" onSubmit={handleSubmit}>
        <div className="card-title">Reporter</div>
        <div className="form-grid">
          <div className="form-field">
            <label>Customer name</label>
            <input name="customer_name" value={form.customer_name} onChange={handleChange} required />
          </div>
          <div className="form-field">
            <label>Email</label>
            <input name="customer_email" type="email" value={form.customer_email} onChange={handleChange} />
          </div>
          <div className="form-field">
            <label>Phone</label>
            <input name="customer_phone" value={form.customer_phone} onChange={handleChange} />
          </div>
          <div className="form-field">
            <label>Complaint type</label>
            <select name="complaint_type" value={form.complaint_type} onChange={handleChange}>
              <option>Quality</option>
              <option>Packaging</option>
              <option>Adverse Event</option>
              <option>Delivery</option>
              <option>Labeling</option>
            </select>
          </div>
        </div>

        <hr className="divider" />

        <div className="card-title">Product</div>
        <div className="form-grid">
          <div className="form-field">
            <label>Product name</label>
            <input name="product_name" value={form.product_name} onChange={handleChange} required />
          </div>
          <div className="form-field">
            <label>Batch number</label>
            <input name="batch_number" value={form.batch_number} onChange={handleChange} required />
          </div>
          <div className="form-field">
            <label>Manufacturing date</label>
            <input name="manufacturing_date" type="date" value={form.manufacturing_date} onChange={handleChange} />
          </div>
          <div className="form-field">
            <label>Expiry date</label>
            <input name="expiry_date" type="date" value={form.expiry_date} onChange={handleChange} />
          </div>
        </div>

        <hr className="divider" />

        <div className="form-field">
          <label>Description</label>
          <textarea
            name="description"
            rows={5}
            value={form.description}
            onChange={handleChange}
            required
            placeholder="What was observed, when, and how it was discovered."
          />
        </div>

        <div className="form-field">
          <label>Attachment (PDF, email, or image — optional)</label>
          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        </div>

        <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7 }}>
              <IconSpark /> Analyzing with AI…
            </span>
          ) : (
            'Submit complaint'
          )}
        </button>
      </form>
    </div>
  )
}
