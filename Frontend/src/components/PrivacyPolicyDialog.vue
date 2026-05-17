<template>
  <DialogRoot :open="open" @update:open="$emit('update:open', $event)">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
      <DialogContent class="fixed top-1/2 left-1/2 z-50 flex max-h-[calc(100vh-2rem)] w-[calc(100%-2rem)] max-w-2xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-2xl border bg-background shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
        <div class="flex shrink-0 items-start justify-between gap-3 border-b px-6 py-5">
          <div>
            <DialogTitle class="font-(--font-display) text-2xl leading-none text-(--color-heading)">
              Privacy Policy
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
              <h2 class="text-base font-semibold text-(--color-heading)">1. Introduction</h2>
              <p class="text-muted-foreground">
                SpeakSmart ("we", "us", or "our") is committed to protecting your personal information. This
                Privacy Policy explains what data we collect, how we use it, and your rights regarding that data.
                By creating an account, you agree to the practices described in this policy.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">2. Information We Collect</h2>
              <p class="text-muted-foreground">
                We collect the following categories of information when you use SpeakSmart:
              </p>
              <ul class="ml-4 flex list-disc flex-col gap-1 text-muted-foreground">
                <li>
                  <span class="font-medium text-foreground">Account information:</span> your full name, email
                  address, and account role (student or instructor)
                </li>
                <li>
                  <span class="font-medium text-foreground">Speech and practice data:</span> audio submissions,
                  pronunciation attempt records, scores, and exercise completion history
                </li>
                <li>
                  <span class="font-medium text-foreground">Usage data:</span> pages visited, features used, and
                  session activity within the platform
                </li>
                <li>
                  <span class="font-medium text-foreground">Device information:</span> browser type, operating
                  system, and IP address collected automatically through Firebase services
                </li>
              </ul>
              <p class="text-muted-foreground">
                We do not collect payment information or any sensitive personal data beyond what is listed above.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">3. How We Use Your Information</h2>
              <p class="text-muted-foreground">
                The information we collect is used exclusively for the following purposes:
              </p>
              <ul class="ml-4 flex list-disc flex-col gap-1 text-muted-foreground">
                <li>Creating and managing your SpeakSmart account</li>
                <li>Delivering speech-practice exercises and tracking your progress</li>
                <li>Providing instructors with analytics and oversight tools for academic use</li>
                <li>Improving platform performance, reliability, and user experience</li>
                <li>Communicating important updates or changes to the platform</li>
                <li>Complying with legal or institutional obligations</li>
              </ul>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">4. Data Sharing</h2>
              <p class="text-muted-foreground">
                We do not sell, rent, or trade your personal information. We share data only in the following
                limited circumstances:
              </p>
              <ul class="ml-4 flex list-disc flex-col gap-1 text-muted-foreground">
                <li>
                  <span class="font-medium text-foreground">Firebase (Google LLC):</span> we use Firebase
                  Authentication and cloud infrastructure to store account credentials and platform data securely.
                  Google's privacy policy applies to data processed through Firebase.
                </li>
                <li>
                  <span class="font-medium text-foreground">Instructors:</span> student progress records and
                  attempt data are accessible to assigned instructors within the platform for academic oversight.
                </li>
                <li>
                  <span class="font-medium text-foreground">Gordon College administrators:</span> aggregated or
                  identifiable data may be shared with institutional administrators as required by academic or
                  compliance policies.
                </li>
                <li>
                  <span class="font-medium text-foreground">Legal obligations:</span> we may disclose information
                  when required by law, court order, or to protect the rights and safety of users and the
                  institution.
                </li>
              </ul>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">5. Data Retention</h2>
              <p class="text-muted-foreground">
                We retain your account and practice data for as long as your account is active or as needed for
                academic record-keeping. If you request account deletion, we will remove your identifiable data
                within a reasonable period, except where retention is required by law or institutional policy.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">6. Security</h2>
              <p class="text-muted-foreground">
                We use industry-standard security measures to protect your data, including encrypted transmission
                via HTTPS, Firebase Authentication for credential management, and role-based access controls to
                limit data access to authorised users only.
              </p>
              <p class="text-muted-foreground">
                While we take reasonable precautions, no system is completely secure. We encourage you to use a
                strong, unique password and to keep your login credentials confidential.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">7. Children's Privacy</h2>
              <p class="text-muted-foreground">
                SpeakSmart is an educational platform operated within an academic institution. Student users may
                include individuals under 18. We collect only the minimum data necessary for academic use and do
                not use it for advertising or commercial profiling. Use of the platform by minors is subject to
                institutional oversight and parental or guardian awareness where required.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">8. Your Rights</h2>
              <p class="text-muted-foreground">
                You have the following rights regarding your personal data:
              </p>
              <ul class="ml-4 flex list-disc flex-col gap-1 text-muted-foreground">
                <li>
                  <span class="font-medium text-foreground">Access:</span> request a copy of the personal data we
                  hold about you
                </li>
                <li>
                  <span class="font-medium text-foreground">Correction:</span> request correction of inaccurate or
                  incomplete data
                </li>
                <li>
                  <span class="font-medium text-foreground">Deletion:</span> request deletion of your account and
                  associated personal data, subject to retention requirements
                </li>
                <li>
                  <span class="font-medium text-foreground">Objection:</span> object to certain uses of your data
                  where applicable law permits
                </li>
              </ul>
              <p class="text-muted-foreground">
                To exercise any of these rights, contact us using the details in the section below.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">9. Changes to This Policy</h2>
              <p class="text-muted-foreground">
                We may update this Privacy Policy periodically. When we do, we will update the "Last updated"
                date at the top of this document and notify users through the platform where practical. Continued
                use of SpeakSmart after changes are posted constitutes your acceptance of the updated policy.
              </p>
            </section>

            <section class="flex flex-col gap-2">
              <h2 class="text-base font-semibold text-(--color-heading)">10. Contact & Data Protection Officer</h2>
              <p class="text-muted-foreground">
                For questions, requests, or concerns about this Privacy Policy or the handling of your personal data,
                please contact our designated Data Protection Officer:
              </p>
              <ul class="ml-4 flex list-disc flex-col gap-1 text-muted-foreground">
                <li><span class="font-medium text-foreground">Name:</span> Mr. Aaron Selubo</li>
                <li><span class="font-medium text-foreground">Institution:</span> Gordon College, Olongapo City, Philippines</li>
                <li><span class="font-medium text-foreground">Email:</span> 202312292@gordoncollege.edu.ph</li>
              </ul>
              <p class="text-muted-foreground">
                This contact is in accordance with the requirements of the Data Privacy Act of 2012 (Republic Act No. 10173)
                and the National Privacy Commission's guidelines.
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
