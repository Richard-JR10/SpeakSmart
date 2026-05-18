<template>
  <DialogRoot :open="open" @update:open="$emit('update:open', $event)">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
      <DialogContent class="fixed top-1/2 left-1/2 z-50 flex max-h-[calc(100vh-2rem)] w-[calc(100%-2rem)] max-w-2xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-2xl border bg-background shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
        <div class="flex shrink-0 items-start justify-between gap-3 border-b px-6 py-5">
          <div>
            <DialogTitle class="font-(--font-display) text-2xl leading-none text-(--color-heading)">
              Terms and Conditions
            </DialogTitle>
            <DialogDescription class="mt-1 text-sm text-muted-foreground">
              Last updated: May 15, 2025
            </DialogDescription>
          </div>
          <Button variant="outline" size="icon" class="shrink-0 rounded-xl" @click="$emit('update:open', false)">
            <X />
            <span class="sr-only">Close</span>
          </Button>
        </div>

        <div class="flex-1 overflow-y-auto px-6 py-5">
          <div class="flex flex-col gap-6 text-sm leading-7 text-foreground">
            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">1. Acceptance of Terms</h2>
              <p class="text-muted-foreground">
                By creating an account on SpeakSmart, you confirm that you have read, understood, and agree to be
                bound by these Terms and Conditions. If you do not agree, you must not create an account or use the
                platform. These terms apply to all users, including students and instructors.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">2. Description of Service</h2>
              <p class="text-muted-foreground">
                SpeakSmart is an educational speech-practice platform developed for Gordon College. It provides
                students with guided pronunciation exercises, attempt tracking, and progress scoring, and gives
                instructors access to analytics, learner oversight tools, and exercise management.
              </p>
              <p class="text-muted-foreground">
                The platform is provided for academic and educational purposes. Access may be limited or withdrawn
                at any time by the institution or platform administrators.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">3. User Accounts</h2>
              <p class="text-muted-foreground">
                You must provide accurate, complete, and current information when registering. Each account is
                personal and non-transferable. You are responsible for maintaining the confidentiality of your
                password and for all activity that occurs under your account.
              </p>
              <p class="text-muted-foreground">
                You must notify us immediately if you become aware of any unauthorised use of your account.
                SpeakSmart is not liable for any loss resulting from unauthorised use of your credentials.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">4. User Responsibilities</h2>
              <p class="text-muted-foreground">
                You agree to use SpeakSmart only for lawful, educational purposes. You must not:
              </p>
              <ul class="ml-4 flex list-disc flex-col gap-1 text-muted-foreground">
                <li>Submit false or misleading information during registration or use</li>
                <li>Attempt to gain unauthorised access to other accounts or system components</li>
                <li>Upload or transmit harmful, offensive, or unlawful content</li>
                <li>Interfere with or disrupt the platform's operation or infrastructure</li>
                <li>Share your account credentials with any other person</li>
                <li>Use the platform in any way that violates applicable laws or regulations</li>
              </ul>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">5. Student-Specific Terms</h2>
              <p class="text-muted-foreground">
                As a student, you agree that your practice submissions, attempt records, scores, and progress data
                may be reviewed by your assigned instructors for academic purposes. You understand that this data
                forms part of your learning record within the institution.
              </p>
              <p class="text-muted-foreground">
                You must complete attempts honestly and without attempting to manipulate or misrepresent your
                performance scores.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">6. Instructor-Specific Terms</h2>
              <p class="text-muted-foreground">
                As an instructor, you are granted access to student analytics, submission data, and progress
                records solely for legitimate educational oversight. You agree to handle learner data with
                confidentiality and in compliance with applicable privacy laws and institutional policies.
              </p>
              <p class="text-muted-foreground">
                You must not share, export, or otherwise disclose identifiable student data to unauthorised
                parties.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">7. Intellectual Property</h2>
              <p class="text-muted-foreground">
                All content, design, code, and materials provided through SpeakSmart — including exercises, scoring
                models, and interface elements — are the property of SpeakSmart and Gordon College, or their
                respective licensors. You may not reproduce, modify, distribute, or create derivative works without
                prior written permission.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">8. Prohibited Activities</h2>
              <p class="text-muted-foreground">
                The following are strictly prohibited on SpeakSmart:
              </p>
              <ul class="ml-4 flex list-disc flex-col gap-1 text-muted-foreground">
                <li>Reverse-engineering, scraping, or automated access to platform data</li>
                <li>Circumventing authentication, role restrictions, or access controls</li>
                <li>Submitting audio or content that is offensive, harmful, or unrelated to academic use</li>
                <li>Impersonating another user, instructor, or administrator</li>
                <li>Using the platform for commercial purposes without express written authorisation</li>
              </ul>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">9. Termination</h2>
              <p class="text-muted-foreground">
                SpeakSmart reserves the right to suspend or terminate your account at any time if you violate
                these Terms and Conditions or if required by institutional policy. You may request account deletion
                by contacting support. Upon termination, your access to the platform will cease immediately.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">10. Limitation of Liability</h2>
              <p class="text-muted-foreground">
                SpeakSmart is provided on an "as is" and "as available" basis. To the fullest extent permitted by
                law, SpeakSmart and Gordon College disclaim all warranties, express or implied. We are not liable
                for any indirect, incidental, or consequential damages arising from your use of the platform,
                including loss of data or academic records.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">11. Changes to Terms</h2>
              <p class="text-muted-foreground">
                We may update these Terms and Conditions from time to time. Changes will be posted within the
                platform and the effective date will be updated. Continued use of SpeakSmart after changes are
                posted constitutes acceptance of the revised terms.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">12. Contact</h2>
              <p class="text-muted-foreground">
                For questions or concerns about these Terms and Conditions, please contact us at
                <span class="font-medium text-foreground">speaksmart@gmail.com</span>.
              </p>
            </section>
          </div>
        </div>

        <div class="shrink-0 border-t px-6 py-4">
          <Button class="w-full" @click="$emit('update:open', false)">
            Close
          </Button>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'
import {
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'

import { Button } from '@/components/ui/button'

defineProps<{ open: boolean }>()
defineEmits<{ 'update:open': [value: boolean] }>()
</script>
