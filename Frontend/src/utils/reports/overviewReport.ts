import autoTable from 'jspdf-autotable'
import html2canvas from 'html2canvas'
import type { jsPDF } from 'jspdf'

import {
  createReportDoc,
  drawFooter,
  drawHeader,
  drawSectionHeading,
  formatReportFilename,
  reportColors,
  reportPage,
  savePdf,
  scoreFillColor,
} from '@/utils/pdfReport'
import type { StudentStat } from '@/types'

export interface OverviewMetric {
  label: string
  value: string
  copy: string
}

export interface OverviewPhonemeBar {
  label: string
  value: number
}

export interface OverviewModuleRow {
  title: string
  overall: number
  mora: number
  consonant: number
  vowel: number
}

export interface OverviewReportInput {
  metrics: OverviewMetric[]
  phonemeBars: OverviewPhonemeBar[]
  modules: OverviewModuleRow[]
  flaggedStudents: StudentStat[]
  topPerformers: StudentStat[]
  flagThreshold: number
  topPerformerThreshold: number
  trendChartElement: HTMLElement | null
  className: string | null
  instructorName: string | null
}

export async function downloadOverviewReport(input: OverviewReportInput) {
  const doc = createReportDoc()
  const generatedAt = new Date()

  let cursorY = drawHeader(doc, {
    title: 'Class analytics overview',
    subtitle: 'Live class pulse — weekly trend, phoneme profile, and intervention candidates.',
    className: input.className,
    instructorName: input.instructorName,
    generatedAt,
  })

  cursorY = drawSectionHeading(doc, 'Today', cursorY)
  cursorY = drawMetricGrid(doc, input.metrics, cursorY)

  if (input.trendChartElement) {
    cursorY = ensureRoomFor(doc, cursorY, 70)
    cursorY = drawSectionHeading(doc, 'Weekly trend', cursorY)
    try {
      cursorY = await drawChartImage(doc, input.trendChartElement, cursorY)
    } catch {
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(9)
      doc.setTextColor(...reportColors.muted)
      doc.text('Weekly trend chart could not be captured.', reportPage.marginX, cursorY + 2)
      cursorY += 8
    }
  }

  cursorY = ensureRoomFor(doc, cursorY, 36)
  cursorY = drawSectionHeading(doc, 'Pronunciation profile', cursorY)
  cursorY = drawPhonemeBars(doc, input.phonemeBars, cursorY)

  if (input.modules.length) {
    cursorY = ensureRoomFor(doc, cursorY, 40)
    cursorY = drawSectionHeading(doc, 'Hardest modules', cursorY)
    autoTable(doc, {
      startY: cursorY,
      margin: { left: reportPage.marginX, right: reportPage.marginX },
      head: [['Module', 'Mora', 'Consonant', 'Vowel', 'Overall']],
      body: input.modules.slice(0, 6).map((module) => [
        module.title,
        formatScore(module.mora),
        formatScore(module.consonant),
        formatScore(module.vowel),
        formatScore(module.overall),
      ]),
      headStyles: {
        fillColor: reportColors.brand,
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        fontSize: 9,
      },
      bodyStyles: { fontSize: 9, textColor: reportColors.heading },
      columnStyles: {
        0: { cellWidth: 70 },
        1: { cellWidth: 26, halign: 'center' },
        2: { cellWidth: 30, halign: 'center' },
        3: { cellWidth: 26, halign: 'center' },
        4: { cellWidth: 30, halign: 'center', fontStyle: 'bold' },
      },
      didParseCell: (data) => {
        if (data.section !== 'body' || data.column.index === 0) return
        const module = input.modules[data.row.index]
        const score = [module.mora, module.consonant, module.vowel, module.overall][data.column.index - 1]
        data.cell.styles.fillColor = scoreFillColor(score)
      },
    })
    cursorY = afterAutoTable(doc, cursorY) + 8
  }

  cursorY = ensureRoomFor(doc, cursorY, 30)
  cursorY = drawSectionHeading(doc, `Flagged students (below ${input.flagThreshold}%)`, cursorY)
  cursorY = drawStudentList(doc, input.flaggedStudents, cursorY, 'flagged')

  cursorY = ensureRoomFor(doc, cursorY + 4, 30)
  cursorY = drawSectionHeading(doc, `Top performers (${input.topPerformerThreshold}% and above)`, cursorY)
  drawStudentList(doc, input.topPerformers, cursorY, 'top')

  drawFooter(doc)
  savePdf(doc, formatReportFilename('overview', input.className, generatedAt))
}

function drawMetricGrid(doc: jsPDF, metrics: OverviewMetric[], startY: number): number {
  if (!metrics.length) return startY

  const columns = Math.min(metrics.length, 5)
  const gap = 3
  const cardWidth = (reportPage.contentWidth - gap * (columns - 1)) / columns
  const cardHeight = 22
  const x = reportPage.marginX

  metrics.forEach((metric, index) => {
    const col = index % columns
    const row = Math.floor(index / columns)
    const cardX = x + col * (cardWidth + gap)
    const cardY = startY + row * (cardHeight + gap)

    doc.setFillColor(...reportColors.surfaceTint)
    doc.setDrawColor(...reportColors.divider)
    doc.roundedRect(cardX, cardY, cardWidth, cardHeight, 1.5, 1.5, 'FD')

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(7.5)
    doc.setTextColor(...reportColors.muted)
    doc.text(metric.label.toUpperCase(), cardX + 3, cardY + 5)

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(14)
    doc.setTextColor(...reportColors.heading)
    doc.text(metric.value, cardX + 3, cardY + 12)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(7.5)
    doc.setTextColor(...reportColors.muted)
    doc.text(metric.copy, cardX + 3, cardY + 17, { maxWidth: cardWidth - 6 })
  })

  const rows = Math.ceil(metrics.length / columns)
  return startY + rows * (cardHeight + gap) + 4
}

async function drawChartImage(doc: jsPDF, element: HTMLElement, startY: number): Promise<number> {
  const canvas = await html2canvas(element, {
    backgroundColor: '#ffffff',
    scale: 2,
    logging: false,
    useCORS: true,
  })
  const dataUrl = canvas.toDataURL('image/png')
  const aspect = canvas.height / canvas.width
  const width = reportPage.contentWidth
  const height = Math.min(width * aspect, 90)
  doc.addImage(dataUrl, 'PNG', reportPage.marginX, startY, width, height)
  return startY + height + 6
}

function drawPhonemeBars(doc: jsPDF, bars: OverviewPhonemeBar[], startY: number): number {
  const x = reportPage.marginX
  const rowHeight = 10
  bars.forEach((bar, index) => {
    const y = startY + index * rowHeight
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(9)
    doc.setTextColor(...reportColors.heading)
    doc.text(bar.label, x, y + 3.2)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.text(`${bar.value.toFixed(1)}%`, x + reportPage.contentWidth, y + 3.2, { align: 'right' })

    const trackY = y + 5
    const trackWidth = reportPage.contentWidth
    doc.setFillColor(...reportColors.divider)
    doc.roundedRect(x, trackY, trackWidth, 2.2, 1.1, 1.1, 'F')

    const fill = scoreFillColor(bar.value)
    const fillWidth = Math.max(0, Math.min(1, bar.value / 100)) * trackWidth
    if (fillWidth > 0) {
      doc.setFillColor(fill[0], fill[1], fill[2])
      doc.roundedRect(x, trackY, fillWidth, 2.2, 1.1, 1.1, 'F')
    }
  })
  return startY + bars.length * rowHeight + 4
}

function drawStudentList(
  doc: jsPDF,
  students: StudentStat[],
  startY: number,
  tone: 'flagged' | 'top',
): number {
  if (!students.length) {
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.setTextColor(...reportColors.muted)
    const message = tone === 'flagged'
      ? 'No students are currently flagged.'
      : 'No top performers in this class yet.'
    doc.text(message, reportPage.marginX, startY + 2)
    return startY + 8
  }

  autoTable(doc, {
    startY,
    margin: { left: reportPage.marginX, right: reportPage.marginX },
    head: [['Learner', 'Email', 'Overall', 'Attempts', 'Streak']],
    body: students.map((student) => [
      student.display_name,
      student.email,
      `${student.overall_average.toFixed(0)}%`,
      String(student.total_attempts),
      `${student.streak_days}d`,
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
      0: { cellWidth: 50 },
      1: { cellWidth: 62 },
      2: { cellWidth: 22, halign: 'right', fontStyle: 'bold', textColor: tone === 'flagged' ? reportColors.scoreWeak : reportColors.scoreStrong },
      3: { cellWidth: 24, halign: 'right' },
      4: { cellWidth: 24, halign: 'right' },
    },
  })

  return afterAutoTable(doc, startY)
}

function ensureRoomFor(doc: jsPDF, currentY: number, neededHeight: number): number {
  const pageHeight = doc.internal.pageSize.getHeight()
  if (currentY + neededHeight > pageHeight - reportPage.marginBottom) {
    doc.addPage()
    return reportPage.marginTop
  }
  return currentY
}

function afterAutoTable(doc: jsPDF, fallbackY: number): number {
  const finalY = (doc as unknown as { lastAutoTable?: { finalY: number } }).lastAutoTable?.finalY
  return (finalY ?? fallbackY) + 6
}

function formatScore(score: number): string {
  if (!score || score <= 0) return '—'
  return `${score.toFixed(0)}%`
}
