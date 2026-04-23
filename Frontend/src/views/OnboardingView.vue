<template>
  <div class="min-h-screen bg-background text-foreground selection:bg-primary/20">
    <a
      href="#main-content"
      class="sr-only absolute left-4 top-4 z-50 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground focus-visible:not-sr-only focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
    >
      Skip to main content
    </a>

    <!-- Sticky Header -->
    <header class="sticky top-0 z-50 w-full border-b border-border/60 bg-background/90 backdrop-blur-md transition-colors">
      <div class="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <a 
          href="#overview" 
          class="group relative flex items-center transition-all hover:opacity-80 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg" 
          @click.prevent="scrollToSection('#overview')"
        >
          <img src="/logo.png" alt="SpeakSmart Logo" class="relative z-10 -ml-2 -mr-10 mt-2 h-24 w-auto scale-110 object-contain drop-shadow-xl transition-transform duration-300 group-hover:scale-125" style="mix-blend-mode: multiply;" />
          <span translate="no" class="relative z-0 font-display text-2xl font-black tracking-tight text-foreground">
            SpeakSmart
          </span>
        </a>

        <!-- Desktop Nav -->
        <nav class="hidden md:flex items-center gap-1 rounded-full border border-border/80 bg-muted/60 px-2 py-1 shadow-sm">
          <Button
            v-for="item in navItems"
            :key="item.href"
            variant="ghost"
            size="sm"
            class="rounded-full text-sm font-bold transition-all active:scale-95 focus-visible:ring-2 focus-visible:ring-offset-2"
            :class="activeSectionHref === item.href ? 'bg-primary text-primary-foreground shadow-md' : 'text-foreground/70 hover:bg-background/80 hover:text-foreground'"
            as-child
          >
            <a :href="item.href" @click.prevent="scrollToSection(item.href)">
              {{ item.label }}
            </a>
          </Button>
        </nav>

        <!-- Auth Actions -->
        <div class="hidden md:flex items-center gap-4">
          <Button variant="ghost" class="font-bold transition-transform active:scale-95" as-child>
            <RouterLink to="/login">Login</RouterLink>
          </Button>
          <Button as-child class="rounded-full font-bold shadow-lg shadow-primary/20 transition-all hover:-translate-y-0.5 active:translate-y-0 active:scale-95">
            <RouterLink to="/signup">Get Started</RouterLink>
          </Button>
        </div>

        <!-- Mobile Menu Trigger -->
        <Sheet>
          <SheetTrigger as-child class="md:hidden">
            <Button variant="ghost" size="icon" class="rounded-full active:scale-95">
              <Menu class="size-5" aria-hidden="true" />
              <span class="sr-only">Toggle menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="right" class="w-[85vw] max-w-sm border-l border-border p-6 sm:max-w-md sm:p-8">
            <SheetHeader class="text-left">
              <SheetTitle class="font-display text-2xl">Navigation</SheetTitle>
              <SheetDescription class="text-foreground/70">Explore SpeakSmart features.</SheetDescription>
            </SheetHeader>
            <nav class="mt-8 flex flex-col gap-2 overscroll-contain">
              <SheetClose v-for="item in navItems" :key="item.href" as-child>
                <a
                  :href="item.href"
                  class="flex items-center rounded-xl px-4 py-3 text-lg font-bold transition-all active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                  :class="activeSectionHref === item.href ? 'bg-primary text-primary-foreground shadow-md' : 'text-foreground/80 hover:bg-muted hover:text-foreground'"
                  @click.prevent="scrollToSection(item.href)"
                >
                  {{ item.label }}
                </a>
              </SheetClose>
            </nav>
            <div class="mt-auto pt-8 flex flex-col gap-4">
              <SheetClose as-child>
                <Button variant="outline" size="lg" class="w-full justify-center font-bold rounded-full transition-transform active:scale-[0.98]" as-child>
                  <RouterLink to="/login">Login</RouterLink>
                </Button>
              </SheetClose>
              <SheetClose as-child>
                <Button size="lg" class="w-full justify-center font-bold rounded-full shadow-md transition-transform active:scale-[0.98]" as-child>
                  <RouterLink to="/signup">Get Started</RouterLink>
                </Button>
              </SheetClose>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>

    <main id="main-content" class="flex flex-col">
      <!-- HERO SECTION -->
      <section id="overview" class="relative flex min-h-[90vh] items-center justify-center overflow-hidden border-b border-border/40 bg-background pt-16 pb-20 md:pt-0">
        <!-- Richer Gradient Background -->
        <div class="absolute inset-0 z-0 bg-[radial-gradient(ellipse_at_top,var(--color-primary)_0%,transparent_60%)] opacity-10" aria-hidden="true"></div>
        <div class="absolute inset-0 z-0 bg-[radial-gradient(circle_at_bottom_left,var(--color-accent)_0%,transparent_50%)] opacity-10" aria-hidden="true"></div>
        
        <div class="container relative z-10 mx-auto px-4 text-center sm:px-6 lg:px-8" data-reveal>
          <Badge variant="outline" class="mb-8 h-auto whitespace-normal rounded-full border-primary/30 bg-primary/10 px-4 py-2 text-center text-xs font-bold leading-snug uppercase tracking-widest text-primary shadow-sm transition-transform hover:scale-105 sm:whitespace-nowrap sm:py-1.5">
            Japanese speaking practice for tourism classrooms
          </Badge>
          
          <h1 class="mx-auto max-w-5xl text-balance font-display text-5xl font-extrabold tracking-tight text-foreground sm:text-6xl md:text-7xl lg:text-8xl lg:leading-[1.05]">
            From first phrase to <br class="hidden sm:inline" />
            <span class="text-primary drop-shadow-sm">front-desk confidence.</span>
          </h1>
          
          <p class="mx-auto mt-8 max-w-2xl text-balance text-lg leading-relaxed text-foreground/80 sm:text-xl">
            <span translate="no" class="font-bold text-foreground">SpeakSmart</span> helps students hear a model line, answer it out loud, and immediately understand what to improve. Instructors get a clean view of class progress without digging through recordings.
          </p>

          <div class="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" class="w-full rounded-full font-bold px-8 text-base shadow-xl shadow-primary/25 transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-primary/30 active:translate-y-0 active:scale-95 sm:w-auto" as-child>
              <RouterLink to="/signup">Start Practicing</RouterLink>
            </Button>
            <Button size="lg" variant="outline" class="w-full rounded-full font-bold px-8 text-base transition-all hover:bg-muted hover:-translate-y-1 active:translate-y-0 active:scale-95 sm:w-auto group" as-child>
              <a href="#practice-loop" @click.prevent="scrollToSection('#practice-loop')">
                See How It Works
                <ArrowRight class="ml-2 size-4 transition-transform group-hover:translate-x-1" aria-hidden="true" />
              </a>
            </Button>
          </div>
        </div>
      </section>

      <!-- PRACTICE LOOP SECTION -->
      <section id="practice-loop" class="py-24 sm:py-32 bg-muted/20">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="mx-auto max-w-3xl text-center" data-reveal>
            <Badge variant="secondary" class="rounded-full px-4 py-1 text-xs font-bold tracking-widest uppercase mb-6 shadow-sm">
              Practice Loop
            </Badge>
            <h2 class="text-balance font-display text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
              A rhythm students can repeat without losing focus.
            </h2>
            <p class="mt-6 text-balance text-lg text-foreground/80">
              The experience stays simple on purpose: hear the line, answer once, then use the feedback to shape the next attempt. That makes the practice loop feel calm for students and measurable for teachers.
            </p>
          </div>

          <div class="mx-auto mt-16 max-w-5xl overflow-hidden rounded-[2rem] border border-border/80 bg-card shadow-2xl shadow-primary/5 transition-transform hover:shadow-primary/10" data-reveal>
            <div class="border-b border-border/60 bg-muted/40 px-6 py-5 sm:px-8">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <p class="text-xs font-bold uppercase tracking-widest text-primary/90">Lesson 04 / Hotel check-in</p>
                  <h3 class="mt-1 font-display text-2xl font-bold text-foreground">One speaking loop. Three clear moments.</h3>
                </div>
                <Badge class="self-start sm:self-center font-bold">Live classroom flow</Badge>
              </div>
            </div>
            
            <div class="p-6 sm:p-8">
              <div class="rounded-2xl bg-primary/5 p-6 border border-primary/15 shadow-inner">
                <p class="text-xs font-bold uppercase tracking-widest text-primary/90">Reference phrase</p>
                <p class="mt-2 text-balance font-display text-2xl font-semibold text-foreground sm:text-3xl">
                  Konbanwa.
                </p>
              </div>

              <div class="mt-8 grid gap-6 sm:grid-cols-3">
                <div v-for="(item, index) in heroCards" :key="item.title" class="group relative rounded-2xl border border-border/60 bg-background p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:border-primary/30" :style="`transition-delay: ${index * 50}ms`">
                  <div class="mb-5 flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary transition-colors duration-300 group-hover:bg-primary group-hover:text-primary-foreground shadow-sm">
                    <AppIcon :name="item.icon" :size="24" aria-hidden="true" />
                  </div>
                  <p class="text-xs font-extrabold uppercase tracking-widest text-foreground/70">{{ item.label }}</p>
                  <h4 class="mt-2 text-xl font-bold text-foreground">{{ item.title }}</h4>
                  <p class="mt-2 text-sm text-foreground/80 leading-relaxed">{{ item.copy }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ROLES SECTION -->
      <section id="roles" class="border-t border-border/60 bg-background py-24 sm:py-32">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="mx-auto max-w-3xl text-center mb-16" data-reveal>
            <Badge variant="secondary" class="rounded-full px-4 py-1 text-xs font-bold tracking-widest uppercase mb-6 shadow-sm">
              One platform, two views
            </Badge>
            <h2 class="text-balance font-display text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
              Clarity for students. <br class="hidden sm:inline" />Signal for instructors.
            </h2>
          </div>

          <div class="grid gap-8 lg:grid-cols-2">
            <!-- Student View -->
            <Card class="overflow-hidden border-border/60 shadow-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl" data-reveal>
              <CardHeader class="border-b border-border/40 bg-muted/30 pb-8">
                <div class="flex items-center gap-4 mb-4">
                  <div class="flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary shadow-sm">
                    <AppIcon name="mic" :size="24" aria-hidden="true" />
                  </div>
                  <Badge variant="outline" class="font-bold uppercase tracking-widest border-border/80 bg-background">For students</Badge>
                </div>
                <CardTitle class="text-3xl sm:text-4xl font-display font-bold">Stay in the speaking flow</CardTitle>
                <CardDescription class="text-base text-foreground/80 mt-3 font-medium">
                  Students get one clear phrase, one clear action, and one clear next step, so practice feels more like rehearsal than homework.
                </CardDescription>
              </CardHeader>
              <CardContent class="bg-background pt-6">
                <ul class="space-y-4">
                  <li v-for="item in studentPoints" :key="item" class="flex items-start gap-4 rounded-xl border border-border/60 bg-card p-4 shadow-sm transition-colors hover:border-primary/30">
                    <div class="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <Check class="size-3.5" aria-hidden="true" />
                    </div>
                    <span class="text-sm font-medium leading-relaxed text-foreground/90">{{ item }}</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <!-- Instructor View -->
            <Card class="overflow-hidden border-border/60 shadow-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl" data-reveal>
              <CardHeader class="border-b border-border/40 bg-primary/5 pb-8 relative">
                <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,var(--color-primary)_0%,transparent_70%)] opacity-5"></div>
                <div class="relative flex items-center gap-4 mb-4">
                  <div class="flex size-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-md">
                    <AppIcon name="chart" :size="24" aria-hidden="true" />
                  </div>
                  <Badge variant="outline" class="font-bold border-primary/20 bg-background text-primary uppercase tracking-widest">For instructors</Badge>
                </div>
                <CardTitle class="relative text-3xl sm:text-4xl font-display font-bold">See where coaching matters next</CardTitle>
                <CardDescription class="relative text-base text-foreground/80 mt-3 font-medium">
                  Teachers can spot class trends, identify weak modules, and decide who needs another demo before the next activity begins.
                </CardDescription>
              </CardHeader>
              <CardContent class="bg-background pt-6">
                <ul class="space-y-4">
                  <li v-for="item in instructorPoints" :key="item" class="flex items-start gap-4 rounded-xl border border-border/60 bg-card p-4 shadow-sm transition-colors hover:border-primary/30">
                    <div class="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <Check class="size-3.5" aria-hidden="true" />
                    </div>
                    <span class="text-sm font-medium leading-relaxed text-foreground/90">{{ item }}</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <!-- ANALYTICS SECTION -->
      <section id="analytics" class="py-24 sm:py-32 bg-muted/20 border-t border-border/40">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid gap-12 lg:grid-cols-[1fr_400px] xl:gap-20">
            <div data-reveal>
              <Badge variant="secondary" class="rounded-full px-4 py-1 text-xs font-bold tracking-widest uppercase mb-6 shadow-sm">
                Why SpeakSmart Fits
              </Badge>
              <h2 class="text-balance font-display text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl lg:text-6xl lg:leading-[1.05]">
                Every attempt becomes something a teacher can act on.
              </h2>
              <p class="mt-6 text-balance text-lg text-foreground/80">
                The product stays anchored in real hospitality language, but the real win is visibility: progress becomes easier to explain, easier to review, and easier to coach.
              </p>

              <div class="mt-12 grid gap-6 sm:grid-cols-2">
                <Card v-for="(item, index) in dashboardStats" :key="item.label" class="border-border/60 bg-card shadow-md transition-transform hover:-translate-y-1 hover:shadow-lg" :style="`transition-delay: ${index * 50}ms`">
                  <CardContent class="p-6">
                    <p class="text-xs font-extrabold uppercase tracking-widest text-foreground/70">{{ item.label }}</p>
                    <p class="mt-4 font-display text-5xl font-extrabold text-foreground">{{ item.value }}</p>
                    <p class="mt-3 text-sm font-medium text-foreground/80">{{ item.copy }}</p>
                  </CardContent>
                </Card>
              </div>
            </div>

            <div class="flex flex-col gap-6">
              <Card v-for="(item, index) in credibilityCards" :key="item.title" class="border-border/60 shadow-sm transition-all duration-300 hover:-translate-x-1 hover:shadow-md" data-reveal :style="`transition-delay: ${index * 100}ms`">
                <CardHeader class="flex flex-row items-start gap-4 space-y-0 p-5 sm:p-6">
                  <div class="flex size-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary shadow-sm">
                    <AppIcon :name="item.icon" :size="20" aria-hidden="true" />
                  </div>
                  <div>
                    <CardTitle class="text-lg font-bold text-foreground leading-tight">{{ item.title }}</CardTitle>
                    <CardDescription class="mt-2 text-sm text-foreground/80 font-medium leading-relaxed">{{ item.copy }}</CardDescription>
                  </div>
                </CardHeader>
              </Card>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA SECTION -->
      <section id="get-started" class="flex min-h-[calc(100vh-64px)] w-full items-center justify-center bg-muted/20 p-4 sm:p-8">
        <div class="container mx-auto w-full max-w-5xl" data-reveal>
          <div class="relative overflow-hidden rounded-[2.5rem] bg-primary px-6 py-12 sm:px-12 sm:py-16 lg:px-20 text-center shadow-2xl transition-transform hover:scale-[1.01] duration-500">
            <!-- Decorative background elements -->
            <div class="absolute inset-0 z-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.15)_0%,transparent_60%)]" aria-hidden="true"></div>
            <div class="absolute inset-0 z-0 bg-[radial-gradient(circle_at_bottom_left,rgba(0,0,0,0.25)_0%,transparent_60%)]" aria-hidden="true"></div>
            
            <div class="relative z-10 mx-auto max-w-3xl">
              <Badge class="mb-8 font-bold border-primary-foreground/30 bg-primary-foreground/15 px-4 py-1.5 text-primary-foreground hover:bg-primary-foreground/25 uppercase tracking-widest backdrop-blur-sm shadow-lg">
                Ready to transform practice?
              </Badge>
              <h2 class="text-balance font-display text-4xl font-extrabold tracking-tight text-primary-foreground sm:text-5xl lg:text-6xl lg:leading-[1.1]">
                Give students a speaking routine that finally feels teachable.
              </h2>
              <p class="mt-8 text-balance text-lg text-primary-foreground/90 sm:text-xl font-medium">
                Create an account to start practicing with guided Japanese phrases, or log in to continue reviewing progress, lessons, and class trends.
              </p>
              
              <div class="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
                <Button size="lg" variant="secondary" class="w-full rounded-full font-bold px-10 py-6 text-lg shadow-xl transition-all hover:bg-background hover:-translate-y-1 hover:shadow-2xl active:translate-y-0 active:scale-95 sm:w-auto" as-child>
                  <RouterLink to="/signup">Create Account</RouterLink>
                </Button>
                <Button size="lg" variant="outline" class="w-full rounded-full font-bold border-primary-foreground/40 bg-transparent px-10 py-6 text-lg text-primary-foreground shadow-lg transition-all hover:bg-primary-foreground/15 hover:text-primary-foreground hover:-translate-y-1 active:translate-y-0 active:scale-95 sm:w-auto" as-child>
                  <RouterLink to="/login">Login</RouterLink>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Menu, Check, ArrowRight } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

