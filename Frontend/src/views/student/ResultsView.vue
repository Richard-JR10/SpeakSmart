<template>
  <StudentLayout title="Your Results" show-back>
    <div class="mx-auto flex w-full max-w-5xl flex-col gap-4">
      <Card v-if="!attempt" class="border-border/80 bg-card/95">
        <CardHeader class="items-center gap-3 text-center">
          <div class="flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
            <BookOpen aria-hidden="true" />
          </div>
          <div class="flex flex-col gap-2">
            <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
              No Results Yet
            </CardTitle>
            <CardDescription class="max-w-xl text-sm leading-7 text-muted-foreground">
              Finish a practice attempt first so this page can show your score,
              pronunciation breakdown, and next step.
            </CardDescription>
          </div>
        </CardHeader>

        <CardFooter class="justify-center border-t">
          <Button @click="router.push('/lessons')">
            <BookOpen aria-hidden="true" data-icon="inline-start" />
            <span>Browse Lessons</span>
          </Button>
        </CardFooter>
      </Card>

      <template v-else>
        <Card class="border-border/80 bg-card/95">
          <CardHeader class="gap-4">
            <div class="flex flex-wrap items-center gap-2">
              <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Latest Attempt
              </Badge>
              <Badge variant="outline" class="rounded-full px-3 py-1">
                {{ formattedAttemptDate }}
              </Badge>
              <Badge
                v-if="currentModule"
                variant="outline"
                class="rounded-full px-3 py-1"
              >
                {{ currentModule.title }}
              </Badge>
            </div>

            <div class="grid gap-5 lg:grid-cols-[minmax(0,1fr)_220px] lg:items-start">
              <div class="flex min-w-0 flex-col gap-3">
                <div class="flex flex-col gap-2">
                  <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading) text-pretty sm:text-4xl">
                    {{ currentPhrase?.japanese_text ?? 'Pronunciation Review' }}
                  </CardTitle>
                  <CardDescription class="text-base font-semibold text-primary sm:text-lg">
                    {{ currentPhrase?.romaji ?? attempt.phrase_id }}
                  </CardDescription>
                  <p
                    v-if="currentPhrase?.english_translation"
                    class="text-sm leading-7 text-foreground/80"
                  >
                    {{ currentPhrase.english_translation }}
                  </p>
                </div>

                <p class="max-w-3xl text-sm leading-7 text-muted-foreground">
                  {{ feedbackCopy }}
                </p>
              </div>

              <div class="flex justify-start lg:justify-end">
                <div class="grid w-full lg:max-w-55 gap-3 rounded-3xl border border-border/70 bg-muted/35 p-4 text-center">
                  <div class="mx-auto flex size-28 items-center justify-center rounded-full border-8 border-primary/15 bg-background shadow-sm">
                    <div class="flex flex-col items-center gap-1">
                      <span class="font-(--font-display) text-4xl leading-none text-(--color-heading)">
                        {{ accuracyScoreText }}
                      </span>
                      <span class="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                        Accuracy
                      </span>
                    </div>
                  </div>

                  <Badge
                    :variant="scoreBadgeVariant"
                    class="mx-auto rounded-full px-3 py-1"
                  >
                    {{ scoreSummaryLabel }}
                  </Badge>

                  <Badge
                    v-if="assessmentConfidence"
                    :variant="confidenceBadgeVariant"
                    class="mx-auto rounded-full px-3 py-1"
                  >
                    {{ assessmentConfidence.label }}
                  </Badge>

                  <p class="text-sm leading-6 text-muted-foreground">
                    {{ scoreSummaryCopy }}
                  </p>
                </div>
              </div>
            </div>
          </CardHeader>

          <CardContent class="grid gap-3 sm:grid-cols-3">
            <div class="rounded-2xl border border-border/70 bg-muted/35 p-4">
              <div class="flex items-center gap-2">
                <Clock3 aria-hidden="true" class="text-primary" />
                <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  Attempted
                </p>
              </div>
              <p class="mt-3 text-base font-semibold text-(--color-heading)">
                {{ formattedAttemptDate }}
              </p>
              <p class="mt-1 text-sm leading-6 text-muted-foreground">
                Latest scored submission for this phrase.
              </p>
            </div>

            <div class="rounded-2xl border border-border/70 bg-muted/35 p-4">
              <div class="flex items-center gap-2">
                <BookOpen aria-hidden="true" class="text-primary" />
                <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  Module
                </p>
              </div>
              <p class="mt-3 text-base font-semibold text-(--color-heading)">
                {{ currentModule?.title ?? 'Current lesson' }}
              </p>
              <p class="mt-1 text-sm leading-6 text-muted-foreground">
                {{ phrasePositionCopy }}
              </p>
            </div>

            <div class="rounded-2xl border border-border/70 bg-muted/35 p-4">
              <div class="flex items-center gap-2">
                <Mic aria-hidden="true" class="text-primary" />
                <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  Recording
                </p>
              </div>
              <p class="mt-3 text-base font-semibold text-(--color-heading)">
                {{ submittedAudioUrl ? 'Available' : 'Unavailable' }}
              </p>
              <p class="mt-1 text-sm leading-6 text-muted-foreground">
                {{ submittedAudioUrl ? 'Preview your latest take below.' : 'Only the score data is available for this attempt.' }}
              </p>
            </div>
          </CardContent>
        </Card>

        <div class="grid gap-4 xl:grid-cols-[minmax(0,1.08fr)_minmax(320px,0.92fr)]">
          <Card class="border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                How to Say It
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Correct Pronunciation Target
              </CardTitle>
              <CardDescription>
                Use this kana and romaji guide as the model for your next try. Highlighted chunks are the ones that need the most attention.
              </CardDescription>
            </CardHeader>

            <CardContent class="grid gap-4">
              <div class="rounded-3xl border border-border/70 bg-muted/30 p-5">
                <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  Full reading
                </p>
                <p class="mt-3 font-(--font-display) text-4xl leading-none text-(--color-heading) text-pretty sm:text-5xl">
                  {{ targetPronunciation?.kana ?? currentPhrase?.japanese_text ?? 'Pronunciation unavailable' }}
                </p>
                <p class="mt-3 text-base font-semibold text-primary sm:text-lg">
                  {{ targetPronunciation?.romaji ?? currentPhrase?.romaji ?? 'Romaji unavailable' }}
                </p>
              </div>

              <div class="grid gap-3">
                <div class="flex items-center justify-between gap-3">
                  <p class="text-sm font-semibold text-(--color-heading)">
                    Mora guide
                  </p>
                  <p class="text-xs text-muted-foreground">
                    Read one mora at a time, then blend them together smoothly.
                  </p>
                </div>

                <Alert v-if="!pronunciationMorae.length">
                  <CircleAlert aria-hidden="true" />
                  <AlertTitle>No mora guide yet</AlertTitle>
                  <AlertDescription>
                    This attempt has the overall pronunciation target, but mora-level guidance was not returned.
                  </AlertDescription>
                </Alert>

                <div v-else class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                  <div
                    v-for="(mora, index) in pronunciationMorae"
                    :key="`${mora.kana}-${index}`"
                    class="rounded-2xl border p-3 transition-colors"
                    :class="highlightedMoraIndexes.has(mora.index) ? 'border-destructive/40 bg-destructive/5' : 'border-border/70 bg-muted/25'"
                  >
                    <div class="flex items-center justify-between gap-2">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Mora {{ index + 1 }}
                      </p>
                      <Badge
                        :variant="highlightedMoraIndexes.has(mora.index) ? 'destructive' : 'outline'"
                        class="rounded-full px-2 py-0.5"
                      >
                        {{ highlightedMoraIndexes.has(mora.index) ? 'Focus' : 'Stable' }}
                      </Badge>
                    </div>
                    <p class="mt-3 text-2xl font-semibold leading-none text-(--color-heading)">
                      {{ mora.kana }}
                    </p>
                    <p class="mt-2 text-sm font-medium text-primary">
                      {{ mora.romaji }}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card class="border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                What to Fix
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Next-Try Coaching
              </CardTitle>
              <CardDescription>
                Focus on one or two sounds first. Small clear fixes are more useful than trying to change everything at once.
              </CardDescription>
            </CardHeader>

            <CardContent class="grid gap-4">
              <Alert
                v-if="attempt.verification_status !== 'accepted'"
                :variant="attempt.verification_status === 'wrong_phrase_detected' ? 'destructive' : 'default'"
              >
                <CircleAlert aria-hidden="true" />
                <AlertTitle>{{ verificationGuidanceTitle }}</AlertTitle>
                <AlertDescription>
                  {{ verificationGuidanceCopy }}
                </AlertDescription>
              </Alert>

              <Alert
                v-if="attempt.verification_status === 'accepted' && isLowAssessmentConfidence"
                variant="default"
              >
                <CircleAlert aria-hidden="true" />
                <AlertTitle>Try one clearer take first</AlertTitle>
                <AlertDescription>
                  {{ assessmentConfidence?.guidance ?? 'The app needs a clearer recording before making strong pronunciation corrections.' }}
                </AlertDescription>
              </Alert>

              <template v-if="attempt.verification_status !== 'accepted'">
                <div
                  v-if="recognizedTextDisplay"
                  class="rounded-2xl border border-border/70 bg-muted/25 p-4"
                >
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Whisper heard
                  </p>
                  <p class="mt-2 text-base font-semibold text-(--color-heading)">
                    {{ recognizedTextDisplay }}
                  </p>
                </div>

                <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Say this target
                  </p>
                  <p class="mt-2 text-lg font-semibold text-(--color-heading)">
                    {{ targetPronunciation?.kana ?? currentPhrase?.japanese_text ?? 'Target unavailable' }}
                  </p>
                  <p class="mt-1 text-sm text-primary">
                    {{ targetPronunciation?.romaji ?? currentPhrase?.romaji ?? 'Romaji unavailable' }}
                  </p>
                </div>
              </template>

              <template v-else-if="isLowAssessmentConfidence">
                <div class="rounded-3xl border border-border/70 bg-muted/25 p-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Before detailed coaching
                  </p>
                  <p class="mt-2 text-xl font-semibold text-(--color-heading)">
                    Record one clearer attempt
                  </p>
                  <p class="mt-2 text-sm leading-7 text-muted-foreground">
                    Speak the phrase in one steady take, keep the microphone close, and reduce background noise. Then the app can give more reliable sound-level tips.
                  </p>
                  <p class="mt-4 rounded-2xl border border-primary/20 bg-primary/5 p-3 text-sm font-semibold text-primary">
                    Try slowly: {{ targetPracticeText }}
                  </p>
                </div>
              </template>

              <template v-else-if="topPronunciationIssues.length">
                <div
                  v-for="item in topPronunciationIssues"
                  :key="`${item.mora_index ?? item.chunk_index}-${item.phoneme_index ?? item.issue_type}-${item.issue_type}`"
                  class="rounded-3xl border border-border/70 bg-muted/25 p-4"
                >
                  <div class="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Sound to improve
                      </p>
                      <p class="mt-2 text-xl font-semibold leading-none text-(--color-heading)">
                        {{ item.sound_to_improve ?? item.kana }}
                      </p>
                      <p class="mt-1 text-sm font-medium text-primary">
                        Try: {{ item.try_slowly ?? item.romaji }}
                      </p>
                    </div>

                    <div class="flex flex-wrap items-center gap-2">
                      <Badge :variant="issueBadgeVariant(item.severity)" class="rounded-full px-2.5 py-1">
                        {{ issueSeverityLabel(item.severity) }}
                      </Badge>
                      <Badge variant="outline" class="rounded-full px-2.5 py-1">
                        {{ item.score.toFixed(0) }}%
                      </Badge>
                    </div>
                  </div>

                  <div
                    v-if="item.expected_phoneme || item.heard_phoneme"
                    class="mt-4 grid gap-3 sm:grid-cols-2"
                  >
                    <div class="rounded-2xl border border-border/70 bg-background/80 p-3">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Expected sound
                      </p>
                      <p class="mt-2 text-lg font-semibold text-(--color-heading)">
                        {{ item.expected_phoneme ?? 'target' }}
                      </p>
                      <p class="mt-1 text-sm text-muted-foreground">
                        {{ item.expected_label ?? 'Target sound' }}
                      </p>
                    </div>

                    <div class="rounded-2xl border border-border/70 bg-background/80 p-3">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Heard sound
                      </p>
                      <p class="mt-2 text-lg font-semibold text-(--color-heading)">
                        {{ item.heard_phoneme ?? 'unclear' }}
                      </p>
                      <p class="mt-1 text-sm text-muted-foreground">
                        {{ item.heard_label ?? 'Unclear sound' }}
                      </p>
                    </div>
                  </div>

                  <div class="mt-4 grid gap-3">
                    <div class="rounded-2xl border border-border/70 bg-background/80 p-3">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        What happened
                      </p>
                      <p class="mt-2 text-sm leading-7 text-foreground/85">
                        {{ item.what_happened ?? item.heard_note }}
                      </p>
                    </div>

                    <div class="rounded-2xl border border-border/70 bg-background/80 p-3">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        How to fix it
                      </p>
                      <p class="mt-2 text-sm leading-7 text-foreground/85">
                        {{ item.how_to_fix ?? item.fix_tip }}
                      </p>
                    </div>

                    <div class="rounded-2xl border border-primary/20 bg-primary/5 p-3">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-primary">
                        Try slowly
                      </p>
                      <p class="mt-2 text-sm leading-7 text-foreground/85">
                        {{ item.try_slowly ?? item.romaji }}
                      </p>
                    </div>
                  </div>
                </div>
              </template>

              <Alert v-else>
                <BookOpen aria-hidden="true" />
                <AlertTitle>Pronunciation stayed stable</AlertTitle>
                <AlertDescription>
                  This accepted take did not surface a strong sound-level correction. Keep the same rhythm, light vowels, and smooth blending on the next phrase.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </div>

        <div class="grid gap-4 xl:grid-cols-[minmax(0,1.05fr)_minmax(320px,0.95fr)]">
          <Card class="border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Scoring
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Acoustic Breakdown
              </CardTitle>
              <CardDescription>
                These supporting scores explain the rhythm and sound quality behind the teaching feedback above.
              </CardDescription>
            </CardHeader>

            <CardContent class="grid gap-4">
              <div
                v-for="item in breakdownItems"
                :key="item.label"
                class="rounded-2xl border border-border/70 bg-muted/25 p-4"
              >
                <div class="flex items-start justify-between gap-3">
                  <div class="flex min-w-0 items-center gap-2">
                    <component :is="item.icon" aria-hidden="true" class="shrink-0 text-primary" />
                    <div class="min-w-0">
                      <p class="font-semibold text-(--color-heading)">
                        {{ item.label }}
                      </p>
                      <p class="text-sm leading-6 text-muted-foreground">
                        {{ item.description }}
                      </p>
                    </div>
                  </div>

                  <Badge :variant="scoreVariant(item.score)" class="rounded-full px-2.5 py-1">
                    {{ item.score.toFixed(0) }}%
                  </Badge>
                </div>

                <div class="mt-4 h-2 overflow-hidden rounded-full bg-border/70">
                  <div
                    class="h-full rounded-full transition-[width] duration-300 ease-out"
                    :class="scoreBarClass(item.score)"
                    :style="{ width: `${item.score}%` }"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card class="border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Sound Analysis
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Breakdown By Sound
              </CardTitle>
              <CardDescription>
                Expected and heard sounds come from the aligned Japanese phoneme and mora assessment.
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Alert v-if="!detailedPhonemeItems.length && !phonemeItems.length">
                <CircleAlert aria-hidden="true" />
                <AlertTitle>No detailed phoneme data</AlertTitle>
                <AlertDescription>
                  This attempt includes the overall score, but the sound-level breakdown was not returned.
                </AlertDescription>
              </Alert>

              <div v-else class="grid gap-3">
                <Alert v-if="recognizerWarning">
                  <CircleAlert aria-hidden="true" />
                  <AlertTitle>Phoneme recognizer fallback</AlertTitle>
                  <AlertDescription>
                    {{ recognizerWarning }}
                  </AlertDescription>
                </Alert>

                <div
                  v-for="item in detailedPhonemeItems"
                  :key="item.key"
                  class="rounded-2xl border bg-muted/25 p-4"
                  :class="item.error ? 'border-destructive/30' : 'border-border/70'"
                >
                  <div class="flex flex-wrap items-start justify-between gap-3">
                    <div class="min-w-0">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Sound {{ item.index + 1 }} / {{ item.kana }} / {{ item.romaji }}
                      </p>
                      <div class="mt-3 flex flex-wrap items-center gap-2">
                        <Badge variant="outline" class="rounded-full px-2.5 py-1">
                          Expected {{ item.expectedSound }}
                        </Badge>
                        <Badge :variant="item.error ? 'destructive' : 'secondary'" class="rounded-full px-2.5 py-1">
                          Heard {{ item.heardSound }}
                        </Badge>
                      </div>
                    </div>

                    <Badge :variant="scoreVariant(item.score)" class="rounded-full px-2.5 py-1">
                      {{ item.score.toFixed(0) }}%
                    </Badge>
                  </div>

                  <div class="mt-4 grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
                    <div>
                      <p class="font-semibold text-(--color-heading)">
                        {{ item.issueLabel }}
                      </p>
                      <p class="mt-1 text-sm leading-6 text-muted-foreground">
                        {{ item.fixTip }}
                      </p>
                    </div>

                    <Badge variant="outline" class="w-fit rounded-full px-2.5 py-1">
                      {{ item.operationLabel }}
                    </Badge>
                  </div>
                </div>

                <div
                  v-for="item in phonemeItems"
                  :key="item.key"
                  class="rounded-2xl border bg-muted/25 p-4"
                  :class="item.error ? 'border-destructive/30' : 'border-border/70'"
                >
                  <div class="flex items-start justify-between gap-3">
                    <div class="flex min-w-0 items-center gap-2">
                      <component :is="item.icon" aria-hidden="true" class="shrink-0 text-primary" />
                      <div class="min-w-0">
                        <p class="font-semibold text-(--color-heading)">
                          {{ item.label }}
                        </p>
                        <p class="text-sm leading-6 text-muted-foreground">
                          {{ item.description }}
                        </p>
                      </div>
                    </div>

                    <Badge
                      :variant="item.error ? 'destructive' : 'secondary'"
                      class="rounded-full px-2.5 py-1"
                    >
                      {{ item.error ? 'Needs Work' : 'Stable' }}
                    </Badge>
                  </div>

                  <div class="mt-4 flex items-center justify-between gap-3">
                    <p class="text-sm font-semibold text-(--color-heading)">
                      {{ item.score.toFixed(0) }}%
                    </p>
                    <div class="h-2 w-28 overflow-hidden rounded-full bg-border/70">
                      <div
                        class="h-full rounded-full transition-[width] duration-300 ease-out"
                        :class="scoreBarClass(item.score)"
                        :style="{ width: `${item.score}%` }"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div class="grid gap-4 lg:grid-cols-2">
          <Card
            v-if="submittedAudioUrl"
            class="border-border/80 bg-card/95"
          >
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Your Audio
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Submitted Recording
              </CardTitle>
              <CardDescription>
                Replay the exact take that was sent for scoring.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-4">
              <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
                <div class="mb-3 flex items-center gap-2">
                  <AudioLines aria-hidden="true" class="text-primary" />
                  <p class="font-semibold text-(--color-heading)">Latest take</p>
                </div>
                <audio
                  class="w-full"
                  :src="submittedAudioUrl"
                  controls
                  preload="metadata"
                />
              </div>
            </CardContent>
          </Card>

          <Card
            class="border-border/80 bg-card/95"
            :class="!submittedAudioUrl ? 'lg:col-span-2' : ''"
          >
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Reference
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Phrase Practiced
              </CardTitle>
              <CardDescription>
                Compare your attempt against the phrase prompt and its model audio.
              </CardDescription>
            </CardHeader>

            <CardContent class="grid gap-4">
              <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
                <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  Japanese
                </p>
                <p class="mt-2 font-(--font-display) text-3xl leading-none text-(--color-heading) text-pretty">
                  {{ currentPhrase?.japanese_text ?? 'Phrase unavailable' }}
                </p>
              </div>

              <div class="grid gap-3 sm:grid-cols-2">
                <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Romaji
                  </p>
                  <p class="mt-2 text-base font-semibold text-(--color-heading)">
                    {{ currentPhrase?.romaji ?? attempt.phrase_id }}
                  </p>
                </div>

                <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Meaning
                  </p>
                  <p class="mt-2 text-base font-semibold text-(--color-heading)">
                    {{ currentPhrase?.english_translation ?? 'Translation unavailable' }}
                  </p>
                </div>
              </div>

              <Alert v-if="!currentPhrase?.reference_audio_url">
                <CircleAlert aria-hidden="true" />
                <AlertTitle>Reference audio unavailable</AlertTitle>
                <AlertDescription>
                  The phrase metadata loaded, but there is no model audio attached to it yet.
                </AlertDescription>
              </Alert>
            </CardContent>

            <CardFooter class="border-t">
              <Button
                variant="outline"
                size="lg"
                class="w-full sm:w-auto"
                :disabled="!currentPhrase?.reference_audio_url || referencePlaying"
                @click="playReference"
              >
                <Volume2
                  v-if="!referencePlaying"
                  aria-hidden="true"
                  data-icon="inline-start"
                />
                <CirclePlay
                  v-else
                  aria-hidden="true"
                  data-icon="inline-start"
                />
                <span>{{ referencePlaying ? 'Playing Reference…' : 'Play Reference Audio' }}</span>
              </Button>
            </CardFooter>
          </Card>
        </div>

        <div class="grid gap-3 md:grid-cols-2">
          <Button variant="outline" size="lg" class="w-full" @click="tryAgain">
            <RotateCcw aria-hidden="true" data-icon="inline-start" />
            <span>Try Again</span>
          </Button>

          <Button size="lg" class="w-full" @click="nextPhraseAction">
            <MoveRight
              v-if="nextPhrase"
              aria-hidden="true"
              data-icon="inline-start"
            />
            <BookOpen
              v-else
              aria-hidden="true"
              data-icon="inline-start"
            />
            <span>{{ nextActionLabel }}</span>
          </Button>
        </div>
      </template>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Activity,
  AudioLines,
  BookOpen,
  CircleAlert,
  CirclePlay,
  Clock3,
  Mic,
  MoveRight,
  RotateCcw,
  TrendingUp,
  Volume2,
} from 'lucide-vue-next'

