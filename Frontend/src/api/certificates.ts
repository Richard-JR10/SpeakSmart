import api from './axios'

export async function fetchCertificateBlob(studentUid: string, moduleId: string): Promise<Blob> {
  const response = await api.get(
    `/api/v1/progress/${studentUid}/module/${moduleId}/certificate`,
    { responseType: 'blob' },
  )
  return new Blob([response.data as BlobPart], { type: 'application/pdf' })
}

export async function downloadCertificate(studentUid: string, moduleId: string): Promise<void> {
  const blob = await fetchCertificateBlob(studentUid, moduleId)
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const moduleSlug = moduleId.replace(/^module_/, '')
  link.download = `${moduleSlug}_certificate.pdf`
  link.href = url
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
