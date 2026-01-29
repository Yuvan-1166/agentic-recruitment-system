import { useState } from 'react'
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  ChevronDown, 
  ChevronUp,
  XCircle,
  AlertCircle,
  Info
} from 'lucide-react'

function BiasAuditPanel({ auditResults }) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!auditResults) return null

  const { 
    audit_passed, 
    overall_fairness_score, 
    findings = [], 
    recommendations = [],
    compliance_notes = []
  } = auditResults

  const getSeverityCount = (severity) => {
    return findings.filter(f => f.severity === severity).length
  }

  const getSeverityStyles = (severity) => {
    switch (severity) {
      case 'critical':
        return { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-200', icon: XCircle }
      case 'high':
        return { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-200', icon: AlertTriangle }
      case 'medium':
        return { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-200', icon: AlertCircle }
      case 'low':
        return { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-200', icon: Info }
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-200', icon: Info }
    }
  }

  return (
    <div className={`card border-2 ${
      audit_passed ? 'border-green-200 bg-green-50/50' : 'border-amber-200 bg-amber-50/50'
    }`}>
      {/* Header */}
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-xl ${
            audit_passed ? 'bg-green-100' : 'bg-amber-100'
          }`}>
            <Shield className={`w-6 h-6 ${
              audit_passed ? 'text-green-600' : 'text-amber-600'
            }`} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-gray-900">Bias Audit</h3>
              {audit_passed ? (
                <span className="flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                  <CheckCircle className="w-3 h-3" />
                  Passed
                </span>
              ) : (
                <span className="flex items-center gap-1 px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">
                  <AlertTriangle className="w-3 h-3" />
                  Review Required
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600">
              Fairness Score: {(overall_fairness_score * 100).toFixed(0)}% • 
              {findings.length} finding{findings.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Severity summary badges */}
          <div className="hidden sm:flex items-center gap-2">
            {getSeverityCount('critical') > 0 && (
              <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">
                {getSeverityCount('critical')} Critical
              </span>
            )}
            {getSeverityCount('high') > 0 && (
              <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
                {getSeverityCount('high')} High
              </span>
            )}
            {getSeverityCount('medium') > 0 && (
              <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">
                {getSeverityCount('medium')} Medium
              </span>
            )}
            {getSeverityCount('low') > 0 && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                {getSeverityCount('low')} Low
              </span>
            )}
          </div>
          
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-500" />
            )}
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-6 space-y-6">
          {/* Fairness Score Gauge */}
          <div className="p-4 bg-white rounded-xl border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Fairness Score</span>
              <span className={`text-lg font-bold ${
                overall_fairness_score >= 0.9 ? 'text-green-600' :
                overall_fairness_score >= 0.7 ? 'text-blue-600' :
                overall_fairness_score >= 0.5 ? 'text-amber-600' : 'text-red-600'
              }`}>
                {(overall_fairness_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${
                  overall_fairness_score >= 0.9 ? 'bg-green-500' :
                  overall_fairness_score >= 0.7 ? 'bg-blue-500' :
                  overall_fairness_score >= 0.5 ? 'bg-amber-500' : 'bg-red-500'
                }`}
                style={{ width: `${overall_fairness_score * 100}%` }}
              />
            </div>
            <div className="flex justify-between mt-1 text-xs text-gray-500">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Findings */}
          {findings.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3">Findings</h4>
              <div className="space-y-3">
                {findings.map((finding, idx) => {
                  const styles = getSeverityStyles(finding.severity)
                  const Icon = styles.icon
                  
                  return (
                    <div 
                      key={idx}
                      className={`p-4 rounded-xl border ${styles.bg} ${styles.border}`}
                    >
                      <div className="flex items-start gap-3">
                        <Icon className={`w-5 h-5 ${styles.text} flex-shrink-0 mt-0.5`} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`text-xs font-semibold uppercase ${styles.text}`}>
                              {finding.severity}
                            </span>
                            <span className={`text-xs ${styles.text} opacity-75`}>
                              • {finding.category?.replace(/_/g, ' ')}
                            </span>
                          </div>
                          <p className={`text-sm ${styles.text}`}>{finding.description}</p>
                          {finding.recommendation && (
                            <p className={`text-xs mt-2 ${styles.text} opacity-75`}>
                              <span className="font-medium">Recommendation:</span> {finding.recommendation}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3">Recommendations</h4>
              <ul className="space-y-2">
                {recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                    <span className="text-primary-500 mt-1">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Compliance Notes */}
          {compliance_notes.length > 0 && (
            <div className="p-4 bg-gray-100 rounded-xl">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Compliance Notes</h4>
              <ul className="space-y-1">
                {compliance_notes.map((note, idx) => (
                  <li key={idx} className="text-xs text-gray-600">
                    {note}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default BiasAuditPanel
