<template>
  <section class="min-h-dvh bg-background text-foreground">
    <a
      href="#main-content"
      class="sr-only absolute left-4 top-4 z-50 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-lg focus-visible:not-sr-only focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20"
    >
      Skip to main content
    </a>

    <header ref="headerRef" :class="[revealClass('header', 'motion-drop'), 'sticky top-0 z-40 border-b border-border/80 bg-background/96 backdrop-blur supports-backdrop-filter:bg-background/90']">
      <div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-3 gap-y-2 px-4 py-3 sm:px-6 lg:grid lg:grid-cols-[auto_minmax(0,1fr)_auto] lg:items-center lg:gap-x-6 lg:px-8">
        <a
          href="#overview"
          class="flex min-w-0 items-center gap-2 rounded-full border border-transparent px-2.5 py-1.5 text-[rgb(22_33_27/0.96)] transition-[background-color,border-color,color] duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] hover:bg-[rgb(248_246_241/0.92)] hover:border-[rgb(187_180_162/0.42)] focus-visible:outline-[3px] focus-visible:outline-[rgb(84_122_99/0.24)] focus-visible:outline-offset-3 lg:justify-self-start"
          @click.prevent="scrollToSection('#overview')"
        >
          <span class="hidden sm:flex size-11 items-center justify-center rounded-2xl bg-secondary text-primary">
            <AppIcon name="spark" :size="18" />
          </span>
          <span class="min-w-0 leading-none">
            <span
              translate="no"
              class="block font-(--font-display) text-[1.65rem] leading-none text-(--color-heading)"
            >
              SpeakSmart
            </span>
          </span>
        </a>

        <nav
          aria-label="Landing sections"
          class="order-1 hidden w-full items-center justify-center gap-1 overflow-x-auto rounded-full border border-[rgb(187_180_162/0.52)] bg-[rgb(255_252_246/0.92)] pb-1 shadow-[0_8px_18px_rgba(23,35,29,0.05)] lg:order-0 lg:inline-flex lg:w-auto lg:max-w-fit lg:justify-self-center lg:pb-0"
        >
          <Button
            v-for="item in navItems"
            :key="item.href"
            as-child
            variant="ghost"
            size="sm"
            :class="navButtonClass(item.href)"
          >
            <a
              :href="item.href"
              :aria-current="activeSectionHref === item.href ? 'location' : undefined"
              @click.prevent="scrollToSection(item.href)"
            >
              {{ item.label }}
            </a>
          </Button>
        </nav>

        <div class="hidden gap-3 lg:flex lg:justify-self-end">
          <RouterLink
            to="/login"
            :class="buttonVariants({ variant: 'outline', size: 'default' })"
          >
            Login
          </RouterLink>
          <RouterLink
            to="/signup"
            :class="buttonVariants({ variant: 'default', size: 'default' })"
          >
            Create account
          </RouterLink>
        </div>

        <Sheet>
          <SheetTrigger as-child class="lg:hidden">
            <Button variant="outline" size="icon" class="border-border/80 bg-card/90 text-foreground shadow-xs hover:bg-secondary">
              <Menu aria-hidden="true" />
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
                    :class="navButtonClass(item.href, true)"
                    :aria-current="activeSectionHref === item.href ? 'location' : undefined"
                    @click.prevent="scrollToSection(item.href)"
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
      <section id="overview" class="story-section story-section--hero scroll-mt-28">
        <div class="story-panel story-panel--hero mx-auto flex min-h-[calc(100dvh-5rem)] w-full max-w-6xl items-center justify-center px-4 py-12 sm:px-6 sm:py-14 lg:px-8 lg:py-20">
          <div :class="[revealClass('hero-copy', 'motion-from-left'), 'mx-auto flex min-w-0 max-w-4xl flex-col items-center gap-5 text-center sm:gap-6']" data-scroll-anchor>
            <Badge variant="secondary" class="story-badge rounded-full px-4 py-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] sm:text-[11px] sm:tracking-[0.18em]">
              Japanese speaking practice for tourism classrooms
            </Badge>
            <h1
              class="max-w-4xl text-balance font-(--font-display) text-[clamp(2.95rem,11vw,6.35rem)] leading-[0.9] tracking-[-0.05em] text-(--color-heading)"
            >
              From first phrase to front-desk confidence.
            </h1>
            <p class="max-w-2xl text-base leading-7 text-[rgb(33_51_43/0.82)] sm:text-lg sm:leading-8 lg:text-xl lg:leading-9">
              <span translate="no">SpeakSmart</span> helps students hear a model line, answer it out loud,
              and immediately understand what to improve. Instructors get a clean view
              of class progress without digging through recordings or guesswork.
            </p>

            <div class="flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:justify-center">
              <RouterLink
                to="/signup"
                :class="buttonVariants({ variant: 'default', size: 'lg' })"
                class="w-full sm:w-auto"
              >
                Get started
              </RouterLink>
              <Button as-child variant="outline" size="lg" class="w-full sm:w-auto">
                <a href="#practice-loop" @click.prevent="scrollToSection('#practice-loop')">
                  How it works
                </a>
              </Button>
            </div>
          </div>

          
        </div>
      </section>

      <section id="practice-loop" class="story-section story-section--practice scroll-mt-28">
        <div data-reveal="practice" class="story-panel story-panel--content mx-auto flex min-h-[calc(100dvh-7rem)] w-full max-w-6xl flex-col justify-center px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div :class="[revealClass('practice', 'motion-section-copy'), 'max-w-3xl']" data-scroll-anchor>
            <Badge variant="secondary" class="story-badge rounded-full px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em]">
              Practice loop
            </Badge>
            <h2 class="mt-5 max-w-4xl text-balance font-(--font-display) text-[clamp(2.8rem,6vw,4.95rem)] leading-[0.95] tracking-[-0.045em] text-(--color-heading)">
              A rhythm students can repeat without losing focus.
            </h2>
            <p class="mt-5 max-w-2xl text-base leading-7 text-[rgb(33_51_43/0.82)] sm:text-lg sm:leading-8">
              The experience stays simple on purpose: hear the line, answer once,
              then use the feedback to shape the next attempt. That makes the practice
              loop feel calm for students and measurable for teachers.
            </p>
          </div>

          <div :class="[revealClass('practice', 'motion-from-right'), `story-showcase motion-surface relative mt-10 overflow-hidden rounded-[30px] border border-[rgb(189_203_194/0.72)] bg-[linear-gradient(145deg,rgba(255,253,248,0.98)_0%,rgba(239,245,240,0.96)_100%)] p-4 shadow-[0_20px_48px_rgba(23,35,29,0.09),inset_0_1px_0_rgba(255,255,255,0.65)] before:pointer-events-none before:absolute before:inset-[auto_-12%_-18%_auto] before:h-72 before:w-[18rem] before:rounded-full before:bg-[radial-gradient(circle,rgba(46,138,103,0.16)_0%,rgba(46,138,103,0)_68%)] sm:rounded-[38px] sm:p-[1.4rem] lg:mt-12`]" >
            <div class="flex flex-wrap items-start justify-between gap-4 border-b border-[rgb(189_203_194/0.6)] pb-4">
              <div class="flex flex-col gap-2">
                <p class="m-0 text-[0.75rem] font-bold uppercase tracking-[0.18em] text-[rgb(75_97_87/0.78)]">
                  Lesson 04 / Hotel check-in
                </p>
                <h2 class="m-0 max-w-full font-(--font-display) text-[clamp(1.7rem,2.2vw,2.15rem)] leading-[0.98] text-(--color-heading) lg:max-w-[18rem]">
                  One speaking loop. Three clear moments.
                </h2>
              </div>
              <span class="story-context-badge self-start rounded-full px-[0.85rem] py-[0.55rem] text-[0.72rem] font-bold uppercase tracking-[0.12em]">Live classroom flow</span>
            </div>

            <div class="mt-4 rounded-[28px] bg-[rgb(255_255_255/0.72)] px-[1.15rem] py-[1.15rem] pb-[1.2rem] shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]">
              <p class="m-0 text-[0.8rem] font-bold uppercase tracking-[0.14em] text-[rgb(77_97_143/0.86)]">
                Reference phrase
              </p>
              <p class="m-[0.7rem_0_0] text-balance font-(--font-display) text-[clamp(1.55rem,2.4vw,2rem)] leading-[1.05] text-(--color-heading)">
                Good evening. I have a reservation under Santos.
              </p>
            </div>

            <div class="mt-4 grid gap-[0.9rem]">
              <article
                v-for="(item, index) in heroCards"
                :key="item.title"
                class="story-showcase-item grid grid-cols-[auto_minmax(0,1fr)] items-start gap-3.5 rounded-[22px] bg-[rgb(255_253_249/0.82)] p-3.5 sm:grid-cols-[auto_auto_minmax(0,1fr)] sm:gap-[0.9rem] sm:rounded-[26px] sm:p-4 sm:pb-[1.05rem]"
                :style="{ '--icon-delay': `${index * 180}ms` }"
              >
                <div class="hidden place-items-center rounded-full bg-[rgb(23_49_39/0.08)] text-[0.78rem] font-extrabold tracking-[0.08em] text-[rgb(23_49_39/0.82)] sm:grid sm:h-[2.4rem] sm:min-w-[2.4rem]">
                  0{{ index + 1 }}
                </div>
                <span class="motion-icon grid size-11 place-items-center rounded-2xl bg-[rgb(237_244_239/0.96)] text-primary sm:size-[2.9rem] sm:rounded-[18px]">
                  <AppIcon :name="item.icon" :size="18" />
                </span>
                <div class="flex min-w-0 flex-col gap-1.5">
                  <p class="m-0 text-[0.72rem] font-extrabold uppercase tracking-[0.14em] text-[rgb(75_97_87/0.78)]">
                    {{ item.label }}
                  </p>
                  <h3 class="m-0 text-[1rem] leading-tight text-(--color-heading) sm:text-[1.08rem]">
                    {{ item.title }}
                  </h3>
                  <p class="m-0 text-[0.92rem] leading-[1.6] text-[rgb(33_51_43/0.8)] sm:text-[0.96rem] sm:leading-[1.65]">
                    {{ item.copy }}
                  </p>
                </div>
              </article>
            </div>

            <div class="mt-4 grid grid-cols-1 gap-[0.9rem] lg:grid-cols-2">
              <div class="rounded-3xl bg-[rgb(23_49_39/0.92)] px-4 py-4 pb-[1.1rem] text-[rgb(255_253_249/0.96)]">
                <span class="mb-2 block text-[0.72rem] font-bold uppercase tracking-[0.14em] text-[rgb(255_253_249/0.7)]">Student view</span>
                <strong class="block text-[1rem] font-bold leading-[1.45]">Listen - Record - Review</strong>
              </div>
              <div class="rounded-3xl bg-[rgb(23_49_39/0.92)] px-4 py-4 pb-[1.1rem] text-[rgb(255_253_249/0.96)]">
                <span class="mb-2 block text-[0.72rem] font-bold uppercase tracking-[0.14em] text-[rgb(255_253_249/0.7)]">Instructor view</span>
                <strong class="block text-[1rem] font-bold leading-[1.45]">Attempt history with visible weak spots</strong>
              </div>
            </div>
          </div>

          <div class="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            <Card
              v-for="(item, index) in steps"
              :key="item.title"
              :class="[revealClass('practice', 'motion-card'), 'motion-surface rounded-[30px] border border-border/80 bg-[linear-gradient(180deg,rgba(255,253,249,0.98)_0%,rgba(246,249,245,0.94)_100%)] shadow-[0_14px_34px_rgba(23,35,29,0.06)] backdrop-blur-sm']"
              :style="{ '--motion-delay': `${120 + index * 90}ms` }"
            >
              <CardHeader class="gap-6 sm:gap-7">
                <div class="flex items-center justify-between gap-4">
                  <Badge variant="outline" class="story-outline-badge rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                    0{{ index + 1 }}
                  </Badge>
                  <span class="flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
                    <AppIcon :name="item.icon" :size="18" />
                  </span>
                </div>
                <div class="flex flex-col gap-3">
                  <CardTitle class="text-[1.7rem] leading-tight text-(--color-heading) sm:text-2xl">
                    {{ item.title }}
                  </CardTitle>
                  <CardDescription class="text-[0.97rem] leading-7 text-foreground/80 sm:text-base">
                    {{ item.copy }}
                  </CardDescription>
                </div>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      <section id="roles" class="story-section story-section--roles scroll-mt-28">
        <div data-reveal="roles" class="story-panel story-panel--content mx-auto flex min-h-[calc(100dvh-7rem)] w-full max-w-6xl flex-col justify-center px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div :class="[revealClass('roles', 'motion-section-copy'), 'max-w-3xl']" data-scroll-anchor>
            <Badge variant="secondary" class="story-badge rounded-full px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em]">
              One platform, two views
            </Badge>
            <h2 class="mt-5 max-w-4xl text-balance font-(--font-display) text-[clamp(2.8rem,6vw,4.95rem)] leading-[0.95] tracking-[-0.045em] text-(--color-heading)">
              Clarity for students. Signal for instructors.
            </h2>
            <p class="mt-5 max-w-2xl text-base leading-7 text-[rgb(33_51_43/0.82)] sm:text-lg sm:leading-8">
              The same attempt creates two useful outcomes: students know what to
              repeat next, and instructors know where the class is getting stuck.
            </p>
          </div>

          <div class="mt-10 grid gap-6 lg:mt-12 lg:grid-cols-2">
            <Card
              :class="[revealClass('roles', 'motion-card'), 'motion-surface rounded-4xl border border-border/80 bg-[linear-gradient(180deg,rgba(255,253,249,0.98)_0%,rgba(243,247,244,0.96)_100%)] shadow-[0_14px_34px_rgba(23,35,29,0.06)] backdrop-blur-sm']"
              :style="{ '--motion-delay': '120ms' }"
            >
              <CardHeader class="gap-5">
                <div class="flex items-start gap-3">
                  <span class="flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
                    <AppIcon name="mic" :size="18" />
                  </span>
                  <div class="flex flex-col gap-2">
                    <Badge variant="secondary" class="story-role-badge rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                      For students
                    </Badge>
                    <CardTitle class="text-[1.7rem] leading-tight text-(--color-heading) sm:text-2xl">
                      Stay in the speaking flow
                    </CardTitle>
                  </div>
                </div>
                <CardDescription class="text-[0.97rem] leading-7 text-foreground/80 sm:text-base">
                  Students get one clear phrase, one clear action, and one clear next step,
                  so practice feels more like rehearsal than homework.
                </CardDescription>
              </CardHeader>

              <CardContent>
                <ul class="m-0 grid list-none gap-[0.85rem] p-0">
                  <li
                  v-for="item in studentPoints"
                  :key="item"
                  class="grid grid-cols-[auto_minmax(0,1fr)] items-start gap-[0.8rem] rounded-[22px] border border-[rgb(215_225_218/0.72)] bg-[rgb(255_255_255/0.62)] px-4 py-[0.95rem]"
                >
                  <span class="mt-[0.55rem] size-[0.7rem] rounded-full bg-primary shadow-[0_0_0_6px_rgba(46,138,103,0.12)]" aria-hidden="true" />
                  <span class="text-sm leading-7 text-foreground/84">
                    {{ item }}
                  </span>
                </li>
                </ul>
              </CardContent>
            </Card>

            <Card
              :class="[revealClass('roles', 'motion-card'), 'motion-surface rounded-4xl border border-border/80 bg-[linear-gradient(180deg,rgba(250,252,249,0.98)_0%,rgba(238,244,239,0.96)_100%)] shadow-[0_14px_34px_rgba(23,35,29,0.06)] backdrop-blur-sm']"
              :style="{ '--motion-delay': '220ms' }"
            >
              <CardHeader class="gap-5">
                <div class="flex items-start gap-3">
                  <span class="flex size-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
                    <AppIcon name="chart" :size="18" />
                  </span>
                  <div class="flex flex-col gap-2">
                    <Badge variant="secondary" class="story-role-badge rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                      For instructors
                    </Badge>
                    <CardTitle class="text-[1.7rem] leading-tight text-(--color-heading) sm:text-2xl">
                      See where coaching matters next
                    </CardTitle>
                  </div>
                </div>
                <CardDescription class="text-[0.97rem] leading-7 text-foreground/80 sm:text-base">
                  Teachers can spot class trends, identify weak modules, and decide who needs another
                  demo before the next activity begins.
                </CardDescription>
              </CardHeader>

              <CardContent>
                <ul class="m-0 grid list-none gap-[0.85rem] p-0">
                  <li
                  v-for="item in instructorPoints"
                  :key="item"
                  class="grid grid-cols-[auto_minmax(0,1fr)] items-start gap-[0.8rem] rounded-[22px] border border-[rgb(215_225_218/0.72)] bg-[rgb(255_255_255/0.62)] px-4 py-[0.95rem]"
                >
                  <span class="mt-[0.55rem] size-[0.7rem] rounded-full bg-primary shadow-[0_0_0_6px_rgba(46,138,103,0.12)]" aria-hidden="true" />
                  <span class="text-sm leading-7 text-foreground/84">
                    {{ item }}
                  </span>
                </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section id="analytics" class="story-section story-section--analytics scroll-mt-28">
        <div data-reveal="analytics" class="story-panel story-panel--content mx-auto flex min-h-[calc(100dvh-7rem)] w-full max-w-6xl flex-col justify-center px-4 py-14 sm:px-6 lg:px-8 lg:py-18">
          <div :class="[revealClass('analytics', 'motion-section-copy'), 'max-w-3xl']" data-scroll-anchor>
            <Badge variant="secondary" class="story-badge rounded-full px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em]">
              Why <span translate="no">SpeakSmart</span> fits
            </Badge>
            <h2 class="mt-5 max-w-4xl text-balance font-(--font-display) text-[clamp(2.8rem,6vw,4.95rem)] leading-[0.95] tracking-[-0.045em] text-(--color-heading)">
              Every attempt becomes something a teacher can act on.
            </h2>
            <p class="mt-5 max-w-2xl text-base leading-7 text-[rgb(33_51_43/0.82)] sm:text-lg sm:leading-8">
              The product stays anchored in real hospitality language, but the real win is visibility:
              progress becomes easier to explain, easier to review, and easier to coach.
            </p>
          </div>

          <div class="mt-10 grid gap-6 lg:mt-12 xl:grid-cols-[minmax(0,1.08fr)_minmax(0,0.92fr)]">
            <Card
              :class="[revealClass('analytics', 'motion-card'), 'motion-surface rounded-[34px] border border-border/80 bg-[linear-gradient(180deg,rgba(255,253,249,0.99)_0%,rgba(245,248,244,0.96)_100%)] shadow-[0_14px_34px_rgba(23,35,29,0.06)] backdrop-blur-sm']"
              :style="{ '--motion-delay': '120ms' }"
            >
              <CardHeader class="gap-4">
                <Badge variant="outline" class="story-outline-badge w-fit rounded-full px-3 py-1 uppercase tracking-[0.16em]">
                  Classroom snapshot
                </Badge>
                <CardTitle class="max-w-xl text-[2rem] leading-tight text-(--color-heading) sm:text-3xl">
                  From one response to a class-level picture.
                </CardTitle>
                <CardDescription class="text-[0.97rem] leading-7 text-foreground/80 sm:text-base">
                  Instructors can see who is improving, who is stalled, and which module
                  needs another modeled example before class momentum drops.
                </CardDescription>
              </CardHeader>

              <CardContent class="grid gap-4 md:grid-cols-3">
                <Card
                  v-for="item in dashboardStats"
                  :key="item.label"
                  class="motion-surface gap-0 rounded-[26px] border border-border/80 bg-[linear-gradient(180deg,rgba(237,244,239,0.98)_0%,rgba(250,252,250,0.96)_100%)] shadow-none"
                >
                  <CardHeader class="gap-3 p-5">
                    <Badge variant="outline" class="story-outline-badge w-fit rounded-full px-3 py-1">
                      {{ item.label }}
                    </Badge>
                    <CardTitle class="tabular-nums font-(--font-display) text-[2.6rem] leading-none text-(--color-heading) sm:text-5xl">
                      {{ item.value }}
                    </CardTitle>
                    <CardDescription class="text-sm leading-6 text-foreground/72">
                      {{ item.copy }}
                    </CardDescription>
                  </CardHeader>
                </Card>
              </CardContent>
            </Card>

            <div class="grid gap-5 lg:grid-cols-2 xl:grid-cols-1">
              <Card
                v-for="(item, index) in credibilityCards"
                :key="item.title"
                :class="[revealClass('analytics', 'motion-card'), 'motion-surface rounded-[30px] border border-border/80 bg-[linear-gradient(180deg,rgba(255,253,249,0.98)_0%,rgba(248,245,239,0.94)_100%)] shadow-[0_14px_34px_rgba(23,35,29,0.06)] backdrop-blur-sm']"
                :style="{ '--motion-delay': `${210 + index * 90}ms` }"
              >
                <CardHeader class="gap-4">
                  <div class="flex items-start gap-4">
                    <span class="flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
                      <AppIcon :name="item.icon" :size="18" />
                    </span>
                    <div class="flex flex-col gap-2">
                      <CardTitle class="text-[1.15rem] leading-tight text-(--color-heading) sm:text-xl">
                        {{ item.title }}
                      </CardTitle>
                      <CardDescription class="text-sm leading-7 text-foreground/80 sm:text-[0.97rem]">
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

      <section id="get-started" class="story-section story-section--cta scroll-mt-28">
        <div data-reveal="get-started" class="story-panel story-panel--content mx-auto flex min-h-[calc(100dvh-7rem)] w-full max-w-6xl flex-col justify-center px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <Card
            :class="[revealClass('get-started', 'motion-card'), `story-cta-panel motion-surface relative overflow-hidden rounded-[32px] border border-primary/20 bg-primary text-primary-foreground shadow-[0_18px_44px_rgba(23,35,29,0.08)] before:pointer-events-none before:absolute before:inset-[-30%_auto_auto_-15%] before:h-56 before:w-56 before:rounded-full before:bg-[radial-gradient(circle,rgba(255,255,255,0.18)_0%,rgba(255,255,255,0)_72%)] before:content-[''] before:animate-[cta-glow_8.5s_ease-in-out_infinite] motion-reduce:before:animate-none sm:rounded-[40px]`]"
            :style="{ '--motion-delay': '80ms' }"
            data-scroll-anchor
          >
            <CardHeader class="gap-5">
              <Badge class="story-cta-badge rounded-full px-4 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-foreground">
                Get started
              </Badge>
              <CardTitle class="max-w-3xl text-balance font-(--font-display) text-[clamp(2.8rem,6vw,5.2rem)] leading-[0.94] tracking-[-0.045em] text-primary-foreground">
                Give students a speaking routine that finally feels teachable.
              </CardTitle>
              <CardDescription class="max-w-2xl text-base leading-7 text-primary-foreground/94 sm:text-lg sm:leading-8">
                Create an account to start practicing with guided Japanese phrases,
                or log in to continue reviewing progress, lessons, and class trends.
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
                class="w-full sm:w-auto border-primary-foreground/45 bg-transparent text-primary-foreground hover:bg-primary-foreground/16 hover:text-primary-foreground"
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
import { onMounted, onUnmounted, shallowRef, useTemplateRef } from 'vue'
import { Menu } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

