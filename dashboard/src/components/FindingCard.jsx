import { useState } from 'react'
import { imgUrl, reviewFinding } from '../api.js'

const STATUS_STYLE = {
  fixed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  unfixable: 'bg-gray-200 text-gray-700',
}
const REVIEW_STYLE = {
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

function Shot({ label, path }) {
  const url = imgUrl(path)
  return (
    <div className="flex-1">
      <p className="mb-1 text-xs font-medium text-gray-500">{label}</p>
      {url ? (
        <a href={url} target="_blank" rel="noreferrer">
          <img src={url} alt={label} className="max-h-64 w-full rounded border bg-gray-100 object-contain" />
        </a>
      ) : (
        <div className="flex h-32 items-center justify-center rounded border bg-gray-50 text-xs text-gray-400">
          no image
        </div>
      )}
    </div>
  )
}

export default function FindingCard({ f, onChanged }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  async function act(action) {
    if (
      action === 'approve' &&
      f.pr_url &&
      !window.confirm('Approve karne par GitHub PR merge ho jaayega. Pakka?')
    ) {
      return
    }
    setBusy(true)
    setError(null)
    try {
      await reviewFinding(f.id, action)
      await onChanged()
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  const canReview = f.status === 'fixed' && f.review === 'pending'

  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <span className="font-semibold">
          {f.page} / {f.viewport}
        </span>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs">{f.issue_type}</span>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs">{f.severity}</span>
        <span className={`rounded px-2 py-0.5 text-xs ${STATUS_STYLE[f.status] || ''}`}>
          {f.status} ({f.attempts} attempt{f.attempts === 1 ? '' : 's'})
        </span>
        <span className={`rounded px-2 py-0.5 text-xs ${REVIEW_STYLE[f.review] || ''}`}>
          review: {f.review}
        </span>
      </div>

      <p className="mb-3 text-sm text-gray-700">{f.description}</p>

      <div className="mb-3 flex gap-3">
        <Shot label="Before" path={f.before_img} />
        <Shot label="After (verified fix)" path={f.after_img} />
      </div>

      {f.pr_url && (
        <a href={f.pr_url} target="_blank" rel="noreferrer" className="mb-3 block text-sm text-indigo-600 underline">
          Open Pull Request #{f.pr_number}
        </a>
      )}

      {canReview && (
        <div className="flex gap-2">
          <button
            onClick={() => act('approve')}
            disabled={busy}
            className="rounded bg-green-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          >
            {f.pr_url ? 'Approve & merge' : 'Approve'}
          </button>
          <button
            onClick={() => act('reject')}
            disabled={busy}
            className="rounded bg-red-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          >
            {f.pr_url ? 'Reject & close PR' : 'Reject'}
          </button>
        </div>
      )}
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
    </div>
  )
}