import StudentLayout from '@/layouts/StudentLayout.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { useAttemptsStore } from '@/stores/attempts'
import { useModulesStore } from '@/stores/modules'
import type { DetailedPhonemeError } from '@/types'
import { formatRecognizedTextForDisplay } from '@/utils/japanese'

type BreakdownItem = {
  label: string
  score: number
  description: string
  icon: Component
}

type PhonemeItem = {
  key: string
  label: string
  score: number
  error: boolean
  description: string
  icon: Component
}

type DetailedPhonemeItem = DetailedPhonemeError & {
  key: string
  expectedSound: string
  heardSound: string
  issueLabel: string
  operationLabel: string
  fixTip: string
}

const route = useRoute()
const router = useRouter()
const attemptsStore = useAttemptsStore()
const modulesStore = useModulesStore()

const referencePlaying = ref(false)

const fullDateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'long',
  day: 'numeric',
  year: 'numeric',
})

let referenceAudio: HTMLAudioElement | null = null

const attempt = computed(() => attemptsStore.lastAttempt)
const submittedAudioUrl = computed(() => attemptsStore.lastSubmittedAudioUrl)
const attemptedModuleId = computed(() => {
  const value = route.query.moduleId
  return typeof value === 'string' && value.length > 0 ? value : ''
})
const attemptedPhraseId = computed(() => {
  const queryValue = route.query.phraseId
  if (typeof queryValue === 'string' && queryValue.length > 0) return queryValue
  return attempt.value?.phrase_id ?? ''
})

