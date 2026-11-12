import { useState } from 'react'
import { startRun } from '../api.js'

const BUGS = [
  { value: '', label: 'None (clean site)' },
  { value: 'clipped-button', label: 'clipped-button' },
  { value: 'hidden-button', label: 'hidden-button' },
  { value: 'overlap', label: 'overlap' },
  { value: 'low-contrast', label: 'low-contrast' },
]
const PAGES = ['home', 'cart', 'checkout']
const VIEWPORTS = ['mobile', 'tablet', 'desktop']

function toggle(list, item) {
  return list.includes(item) ? list.filter((x) => x !== item) : [...list, item]
}

export default function RunForm({ onStarted }) {
  const [bug, setBug] = useState('clipped-button')
  const [pages, setPages] = useState(['checkout'])
  const [viewports, setViewports] = useState(['mobile'])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  async function submit() {
    if (pages.length === 0 || viewports.length === 0) {
      setError('Kam se kam ek page aur ek viewport chuno.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const res = await startRun({
        commit_sha: 'dashboard',
        bug: bug || null,
        pages,
        viewports,
      })
      onStarted(res.run_id)
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="rounded-lg border bg-white p-4">
      <h2 className="mb-3 font-semibold">New run</h2>

      <label className="block text-sm font-medium">Bug to simulate</label>
      <select
        value={bug}
        onChange={(e) => setBug(e.target.value)}
        className="mb-3 w-full rounded border p-2 text-sm"
      >
        {BUGS.map((b) => (
          <option key={b.value} value={b.value}>
            {b.label}
          </option>
        ))}
      </select>

      <p className="text-sm font-medium">Pages</p>
      <div className="mb-3 flex flex-wrap gap-3 text-sm">
        {PAGES.map((p) => (
          <label key={p} className="flex items-center gap-1">
            <input
              type="checkbox"
              checked={pages.includes(p)}
              onChange={() => setPages(toggle(pages, p))}
            />
            {p}
          </label>
        ))}
      </div>

      <p className="text-sm font-medium">Screen sizes</p>
      <div className="mb-3 flex flex-wrap gap-3 text-sm">
        {VIEWPORTS.map((v) => (
          <label key={v} className="flex items-center gap-1">
            <input
              type="checkbox"
              checked={viewports.includes(v)}
              onChange={() => setViewports(toggle(viewports, v))}
            />
            {v}
          </label>
        ))}
      </div>

      <button
        onClick={submit}
        disabled={busy}
        className="w-full rounded bg-indigo-600 px-3 py-2 text-sm text-white disabled:opacity-50"
      >
        {busy ? 'Starting...' : 'Start run'}
      </button>
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
    </div>
  )
}