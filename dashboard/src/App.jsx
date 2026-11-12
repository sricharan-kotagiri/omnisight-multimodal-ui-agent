import { useCallback, useEffect, useState } from 'react'
import { getRun, getRuns } from './api.js'
import FindingCard from './components/FindingCard.jsx'
import RunForm from './components/RunForm.jsx'

const RUN_STYLE = {
  queued: 'bg-gray-200 text-gray-700',
  running: 'bg-blue-100 text-blue-800',
  done: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

export default function App() {
  const [runs, setRuns] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [run, setRun] = useState(null)
  const [error, setError] = useState(null)

  const loadRuns = useCallback(async () => {
    try {
      setRuns(await getRuns())
      setError(null)
    } catch {
      setError('Backend se connect nahi ho paya. Kya uvicorn (port 8000) chal raha hai?')
    }
  }, [])

  const loadRun = useCallback(async () => {
    if (selectedId == null) return
    try {
      setRun(await getRun(selectedId))
    } catch {
      /* agli poll mein dobara try hoga */
    }
  }, [selectedId])

  // Har 3 second mein runs ki list refresh
  useEffect(() => {
    loadRuns()
    const t = setInterval(loadRuns, 3000)
    return () => clearInterval(t)
  }, [loadRuns])

  // Chuna hua run bhi har 3 second mein refresh
  useEffect(() => {
    loadRun()
    const t = setInterval(loadRun, 3000)
    return () => clearInterval(t)
  }, [loadRun])

  function onStarted(id) {
    setSelectedId(id)
    loadRuns()
  }

  const current = run && run.id === selectedId ? run : null

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-indigo-700">OmniSight</h1>
        <p className="text-sm text-gray-500">Self-healing UI QA dashboard</p>
      </header>

      {error && <div className="bg-red-50 px-6 py-2 text-sm text-red-700">{error}</div>}

      <div className="mx-auto grid max-w-6xl gap-6 p-6 md:grid-cols-[320px_1fr]">
        <aside className="space-y-4">
          <RunForm onStarted={onStarted} />

          <div className="rounded-lg border bg-white p-4">
            <h2 className="mb-3 font-semibold">Runs</h2>
            {runs.length === 0 && <p className="text-sm text-gray-400">Abhi koi run nahi.</p>}
            <ul className="space-y-2">
              {runs.map((r) => (
                <li key={r.id}>
                  <button
                    onClick={() => setSelectedId(r.id)}
                    className={`flex w-full items-center justify-between rounded border px-3 py-2 text-left text-sm ${
                      r.id === selectedId ? 'border-indigo-500 bg-indigo-50' : 'hover:bg-gray-50'
                    }`}
                  >
                    <span>
                      #{r.id} <span className="text-gray-500">{r.bug || 'clean'}</span>
                    </span>
                    <span className={`rounded px-2 py-0.5 text-xs ${RUN_STYLE[r.status] || ''}`}>
                      {r.status}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        <main>
          {selectedId == null && (
            <p className="text-gray-500">Left se koi run chuno, ya naya run start karo.</p>
          )}

          {selectedId != null && !current && <p className="text-gray-500">Loading...</p>}

          {current && (
            <div className="space-y-4">
              <div className="rounded-lg border bg-white p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-lg font-semibold">Run #{current.id}</h2>
                  <span className={`rounded px-2 py-0.5 text-xs ${RUN_STYLE[current.status] || ''}`}>
                    {current.status}
                  </span>
                </div>
                <p className="mt-1 text-sm text-gray-500">
                  bug: {current.bug || 'clean'} | commit: {current.commit_sha} | started:{' '}
                  {current.created_at}
                </p>
                {current.message && <p className="mt-2 text-sm text-red-600">{current.message}</p>}
              </div>

              {(current.status === 'queued' || current.status === 'running') && (
                <p className="text-sm text-blue-700">Scan chal raha hai, results apne aap aa jaayenge...</p>
              )}

              {current.status === 'done' && current.findings.length === 0 && (
                <p className="rounded border bg-green-50 p-4 text-sm text-green-800">
                  Koi UI issue nahi mila.
                </p>
              )}

              {current.findings.map((f) => (
                <FindingCard key={f.id} f={f} onChanged={loadRun} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}