import AppIcon from '@/components/shared/AppIcon.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'

const activeSectionHref = ref('#overview')
let scrollFrame = 0
const observer = ref<IntersectionObserver | null>(null)

function getHeaderOffset() {
  return 64
}

function scrollToSection(href: string, updateHistory = true) {
  const target = document.querySelector<HTMLElement>(href)
  if (!target) return

  const targetTop = target.getBoundingClientRect().top + window.scrollY - getHeaderOffset()
  activeSectionHref.value = href

  if (updateHistory) {
    window.history.replaceState(null, '', href)
  }

  window.scrollTo({
    top: Math.max(targetTop, 0),
    behavior: 'smooth',
  })
}

function updateActiveSection() {
  const sections = Array.from(document.querySelectorAll<HTMLElement>('main section[id]'))
  if (!sections.length) return

  const threshold = getHeaderOffset() + 100
  const pageBottom = window.scrollY + window.innerHeight
  const documentHeight = document.documentElement.scrollHeight

  if (documentHeight - pageBottom < 120) {
    activeSectionHref.value = `#${sections.at(-1)?.id ?? 'overview'}`
    return
  }

  let currentSection = sections[0]
  sections.forEach((section) => {
    const { top, bottom } = section.getBoundingClientRect()
    if (top <= threshold && bottom > threshold) {
      currentSection = section
      return
    }
    if (top <= threshold) {
      currentSection = section
    }
  })

  activeSectionHref.value = `#${currentSection.id}`
}