import AppIcon from '@/components/shared/AppIcon.vue'
import { Badge } from '@/components/ui/badge'
import { Button, buttonVariants } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'

const revealTargets = ['header', 'hero-copy', 'hero-cards', 'practice', 'roles', 'analytics', 'get-started'] as const

type RevealKey = (typeof revealTargets)[number]

const prefersReducedMotion = shallowRef(false)
const revealedSections = shallowRef(new Set<RevealKey>())
const activeSectionHref = shallowRef('#overview')
const headerRef = useTemplateRef<HTMLElement>('headerRef')

let revealObserver: IntersectionObserver | null = null
let mediaQuery: MediaQueryList | null = null
let handleMotionPreferenceChange: ((event: MediaQueryListEvent) => void) | null = null
let scrollFrame = 0

function isRevealKey(value: string): value is RevealKey {
  return (revealTargets as readonly string[]).includes(value)
}

function mergeRevealed(keys: RevealKey[]) {
  const next = new Set(revealedSections.value)

  keys.forEach((key) => next.add(key))
  revealedSections.value = next
}

function isRevealed(key: RevealKey) {
  return prefersReducedMotion.value || revealedSections.value.has(key)
}

function revealClass(key: RevealKey, variant = 'motion-rise') {
  return ['motion-block', variant, isRevealed(key) && 'motion-visible']
}

