const kanaDigraphs: Record<string, string> = {
  きゃ: 'kya',
  きゅ: 'kyu',
  きょ: 'kyo',
  ぎゃ: 'gya',
  ぎゅ: 'gyu',
  ぎょ: 'gyo',
  しゃ: 'sha',
  しゅ: 'shu',
  しょ: 'sho',
  じゃ: 'ja',
  じゅ: 'ju',
  じょ: 'jo',
  ちゃ: 'cha',
  ちゅ: 'chu',
  ちょ: 'cho',
  にゃ: 'nya',
  にゅ: 'nyu',
  にょ: 'nyo',
  ひゃ: 'hya',
  ひゅ: 'hyu',
  ひょ: 'hyo',
  びゃ: 'bya',
  びゅ: 'byu',
  びょ: 'byo',
  ぴゃ: 'pya',
  ぴゅ: 'pyu',
  ぴょ: 'pyo',
  みゃ: 'mya',
  みゅ: 'myu',
  みょ: 'myo',
  りゃ: 'rya',
  りゅ: 'ryu',
  りょ: 'ryo',
}

const kanaRomaji: Record<string, string> = {
  あ: 'a',
  い: 'i',
  う: 'u',
  え: 'e',
  お: 'o',
  か: 'ka',
  き: 'ki',
  く: 'ku',
  け: 'ke',
  こ: 'ko',
  が: 'ga',
  ぎ: 'gi',
  ぐ: 'gu',
  げ: 'ge',
  ご: 'go',
  さ: 'sa',
  し: 'shi',
  す: 'su',
  せ: 'se',
  そ: 'so',
  ざ: 'za',
  じ: 'ji',
  ず: 'zu',
  ぜ: 'ze',
  ぞ: 'zo',
  た: 'ta',
  ち: 'chi',
  つ: 'tsu',
  て: 'te',
  と: 'to',
  だ: 'da',
  ぢ: 'ji',
  づ: 'zu',
  で: 'de',
  ど: 'do',
  な: 'na',
  に: 'ni',
  ぬ: 'nu',
  ね: 'ne',
  の: 'no',
  は: 'ha',
  ひ: 'hi',
  ふ: 'fu',
  へ: 'he',
  ほ: 'ho',
  ば: 'ba',
  び: 'bi',
  ぶ: 'bu',
  べ: 'be',
  ぼ: 'bo',
  ぱ: 'pa',
  ぴ: 'pi',
  ぷ: 'pu',
  ぺ: 'pe',
  ぽ: 'po',
  ま: 'ma',
  み: 'mi',
  む: 'mu',
  め: 'me',
  も: 'mo',
  や: 'ya',
  ゆ: 'yu',
  よ: 'yo',
  ら: 'ra',
  り: 'ri',
  る: 'ru',
  れ: 're',
  ろ: 'ro',
  わ: 'wa',
  を: 'wo',
  ん: 'n',
  ぁ: 'a',
  ぃ: 'i',
  ぅ: 'u',
  ぇ: 'e',
  ぉ: 'o',
  ゎ: 'wa',
}

export function formatRecognizedTextForDisplay(text: string | null): string | null {
  if (!text) return null

  const collapsed = text.trim().replace(/\s+/g, ' ')
  const romaji = applyParticlePronunciation(collapsed, kanaToRomaji(collapsed))

  if (!romaji || romaji === collapsed) {
    return collapsed
  }

  return romaji
    .split(' ')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

export function kanaToRomaji(text: string): string {
  const normalized = katakanaToHiragana(text.normalize('NFKC').toLowerCase())
  const result: string[] = []
  let geminateNext = false
  let index = 0

  while (index < normalized.length) {
    const pair = normalized.slice(index, index + 2)
    const char = normalized[index]

    if (pair in kanaDigraphs) {
      const romaji = kanaDigraphs[pair]
      if (geminateNext && romaji[0]) {
        result.push(romaji[0])
      }
      geminateNext = false
      result.push(romaji)
      index += 2
      continue
    }

    if (char === 'っ') {
      geminateNext = true
      index += 1
      continue
    }

    if (char === 'ー') {
      const lastVowel = getLastVowel(result[result.length - 1] ?? '')
      if (lastVowel) {
        result.push(lastVowel)
      }
      index += 1
      continue
    }

    const romaji = kanaRomaji[char] ?? char
    if (geminateNext && /^[a-z]/.test(romaji)) {
      result.push(romaji[0])
    }
    geminateNext = false
    result.push(romaji)
    index += 1
  }

  return result.join('')
}

function katakanaToHiragana(text: string): string {
  return Array.from(text, (char) => {
    const codepoint = char.charCodeAt(0)
    if (codepoint >= 0x30a1 && codepoint <= 0x30f6) {
      return String.fromCharCode(codepoint - 0x60)
    }
    return char
  }).join('')
}

function getLastVowel(value: string): string {
  for (let index = value.length - 1; index >= 0; index -= 1) {
    const char = value[index]
    if ('aeiou'.includes(char)) {
      return char
    }
  }
  return ''
}

function applyParticlePronunciation(sourceText: string, romaji: string): string {
  const normalized = katakanaToHiragana(sourceText.normalize('NFKC').toLowerCase())

  if (normalized.endsWith('は') && romaji.endsWith('ha')) {
    return `${romaji.slice(0, -2)}wa`
  }

  if (normalized.endsWith('へ') && romaji.endsWith('he')) {
    return `${romaji.slice(0, -2)}e`
  }

  if (normalized.endsWith('を') && romaji.endsWith('wo')) {
    return `${romaji.slice(0, -2)}o`
  }

  return romaji
}
