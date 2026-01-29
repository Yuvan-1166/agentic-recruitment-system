import { useState } from 'react'
import { 
  Eye, 
  AlertTriangle, 
  CheckCircle, 
  ChevronUp, 
  ChevronDown,
  Star,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'

function CandidateTable({ candidates, onViewAuditTrail, onReviewRequest }) {
  const [sortField, setSortField] = useState('rank')
  const [sortDirection, setSortDirection] = useState('asc')
  const [expandedRow, setExpandedRow] = useState(null)

  // Sort candidates
  const sortedCandidates = [...candidates].sort((a, b) => {
    let aVal = a[sortField]
    let bVal = b[sortField]
    
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }
    
    if (sortDirection === 'asc') {
      return aVal > bVal ? 1 : -1
    }
    return aVal < bVal ? 1 : -1
  })

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const getScoreColor = (score) => {
    if (score >= 0.85) return 'text-green-600 bg-green-50'
    if (score >= 0.7) return 'text-blue-600 bg-blue-50'
    if (score >= 0.5) return 'text-amber-600 bg-amber-50'
    return 'text-red-600 bg-red-50'
  }

  const getRecommendationBadge = (recommendation) => {
    const badges = {
      strongly_recommend: { color: 'bg-green-100 text-green-800', label: 'Strongly Recommend' },
      recommend: { color: 'bg-blue-100 text-blue-800', label: 'Recommend' },
      consider: { color: 'bg-amber-100 text-amber-800', label: 'Consider' },
      not_recommended: { color: 'bg-red-100 text-red-800', label: 'Not Recommended' },
    }
    const badge = badges[recommendation] || { color: 'bg-gray-100 text-gray-800', label: recommendation }
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badge.color}`}>
        {badge.label}
      </span>
    )
  }

  const SortHeader = ({ field, children }) => (
    <th 
      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-50"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-1">
        {children}
        {sortField === field && (
          sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
        )}
      </div>
    </th>
  )

  if (candidates.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No candidates to display</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <SortHeader field="rank">Rank</SortHeader>
            <SortHeader field="candidate_id">Candidate</SortHeader>
            <SortHeader field="final_composite_score">Match Score</SortHeader>
            <SortHeader field="resume_match_score">Resume</SortHeader>
            <SortHeader field="test_score">Test</SortHeader>
            <SortHeader field="recommendation">Recommendation</SortHeader>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedCandidates.map((candidate) => (
            <>
              <tr 
                key={candidate.candidate_id} 
                className={`hover:bg-gray-50 transition-colors ${
                  expandedRow === candidate.candidate_id ? 'bg-gray-50' : ''
                }`}
              >
                {/* Rank */}
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    {candidate.rank <= 3 && (
                      <Star className={`w-4 h-4 ${
                        candidate.rank === 1 ? 'text-yellow-500 fill-yellow-500' :
                        candidate.rank === 2 ? 'text-gray-400 fill-gray-400' :
                        'text-amber-600 fill-amber-600'
                      }`} />
                    )}
                    <span className="text-sm font-medium text-gray-900">
                      #{candidate.rank}
                    </span>
                  </div>
                </td>

                {/* Candidate ID */}
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {candidate.candidate_id.slice(0, 12)}...
                  </div>
                </td>

                {/* Match Score */}
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className={`inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-semibold ${getScoreColor(candidate.final_composite_score)}`}>
                    {(candidate.final_composite_score * 100).toFixed(0)}%
                  </div>
                </td>

                {/* Resume Score */}
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-1">
                    <span className="text-sm text-gray-600">
                      {(candidate.resume_match_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </td>

                {/* Test Score */}
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-1">
                    <span className="text-sm text-gray-600">
                      {(candidate.test_score * 100).toFixed(0)}%
                    </span>
                    {candidate.test_score > candidate.resume_match_score && (
                      <TrendingUp className="w-4 h-4 text-green-500" />
                    )}
                    {candidate.test_score < candidate.resume_match_score && (
                      <TrendingDown className="w-4 h-4 text-red-500" />
                    )}
                    {candidate.test_score === candidate.resume_match_score && (
                      <Minus className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                </td>

                {/* Recommendation */}
                <td className="px-4 py-4 whitespace-nowrap">
                  {getRecommendationBadge(candidate.recommendation)}
                </td>

                {/* Status */}
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    {candidate.human_review_required && !candidate.human_review_completed ? (
                      <span className="flex items-center gap-1 text-amber-600">
                        <AlertTriangle className="w-4 h-4" />
                        <span className="text-xs font-medium">Review Needed</span>
                      </span>
                    ) : candidate.bias_audit_passed ? (
                      <span className="flex items-center gap-1 text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-xs font-medium">Audit Passed</span>
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-gray-500">
                        <span className="text-xs">Pending</span>
                      </span>
                    )}
                  </div>
                </td>

                {/* Actions */}
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => onViewAuditTrail(candidate)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Audit Trail
                    </button>
                    {candidate.human_review_required && !candidate.human_review_completed && (
                      <button
                        onClick={() => onReviewRequest(candidate)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-amber-500 rounded-lg hover:bg-amber-600 transition-colors"
                      >
                        Review
                      </button>
                    )}
                    <button
                      onClick={() => setExpandedRow(
                        expandedRow === candidate.candidate_id ? null : candidate.candidate_id
                      )}
                      className="p-1.5 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      {expandedRow === candidate.candidate_id ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </td>
              </tr>

              {/* Expanded details row */}
              {expandedRow === candidate.candidate_id && (
                <tr key={`${candidate.candidate_id}-expanded`}>
                  <td colSpan="8" className="px-4 py-4 bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Strengths */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Key Strengths</h4>
                        <ul className="space-y-1">
                          {candidate.key_strengths?.length > 0 ? (
                            candidate.key_strengths.map((strength, idx) => (
                              <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                                {strength}
                              </li>
                            ))
                          ) : (
                            <li className="text-sm text-gray-500 italic">No strengths recorded</li>
                          )}
                        </ul>
                      </div>

                      {/* Concerns */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Key Concerns</h4>
                        <ul className="space-y-1">
                          {candidate.key_concerns?.length > 0 ? (
                            candidate.key_concerns.map((concern, idx) => (
                              <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                                <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                                {concern}
                              </li>
                            ))
                          ) : (
                            <li className="text-sm text-gray-500 italic">No concerns recorded</li>
                          )}
                        </ul>
                      </div>

                      {/* Ranking Explanation */}
                      <div className="md:col-span-2">
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Ranking Explanation</h4>
                        <p className="text-sm text-gray-600 bg-white p-3 rounded-lg border border-gray-200">
                          {candidate.ranking_explanation || 'No explanation provided'}
                        </p>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default CandidateTable
