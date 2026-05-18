import { jsPDF } from 'jspdf'

export type RGB = [number, number, number]

export const reportColors = {
  brand: [194, 65, 96] as RGB,
  heading: [55, 31, 41] as RGB,
  muted: [120, 113, 116] as RGB,
  divider: [232, 213, 219] as RGB,
  surfaceTint: [253, 245, 247] as RGB,
  scoreStrong: [35, 116, 92] as RGB,
  scoreSteady: [184, 123, 38] as RGB,
  scoreWeak: [198, 85, 73] as RGB,
}

export const reportPage = {
  marginX: 14,
  marginTop: 14,
  marginBottom: 18,
  contentWidth: 182,
}

export interface ReportHeaderOptions {
  title: string
  subtitle?: string | null
  className?: string | null
  instructorName?: string | null
  generatedAt?: Date
}

export function createReportDoc() {
  return new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' })
}

export function drawHeader(doc: jsPDF, options: ReportHeaderOptions): number {
  const generatedAt = options.generatedAt ?? new Date()
  const x = reportPage.marginX
  let y = reportPage.marginTop

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(10)
  doc.setTextColor(...reportColors.brand)
  doc.text('SpeakSmart', x, y)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.setTextColor(...reportColors.muted)
  doc.text(formatGeneratedAt(generatedAt), pageRight(doc), y, { align: 'right' })

  y += 7
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(18)
  doc.setTextColor(...reportColors.heading)
  doc.text(options.title, x, y)

  if (options.subtitle) {
    y += 5.5
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(...reportColors.muted)
    doc.text(options.subtitle, x, y, { maxWidth: reportPage.contentWidth })
  }

  const metaLine = buildMetaLine(options)
  if (metaLine) {
    y += 5
    doc.setFontSize(9)
    doc.setTextColor(...reportColors.muted)
    doc.text(metaLine, x, y)
  }

  y += 3
  doc.setDrawColor(...reportColors.divider)
  doc.setLineWidth(0.4)
  doc.line(x, y, pageRight(doc), y)

  return y + 6
}

export function drawSectionHeading(doc: jsPDF, label: string, y: number): number {
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(11)
  doc.setTextColor(...reportColors.heading)
  doc.text(label, reportPage.marginX, y)
  return y + 5
}

export function drawFilterSummary(
  doc: jsPDF,
  filters: { label: string; value: string }[],
  startY: number,
): number {
  const active = filters.filter((f) => f.value && f.value.trim().length > 0)
  if (!active.length) return startY

  let y = startY
  const x = reportPage.marginX
  const lineHeight = 4.4
  const rows = active.map((f) => `${f.label}: ${f.value}`)

  const padding = 3
  const boxHeight = rows.length * lineHeight + padding * 2

  doc.setFillColor(...reportColors.surfaceTint)
  doc.setDrawColor(...reportColors.divider)
  doc.roundedRect(x, y, reportPage.contentWidth, boxHeight, 1.5, 1.5, 'FD')

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.setTextColor(...reportColors.heading)

  let textY = y + padding + 3
  for (const row of rows) {
    doc.text(row, x + padding + 1, textY)
    textY += lineHeight
  }

  return y + boxHeight + 5
}

export function drawFooter(doc: jsPDF) {
  const pageCount = doc.getNumberOfPages()
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(8)
  doc.setTextColor(...reportColors.muted)

  for (let page = 1; page <= pageCount; page += 1) {
    doc.setPage(page)
    const pageHeight = doc.internal.pageSize.getHeight()
    const y = pageHeight - 8
    doc.text('SpeakSmart instructor report', reportPage.marginX, y)
    doc.text(`Page ${page} of ${pageCount}`, pageRight(doc), y, { align: 'right' })
  }
}

export function savePdf(doc: jsPDF, filename: string) {
  const blob = doc.output('blob')
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function formatReportFilename(view: string, className: string | null | undefined, date: Date = new Date()) {
  const datePart = date.toISOString().slice(0, 10)
  const classPart = slugify(className) || 'class'
  return `speaksmart-${view}-${classPart}-${datePart}.pdf`
}

export function scoreFillColor(score: number): RGB {
  if (score <= 0) return [244, 244, 245]
  if (score < 55) return mixWithWhite(reportColors.scoreWeak, 0.72)
  if (score < 70) return mixWithWhite(reportColors.scoreSteady, 0.7)
  if (score < 85) return mixWithWhite(reportColors.scoreStrong, 0.74)
  return mixWithWhite(reportColors.scoreStrong, 0.58)
}

export function pageRight(doc: jsPDF): number {
  return doc.internal.pageSize.getWidth() - reportPage.marginX
}

export function formatGeneratedAt(date: Date): string {
  return `Generated ${date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })} at ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`
}

function buildMetaLine(options: ReportHeaderOptions): string {
  const parts: string[] = []
  if (options.className) parts.push(`Class: ${options.className}`)
  if (options.instructorName) parts.push(`Instructor: ${options.instructorName}`)
  return parts.join('   ·   ')
}

function slugify(value: string | null | undefined): string {
  if (!value) return ''
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function mixWithWhite(color: RGB, whiteAmount: number): RGB {
  const clamp = Math.min(Math.max(whiteAmount, 0), 1)
  return [
    Math.round(color[0] * (1 - clamp) + 255 * clamp),
    Math.round(color[1] * (1 - clamp) + 255 * clamp),
    Math.round(color[2] * (1 - clamp) + 255 * clamp),
  ]
}
