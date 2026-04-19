<template>
  <section class="min-h-dvh bg-[#f8f5ee] text-[var(--color-text)]">
    <a
      href="#main-content"
      class="sr-only absolute left-4 top-4 z-[60] rounded-full bg-[#173127] px-4 py-2 text-sm font-semibold text-white shadow-lg focus-visible:not-sr-only focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[#173127]/20"
    >
      Skip to main content
    </a>

    <header class="sticky top-0 z-50 border-b border-[#d7e1da] bg-[#f8f5ee]/95 backdrop-blur">
      <div class="mx-auto flex w-full max-w-6xl flex-wrap items-center gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <a
          href="#overview"
          class="flex min-w-0 items-center gap-3 rounded-full px-2 py-2 -m-2 transition hover:bg-white/70 hover:shadow-[0_12px_28px_rgba(23,35,29,0.08)]"
        >
          <span
            class="flex size-11 items-center justify-center rounded-2xl bg-[#e4f2ea] text-[#1f664b]"
          >
            <AppIcon name="spark" :size="18" />
          </span>
          <span class="min-w-0">
            <span
              translate="no"
              class="block font-[var(--font-display)] text-2xl leading-none text-[var(--color-heading)]"
            >
              SpeakSmart
            </span>
            <span class="mt-1 block text-xs font-semibold uppercase tracking-[0.18em] text-[var(--color-subtext)]">
              Japanese pronunciation practice
            </span>
          </span>
        </a>

        <nav
          aria-label="Landing sections"
          class="order-3 flex w-full items-center gap-2 overflow-x-auto pb-1 md:order-none md:ml-auto md:w-auto"
        >
          <a
            v-for="item in navItems"
            :key="item.href"
            :href="item.href"
            class="whitespace-nowrap rounded-full px-3 py-2 text-sm font-medium text-[var(--color-subtext)] transition hover:bg-white hover:text-[var(--color-heading)]"
          >
            {{ item.label }}
          </a>
        </nav>

        <div class="ml-auto flex w-full gap-3 sm:w-auto">
          <RouterLink
            to="/login"
            class="inline-flex flex-1 items-center justify-center rounded-full border border-[#93aa9f] bg-white px-5 py-3 text-sm font-semibold text-[#17231d] transition hover:bg-[#f3f7f4] sm:flex-none"
          >
            Login
          </RouterLink>
          <RouterLink
            to="/signup"
            class="inline-flex flex-1 items-center justify-center rounded-full bg-[#173127] px-5 py-3 text-sm font-semibold !text-white transition hover:bg-[#0f221a] sm:flex-none"
          >
            Create account
          </RouterLink>
        </div>
      </div>
    </header>

    <main id="main-content" tabindex="-1">
      <section id="overview" class="scroll-mt-28">
        <div class="mx-auto grid w-full max-w-6xl gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(280px,0.85fr)] lg:px-8 lg:py-20">
          <div class="flex flex-col gap-6">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-[#1f664b]">
              Built for tourism and hospitality learners
            </p>
            <h1
              class="max-w-4xl text-balance font-[var(--font-display)] text-5xl leading-[0.96] tracking-[-0.04em] text-[var(--color-heading)] sm:text-6xl"
            >
              Simple Japanese speaking practice for students and instructors.
            </h1>
            <p class="max-w-2xl text-lg leading-8 text-[var(--color-subtext)]">
              <span translate="no">SpeakSmart</span> helps students listen to a phrase, record a response, and
              review clear feedback. Instructors can check progress, class trends,
              and weak areas in one place.
            </p>

            <div class="flex flex-col gap-3 sm:flex-row">
              <RouterLink
                to="/signup"
                class="inline-flex items-center justify-center rounded-full bg-[#173127] px-6 py-4 text-sm font-semibold !text-white transition hover:bg-[#0f221a]"
              >
                Get started
              </RouterLink>
              <a
                href="#practice-loop"
                class="inline-flex items-center justify-center rounded-full border border-[#93aa9f] bg-white px-6 py-4 text-sm font-semibold text-[#17231d] transition hover:bg-[#f3f7f4]"
              >
                How it works
              </a>
            </div>
          </div>

          <div class="grid gap-4">
            <article
              v-for="item in heroCards"
              :key="item.title"
              class="rounded-[28px] border border-[#d7e1da] bg-white p-6 shadow-[0_14px_34px_rgba(23,35,29,0.06)]"
            >
              <div class="flex items-start gap-4">
                <span
                  class="flex size-11 items-center justify-center rounded-2xl bg-[#edf4ef] text-[#1f664b]"
                >
                  <AppIcon :name="item.icon" :size="18" />
                </span>
                <div>
                  <h2 class="text-xl font-semibold text-[var(--color-heading)]">
                    {{ item.title }}
                  </h2>
                  <p class="mt-2 text-sm leading-7 text-[var(--color-subtext)]">
                    {{ item.copy }}
                  </p>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section id="practice-loop" class="scroll-mt-28">
        <div class="mx-auto w-full max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div class="max-w-3xl">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-[#1f664b]">
              Practice loop
            </p>
            <h2 class="mt-4 text-balance font-[var(--font-display)] text-4xl leading-none text-[var(--color-heading)] sm:text-5xl">
              Clear steps from start to feedback.
            </h2>
            <p class="mt-4 text-lg leading-8 text-[var(--color-subtext)]">
              Students stay focused on a simple flow. Instructors still get useful
              data from every attempt.
            </p>
          </div>

          <div class="mt-10 grid gap-5 lg:grid-cols-3">
            <article
              v-for="(item, index) in steps"
              :key="item.title"
              class="rounded-[28px] border border-[#d7e1da] bg-white p-6 shadow-[0_14px_34px_rgba(23,35,29,0.06)]"
            >
              <div class="flex items-center justify-between gap-4">
                <span class="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--color-subtext)]">
                  0{{ index + 1 }}
                </span>
                <span
                  class="flex size-11 items-center justify-center rounded-2xl bg-[#edf4ef] text-[#1f664b]"
                >
                  <AppIcon :name="item.icon" :size="18" />
                </span>
              </div>
              <h3 class="mt-8 text-2xl font-semibold text-[var(--color-heading)]">
                {{ item.title }}
              </h3>
              <p class="mt-3 text-base leading-7 text-[var(--color-subtext)]">
                {{ item.copy }}
              </p>
            </article>
          </div>
        </div>
      </section>

      <section id="roles" class="scroll-mt-28">
        <div class="mx-auto w-full max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div class="max-w-3xl">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-[#1f664b]">
              One platform, two views
            </p>
            <h2 class="mt-4 text-balance font-[var(--font-display)] text-4xl leading-none text-[var(--color-heading)] sm:text-5xl">
              Designed for both learning and teaching.
            </h2>
            <p class="mt-4 text-lg leading-8 text-[var(--color-subtext)]">
              <span translate="no">SpeakSmart</span> keeps students and instructors connected to the same
              pronunciation data, with the right information for each role.
            </p>
          </div>

          <div class="mt-10 grid gap-5 lg:grid-cols-2">
            <article class="rounded-[30px] border border-[#d7e1da] bg-white p-6 shadow-[0_14px_34px_rgba(23,35,29,0.06)]">
              <div class="flex items-center gap-3">
                <span
                  class="flex size-11 items-center justify-center rounded-2xl bg-[#edf4ef] text-[#1f664b]"
                >
                  <AppIcon name="mic" :size="18" />
                </span>
                <div>
                  <p class="text-sm font-semibold uppercase tracking-[0.18em] text-[#1f664b]">
                    For students
                  </p>
                  <h3 class="text-2xl font-semibold text-[var(--color-heading)]">
                    Practice with less confusion
                  </h3>
                </div>
              </div>

              <ul class="mt-6 flex flex-col gap-3">
                <li
                  v-for="item in studentPoints"
                  :key="item"
                  class="rounded-2xl bg-[#f4f7f5] px-4 py-3 text-sm leading-7 text-[var(--color-heading)]"
                >
                  {{ item }}
                </li>
              </ul>
            </article>

            <article class="rounded-[30px] border border-[#d7e1da] bg-white p-6 shadow-[0_14px_34px_rgba(23,35,29,0.06)]">
              <div class="flex items-center gap-3">
                <span
                  class="flex size-11 items-center justify-center rounded-2xl bg-[#fbf6ea] text-[#8b5e18]"
                >
                  <AppIcon name="chart" :size="18" />
                </span>
                <div>
                  <p class="text-sm font-semibold uppercase tracking-[0.18em] text-[#8b5e18]">
                    For instructors
                  </p>
                  <h3 class="text-2xl font-semibold text-[var(--color-heading)]">
                    Review progress more quickly
                  </h3>
                </div>
              </div>

              <ul class="mt-6 flex flex-col gap-3">
                <li
                  v-for="item in instructorPoints"
                  :key="item"
                  class="rounded-2xl bg-[#fcf8ef] px-4 py-3 text-sm leading-7 text-[var(--color-heading)]"
                >
                  {{ item }}
                </li>
              </ul>
            </article>
          </div>
        </div>
      </section>

      <section id="analytics" class="scroll-mt-28">
        <div class="mx-auto w-full max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div class="max-w-3xl">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-[#1f664b]">
              Why <span translate="no">SpeakSmart</span> fits
            </p>
            <h2 class="mt-4 text-balance font-[var(--font-display)] text-4xl leading-none text-[var(--color-heading)] sm:text-5xl">
              Built around practical speaking and visible progress.
            </h2>
            <p class="mt-4 text-lg leading-8 text-[var(--color-subtext)]">
              The product stays focused on Japanese pronunciation for tourism
              learners, with progress signals instructors can actually use.
            </p>
          </div>

          <div class="mt-10 grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <article class="rounded-[30px] border border-[#d7e1da] bg-white p-6 shadow-[0_14px_34px_rgba(23,35,29,0.06)]">
              <h3 class="text-2xl font-semibold text-[var(--color-heading)]">
                Simple class overview
              </h3>
              <div class="mt-6 grid gap-4 sm:grid-cols-3">
                <div
                  v-for="item in dashboardStats"
                  :key="item.label"
                  class="rounded-2xl bg-[#f4f7f5] p-4"
                >
                  <p class="tabular-nums font-[var(--font-display)] text-4xl leading-none text-[var(--color-heading)]">
                    {{ item.value }}
                  </p>
                  <p class="mt-2 text-sm leading-6 text-[var(--color-subtext)]">
                    {{ item.label }}
                  </p>
                </div>
              </div>
              <p class="mt-6 text-base leading-7 text-[var(--color-subtext)]">
                Instructors can check overall performance, active students, and
                learners who may need follow-up support.
              </p>
            </article>

            <div class="grid gap-5">
              <article
                v-for="item in credibilityCards"
                :key="item.title"
                class="rounded-[28px] border border-[#d7e1da] bg-white p-5 shadow-[0_14px_34px_rgba(23,35,29,0.06)]"
              >
                <div class="flex items-start gap-4">
                  <span
                    class="flex size-11 items-center justify-center rounded-2xl bg-[#edf4ef] text-[#1f664b]"
                  >
                    <AppIcon :name="item.icon" :size="18" />
                  </span>
                  <div>
                    <h3 class="text-xl font-semibold text-[var(--color-heading)]">
                      {{ item.title }}
                    </h3>
                    <p class="mt-2 text-sm leading-7 text-[var(--color-subtext)]">
                      {{ item.copy }}
                    </p>
                  </div>
                </div>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section id="get-started" class="scroll-mt-28">
        <div class="mx-auto w-full max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <article
            class="rounded-[32px] border border-[#d7e1da] bg-white p-8 shadow-[0_18px_44px_rgba(23,35,29,0.08)]"
          >
            <p class="text-sm font-semibold uppercase tracking-[0.18em] text-[#1f664b]">
              Get started
            </p>
            <h2 class="mt-4 text-balance font-[var(--font-display)] text-4xl leading-none text-[var(--color-heading)] sm:text-5xl">
              Start using <span translate="no">SpeakSmart</span> today.
            </h2>
            <p class="mt-4 max-w-2xl text-lg leading-8 text-[var(--color-subtext)]">
              Create an account to begin practicing, or log in to continue
              reviewing lessons and progress.
            </p>

            <div class="mt-8 flex flex-col gap-3 sm:flex-row">
              <RouterLink
                to="/signup"
                class="inline-flex items-center justify-center rounded-full bg-[#173127] px-6 py-4 text-sm font-semibold !text-white transition hover:bg-[#0f221a]"
              >
                Create account
              </RouterLink>
              <RouterLink
                to="/login"
                class="inline-flex items-center justify-center rounded-full border border-[#93aa9f] bg-white px-6 py-4 text-sm font-semibold text-[#17231d] transition hover:bg-[#f3f7f4]"
              >
                Login
              </RouterLink>
            </div>
          </article>
        </div>
      </section>
    </main>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import AppIcon from '@/components/shared/AppIcon.vue'

const navItems = [
  { label: 'Overview', href: '#overview' },
  { label: 'Practice Loop', href: '#practice-loop' },
  { label: 'Roles', href: '#roles' },
  { label: 'Analytics', href: '#analytics' },
  { label: 'Get Started', href: '#get-started' },
]

const heroCards = [
  {
    icon: 'mic',
    title: 'Guided speaking practice',
    copy: 'Students can focus on listening, recording, and improving one phrase at a time.',
  },
  {
    icon: 'chart',
    title: 'Clear feedback',
    copy: 'Each attempt contributes to visible scores and progress without overcomplicating the page.',
  },
  {
    icon: 'building',
    title: 'Course-friendly design',
    copy: 'SpeakSmart supports tourism and hospitality learners with practical Japanese phrases.',
  },
]

const steps = [
  {
    icon: 'play',
    title: 'Hear the reference',
    copy: 'Students begin with a model phrase before recording their own response.',
  },
  {
    icon: 'mic',
    title: 'Record a response',
    copy: 'The recording step stays straightforward on both desktop and mobile.',
  },
  {
    icon: 'chart',
    title: 'Review the result',
    copy: 'Scores and attempt history make pronunciation practice easier to track over time.',
  },
]

const studentPoints = [
  'Reference audio before each attempt.',
  'Simple recording and playback flow.',
  'Lesson modules for greetings, hotel, food, directions, and emergencies.',
]

const instructorPoints = [
  'Overview metrics for class performance.',
  'Progress tracking for individual learners.',
  'Weak-area visibility for better follow-up activities.',
]

const dashboardStats = [
  { value: '84%', label: 'Class average' },
  { value: '32', label: 'Active students' },
  { value: '6', label: 'Flagged learners' },
]

const credibilityCards = [
  {
    icon: 'globe',
    title: 'Tourism education context',
    copy: 'The content is framed for learners preparing to communicate with Japanese visitors.',
  },
  {
    icon: 'book',
    title: 'Practical Japanese phrases',
    copy: 'Lessons stay tied to real hospitality and service situations instead of generic drills.',
  },
  {
    icon: 'shield',
    title: 'Useful classroom support',
    copy: 'Students can practice independently while instructors still get visible progress data.',
  },
]
</script>
