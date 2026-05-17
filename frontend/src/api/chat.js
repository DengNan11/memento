const BASE = '/api'

export async function sendMessage(message) {
  const resp = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })
  return resp.json()
}

export async function getMemory() {
  const resp = await fetch(`${BASE}/memory`)
  return resp.json()
}

export async function clearMemory() {
  const resp = await fetch(`${BASE}/clear`, { method: 'POST' })
  return resp.json()
}

export async function manualExtract() {
  const resp = await fetch(`${BASE}/extract`, { method: 'POST' })
  return resp.json()
}