function navButtonClass(href: string, isMobile = false) {
  const isActive = activeSectionHref.value === href

  return [
    isMobile
      ? buttonVariants({ variant: 'ghost', size: 'lg' })
      : '',
    'rounded-full px-[0.8rem] text-[rgb(42_50_47/0.9)] transition-[background-color,color,box-shadow] duration-[180ms] ease-[cubic-bezier(0.16,1,0.3,1)] focus-visible:outline-[3px] focus-visible:outline-[rgb(84_122_99/0.22)] focus-visible:outline-offset-2',
    !isActive && 'hover:bg-[rgb(238_233_223/0.9)] hover:text-[rgb(20_26_23/1)]',
    isMobile && 'w-full justify-start',
    isMobile && 'px-4 text-[rgb(28_36_33/0.94)]',
    isActive && 'bg-[rgb(47_84_63/0.96)] text-[rgb(250_247_240/1)] shadow-[0_8px_18px_rgba(47,84,63,0.22)] hover:bg-[rgb(39_72_54/1)] hover:text-[rgb(255_251_244/1)]',
  ]
}

function getHeaderOffset() {
  const headerBounds = headerRef.value?.getBoundingClientRect()
  const breathingRoom = window.innerWidth >= 1024 ? 24 : window.innerWidth >= 640 ? 18 : 14

  if (!headerBounds) {
    return breathingRoom
  }

  return Math.max(headerBounds.bottom, 0) + breathingRoom
}

