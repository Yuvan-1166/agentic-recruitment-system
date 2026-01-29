import { 
  FileText, 
  Users, 
  GitCompare, 
  Filter, 
  FileQuestion, 
  ClipboardCheck, 
  Trophy, 
  Shield, 
  CheckCircle2,
  Clock,
  AlertCircle,
  XCircle
} from 'lucide-react'

// Pipeline stages configuration
const PIPELINE_STAGES = [
  { 
    id: 'initialized', 
    label: 'Initialized', 
    icon: Clock,
    description: 'Pipeline created'
  },
  { 
    id: 'jd_analysis', 
    label: 'JD Analysis', 
    icon: FileText,
    description: 'Analyzing job description'
  },
  { 
    id: 'resume_parsing', 
    label: 'Resume Parsing', 
    icon: Users,
    description: 'Extracting candidate data'
  },
  { 
    id: 'matching', 
    label: 'Matching', 
    icon: GitCompare,
    description: 'Calculating match scores'
  },
  { 
    id: 'shortlisting', 
    label: 'Shortlisting', 
    icon: Filter,
    description: 'Filtering candidates'
  },
  { 
    id: 'test_generation', 
    label: 'Test Generation', 
    icon: FileQuestion,
    description: 'Creating assessments'
  },
  { 
    id: 'test_evaluation', 
    label: 'Test Evaluation', 
    icon: ClipboardCheck,
    description: 'Scoring responses'
  },
  { 
    id: 'ranking', 
    label: 'Ranking', 
    icon: Trophy,
    description: 'Final rankings'
  },
  { 
    id: 'bias_audit', 
    label: 'Bias Audit', 
    icon: Shield,
    description: 'Fairness review'
  },
]

// Special terminal states
const TERMINAL_STATES = {
  completed: { label: 'Completed', color: 'green', icon: CheckCircle2 },
  failed: { label: 'Failed', color: 'red', icon: XCircle },
  awaiting_human_review: { label: 'Awaiting Review', color: 'amber', icon: AlertCircle },
}

function PipelineStepper({ currentStage, stages = [] }) {
  // Find current stage index
  const currentIndex = PIPELINE_STAGES.findIndex(s => s.id === currentStage)
  const isTerminalState = currentStage in TERMINAL_STATES

  const getStageStatus = (stage, index) => {
    if (isTerminalState) {
      // All stages before terminal state are completed
      if (index < PIPELINE_STAGES.length) {
        return stages.includes(stage.id) ? 'completed' : 'pending'
      }
    }
    
    if (index < currentIndex) return 'completed'
    if (index === currentIndex) return 'current'
    return 'pending'
  }

  const getStatusStyles = (status) => {
    switch (status) {
      case 'completed':
        return {
          circle: 'bg-green-500 text-white border-green-500',
          line: 'bg-green-500',
          label: 'text-green-700',
          icon: 'text-white',
        }
      case 'current':
        return {
          circle: 'bg-primary-500 text-white border-primary-500 ring-4 ring-primary-100',
          line: 'bg-gray-200',
          label: 'text-primary-700 font-semibold',
          icon: 'text-white',
        }
      default:
        return {
          circle: 'bg-gray-100 text-gray-400 border-gray-300',
          line: 'bg-gray-200',
          label: 'text-gray-500',
          icon: 'text-gray-400',
        }
    }
  }

  return (
    <div className="w-full">
      {/* Desktop view */}
      <div className="hidden lg:block">
        <div className="flex items-start justify-between">
          {PIPELINE_STAGES.map((stage, index) => {
            const status = getStageStatus(stage, index)
            const styles = getStatusStyles(status)
            const Icon = status === 'completed' ? CheckCircle2 : stage.icon

            return (
              <div key={stage.id} className="flex-1 relative">
                {/* Connector line */}
                {index < PIPELINE_STAGES.length - 1 && (
                  <div 
                    className={`absolute top-5 left-1/2 w-full h-0.5 ${
                      status === 'completed' ? 'bg-green-500' : 'bg-gray-200'
                    }`}
                  />
                )}
                
                {/* Stage circle and label */}
                <div className="flex flex-col items-center relative z-10">
                  <div 
                    className={`w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${styles.circle}`}
                  >
                    <Icon className={`w-5 h-5 ${styles.icon}`} />
                  </div>
                  <span className={`mt-2 text-xs text-center max-w-[80px] ${styles.label}`}>
                    {stage.label}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Mobile/Tablet view */}
      <div className="lg:hidden">
        <div className="space-y-4">
          {PIPELINE_STAGES.map((stage, index) => {
            const status = getStageStatus(stage, index)
            const styles = getStatusStyles(status)
            const Icon = status === 'completed' ? CheckCircle2 : stage.icon

            return (
              <div key={stage.id} className="flex items-center gap-4">
                <div 
                  className={`w-10 h-10 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${styles.circle}`}
                >
                  <Icon className={`w-5 h-5 ${styles.icon}`} />
                </div>
                <div className="flex-1">
                  <p className={`text-sm font-medium ${styles.label}`}>{stage.label}</p>
                  <p className="text-xs text-gray-500">{stage.description}</p>
                </div>
                {status === 'current' && (
                  <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded-full animate-pulse">
                    In Progress
                  </span>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Terminal state indicator */}
      {isTerminalState && (
        <div className={`mt-6 p-4 rounded-lg border ${
          currentStage === 'completed' 
            ? 'bg-green-50 border-green-200' 
            : currentStage === 'failed'
            ? 'bg-red-50 border-red-200'
            : 'bg-amber-50 border-amber-200'
        }`}>
          <div className="flex items-center gap-3">
            {currentStage === 'completed' && <CheckCircle2 className="w-5 h-5 text-green-600" />}
            {currentStage === 'failed' && <XCircle className="w-5 h-5 text-red-600" />}
            {currentStage === 'awaiting_human_review' && <AlertCircle className="w-5 h-5 text-amber-600" />}
            <span className={`font-medium ${
              currentStage === 'completed' ? 'text-green-700' :
              currentStage === 'failed' ? 'text-red-700' : 'text-amber-700'
            }`}>
              {TERMINAL_STATES[currentStage]?.label}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default PipelineStepper