const currentPhrase = computed(() => {
  if (!attemptedPhraseId.value) return null

  if (attemptedModuleId.value) {
    const phrase = modulesStore
      .getPhrasesForModule(attemptedModuleId.value)
      .find((item) => item.phrase_id === attemptedPhraseId.value)

    if (phrase) return phrase
  }

  for (const phrases of Object.values(modulesStore.phrases)) {
    const found = phrases.find((item) => item.phrase_id === attemptedPhraseId.value)
    if (found) return found
  }

  return null
})

const currentModule = computed(() => {
  if (!currentPhrase.value) return null
  return modulesStore.getModuleById(currentPhrase.value.module_id) ?? null
})

const currentPhraseIndex = computed(() => {
  if (!resolvedModuleId.value || !resolvedPhraseId.value) return -1

  return modulesStore
    .getPhrasesForModule(resolvedModuleId.value)
    .findIndex((item) => item.phrase_id === resolvedPhraseId.value)
})

const nextPhrase = computed(() => {
  if (!resolvedModuleId.value || currentPhraseIndex.value < 0) return null

  const phrases = modulesStore.getPhrasesForModule(resolvedModuleId.value)
  return phrases[currentPhraseIndex.value + 1] ?? null
})

const resolvedModuleId = computed(() =>
  currentPhrase.value?.module_id ?? attemptedModuleId.value,
)