function scrollToSection(
  href: string,
  updateHistory = true,
  behavior: ScrollBehavior = prefersReducedMotion.value ? 'auto' : 'smooth',
) {
  const target = document.querySelector<HTMLElement>(href)

  if (!target) {
    return
  }

  const anchor = href === '#overview' || href === '#get-started'
    ? target
    : (target.querySelector<HTMLElement>('[data-scroll-anchor]') ?? target)
  const targetTop = anchor.getBoundingClientRect().top + window.scrollY - getHeaderOffset()

  activeSectionHref.value = href

  if (updateHistory) {
    window.history.replaceState(null, '', href)
  }

  window.scrollTo({
    top: Math.max(targetTop, 0),
    behavior,
  })
}

function updateActiveSection() {
  const sections = Array.from(document.querySelectorAll<HTMLElement>('main section[id]'))

  if (!sections.length) {
    return
  }

  const threshold = getHeaderOffset() + 32
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
  if (scrollFrame) {
    return
  }

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

const steps = [
  {
    icon: 'play',
    title: 'Start with a real hospitality phrase',
    copy: 'Each activity opens with a model line tied to a front-desk, restaurant, or service interaction.',
  },
  {
    icon: 'mic',
    title: 'Capture one spoken answer',
    copy: 'Students stay focused on saying the line clearly, whether they are practicing on desktop or mobile.',
  },
  {
    icon: 'chart',
    title: 'Turn the result into the next repetition',
    copy: 'Feedback and attempt history make improvement visible instead of leaving students guessing.',
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
  mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  handleMotionPreferenceChange = (event) => {
    prefersReducedMotion.value = event.matches

    if (event.matches) {
      mergeRevealed([...revealTargets])
    }
  }

  prefersReducedMotion.value = mediaQuery.matches

  if (mediaQuery.addEventListener && handleMotionPreferenceChange) {
    mediaQuery.addEventListener('change', handleMotionPreferenceChange)
  } else if (handleMotionPreferenceChange) {
    mediaQuery.addListener(handleMotionPreferenceChange)
  }

  if (prefersReducedMotion.value) {
    mergeRevealed([...revealTargets])
    return
  }

  window.requestAnimationFrame(() => {
    mergeRevealed(['header', 'hero-copy', 'hero-cards'])
  })

  if (!('IntersectionObserver' in window)) {
    mergeRevealed(['practice', 'roles', 'analytics', 'get-started'])
    return
  }

  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return
        }

        const key = entry.target instanceof HTMLElement ? entry.target.dataset.reveal : undefined

        if (key && isRevealKey(key)) {
          mergeRevealed([key])
          revealObserver?.unobserve(entry.target)
        }
      })
    },
    {
      threshold: 0.2,
      rootMargin: '0px 0px -10% 0px',
    },
  )

  document.querySelectorAll<HTMLElement>('[data-reveal]').forEach((element) => {
    revealObserver?.observe(element)
  })
  updateActiveSection()

  if (window.location.hash) {
    window.requestAnimationFrame(() => {
      scrollToSection(window.location.hash, false, 'auto')
    })
  }

  window.addEventListener('scroll', scheduleActiveSectionUpdate, { passive: true })
  window.addEventListener('resize', scheduleActiveSectionUpdate)
})

