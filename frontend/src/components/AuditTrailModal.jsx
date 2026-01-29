import { X, Clock, CheckCircle, AlertCircle, Bot, User } from 'lucide-react'

function AuditTrailModal({ isOpen, onClose, candidate }) {
  if (!isOpen || !candidate) return null

  // Mock audit trail data - in production this would come from the backend
  const auditTrail = candidate.audit_trail || [
    {
      timestamp: '2026-01-29T10:00:00Z',
      agent: 'ResumeParserAgent',
      action: 'Resume parsed',
      details: 'Extracted skills, experience, and education from resume',
      confidence: 0.92,
    },
    {
      timestamp: '2026-01-29T10:01:00Z',
      agent: 'MatcherAgent',
      action: 'Match calculated',
      details: `Skills: ${(candidate.resume_match_score * 100).toFixed(0)}% match. Experience meets requirements.`,
      confidence: 0.88,
    },
    {
      timestamp: '2026-01-29T10:02:00Z',
      agent: 'ShortlisterAgent',
      action: 'Candidate shortlisted',
      details: 'Score exceeded threshold of 0.7',
      confidence: 0.95,
    },
    {
      timestamp: '2026-01-29T10:05:00Z',
      agent: 'TestEvaluatorAgent',
      action: 'Test evaluated',
      details: `Scored ${(candidate.test_score * 100).toFixed(0)}% on technical assessment`,
      confidence: 0.99,
    },
    {
      timestamp: '2026-01-29T10:06:00Z',
      agent: 'RankerAgent',
      action: 'Final ranking assigned',
      details: `Ranked #${candidate.rank} with composite score of ${(candidate.final_composite_score * 100).toFixed(0)}%`,
      confidence: 0.90,
    },
    {
      timestamp: '2026-01-29T10:07:00Z',
      agent: 'BiasAuditorAgent',
      action: candidate.bias_audit_passed ? 'Audit passed' : 'Audit flagged for review',
      details: candidate.bias_audit_passed 
        ? 'No bias concerns detected'
        : 'Potential concerns flagged for human review',
      confidence: 0.95,
    },
  ]

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getAgentIcon = (agent) => {
    return <Bot className="w-4 h-4" />
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600'
    if (confidence >= 0.7) return 'text-blue-600'
    if (confidence >= 0.5) return 'text-amber-600'
    return 'text-red-600'
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Audit Trail</h2>
              <p className="text-sm text-gray-600">
                Candidate: {candidate.candidate_id?.slice(0, 12)}...
              </p>
            </div>
            <button 
              onClick={onClose}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 overflow-y-auto max-h-[calc(90vh-140px)]">
            {/* Summary Cards */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-gray-50 rounded-xl">
                <p className="text-xs text-gray-500">Final Score</p>
                <p className="text-xl font-bold text-gray-900">
                  {(candidate.final_composite_score * 100).toFixed(0)}%
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-xl">
                <p className="text-xs text-gray-500">Rank</p>
                <p className="text-xl font-bold text-gray-900">#{candidate.rank}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-xl">
                <p className="text-xs text-gray-500">Audit Status</p>
                <div className="flex items-center gap-1 mt-1">
                  {candidate.bias_audit_passed ? (
                    <>
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="text-sm font-medium text-green-600">Passed</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-5 h-5 text-amber-600" />
                      <span className="text-sm font-medium text-amber-600">Review</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
              
              <div className="space-y-6">
                {auditTrail.map((entry, idx) => (
                  <div key={idx} className="relative flex gap-4">
                    {/* Timeline dot */}
                    <div className="relative z-10 flex items-center justify-center w-8 h-8 bg-white border-2 border-gray-200 rounded-full">
                      {getAgentIcon(entry.agent)}
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 pb-6">
                      <div className="p-4 bg-gray-50 rounded-xl">
                        {/* Header */}
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-900">
                            {entry.agent.replace('Agent', '')}
                          </span>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <Clock className="w-3 h-3" />
                            {formatTimestamp(entry.timestamp)}
                          </div>
                        </div>
                        
                        {/* Action */}
                        <p className="text-sm font-medium text-primary-700 mb-1">
                          {entry.action}
                        </p>
                        
                        {/* Details */}
                        <p className="text-sm text-gray-600 mb-2">
                          {entry.details}
                        </p>
                        
                        {/* Confidence */}
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">Confidence:</span>
                          <span className={`text-xs font-medium ${getConfidenceColor(entry.confidence)}`}>
                            {(entry.confidence * 100).toFixed(0)}%
                          </span>
                          <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                entry.confidence >= 0.9 ? 'bg-green-500' :
                                entry.confidence >= 0.7 ? 'bg-blue-500' :
                                entry.confidence >= 0.5 ? 'bg-amber-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${entry.confidence * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Human review entry if applicable */}
                {candidate.human_review_completed && (
                  <div className="relative flex gap-4">
                    <div className="relative z-10 flex items-center justify-center w-8 h-8 bg-primary-100 border-2 border-primary-500 rounded-full">
                      <User className="w-4 h-4 text-primary-600" />
                    </div>
                    <div className="flex-1">
                      <div className="p-4 bg-primary-50 rounded-xl border border-primary-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-900">
                            Human Reviewer
                          </span>
                          <span className="text-xs text-gray-500">Manual Review</span>
                        </div>
                        <p className="text-sm font-medium text-primary-700">
                          Decision: {candidate.human_decision === 'approve' ? 'Approved' : 'Rejected'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end px-6 py-4 border-t border-gray-200 bg-gray-50">
            <button onClick={onClose} className="btn-secondary">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuditTrailModal
