import { useState, useEffect, useCallback } from 'react'
import PipelineStepper from './components/PipelineStepper'
import CandidateTable from './components/CandidateTable'
import HumanReviewModal from './components/HumanReviewModal'
import AuditTrailModal from './components/AuditTrailModal'
import BiasAuditPanel from './components/BiasAuditPanel'
import { mockPipelineData } from './data/mockData'
import { Briefcase, RefreshCw, AlertCircle } from 'lucide-react'

function App() {
  const [pipelineState, setPipelineState] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showHumanReview, setShowHumanReview] = useState(false)
  const [reviewCandidate, setReviewCandidate] = useState(null)
  const [showAuditTrail, setShowAuditTrail] = useState(false)
  const [auditTrailCandidate, setAuditTrailCandidate] = useState(null)

  // Fetch pipeline state from backend
  const fetchPipelineState = useCallback(async () => {
    try {
      setLoading(true)
      // In production, this would be an API call:
      // const response = await axios.get('/api/pipeline/current')
      // setPipelineState(response.data)
      
      // For now, use mock data
      await new Promise(resolve => setTimeout(resolve, 500)) // Simulate network delay
      setPipelineState(mockPipelineData)
      setError(null)
    } catch (err) {
      setError('Failed to fetch pipeline state')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchPipelineState()
  }, [fetchPipelineState])

  // Check if human review is needed
  useEffect(() => {
    if (pipelineState?.current_stage === 'awaiting_human_review') {
      setShowHumanReview(true)
    }
  }, [pipelineState])

  // Handle viewing audit trail
  const handleViewAuditTrail = (candidate) => {
    setAuditTrailCandidate(candidate)
    setShowAuditTrail(true)
  }

  // Handle human review request
  const handleReviewRequest = (candidate) => {
    setReviewCandidate(candidate)
    setShowHumanReview(true)
  }

  // Handle review decision
  const handleReviewDecision = async (candidateId, decision, notes) => {
    try {
      // In production:
      // await axios.post(`/api/pipeline/review/${candidateId}`, { decision, notes })
      console.log('Review decision:', { candidateId, decision, notes })
      
      // Update local state
      setPipelineState(prev => ({
        ...prev,
        current_stage: decision === 'approve' ? 'completed' : prev.current_stage,
        final_rankings: prev.final_rankings.map(r => 
          r.candidate_id === candidateId 
            ? { ...r, human_review_completed: true, human_decision: decision }
            : r
        )
      }))
      
      setShowHumanReview(false)
      setReviewCandidate(null)
    } catch (err) {
      console.error('Failed to submit review:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="w-8 h-8 text-primary-600 animate-spin" />
          <p className="text-gray-600">Loading pipeline data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-red-600">
          <AlertCircle className="w-12 h-12" />
          <p className="text-lg font-medium">{error}</p>
          <button onClick={fetchPipelineState} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Briefcase className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Recruitment Pipeline</h1>
                <p className="text-sm text-gray-500">
                  Job ID: {pipelineState?.job_id?.slice(0, 8)}...
                </p>
              </div>
            </div>
            <button 
              onClick={fetchPipelineState}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Pipeline Progress */}
        <section className="mb-8">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Pipeline Progress</h2>
            <PipelineStepper 
              currentStage={pipelineState?.current_stage} 
              stages={pipelineState?.completed_stages || []}
            />
          </div>
        </section>

        {/* Stats Overview */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="card">
            <p className="text-sm text-gray-500">Total Candidates</p>
            <p className="text-2xl font-bold text-gray-900">
              {pipelineState?.candidates?.length || 0}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-500">Shortlisted</p>
            <p className="text-2xl font-bold text-green-600">
              {pipelineState?.shortlisted_candidates?.length || 0}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-500">Pending Review</p>
            <p className="text-2xl font-bold text-amber-600">
              {pipelineState?.final_rankings?.filter(r => r.human_review_required && !r.human_review_completed).length || 0}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-500">Fairness Score</p>
            <p className="text-2xl font-bold text-primary-600">
              {pipelineState?.bias_audit_results?.overall_fairness_score 
                ? `${(pipelineState.bias_audit_results.overall_fairness_score * 100).toFixed(0)}%`
                : 'N/A'}
            </p>
          </div>
        </section>

        {/* Bias Audit Panel */}
        {pipelineState?.bias_audit_results && (
          <section className="mb-8">
            <BiasAuditPanel auditResults={pipelineState.bias_audit_results} />
          </section>
        )}

        {/* Candidate Rankings */}
        <section>
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Candidate Rankings</h2>
              <span className="text-sm text-gray-500">
                Showing {pipelineState?.final_rankings?.length || 0} candidates
              </span>
            </div>
            <CandidateTable 
              candidates={pipelineState?.final_rankings || []}
              onViewAuditTrail={handleViewAuditTrail}
              onReviewRequest={handleReviewRequest}
            />
          </div>
        </section>
      </main>

      {/* Human Review Modal */}
      <HumanReviewModal
        isOpen={showHumanReview}
        onClose={() => {
          setShowHumanReview(false)
          setReviewCandidate(null)
        }}
        candidate={reviewCandidate}
        biasFindings={pipelineState?.bias_audit_results?.findings || []}
        onDecision={handleReviewDecision}
      />

      {/* Audit Trail Modal */}
      <AuditTrailModal
        isOpen={showAuditTrail}
        onClose={() => {
          setShowAuditTrail(false)
          setAuditTrailCandidate(null)
        }}
        candidate={auditTrailCandidate}
      />
    </div>
  )
}

export default App