onUnmounted(() => {
  revealObserver?.disconnect()
  window.removeEventListener('scroll', scheduleActiveSectionUpdate)
  window.removeEventListener('resize', scheduleActiveSectionUpdate)

  if (scrollFrame) {
    window.cancelAnimationFrame(scrollFrame)
  }

  if (!mediaQuery || !handleMotionPreferenceChange) {
    return
  }

  if (mediaQuery.removeEventListener) {
    mediaQuery.removeEventListener('change', handleMotionPreferenceChange)
    return
  }

  mediaQuery.removeListener(handleMotionPreferenceChange)
})
</script>

<style scoped>
.story-section {
  position: relative;
  overflow: hidden;
  isolation: isolate;
  background: var(--section-surface, rgb(250 247 240 / 1));
}

.story-panel {
  position: relative;
  z-index: 1;
}

.story-panel--hero,
.story-panel--content {
  scroll-margin-top: 0;
}

.story-panel--content {
  justify-content: flex-start;
  padding-top: 3.75rem;
  padding-bottom: 4.5rem;
}

.story-section--hero::before,
.story-section--practice::before,
.story-section--roles::before,
.story-section--analytics::before,
.story-section--cta::before {
  position: absolute;
  inset: 0;
  z-index: 0;
  content: '';
  pointer-events: none;
}