const resolvedPhraseId = computed(() =>
  currentPhrase.value?.phrase_id ?? attemptedPhraseId.value,
)

const accuracyScoreText = computed(() =>
  attempt.value ? `${attempt.value.accuracy_score.toFixed(0)}%` : '--',
)

const targetPronunciation = computed(() => {
  if (attempt.value?.target_pronunciation) {
    return attempt.value.target_pronunciation
  }

  if (!currentPhrase.value) {
    return null
  }

  return {
    kana: currentPhrase.value.japanese_text,
    romaji: currentPhrase.value.romaji,
    chunks: [],
    morae: [],
    phonemes: [],
  }
})

const pronunciationChunks = computed(() =>
  targetPronunciation.value?.chunks ?? [],
)

const pronunciationMorae = computed(() => {
  if (targetPronunciation.value?.morae?.length) {
    return targetPronunciation.value.morae
  }

  return pronunciationChunks.value.map((chunk) => ({
    index: chunk.index,
    chunk_index: chunk.index,
    display_text: chunk.display_text,
    kana: chunk.kana,
    romaji: chunk.romaji,
    phoneme_indexes: [],
    phonemes: [],
    issue_type: 'unknown',
  }))
})

const targetPracticeText = computed(() => {
  const moraText = pronunciationMorae.value
    .map((item) => item.kana)
    .filter(Boolean)
    .join('・')

  return moraText || targetPronunciation.value?.kana || currentPhrase.value?.japanese_text || 'target phrase'
})

