import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens, etc.
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access')
    }
    return Promise.reject(error)
  }
)

// Pipeline API endpoints
export const pipelineApi = {
  // Get current pipeline state
  getCurrentState: async () => {
    const response = await api.get('/pipeline/current')
    return response.data
  },

  // Get pipeline by ID
  getPipelineById: async (pipelineId) => {
    const response = await api.get(`/pipeline/${pipelineId}`)
    return response.data
  },

  // Start a new pipeline
  startPipeline: async (jobId, resumeIds) => {
    const response = await api.post('/pipeline/start', { 
      job_id: jobId, 
      resume_ids: resumeIds 
    })
    return response.data
  },

  // Get pipeline history
  getPipelineHistory: async (limit = 10) => {
    const response = await api.get('/pipeline/history', { params: { limit } })
    return response.data
  },
}

// Human Review API endpoints
export const reviewApi = {
  // Submit human review decision
  submitReview: async (candidateId, decision, notes = '') => {
    const response = await api.post(`/review/${candidateId}`, {
      decision,
      notes,
      reviewed_at: new Date().toISOString(),
    })
    return response.data
  },

  // Get pending reviews
  getPendingReviews: async () => {
    const response = await api.get('/review/pending')
    return response.data
  },

  // Get review history for a candidate
  getReviewHistory: async (candidateId) => {
    const response = await api.get(`/review/history/${candidateId}`)
    return response.data
  },
}

// Candidates API endpoints
export const candidatesApi = {
  // Get all candidates for a pipeline
  getCandidates: async (pipelineId) => {
    const response = await api.get(`/candidates/${pipelineId}`)
    return response.data
  },

  // Get candidate details
  getCandidateDetails: async (candidateId) => {
    const response = await api.get(`/candidates/details/${candidateId}`)
    return response.data
  },

  // Get candidate audit trail
  getAuditTrail: async (candidateId) => {
    const response = await api.get(`/candidates/${candidateId}/audit-trail`)
    return response.data
  },
}

// Jobs API endpoints
export const jobsApi = {
  // Get all jobs
  getJobs: async () => {
    const response = await api.get('/jobs')
    return response.data
  },

  // Get job by ID
  getJobById: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}`)
    return response.data
  },

  // Create new job
  createJob: async (jobData) => {
    const response = await api.post('/jobs', jobData)
    return response.data
  },

  // Upload job description file
  uploadJobDescription: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/jobs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

// Resumes API endpoints
export const resumesApi = {
  // Upload resumes
  uploadResumes: async (files) => {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    const response = await api.post('/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  // Get resume by ID
  getResumeById: async (resumeId) => {
    const response = await api.get(`/resumes/${resumeId}`)
    return response.data
  },
}

// Bias Audit API endpoints
export const biasApi = {
  // Get audit results for a pipeline
  getAuditResults: async (pipelineId) => {
    const response = await api.get(`/bias-audit/${pipelineId}`)
    return response.data
  },

  // Request re-audit
  requestReaudit: async (pipelineId) => {
    const response = await api.post(`/bias-audit/${pipelineId}/reaudit`)
    return response.data
  },
}

export default api