.story-section--hero {
  --section-surface: rgb(250 247 240 / 1);
}

.story-section--practice {
  --section-surface: rgb(246 249 245 / 1);
}

.story-section--roles {
  --section-surface: rgb(247 249 246 / 1);
}

.story-section--analytics {
  --section-surface: rgb(246 243 236 / 1);
}

.story-section--cta {
  --section-surface: rgb(250 247 240 / 1);
}

.story-section--hero::before {
  background:
    radial-gradient(circle at 82% 24%, rgb(184 141 70 / 0.14), transparent 24%),
    radial-gradient(circle at 18% 28%, rgb(46 138 103 / 0.1), transparent 20%);
}

.story-section--practice::before {
  background:
    linear-gradient(180deg, rgb(255 252 246 / 0.82) 0%, rgb(246 249 245 / 0.98) 100%);
}

.story-section--roles::before {
  background:
    linear-gradient(90deg, rgb(255 253 249 / 0.94) 0%, rgb(241 246 241 / 0.9) 100%);
}

.story-section--analytics::before {
  background:
    radial-gradient(circle at 85% 18%, rgb(46 138 103 / 0.1), transparent 18%),
    linear-gradient(180deg, rgb(252 249 243 / 0.96) 0%, rgb(246 243 236 / 0.99) 100%);
}