function scheduleActiveSectionUpdate() {
  if (scrollFrame) return
  scrollFrame = window.requestAnimationFrame(() => {
    scrollFrame = 0
    updateActiveSection()
  })
}

const navItems = [
  { label: 'Overview', href: '#overview' },
  { label: 'Practice Loop', href: '#practice-loop' },
  { label: 'Roles', href: '#roles' },
  { label: 'Analytics', href: '#analytics' },
  { label: 'Get Started', href: '#get-started' },
]

const heroCards = [
  {
    icon: 'play',
    label: 'Listen',
    title: 'Hear a natural model first',
    copy: 'Students begin with the target line before they ever press record.',
  },
  {
    icon: 'mic',
    label: 'Respond',
    title: 'Answer out loud right away',
    copy: 'The speaking step stays focused on one useful phrase instead of a crowded interface.',
  },
  {
    icon: 'chart',
    label: 'Improve',
    title: 'See what to repeat next',
    copy: 'Scores and teacher insight turn every attempt into a practical next move.',
  },
]

const studentPoints = [
  'Reference audio is always there before the student speaks.',
  'The recording flow stays short, clear, and easy to repeat.',
  'Modules match greetings, check-in, food service, directions, and emergencies.',
]

const instructorPoints = [
  'Class-level metrics show whether the group is actually progressing.',
  'Individual attempts reveal who needs another model or more repetition.',
  'Weak modules are easier to spot before the next lesson is planned.',
]

