import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import apiClient from '../api/client'

export const fetchComplaints = createAsyncThunk(
  'complaints/fetchAll',
  async (filters = {}) => {
    const params = {}
    if (filters.status) params.status = filters.status
    if (filters.severity) params.severity = filters.severity
    const res = await apiClient.get('/complaints', { params })
    return res.data
  }
)

export const fetchComplaintById = createAsyncThunk(
  'complaints/fetchOne',
  async (id) => {
    const res = await apiClient.get(`/complaints/${id}`)
    return res.data
  }
)

export const createComplaint = createAsyncThunk(
  'complaints/create',
  async (formData) => {
    const res = await apiClient.post('/complaints', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  }
)

export const updateComplaintStatus = createAsyncThunk(
  'complaints/updateStatus',
  async ({ id, status }) => {
    const res = await apiClient.patch(`/complaints/${id}/status`, { status })
    return res.data
  }
)

const complaintsSlice = createSlice({
  name: 'complaints',
  initialState: {
    items: [],
    total: 0,
    selected: null,
    status: 'idle', // idle | loading | succeeded | failed
    createStatus: 'idle',
    error: null,
  },
  reducers: {
    clearSelected(state) {
      state.selected = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchComplaints.pending, (state) => {
        state.status = 'loading'
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.items = action.payload.items
        state.total = action.payload.total
      })
      .addCase(fetchComplaints.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.error.message
      })
      .addCase(fetchComplaintById.fulfilled, (state, action) => {
        state.selected = action.payload
      })
      .addCase(createComplaint.pending, (state) => {
        state.createStatus = 'loading'
      })
      .addCase(createComplaint.fulfilled, (state, action) => {
        state.createStatus = 'succeeded'
        state.items.unshift(action.payload)
      })
      .addCase(createComplaint.rejected, (state, action) => {
        state.createStatus = 'failed'
        state.error = action.error.message
      })
      .addCase(updateComplaintStatus.fulfilled, (state, action) => {
        state.selected = action.payload
        const idx = state.items.findIndex((c) => c.id === action.payload.id)
        if (idx !== -1) state.items[idx] = action.payload
      })
  },
})

export const { clearSelected } = complaintsSlice.actions
export default complaintsSlice.reducer