.story-section--cta::before {
  background:
    linear-gradient(180deg, rgb(245 240 232 / 0.72) 0%, rgb(250 247 240 / 0.82) 100%);
}

.motion-block {
  --motion-distance: 2.25rem;
  opacity: 0;
  transform: translate3d(0, var(--motion-distance), 0) scale(0.985);
  transition:
    opacity 720ms cubic-bezier(0.16, 1, 0.3, 1),
    transform 720ms cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--motion-delay, 0ms);
  will-change: transform, opacity;
}

.motion-drop {
  --motion-distance: 1.25rem;
  transform: translate3d(0, calc(var(--motion-distance) * -1), 0);
}

.motion-from-left {
  transform: translate3d(calc(var(--motion-distance) * -1), 0, 0) scale(0.985);
}

.motion-from-right {
  transform: translate3d(var(--motion-distance), 0, 0) scale(0.985);
}

.motion-section-copy {
  --motion-distance: 1.75rem;
}

.motion-card {
  --motion-distance: 2rem;
}

.motion-visible {
  opacity: 1;
  transform: translate3d(0, 0, 0) scale(1);
}

.motion-surface {
  transition:
    box-shadow 260ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 260ms cubic-bezier(0.16, 1, 0.3, 1);
}

.motion-block.motion-surface {
  transition:
    opacity 720ms cubic-bezier(0.16, 1, 0.3, 1),
    transform 720ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 260ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 260ms cubic-bezier(0.16, 1, 0.3, 1);
}

