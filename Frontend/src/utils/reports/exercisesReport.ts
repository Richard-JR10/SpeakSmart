import autoTable from 'jspdf-autotable'

import {
  createReportDoc,
  drawFilterSummary,
  drawFooter,
  drawHeader,
  drawSectionHeading,
  formatReportFilename,
  reportColors,
  reportPage,
  savePdf,
} from '@/utils/pdfReport'

export type ExerciseStudentStatus = 'graded' | 'partial' | 'ready' | 'incomplete'

export interface ExerciseStudentRow {
  studentName: string
  status: ExerciseStudentStatus
  teacherScore: number | null
  submittedCount: number
  requiredCount: number
  releasedAt: string | null
}

export interface ExerciseSummaryItem {
  label: string
  value: string
}

export interface ExercisesReportInput {
  assignmentTitle: string
  summaryItems: ExerciseSummaryItem[]
  rows: ExerciseStudentRow[]
  filters: { label: string; value: string }[]
  className: string | null
  instructorName: string | null
}

export function downloadExercisesReport(input: ExercisesReportInput) {
  const doc = createReportDoc()
  const generatedAt = new Date()

  let cursorY = drawHeader(doc, {
    title: 'Assignment grading report',
    subtitle: input.assignmentTitle,
    className: input.className,
    instructorName: input.instructorName,
    generatedAt,
  })

  cursorY = drawFilterSummary(doc, input.filters, cursorY)

  cursorY = drawSummaryRow(doc, input.summaryItems, cursorY)

  cursorY = drawSectionHeading(doc, 'Student review queue', cursorY)

  if (!input.rows.length) {
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(...reportColors.muted)
    doc.text('No students match the current filters for this assignment.', reportPage.marginX, cursorY + 2)
    drawFooter(doc)
    savePdf(doc, formatReportFilename(`assignment-${slugifyTitle(input.assignmentTitle)}`, input.className, generatedAt))
    return
  }

  autoTable(doc, {
    startY: cursorY,
    margin: { left: reportPage.marginX, right: reportPage.marginX },
    head: [['Student', 'Status', 'Submitted', 'Teacher score', 'Released']],
    body: input.rows.map((row) => [
      row.studentName,
      formatStatus(row.status),
      `${row.submittedCount}/${row.requiredCount}`,
      row.teacherScore == null ? '—' : `${row.teacherScore.toFixed(0)}%`,
      row.releasedAt ? formatDate(row.releasedAt) : '—',
    ]),
    headStyles: {
      fillColor: reportColors.brand,
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 9,
    },
    bodyStyles: { fontSize: 9, textColor: reportColors.heading },
    alternateRowStyles: { fillColor: reportColors.surfaceTint },
    columnStyles: {
      0: { cellWidth: 56 },
      1: { cellWidth: 32 },
      2: { cellWidth: 26, halign: 'center' },
      3: { cellWidth: 32, halign: 'right' },
      4: { cellWidth: 36, halign: 'right' },
    },
    didParseCell: (data) => {
      if (data.section !== 'body' || data.column.index !== 1) return
      const status = input.rows[data.row.index].status
      if (status === 'graded') data.cell.styles.textColor = reportColors.scoreStrong
      else if (status === 'ready') data.cell.styles.textColor = reportColors.scoreSteady
      else if (status === 'partial') data.cell.styles.textColor = reportColors.scoreSteady
      else data.cell.styles.textColor = reportColors.muted
    },
  })

  drawFooter(doc)
  savePdf(doc, formatReportFilename(`assignment-${slugifyTitle(input.assignmentTitle)}`, input.className, generatedAt))
}

function drawSummaryRow(
  doc: ReturnType<typeof createReportDoc>,
  items: ExerciseSummaryItem[],
  startY: number,
): number {
  if (!items.length) return startY
  const x = reportPage.marginX
  const columns = Math.min(items.length, 5)
  const gap = 3
  const cardWidth = (reportPage.contentWidth - gap * (columns - 1)) / columns
  const cardHeight = 16

  items.forEach((item, index) => {
    const cardX = x + index * (cardWidth + gap)
    doc.setFillColor(...reportColors.surfaceTint)
    doc.setDrawColor(...reportColors.divider)
    doc.roundedRect(cardX, startY, cardWidth, cardHeight, 1.5, 1.5, 'FD')

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(7.5)
    doc.setTextColor(...reportColors.muted)
    doc.text(item.label.toUpperCase(), cardX + 3, startY + 5)

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(12)
    doc.setTextColor(...reportColors.heading)
    doc.text(item.value, cardX + 3, startY + 12)
  })

  return startY + cardHeight + 6
}

function formatStatus(status: ExerciseStudentStatus): string {
  if (status === 'graded') return 'Graded'
  if (status === 'ready') return 'Ready to grade'
  if (status === 'partial') return 'Partially graded'
  return 'Incomplete'
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function slugifyTitle(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    || 'assignment'
}