const topPronunciationIssues = computed(() =>
  (attempt.value?.pronunciation_feedback ?? []).slice(0, 2),
)

const highlightedMoraIndexes = computed(
  () => new Set(topPronunciationIssues.value.map((item) => item.mora_index ?? item.chunk_index)),
)

const detailedPhonemeItems = computed<DetailedPhonemeItem[]>(() => {
  const phonemes = attempt.value?.phoneme_error_map?.phonemes ?? []

  return [...phonemes]
    .sort((first, second) => {
      if (first.error !== second.error) return first.error ? -1 : 1
      if (first.score !== second.score) return first.score - second.score
      return first.index - second.index
    })
    .map((item) => ({
      ...item,
      key: `${item.index}-${item.expected_phoneme}-${item.issue_type}`,
      expectedSound: formatSound(item.expected_phoneme, item.expected_label),
      heardSound: formatSound(item.heard_phoneme, item.heard_label),
      issueLabel: issueTypeLabel(item.issue_type),
      operationLabel: operationLabel(item.operation),
      fixTip: phonemeFixTip(item),
    }))
})

const recognizerWarning = computed(() =>
  attempt.value?.phoneme_error_map?.recognizer?.warning ?? '',
)

const assessmentConfidence = computed(() =>
  attempt.value?.phoneme_error_map?.assessment_confidence ?? null,
)

