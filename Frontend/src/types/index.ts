import 'vue-router'

export interface User {
    uid: string
    email: string
    display_name: string
    role: 'student' | 'instructor'
    created_at: string
    last_login: string | null
}

export type UserRole = 'student' | 'instructor'

export type AuthFlowResult = 'signed-in' | 'profile-setup' | 'redirect'

export interface Module {
    module_id: string
    title: string
    description: string | null
    order_index: number
    created_at: string
}

export interface Phrase {
  phrase_id: string
  module_id: string
  japanese_text: string
  romaji: string
  english_translation: string
  reference_audio_url: string | null
  difficulty_level: number
  created_at: string
}

export interface PhonemeError {
  score: number
  error: boolean
  label: string
}

export interface PhonemeErrorMap {
  mora_timing: PhonemeError
  consonants: PhonemeError
  vowels: PhonemeError
  overall_acoustic: PhonemeError
}

export interface PronunciationChunk {
  index: number
  display_text: string
  kana: string
  romaji: string
}

export interface TargetPronunciation {
  kana: string
  romaji: string
  chunks: PronunciationChunk[]
}

export interface PronunciationFeedbackItem {
  chunk_index: number
  display_text: string
  kana: string
  romaji: string
  issue_type: string
  severity: 'low' | 'medium' | 'high'
  score: number
  expected_note: string
  heard_note: string
  fix_tip: string
}

export interface Attempt {
  attempt_id: string
  student_uid: string
  phrase_id: string
  audio_file_url: string | null
  accuracy_score: number
  mora_timing_score: number
  consonant_score: number
  vowel_score: number
  phoneme_error_map: PhonemeErrorMap | null
  feedback_text: string | null
  verification_status: 'accepted' | 'wrong_phrase_detected' | 'no_clear_speech' | 'retry_needed'
  recognized_phrase_id: string | null
  recognized_text: string | null
  recognized_text_romaji: string | null
  target_pronunciation: TargetPronunciation | null
  pronunciation_feedback: PronunciationFeedbackItem[] | null
  verification_confidence: number | null
  verification_margin: number | null
  counts_for_progress: boolean
  attempted_at: string
}

export interface AttemptSummary {
  attempt_id: string
  phrase_id: string
  accuracy_score: number
  feedback_text: string | null
  verification_status: 'accepted' | 'wrong_phrase_detected' | 'no_clear_speech' | 'retry_needed'
  recognized_phrase_id: string | null
  recognized_text: string | null
  recognized_text_romaji: string | null
  target_pronunciation: TargetPronunciation | null
  pronunciation_feedback: PronunciationFeedbackItem[] | null
  counts_for_progress: boolean
  attempted_at: string
}

export interface ProgressSummary {
  id: number
  student_uid: string
  module_id: string
  average_accuracy: number
  total_attempts: number
  streak_days: number
  last_attempted_at: string | null
  updated_at: string
}

export interface WeeklyAccuracy {
  week_start: string
  average_accuracy: number
  attempt_count: number
}

export interface StudentDashboard {
  overall_average: number
  total_attempts: number
  streak_days: number
  weakest_module_id: string | null
  weakest_module_score: number | null
  progress_by_module: ProgressSummary[]
  weekly_accuracy: WeeklyAccuracy[]
}

export interface StudentStat {
  uid: string
  display_name: string
  email: string
  overall_average: number
  total_attempts: number
  streak_days: number
  weakest_module_id: string | null
  is_flagged: boolean
}

export interface PhonemeBreakdown {
  mora_timing_avg: number
  consonant_avg: number
  vowel_avg: number
  overall_avg: number
}

export interface ClassOverview {
  class_id: string
  total_students: number
  active_students: number
  weekly_attempts: number
  class_average: number
  flagged_students: StudentStat[]
  phoneme_breakdown: PhonemeBreakdown
  weekly_trend: WeeklyAccuracy[]
}

