// Mock data for testing the frontend without a backend connection

export const mockPipelineData = {
  pipeline_id: "pipe_a1b2c3d4e5f6",
  job_id: "job_789xyz123abc",
  current_stage: "awaiting_human_review",
  completed_stages: [
    "initialized",
    "jd_analysis", 
    "resume_parsing",
    "matching",
    "shortlisting",
    "test_generation",
    "test_evaluation",
    "ranking",
    "bias_audit"
  ],
  job_description: {
    title: "Senior Full Stack Engineer",
    department: "Engineering",
    location: "Remote",
  },
  candidates: [
    { candidate_id: "cand_001" },
    { candidate_id: "cand_002" },
    { candidate_id: "cand_003" },
    { candidate_id: "cand_004" },
    { candidate_id: "cand_005" },
    { candidate_id: "cand_006" },
    { candidate_id: "cand_007" },
    { candidate_id: "cand_008" },
  ],
  shortlisted_candidates: [
    "cand_001",
    "cand_002", 
    "cand_003",
    "cand_004",
    "cand_005",
  ],
  final_rankings: [
    {
      candidate_id: "cand_8f3a9b2c1d4e",
      job_id: "job_789xyz123abc",
      rank: 1,
      resume_match_score: 0.92,
      test_score: 0.88,
      final_composite_score: 0.90,
      weights_used: { resume: 0.5, test: 0.5 },
      recommendation: "strongly_recommend",
      confidence: 0.95,
      ranking_explanation: "Excellent match with 90% composite score. Strong skills alignment (92%) and solid test performance (88%). Candidate demonstrates expertise in React, Node.js, and PostgreSQL with 6+ years of relevant experience.",
      key_strengths: [
        "Strong match on all required technical skills",
        "Exceeds experience requirements by 2 years",
        "Excellent test performance in system design"
      ],
      key_concerns: [],
      bias_audit_passed: true,
      human_review_required: false,
      human_review_completed: false,
    },
    {
      candidate_id: "cand_2b4c6d8e0f1a",
      job_id: "job_789xyz123abc",
      rank: 2,
      resume_match_score: 0.85,
      test_score: 0.91,
      final_composite_score: 0.88,
      weights_used: { resume: 0.5, test: 0.5 },
      recommendation: "strongly_recommend",
      confidence: 0.92,
      ranking_explanation: "Strong candidate with 88% composite score. Test performance (91%) exceeded resume match (85%), indicating strong practical skills. Good experience with microservices architecture.",
      key_strengths: [
        "Outstanding test performance",
        "Strong problem-solving skills demonstrated",
        "Experience with cloud-native technologies"
      ],
      key_concerns: [
        "Slightly below on preferred years of experience"
      ],
      bias_audit_passed: true,
      human_review_required: false,
      human_review_completed: false,
    },
    {
      candidate_id: "cand_3c5d7e9f1a2b",
      job_id: "job_789xyz123abc",
      rank: 3,
      resume_match_score: 0.78,
      test_score: 0.82,
      final_composite_score: 0.80,
      weights_used: { resume: 0.5, test: 0.5 },
      recommendation: "recommend",
      confidence: 0.88,
      ranking_explanation: "Good match with 80% composite score. Solid technical foundation with room for growth. Strong in frontend technologies but less experience with backend systems.",
      key_strengths: [
        "Expert-level React skills",
        "Good communication demonstrated in projects",
        "Quick learner based on career progression"
      ],
      key_concerns: [
        "Limited backend experience",
        "No experience with PostgreSQL specifically"
      ],
      bias_audit_passed: true,
      human_review_required: false,
      human_review_completed: false,
    },
    {
      candidate_id: "cand_4d6e8f0a2b3c",
      job_id: "job_789xyz123abc",
      rank: 4,
      resume_match_score: 0.72,
      test_score: 0.78,
      final_composite_score: 0.75,
      weights_used: { resume: 0.5, test: 0.5 },
      recommendation: "recommend",
      confidence: 0.85,
      ranking_explanation: "Solid candidate with 75% composite score. Meets most requirements but lacks some advanced skills. Good cultural fit indicators.",
      key_strengths: [
        "Strong JavaScript fundamentals",
        "Good teamwork experience",
        "Relevant industry background"
      ],
      key_concerns: [
        "Missing required TypeScript experience",
        "Lower test score in system design section"
      ],
      bias_audit_passed: true,
      human_review_required: true,
      human_review_reason: "Borderline candidate - score close to threshold",
      human_review_completed: false,
    },
    {
      candidate_id: "cand_5e7f9a1b3c4d",
      job_id: "job_789xyz123abc",
      rank: 5,
      resume_match_score: 0.68,
      test_score: 0.72,
      final_composite_score: 0.70,
      weights_used: { resume: 0.5, test: 0.5 },
      recommendation: "consider",
      confidence: 0.78,
      ranking_explanation: "Borderline candidate with 70% composite score. Has potential but missing several preferred qualifications. Would require more onboarding time.",
      key_strengths: [
        "Strong motivation demonstrated",
        "Good foundational skills",
        "Relevant side projects"
      ],
      key_concerns: [
        "Below minimum experience requirement",
        "Missing 3 required skills",
        "Lower confidence due to limited data"
      ],
      bias_audit_passed: true,
      human_review_required: true,
      human_review_reason: "Multiple concerns and borderline score",
      human_review_completed: false,
    },
  ],
  bias_audit_results: {
    audit_passed: false,
    overall_fairness_score: 0.78,
    findings: [
      {
        category: "gendered_language",
        severity: "medium",
        description: "Job description contains term 'rockstar' which may discourage female applicants",
        affected_items: ["all_candidates"],
        recommendation: "Replace 'rockstar' with 'high performer' or 'expert'",
      },
      {
        category: "threshold_calibration",
        severity: "low",
        description: "2 candidates are within 5% of the shortlist threshold, indicating borderline decisions",
        affected_items: ["cand_4d6e8f0a2b3c", "cand_5e7f9a1b3c4d"],
        recommendation: "Review threshold settings and consider adjusting based on candidate pool quality",
      },
      {
        category: "explanation_quality",
        severity: "low",
        description: "All rankings have adequate explanations meeting compliance requirements",
        affected_items: [],
        recommendation: null,
      },
    ],
    recommendations: [
      "Review and revise job description to remove potentially biased language",
      "Consider reviewing borderline candidates manually",
      "Document reasoning for threshold selection",
    ],
    compliance_notes: [
      "Audit completed at pipeline stage: bias_audit",
      "Total candidates processed: 8",
      "Total findings: 3 (Critical: 0, High: 0, Medium: 1, Low: 2)",
      "COMPLIANCE STATUS: CONDITIONAL PASS - Minor issues to address",
    ],
  },
  errors: [],
  warnings: [
    "2 borderline candidates flagged for human review",
  ],
}

// Additional mock data for different scenarios
export const mockCompletedPipeline = {
  ...mockPipelineData,
  current_stage: "completed",
  bias_audit_results: {
    ...mockPipelineData.bias_audit_results,
    audit_passed: true,
    overall_fairness_score: 0.95,
    findings: [],
  },
}

export const mockFailedPipeline = {
  ...mockPipelineData,
  current_stage: "failed",
  errors: ["Failed to parse resume for candidate cand_006: Invalid file format"],
}