const isLowAssessmentConfidence = computed(() =>
  assessmentConfidence.value?.level === 'low',
)

const recognizedTextDisplay = computed(() => {
  if (attempt.value?.recognized_text_romaji) {
    return attempt.value.recognized_text_romaji
  }

  return formatRecognizedTextForDisplay(attempt.value?.recognized_text ?? null)
})

const verificationGuidanceTitle = computed(() => {
  if (attempt.value?.verification_status === 'wrong_phrase_detected') {
    return 'Match the target phrase first'
  }

  if (attempt.value?.verification_status === 'no_clear_speech') {
    return 'Record a clearer take'
  }

  return 'Verification was not confident enough'
})

const verificationGuidanceCopy = computed(() => {
  if (attempt.value?.verification_status === 'wrong_phrase_detected') {
    return 'The system detected a different phrase, so pronunciation coaching is paused until the spoken phrase matches the target.'
  }

  if (attempt.value?.verification_status === 'no_clear_speech') {
    return 'There was not enough clear speech to teach pronunciation reliably. Try again in a quieter space and keep the phrase in one steady take.'
  }

  return 'The transcript was too uncertain to trust as a teaching signal, so this attempt does not count toward progress. Use the target guide and try one more clear retake.'
})

const feedbackCopy = computed(() => {
  if (!attempt.value) {
    return 'Listen to the model audio, focus on the weaker sounds below, and record another clear take.'
  }

  if (attempt.value.verification_status === 'wrong_phrase_detected') {
    if (recognizedTextDisplay.value) {
      return `The phrase verification matched a different phrase: ${recognizedTextDisplay.value}. Try the target phrase again before focusing on pronunciation scoring.`
    }
    return 'The phrase verification matched a different phrase. Try the target phrase again before focusing on pronunciation scoring.'
  }

  if (attempt.value.verification_status === 'no_clear_speech') {
    return 'The recording did not contain enough clear speech to verify the target phrase. Try again in a quieter space and speak a little closer to the microphone.'
  }

  if (attempt.value.verification_status === 'retry_needed') {
    if (recognizedTextDisplay.value) {
      return `Phrase verification was uncertain for this recording. Whisper heard: ${recognizedTextDisplay.value}. Please try the target phrase again.`
    }
    return attempt.value.feedback_text ??
      'Phrase verification was uncertain, so this score is provisional and will not count toward progress.'
  }

  return attempt.value.feedback_text ??
    'Listen to the model audio, focus on the weaker sounds below, and record another clear take.'
})