export interface ClassSummary {
  class_id: string
  name: string
  instructor_uid: string
  instructor_name: string | null
  join_code: string | null
  created_at: string
  joined_at: string | null
  student_count: number
  is_owner: boolean
}

export interface JoinCodeResponse {
  class_id: string
  join_code: string
}

export interface Exercise {
  exercise_id: string
  class_id: string | null
  title: string
  instructor_uid: string
  created_at: string
  due_date: string | null
  phrases: { id: number; exercise_id: string; phrase_id: string }[]
  assignments: {
    id: number
    exercise_id: string
    student_uid: string
    assigned_at: string
    completed_at: string | null
  }[]
}

export interface StudentExercise {
  exercise_id: string
  class_id: string | null
  title: string
  due_date: string | null
  assigned_at: string
  completed_at: string | null
  is_overdue: boolean
  phrase_ids: string[]
}

export interface AssignmentPhraseStatus {
  phrase_id: string
  submitted_at: string | null
  reviewed_at: string | null
  released_at: string | null
  teacher_accuracy_score: number | null
  teacher_feedback_text: string | null
}

export interface StudentAssignment {
  exercise_id: string
  class_id: string | null
  title: string
  due_date: string | null
  assigned_at: string
  completed_at: string | null
  is_overdue: boolean
  phrase_ids: string[]
  phrases: AssignmentPhraseStatus[]
}

export interface AssignmentSubmission {
  submission_id: string
  exercise_id: string
  student_uid: string
  phrase_id: string
  audio_file_url: string
  submitted_at: string
  reviewed_at: string | null
  released_at: string | null
  verification_status: 'accepted' | 'wrong_phrase_detected' | 'no_clear_speech' | 'retry_needed'
  recognized_phrase_id: string | null
  recognized_text: string | null
  recognized_text_romaji: string | null
  target_pronunciation: TargetPronunciation | null
  pronunciation_feedback: PronunciationFeedbackItem[] | null
  verification_confidence: number | null
  verification_margin: number | null
  counts_for_progress: boolean
}

export interface InstructorAssignmentSubmission {
  submission_id: string
  exercise_id: string
  student_uid: string
  student_display_name: string
  phrase_id: string
  audio_file_url: string
  submitted_at: string
  reviewed_at: string | null
  released_at: string | null
  suggested_accuracy_score: number
  suggested_mora_timing_score: number
  suggested_consonant_score: number
  suggested_vowel_score: number
  suggested_feedback_text: string | null
  verification_status: 'accepted' | 'wrong_phrase_detected' | 'no_clear_speech' | 'retry_needed'
  recognized_phrase_id: string | null
  recognized_text: string | null
  recognized_text_romaji: string | null
  target_pronunciation: TargetPronunciation | null
  pronunciation_feedback: PronunciationFeedbackItem[] | null
  verification_confidence: number | null
  verification_margin: number | null
  counts_for_progress: boolean
  teacher_accuracy_score: number | null
  teacher_feedback_text: string | null
}

export interface StudentDrillDown {
  uid: string
  display_name: string
  email: string
  overall_average: number
  total_attempts: number
  streak_days: number
  phoneme_breakdown: PhonemeBreakdown
  weakest_module_id: string | null
  weakest_module_score: number | null
  recent_attempts: {
    attempt_id: string
    phrase_id: string
    accuracy_score: number
    mora_timing_score: number
    consonant_score: number
    vowel_score: number
    feedback_text: string | null
    verification_status: 'accepted' | 'wrong_phrase_detected' | 'no_clear_speech' | 'retry_needed'
    recognized_phrase_id: string | null
    recognized_text: string | null
    recognized_text_romaji: string | null
    target_pronunciation: TargetPronunciation | null
    pronunciation_feedback: PronunciationFeedbackItem[] | null
    counts_for_progress: boolean
    attempted_at: string
  }[]
}

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    role?: 'student' | 'instructor'
    allowPendingProfile?: boolean
  }
}
