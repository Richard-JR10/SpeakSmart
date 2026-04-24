const LAST_PRACTICE_SESSION_KEY = 'speaksmart-last-practice-session'

export type LastPracticeSession = {
  moduleId: string
  phraseId?: string
}

function storageKey(uid?: string | null) {
  return `${LAST_PRACTICE_SESSION_KEY}:${uid ?? 'anonymous'}`
}

export function getLastPracticeSession(uid?: string | null): LastPracticeSession | null {
  if (typeof window === 'undefined') return null

  const rawSession = window.localStorage.getItem(storageKey(uid))
  if (!rawSession) return null

  try {
    const session = JSON.parse(rawSession) as Partial<LastPracticeSession>
    if (!session.moduleId) return null
    return {
      moduleId: session.moduleId,
      phraseId: session.phraseId,
    }
  } catch {
    return null
  }
}

export function setLastPracticeSession(
  uid: string | null | undefined,
  session: LastPracticeSession,
) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(storageKey(uid), JSON.stringify(session))
}
