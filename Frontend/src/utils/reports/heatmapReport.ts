import autoTable from 'jspdf-autotable'

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

export interface HeatmapModuleRow {
  moduleId: string
  title: string
  timing: number
  consonants: number
  vowels: number
  overall: number
}

export interface HeatmapTopError {
  moduleTitle: string
  phonemeLabel: string
  score: number
}

export interface HeatmapReportInput {
  modules: HeatmapModuleRow[]
  topErrors: HeatmapTopError[]
  className: string | null
  instructorName: string | null
}

export function downloadHeatmapReport(input: HeatmapReportInput) {
  const doc = createReportDoc()
  const generatedAt = new Date()

  let cursorY = drawHeader(doc, {
    title: 'Pronunciation heatmap',
    subtitle: 'Timing, consonants, vowels, and overall class accuracy across every module.',
    className: input.className,
    instructorName: input.instructorName,
    generatedAt,
  })

  cursorY = drawSectionHeading(doc, 'Module matrix', cursorY)

  if (!input.modules.length) {
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(...reportColors.muted)
    doc.text('No module data available yet.', reportPage.marginX, cursorY + 2)
    drawFooter(doc)
    savePdf(doc, formatReportFilename('heatmap', input.className, generatedAt))
    return
  }

  autoTable(doc, {
    startY: cursorY,
    margin: { left: reportPage.marginX, right: reportPage.marginX },
    head: [['Module', 'Timing', 'Consonants', 'Vowels', 'Overall']],
    body: input.modules.map((module) => [
      module.title,
      formatScore(module.timing),
      formatScore(module.consonants),
      formatScore(module.vowels),
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
      const score = [module.timing, module.consonants, module.vowels, module.overall][data.column.index - 1]
      data.cell.styles.fillColor = scoreFillColor(score)
    },
  })

  const afterMatrixY = ((doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable?.finalY ?? cursorY) + 10
  let nextY = afterMatrixY

  if (input.topErrors.length) {
    nextY = drawSectionHeading(doc, 'Top error clusters', nextY)
    autoTable(doc, {
      startY: nextY,
      margin: { left: reportPage.marginX, right: reportPage.marginX },
      head: [['Module', 'Category', 'Score']],
      body: input.topErrors.map((error) => [
        error.moduleTitle,
        error.phonemeLabel,
        formatScore(error.score),
      ]),
      headStyles: {
        fillColor: reportColors.brand,
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        fontSize: 9,
      },
      bodyStyles: { fontSize: 9, textColor: reportColors.heading },
      columnStyles: {
        0: { cellWidth: 90 },
        1: { cellWidth: 60 },
        2: { cellWidth: 32, halign: 'right', fontStyle: 'bold', textColor: reportColors.scoreWeak },
      },
    })
  }

  drawFooter(doc)
  savePdf(doc, formatReportFilename('heatmap', input.className, generatedAt))
}

function formatScore(score: number): string {
  if (!score || score <= 0) return '—'
  return `${score.toFixed(0)}%`
}