.story-badge {
  border: 1px solid rgb(144 178 158 / 0.72);
  background: rgb(234 244 237 / 0.98);
  color: rgb(18 49 38 / 0.98);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.72);
}

.story-context-badge {
  border: 1px solid rgb(168 126 56 / 0.42);
  background: rgb(252 245 229 / 0.98);
  color: rgb(92 63 20 / 1);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.72);
}

.story-outline-badge {
  border-color: rgb(122 144 130 / 0.58);
  background: rgb(255 252 246 / 0.98);
  color: rgb(24 41 34 / 0.96);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.74);
}

.story-role-badge {
  border: 1px solid rgb(156 188 170 / 0.7);
  background: rgb(235 245 238 / 0.98);
  color: rgb(18 51 39 / 0.98);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.7);
}

.story-cta-badge {
  border: 1px solid rgb(255 255 255 / 0.3);
  background: rgb(255 255 255 / 0.18);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.16);
}

.motion-icon {
  animation: icon-drift 5.8s cubic-bezier(0.65, 0, 0.35, 1) infinite;
  animation-delay: var(--icon-delay, 0ms);
}

@keyframes icon-drift {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }

  50% {
    transform: translate3d(0, -0.35rem, 0);
  }
}

@keyframes cta-glow {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
    opacity: 0.72;
  }

  50% {
    transform: translate3d(1.5rem, 1rem, 0) scale(1.08);
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .motion-block {
    opacity: 1;
    transform: none;
    transition: none;
    will-change: auto;
  }

  .motion-surface,
  .motion-block.motion-surface {
    transition: none;
  }

  .motion-icon {
    animation: none;
  }
}

@media (max-width: 1023px) {
  .story-panel--content {
    padding-top: 2.75rem;
    padding-bottom: 3.5rem;
  }

  .story-panel--hero {
    min-height: calc(100dvh - 6.5rem);
    padding-top: 4.5rem;
    padding-bottom: 3.5rem;
  }

  .story-showcase {
    border-radius: 2rem;
  }

  .story-cta-panel {
    border-radius: 2rem;
  }
}

@media (max-width: 767px) {
  .story-panel--hero {
    min-height: calc(100dvh - 6rem);
    padding-top: 4rem;
    padding-bottom: 3rem;
  }

  .story-panel--content {
    padding-top: 2.25rem;
    padding-bottom: 3rem;
  }

  .story-showcase {
    padding: 1rem;
  }

  .story-showcase::before {
    width: 12rem;
    height: 12rem;
    inset: auto -15% -10% auto;
  }

  .story-showcase-item {
    border-radius: 1.35rem;
  }

  .story-cta-panel {
    border-radius: 1.75rem;
  }
}
</style>
