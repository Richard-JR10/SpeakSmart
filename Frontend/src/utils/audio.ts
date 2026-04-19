async function blobToArrayBuffer(blob: Blob): Promise<ArrayBuffer> {
  return await blob.arrayBuffer()
}

function interleaveChannels(audioBuffer: AudioBuffer): Float32Array {
  const sampleCount = audioBuffer.length
  const channelCount = audioBuffer.numberOfChannels
  const output = new Float32Array(sampleCount)

  if (channelCount === 1) {
    output.set(audioBuffer.getChannelData(0))
    return output
  }

  for (let i = 0; i < sampleCount; i += 1) {
    let mixed = 0
    for (let channel = 0; channel < channelCount; channel += 1) {
      mixed += audioBuffer.getChannelData(channel)[i] ?? 0
    }
    output[i] = mixed / channelCount
  }

  return output
}

function encodeWav(samples: Float32Array, sampleRate: number): Blob {
  const bytesPerSample = 2
  const dataLength = samples.length * bytesPerSample
  const buffer = new ArrayBuffer(44 + dataLength)
  const view = new DataView(buffer)

  const writeString = (offset: number, value: string) => {
    for (let i = 0; i < value.length; i += 1) {
      view.setUint8(offset + i, value.charCodeAt(i))
    }
  }

  writeString(0, 'RIFF')
  view.setUint32(4, 36 + dataLength, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * bytesPerSample, true)
  view.setUint16(32, bytesPerSample, true)
  view.setUint16(34, 16, true)
  writeString(36, 'data')
  view.setUint32(40, dataLength, true)

  let offset = 44
  for (let i = 0; i < samples.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, samples[i] ?? 0))
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
    offset += bytesPerSample
  }

  return new Blob([buffer], { type: 'audio/wav' })
}

export async function convertAudioBlobToWav(
  blob: Blob,
  targetSampleRate = 16000,
): Promise<Blob> {
  if (blob.type === 'audio/wav') {
    return blob
  }

  const AudioContextCtor =
    window.AudioContext ||
    (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!AudioContextCtor) {
    throw new Error('Audio conversion is not supported in this browser.')
  }

  const audioContext = new AudioContextCtor()

  try {
    const arrayBuffer = await blobToArrayBuffer(blob)
    const decodedBuffer = await audioContext.decodeAudioData(arrayBuffer.slice(0))

    const offlineContext = new OfflineAudioContext(
      1,
      Math.ceil(decodedBuffer.duration * targetSampleRate),
      targetSampleRate,
    )
    const source = offlineContext.createBufferSource()
    source.buffer = decodedBuffer
    source.connect(offlineContext.destination)
    source.start(0)

    const renderedBuffer = await offlineContext.startRendering()
    const monoSamples = interleaveChannels(renderedBuffer)

    return encodeWav(monoSamples, renderedBuffer.sampleRate)
  } finally {
    await audioContext.close()
  }
}
