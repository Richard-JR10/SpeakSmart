<template>
  <section class="min-h-dvh bg-background text-foreground">
    <a
      href="#main-content"
      class="sr-only absolute left-4 top-4 z-50 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-lg focus-visible:not-sr-only focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20"
    >
      Skip to main content
    </a>

    <header class="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
      <div class="justify-between mx-auto flex max-w-6xl flex-wrap items-center gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <a
          href="#overview"
          class="flex min-w-0 items-center gap-3 rounded-full px-2 py-2 transition hover:bg-card"
        >
          <span class="hidden sm:flex size-11 items-center justify-center rounded-2xl bg-secondary text-primary">
            <AppIcon name="spark" :size="18" />
          </span>
          <span class="min-w-0">
            <span
              translate="no"
              class="block font-(--font-display) text-2xl leading-none text-(--color-heading)"
            >
              SpeakSmart
            </span>
            <span class="hidden sm:block mt-1 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Japanese pronunciation practice
            </span>
          </span>
        </a>

        <nav
          aria-label="Landing sections"
          class="order-1 hidden w-full items-center gap-2 overflow-x-auto pb-1 md:order-0 md:ml-auto md:flex md:w-auto"
        >
          <Button
            v-for="item in navItems"
            :key="item.href"
            as-child
            variant="ghost"
            size="sm"
          >
            <a :href="item.href">
              {{ item.label }}
            </a>
          </Button>
        </nav>

        <div class="hidden gap-3 md:flex">
          <RouterLink
            to="/login"
            :class="buttonVariants({ variant: 'outline', size: 'lg' })"
          >
            Login
          </RouterLink>
          <RouterLink
            to="/signup"
            :class="buttonVariants({ variant: 'default', size: 'lg' })"
          >
            Create account
          </RouterLink>
        </div>

        <Sheet>
          <SheetTrigger as-child class="md:hidden">
            <Button variant="outline" size="icon">
              <Menu />
              <span class="sr-only">Open navigation menu</span>
            </Button>
          </SheetTrigger>

          <SheetContent side="right" class="w-[min(88vw,22rem)]">
            <SheetHeader class="pr-12">
              <SheetTitle>
                Navigation
              </SheetTitle>
              <SheetDescription>
                Explore the page sections or move straight to your account.
              </SheetDescription>
            </SheetHeader>

            <div class="flex flex-col gap-6 px-4 pb-4">
              <nav aria-label="Mobile landing sections" class="flex flex-col gap-2">
                <SheetClose
                  v-for="item in navItems"
                  :key="item.href"
                  as-child
                >
                  <a
                    :href="item.href"
                    :class="[buttonVariants({ variant: 'ghost', size: 'lg' }), 'w-full justify-start']"
                  >
                    {{ item.label }}
                  </a>
                </SheetClose>
              </nav>

              <Separator />

              <div class="flex flex-col gap-3">
                <SheetClose as-child>
                  <RouterLink
                    to="/login"
                    :class="[buttonVariants({ variant: 'outline', size: 'lg' }), 'w-full']"
                  >
                    Login
                  </RouterLink>
                </SheetClose>
                <SheetClose as-child>
                  <RouterLink
                    to="/signup"
                    :class="[buttonVariants({ variant: 'default', size: 'lg' }), 'w-full']"
                  >
                    Create account
                  </RouterLink>
                </SheetClose>
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>

    <main id="main-content" tabindex="-1">
      <section id="overview" class="scroll-mt-28">
        <div class="mx-auto grid w-full max-w-6xl gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(280px,0.85fr)] lg:px-8 lg:py-20">
          <div class="min-w-0 flex flex-col gap-6">
            <Badge variant="secondary" class="rounded-full px-4 py-1.5 text-[9px] sm:text-[11px] font-semibold uppercase tracking-[0.18em]">
              Built for tourism and hospitality learners
            </Badge>
            <h1
              class="max-w-4xl text-balance font-(--font-display) text-5xl leading-[0.96] tracking-[-0.04em] text-(--color-heading) sm:text-6xl"
            >
              Simple Japanese speaking practice for students and instructors.
            </h1>
            <p class="max-w-2xl text-lg leading-8 text-muted-foreground">
              <span translate="no">SpeakSmart</span> helps students listen to a phrase, record a response, and
              review clear feedback. Instructors can check progress, class trends,
              and weak areas in one place.
            </p>

            <div class="flex flex-col gap-3 sm:flex-row">
              <RouterLink
                to="/signup"
                :class="buttonVariants({ variant: 'default', size: 'lg' })"
              >
                Get started
              </RouterLink>
              <Button as-child variant="outline" size="lg">
                <a href="#practice-loop">
                  How it works
                </a>
              </Button>
            </div>
          </div>

          <div class="grid gap-4">
            <Card
              v-for="item in heroCards"
              :key="item.title"
              class="w-full rounded-[28px] border-border/80 bg-card/95 shadow-[0_14px_34px_rgba(23,35,29,0.06)]"
            >
              <CardHeader class="gap-4">
                <div class="flex min-w-0 flex-col gap-4 sm:flex-row sm:items-start">
                  <span class="flex size-11 items-center justify-center rounded-2xl bg-secondary text-primary">
                    <AppIcon :name="item.icon" :size="18" />
                  </span>
                  <div class="flex min-w-0 flex-col gap-2">
                    <CardTitle class="text-xl text-(--color-heading)">
                      {{ item.title }}
                    </CardTitle>
                    <CardDescription class="text-sm leading-7 text-foreground/80">
                      {{ item.copy }}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      <section id="practice-loop" class="scroll-mt-28">
        <div class="mx-auto w-full max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div class="max-w-3xl">
            <Badge variant="secondary" class="rounded-full px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em]">
              Practice loop
            </Badge>
            <h2 class="mt-4 text-balance font-(--font-display) text-4xl leading-none text-(--color-heading) sm:text-5xl">
              Clear steps from start to feedback.
            </h2>
            <p class="mt-4 text-lg leading-8 text-muted-foreground">
              Students stay focused on a simple flow. Instructors still get useful
              data from every attempt.
            </p>
          </div>

          <div class="mt-10 grid gap-5 lg:grid-cols-3">
            <Card
              v-for="(item, index) in steps"
              :key="item.title"
              class="rounded-[28px] border-border/80 bg-card/95 shadow-[0_14px_34px_rgba(23,35,29,0.06)]"
            >
              <CardHeader class="gap-6">
                <div class="flex items-center justify-between gap-4">
                  <Badge variant="outline" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                    0{{ index + 1 }}
                  </Badge>
                  <span class="flex size-11 items-center justify-center rounded-2xl bg-secondary text-primary">
                    <AppIcon :name="item.icon" :size="18" />
                  </span>
                </div>
                <div class="flex flex-col gap-3">
                  <CardTitle class="text-2xl text-(--color-heading)">
                    {{ item.title }}
                  </CardTitle>
                  <CardDescription class="text-base leading-7 text-foreground/80">
                    {{ item.copy }}
                  </CardDescription>
                </div>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      <section id="roles" class="scroll-mt-28">
        <div class="mx-auto w-full max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div class="max-w-3xl">
            <Badge variant="secondary" class="rounded-full px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em]">
              One platform, two views
            </Badge>
            <h2 class="mt-4 text-balance font-(--font-display) text-4xl leading-none text-(--color-heading) sm:text-5xl">
              Designed for both learning and teaching.
            </h2>
            <p class="mt-4 text-lg leading-8 text-muted-foreground">
              <span translate="no">SpeakSmart</span> keeps students and instructors connected to the same
              pronunciation data, with the right information for each role.
            </p>
          </div>

          <div class="mt-10 grid gap-5 lg:grid-cols-2">
            <Card class="rounded-[30px] border-border/80 bg-card/95 shadow-[0_14px_34px_rgba(23,35,29,0.06)]">
              <CardHeader class="gap-4">
                <div class="flex items-center gap-3">
                  <span class="flex size-11 items-center justify-center rounded-2xl bg-secondary text-primary">
                    <AppIcon name="mic" :size="18" />
                  </span>
                  <div class="flex flex-col gap-2">
                    <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                      For students
                    </Badge>
                    <CardTitle class="text-2xl text-(--color-heading)">
                      Practice with less confusion
                    </CardTitle>
                  </div>
                </div>
              </CardHeader>

              <CardContent class="flex flex-col gap-3">
                <Alert
                  v-for="item in studentPoints"
                  :key="item"
                  class="border-border/80 bg-secondary/60"
                >
                  <AlertDescription class="text-sm leading-7 text-foreground/85">
                    {{ item }}
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>

            <Card class="rounded-[30px] border-border/80 bg-card/95 shadow-[0_14px_34px_rgba(23,35,29,0.06)]">
              <CardHeader class="gap-4">
                <div class="flex items-center gap-3">
                  <span class="flex size-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
                    <AppIcon name="chart" :size="18" />
                  </span>
                  <div class="flex flex-col gap-2">
                    <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                      For instructors
                    </Badge>
                    <CardTitle class="text-2xl text-(--color-heading)">
                      Review progress more quickly
                    </CardTitle>
                  </div>
                </div>
              </CardHeader>

              <CardContent class="flex flex-col gap-3">
                <Alert
                  v-for="item in instructorPoints"
                  :key="item"
                  class="border-border/80 bg-secondary/60"
                >
                  <AlertDescription class="text-sm leading-7 text-foreground/85">
                    {{ item }}
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section id="analytics" class="scroll-mt-28">
        <div class="mx-auto w-full max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div class="max-w-3xl">
            <Badge variant="secondary" class="rounded-full px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em]">
              Why <span translate="no">SpeakSmart</span> fits
            </Badge>
            <h2 class="mt-4 text-balance font-(--font-display) text-4xl leading-none text-(--color-heading) sm:text-5xl">
              Built around practical speaking and visible progress.
            </h2>
            <p class="mt-4 text-lg leading-8 text-muted-foreground">
              The product stays focused on Japanese pronunciation for tourism
              learners, with progress signals instructors can actually use.
            </p>
          </div>

          <div class="mt-10 grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <Card class="rounded-[30px] border-border/80 bg-card/95 shadow-[0_14px_34px_rgba(23,35,29,0.06)]">
              <CardHeader class="gap-3">
                <CardTitle class="text-2xl text-(--color-heading)">
                  Simple class overview
                </CardTitle>
                <CardDescription class="text-base leading-7 text-foreground/80">
                  Instructors can check overall performance, active students, and
                  learners who may need follow-up support.
                </CardDescription>
              </CardHeader>

              <CardContent class="grid gap-4 sm:grid-cols-3">
                <Card
                  v-for="item in dashboardStats"
                  :key="item.label"
                  class="gap-0 rounded-2xl border-border/80 bg-secondary shadow-none"
                >
                  <CardHeader class="gap-2 p-4">
                    <Badge variant="outline" class="rounded-full bg-card px-3 py-1 text-(--color-heading)">
                      {{ item.label }}
                    </Badge>
                    <CardTitle class="tabular-nums font-(--font-display) text-4xl leading-none text-(--color-heading)">
                      {{ item.value }}
                    </CardTitle>
                  </CardHeader>
                </Card>
              </CardContent>
            </Card>

            <div class="grid gap-5">
              <Card
                v-for="item in credibilityCards"
                :key="item.title"
                class="rounded-[28px] border-border/80 bg-card/95 shadow-[0_14px_34px_rgba(23,35,29,0.06)]"
              >
                <CardHeader class="gap-4">
                  <div class="flex items-start gap-4">
                    <span class="flex size-11 items-center justify-center rounded-2xl bg-secondary text-primary">
                      <AppIcon :name="item.icon" :size="18" />
                    </span>
                    <div class="flex flex-col gap-2">
                      <CardTitle class="text-xl text-(--color-heading)">
                        {{ item.title }}
                      </CardTitle>
                      <CardDescription class="text-sm leading-7 text-foreground/80">
                        {{ item.copy }}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            </div>
          </div>
        </div>
      </section>

      <section id="get-started" class="scroll-mt-28">
        <div class="mx-auto w-full max-w-6xl px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <Card class="rounded-4xl border-primary/20 bg-primary text-primary-foreground shadow-[0_18px_44px_rgba(23,35,29,0.08)]">
            <CardHeader class="gap-4">
              <Badge class="rounded-full border border-primary-foreground/15 bg-primary-foreground/12 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-foreground">
                Get started
              </Badge>
              <CardTitle class="text-balance font-(--font-display) text-4xl leading-none text-primary-foreground sm:text-5xl">
                Start using <span translate="no">SpeakSmart</span> today.
              </CardTitle>
              <CardDescription class="max-w-2xl text-lg leading-8 text-primary-foreground/80">
                Create an account to begin practicing, or log in to continue
                reviewing lessons and progress.
              </CardDescription>
            </CardHeader>

            <CardFooter class="flex-col gap-3 sm:flex-row sm:items-center">
              <RouterLink
                to="/signup"
                :class="buttonVariants({ variant: 'secondary', size: 'lg' })"
                class="w-full sm:w-auto"
              >
                Create account
              </RouterLink>
              <RouterLink
                to="/login"
                :class="buttonVariants({ variant: 'outline', size: 'lg' })"
                class="w-full sm:w-auto border-primary-foreground/25 bg-transparent text-primary-foreground hover:bg-primary-foreground/10 hover:text-primary-foreground"
              >
                Login
              </RouterLink>
            </CardFooter>
          </Card>
        </div>
      </section>
    </main>
  </section>
</template>

<script setup lang="ts">
import { Menu } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

import AppIcon from '@/components/shared/AppIcon.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button, buttonVariants } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'

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
