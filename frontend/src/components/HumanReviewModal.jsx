import { useState } from 'react'
import { 
  X, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  FileText,
  MessageSquare
} from 'lucide-react'

function HumanReviewModal({ isOpen, onClose, candidate, biasFindings, onDecision }) {
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!isOpen) return null

  const handleDecision = async (decision) => {
    setIsSubmitting(true)
    try {
      await onDecision(candidate?.candidate_id, decision, notes)
      setNotes('')
    } finally {
      setIsSubmitting(false)
    }
  }

  const getSeverityStyles = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-amber-100 text-amber-800 border-amber-200'
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-orange-600" />
      case 'medium':
        return <AlertCircle className="w-5 h-5 text-amber-600" />
      default:
        return <AlertCircle className="w-5 h-5 text-blue-600" />
    }
  }

  // Filter findings related to this candidate
  const relevantFindings = biasFindings.filter(f => 
    f.affected_items?.includes(candidate?.candidate_id) ||
    f.affected_items?.includes('all') ||
    f.affected_items?.includes('all_candidates') ||
    f.affected_items?.includes('all_ranked')
  )

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
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-amber-50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-100 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-amber-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Human Review Required</h2>
                <p className="text-sm text-gray-600">
                  Candidate: {candidate?.candidate_id?.slice(0, 12)}...
                </p>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 overflow-y-auto max-h-[calc(90vh-200px)]">
            {/* Candidate Summary */}
            {candidate && (
              <div className="mb-6 p-4 bg-gray-50 rounded-xl">
                <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Candidate Summary
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Match Score</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {(candidate.final_composite_score * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Recommendation</p>
                    <p className="text-sm font-medium text-gray-900 capitalize">
                      {candidate.recommendation?.replace(/_/g, ' ')}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Resume Score</p>
                    <p className="text-sm text-gray-600">
                      {(candidate.resume_match_score * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Test Score</p>
                    <p className="text-sm text-gray-600">
                      {(candidate.test_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
                
                {candidate.human_review_reason && (
                  <div className="mt-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
                    <p className="text-sm text-amber-800">
                      <span className="font-medium">Review Reason:</span> {candidate.human_review_reason}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Bias Findings */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Bias Audit Findings ({relevantFindings.length})
              </h3>
              
              {relevantFindings.length === 0 ? (
                <div className="p-4 bg-green-50 rounded-xl border border-green-200">
                  <div className="flex items-center gap-2 text-green-700">
                    <CheckCircle className="w-5 h-5" />
                    <span className="text-sm font-medium">No bias concerns found for this candidate</span>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {relevantFindings.map((finding, idx) => (
                    <div 
                      key={idx}
                      className={`p-4 rounded-xl border ${getSeverityStyles(finding.severity)}`}
                    >
                      <div className="flex items-start gap-3">
                        {getSeverityIcon(finding.severity)}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium uppercase">
                              {finding.severity}
                            </span>
                            <span className="text-xs opacity-75">
                              • {finding.category?.replace(/_/g, ' ')}
                            </span>
                          </div>
                          <p className="text-sm">{finding.description}</p>
                          {finding.recommendation && (
                            <p className="text-xs mt-2 opacity-75">
                              <span className="font-medium">Recommendation:</span> {finding.recommendation}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Review Notes */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-900 mb-2">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Review Notes (Optional)
                </div>
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any notes about your decision..."
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              />
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50">
            <button
              onClick={onClose}
              className="btn-secondary"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              onClick={() => handleDecision('reject')}
              className="btn-danger flex items-center gap-2"
              disabled={isSubmitting}
            >
              <XCircle className="w-4 h-4" />
              Reject
            </button>
            <button
              onClick={() => handleDecision('approve')}
              className="btn-success flex items-center gap-2"
              disabled={isSubmitting}
            >
              <CheckCircle className="w-4 h-4" />
              Approve
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HumanReviewModal
