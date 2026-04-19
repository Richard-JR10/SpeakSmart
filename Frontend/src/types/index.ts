import 'vue-router'

export interface User {
    uid: string
    email: string
    display_name: string
    role: 'student' | 'instructor'
    class_id: string | null
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
  attempted_at: string
}

export interface AttemptSummary {
  attempt_id: string
  phrase_id: string
  accuracy_score: number
  feedback_text: string | null
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

export interface Exercise {
  exercise_id: string
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
  title: string
  due_date: string | null
  assigned_at: string
  completed_at: string | null
  is_overdue: boolean
  phrase_ids: string[]
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
