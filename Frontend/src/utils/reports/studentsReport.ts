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
import type { StudentStat } from '@/types'

export interface StudentsReportInput {
  students: StudentStat[]
  totalStudents: number
  flaggedCount: number
  filters: { label: string; value: string }[]
  className: string | null
  instructorName: string | null
}

export function downloadStudentsReport(input: StudentsReportInput) {
  const doc = createReportDoc()
  const generatedAt = new Date()

  let cursorY = drawHeader(doc, {
    title: 'Class progress report',
    subtitle: 'Snapshot of student standings, attempt activity, and review flags from the class directory.',
    className: input.className,
    instructorName: input.instructorName,
    generatedAt,
  })

  cursorY = drawFilterSummary(doc, input.filters, cursorY)

  cursorY = drawSummaryRow(
    doc,
    [
      { label: 'Students', value: String(input.totalStudents) },
      { label: 'Flagged', value: String(input.flaggedCount) },
      { label: 'In this report', value: String(input.students.length) },
    ],
    cursorY,
  )

  cursorY = drawSectionHeading(doc, 'Learners', cursorY)

  if (!input.students.length) {
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(...reportColors.muted)
    doc.text('No students match the current filters.', reportPage.marginX, cursorY + 2)
    drawFooter(doc)
    savePdf(doc, formatReportFilename('students', input.className, generatedAt))
    return
  }

  autoTable(doc, {
    startY: cursorY,
    margin: { left: reportPage.marginX, right: reportPage.marginX },
    head: [['Learner', 'Email', 'Overall', 'Attempts', 'Streak', 'Status']],
    body: input.students.map((student) => [
      student.display_name,
      student.email,
      `${student.overall_average.toFixed(0)}%`,
      String(student.total_attempts),
      `${student.streak_days}d`,
      student.is_flagged ? 'Needs review' : 'On track',
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
      0: { cellWidth: 42 },
      1: { cellWidth: 56 },
      2: { cellWidth: 18, halign: 'right' },
      3: { cellWidth: 20, halign: 'right' },
      4: { cellWidth: 16, halign: 'right' },
      5: { cellWidth: 30 },
    },
    didParseCell: (data) => {
      if (data.section === 'body' && data.column.index === 5) {
        const text = String(data.cell.raw ?? '')
        if (text === 'Needs review') data.cell.styles.textColor = reportColors.scoreWeak
        else data.cell.styles.textColor = reportColors.scoreStrong
      }
    },
  })

  drawFooter(doc)
  savePdf(doc, formatReportFilename('students', input.className, generatedAt))
}

function drawSummaryRow(
  doc: ReturnType<typeof createReportDoc>,
  items: { label: string; value: string }[],
  startY: number,
): number {
  const x = reportPage.marginX
  const cardWidth = (reportPage.contentWidth - (items.length - 1) * 3) / items.length
  const cardHeight = 14

  items.forEach((item, index) => {
    const cardX = x + index * (cardWidth + 3)
    doc.setFillColor(...reportColors.surfaceTint)
    doc.setDrawColor(...reportColors.divider)
    doc.roundedRect(cardX, startY, cardWidth, cardHeight, 1.5, 1.5, 'FD')

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(8)
    doc.setTextColor(...reportColors.muted)
    doc.text(item.label.toUpperCase(), cardX + 3, startY + 4.5)

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(12)
    doc.setTextColor(...reportColors.heading)
    doc.text(item.value, cardX + 3, startY + 11)
  })

  return startY + cardHeight + 6
}