const formattedAttemptDate = computed(() => {
  if (!attempt.value) return 'Attempt Date Unavailable'
  return fullDateFormatter.format(new Date(attempt.value.attempted_at))
})

const phrasePositionCopy = computed(() => {
  if (!currentPhrase.value) {
    return 'Phrase position will appear when the module context finishes loading.'
  }

  const total = modulesStore.getPhrasesForModule(currentPhrase.value.module_id).length
  if (!total || currentPhraseIndex.value < 0) {
    return 'Module phrase order is unavailable right now.'
  }

  return `Phrase ${currentPhraseIndex.value + 1} of ${total} in this module.`
})

const scoreSummaryLabel = computed(() => {
  if (attempt.value?.verification_status === 'wrong_phrase_detected') return 'Phrase Mismatch'
  if (attempt.value?.verification_status === 'no_clear_speech') return 'Retry Needed'
  if (attempt.value?.verification_status === 'retry_needed') return 'Provisional'
  if (isLowAssessmentConfidence.value) return 'Practice Take'

  const score = attempt.value?.accuracy_score ?? 0

  if (score >= 90) return 'Excellent'
  if (score >= 75) return 'Strong'
  if (score >= 60) return 'Developing'
  return 'Needs Work'
})

const scoreSummaryCopy = computed(() => {
  if (attempt.value?.verification_status === 'wrong_phrase_detected') {
    return 'Pronunciation scoring was blocked because the spoken phrase did not confidently match the target.'
  }

  if (attempt.value?.verification_status === 'no_clear_speech') {
    return 'No clear phrase was detected. Re-record the phrase in one steady take.'
  }

  if (attempt.value?.verification_status === 'retry_needed') {
    return 'This score is shown for reference only because phrase verification was uncertain.'
  }

  if (isLowAssessmentConfidence.value) {
    return 'The app scored this take, but the recording or recognizer signal was not strong enough for detailed correction claims.'
  }

  const score = attempt.value?.accuracy_score ?? 0

  if (score >= 90) {
    return 'This take is consistent and clear. Keep the same pacing on the next phrase.'
  }

  if (score >= 75) {
    return 'The phrase is mostly stable. A cleaner replay can still sharpen weaker sounds.'
  }

  if (score >= 60) {
    return 'The base pronunciation is there, but some sound groups still need another pass.'
  }

  return 'Replay the model audio, slow down slightly, and focus on one stronger retake.'
})

const scoreBadgeVariant = computed(() => scoreVariant(attempt.value?.accuracy_score ?? 0))

const confidenceBadgeVariant = computed(() => {
  if (assessmentConfidence.value?.level === 'high') return 'default'
  if (assessmentConfidence.value?.level === 'medium') return 'outline'
  return 'secondary'
})

const breakdownItems = computed<BreakdownItem[]>(() => {
  if (!attempt.value) return []

  return [
    {
      label: 'Mora Timing',
      score: attempt.value.mora_timing_score,
      description: 'How steady the timing and beat of each mora sounded.',
      icon: Clock3,
    },
    {
      label: 'Consonants',
      score: attempt.value.consonant_score,
      description: 'How clearly consonant sounds landed across the phrase.',
      icon: TrendingUp,
    },
    {
      label: 'Vowel Purity',
      score: attempt.value.vowel_score,
      description: 'How stable and accurate the vowel shapes sounded.',
      icon: Volume2,
    },
  ]
})

const phonemeItems = computed<PhonemeItem[]>(() => {
  const map = attempt.value?.phoneme_error_map
  if (!map) return []

  const items: PhonemeItem[] = []

  if (map.phoneme_match) {
    items.push({
      key: 'phoneme_match',
      label: map.phoneme_match.label,
      score: map.phoneme_match.score,
      error: map.phoneme_match.error,
      description: 'How closely expected Japanese phonemes matched the aligned audio.',
      icon: Mic,
    })
  }

  items.push(
    {
      key: 'overall_acoustic',
      label: map.overall_acoustic.label,
      score: map.overall_acoustic.score,
      error: map.overall_acoustic.error,
      description: 'Overall speech signal and pronunciation stability.',
      icon: Activity,
    },
    {
      key: 'mora_timing',
      label: map.mora_timing.label,
      score: map.mora_timing.score,
      error: map.mora_timing.error,
      description: 'Timing control across the phrase rhythm.',
      icon: Clock3,
    },
    {
      key: 'consonants',
      label: map.consonants.label,
      score: map.consonants.score,
      error: map.consonants.error,
      description: 'Consonant clarity and articulation consistency.',
      icon: TrendingUp,
    },
    {
      key: 'vowels',
      label: map.vowels.label,
      score: map.vowels.score,
      error: map.vowels.error,
      description: 'Vowel shape accuracy and stability.',
      icon: Volume2,
    },
  )

  if (map.fluency) {
    items.push({
      key: 'fluency',
      label: map.fluency.label,
      score: map.fluency.score,
      error: map.fluency.error,
      description: 'Pause density, speaking rate, and prosody stability.',
      icon: AudioLines,
    })
  }

  return items
})

