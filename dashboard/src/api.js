export const API = 'http://localhost:8000'

async function request(path, options) {
  const res = await fetch(`${API}${path}`, options)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json()
}

export const getRuns = () => request('/runs')
export const getRun = (id) => request(`/runs/${id}`)

export const startRun = (body) =>
  request('/runs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

export const reviewFinding = (id, action) =>
  request(`/findings/${id}/${action}`, { method: 'POST' })

export const imgUrl = (path) => (path ? `${API}/artifacts/${path}` : null)