const dashboardStats = [
  { value: '91', label: 'Average clarity', copy: 'latest speaking cycle' },
  { value: '32', label: 'Students active', copy: 'this week in practice' },
  { value: '6', label: 'Need follow-up', copy: 'before the next module' },
]

const credibilityCards = [
  {
    icon: 'building',
    title: 'Built around real service situations',
    copy: 'The phrase bank stays close to hospitality, tourism, and guest-facing communication instead of abstract drills.',
  },
  {
    icon: 'book',
    title: 'Lessons feel curriculum-ready',
    copy: 'Modules are easier to fit into classroom routines because each one points to a specific spoken scenario.',
  },
  {
    icon: 'shield',
    title: 'Independent practice still creates teacher signal',
    copy: 'Students can rehearse on their own while instructors keep a visible record of growth, consistency, and weak spots.',
  },
]

onMounted(() => {
  // Respect user preference for reduced motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  // Initialize scroll spy
  updateActiveSection()
  if (window.location.hash) {
    window.requestAnimationFrame(() => {
      scrollToSection(window.location.hash, false)
    })
  }
  window.addEventListener('scroll', scheduleActiveSectionUpdate, { passive: true })
  window.addEventListener('resize', scheduleActiveSectionUpdate)

  // Initialize IntersectionObserver for scroll animations
  if (!prefersReducedMotion && 'IntersectionObserver' in window) {
    observer.value = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('opacity-100', 'translate-y-0')
          entry.target.classList.remove('opacity-0', 'translate-y-8')
          observer.value?.unobserve(entry.target)
        }
      })
    }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' })

    document.querySelectorAll('[data-reveal]').forEach(el => {
      // Set initial state
      el.classList.add('opacity-0', 'translate-y-8', 'transition-all', 'duration-[800ms]', 'ease-out')
      observer.value?.observe(el)
    })
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', scheduleActiveSectionUpdate)
  window.removeEventListener('resize', scheduleActiveSectionUpdate)
  observer.value?.disconnect()
  if (scrollFrame) {
    window.cancelAnimationFrame(scrollFrame)
  }
})
</script>