const nextActionLabel = computed(() =>
  nextPhrase.value ? 'Next Phrase' : 'Back to Lessons',
)

onMounted(async () => {
  await ensureResultContext()
})

onBeforeUnmount(() => {
  stopReferenceAudio()
})

function scoreVariant(score: number): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (score >= 90) return 'default'
  if (score >= 75) return 'secondary'
  if (score >= 60) return 'outline'
  return 'destructive'
}

function scoreBarClass(score: number) {
  if (score >= 90) return 'bg-primary'
  if (score >= 75) return 'bg-primary/80'
  if (score >= 60) return 'bg-primary/60'
  return 'bg-destructive'
}

function issueBadgeVariant(
  severity: 'low' | 'medium' | 'high',
): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (severity === 'high') return 'destructive'
  if (severity === 'medium') return 'outline'
  return 'secondary'
}

function issueSeverityLabel(severity: 'low' | 'medium' | 'high') {
  if (severity === 'high') return 'Priority Fix'
  if (severity === 'medium') return 'Watch Closely'
  return 'Light Adjustment'
}

function formatSound(symbol: string | null, label: string) {
  if (!symbol && !label) return 'unclear'
  if (!label || label === symbol) return symbol || label
  return `${symbol} (${label})`
}

function issueTypeLabel(issueType: string) {
  const labels: Record<string, string> = {
    match: 'Matched target sound',
    substitution: 'Sound substitution',
    deletion: 'Missing or clipped sound',
    long_vowel_issue: 'Long vowel timing',
    geminate_issue: 'Small-tsu hold',
    nasal_issue: 'Nasal mora clarity',
    r_flap_issue: 'Japanese r-flap',
    vowel_drift: 'Vowel drift',
    devoicing_issue: 'Devoicing control',
  }

  return labels[issueType] ?? 'Sound clarity'
}

function operationLabel(operation: DetailedPhonemeError['operation']) {
  const labels: Record<DetailedPhonemeError['operation'], string> = {
    match: 'Match',
    substitution: 'Substitution',
    deletion: 'Deletion',
    insertion: 'Insertion',
    duration_error: 'Timing',
  }

  return labels[operation]
}

function phonemeFixTip(item: DetailedPhonemeError) {
  if (!item.error) return 'Keep this sound stable in the next take.'
  if (item.issue_type === 'long_vowel_issue') return 'Hold this vowel for the full extra beat.'
  if (item.issue_type === 'geminate_issue') return 'Hold a tiny beat before releasing the next consonant.'
  if (item.issue_type === 'nasal_issue') return 'Keep the nasal sound closed and distinct.'
  if (item.issue_type === 'r_flap_issue') return 'Tap the Japanese r lightly behind the teeth.'
  if (item.issue_type === 'vowel_drift') return 'Keep the vowel steady without sliding.'
  if (item.issue_type === 'devoicing_issue') return 'Lighten the ending so it does not sound too fully voiced.'
  if (item.operation === 'deletion') return 'Give this sound enough time instead of clipping it.'
  return 'Replay the reference and make this sound cleaner on the next take.'
}

async function ensureResultContext() {
  if (!attempt.value) return

  if (!modulesStore.modules.length) {
    await modulesStore.fetchModules()
  }

  if (attemptedModuleId.value) {
    await modulesStore.fetchPhrases(attemptedModuleId.value)
    return
  }

  if (!currentPhrase.value && modulesStore.modules.length) {
    await Promise.all(
      modulesStore.modules.map((module) =>
        modulesStore.fetchPhrases(module.module_id),
      ),
    )
  }
}

function stopReferenceAudio() {
  if (referenceAudio) {
    referenceAudio.pause()
    referenceAudio.currentTime = 0
    referenceAudio = null
  }

  referencePlaying.value = false
}

async function playReference() {
  if (!currentPhrase.value?.reference_audio_url) return

  stopReferenceAudio()
  referencePlaying.value = true

  try {
    referenceAudio = new Audio(currentPhrase.value.reference_audio_url)
    referenceAudio.onended = () => {
      referencePlaying.value = false
      referenceAudio = null
    }
    referenceAudio.onerror = () => {
      referencePlaying.value = false
      referenceAudio = null
    }
    await referenceAudio.play()
  } catch {
    referencePlaying.value = false
    referenceAudio = null
  }
}

async function tryAgain() {
  await ensureResultContext()

  if (!resolvedModuleId.value || !resolvedPhraseId.value) {
    router.push('/lessons')
    return
  }

  attemptsStore.clearLastAttempt()
  router.push(`/practice/${resolvedModuleId.value}/${resolvedPhraseId.value}`)
}

async function nextPhraseAction() {
  await ensureResultContext()

  if (!resolvedModuleId.value || !resolvedPhraseId.value) {
    router.push('/lessons')
    return
  }

  attemptsStore.clearLastAttempt()

  if (nextPhrase.value) {
    router.push(`/practice/${resolvedModuleId.value}/${nextPhrase.value.phrase_id}`)
    return
  }

  router.push('/lessons')
}
</script>
