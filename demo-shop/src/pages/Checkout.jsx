import { useBug } from '../bugs/useBug.js'

export default function Checkout() {
  const bug = useBug()

  let buttonClass = 'mt-4 rounded bg-green-600 px-4 py-2 text-white'
  if (bug === 'clipped-button') buttonClass += ' relative left-64'
  if (bug === 'hidden-button') buttonClass += ' opacity-0'

  return (
    <div data-source="demo-shop/src/pages/Checkout.jsx">
      <h1 className="mb-4 text-2xl font-bold">Checkout</h1>
      <form
        className="rounded-lg border bg-white p-4"
        onSubmit={(e) => e.preventDefault()}
      >
        <label className="block text-sm font-medium">Full name</label>
        <input className="mb-3 w-full rounded border p-2" placeholder="Your name" />

        <label className="block text-sm font-medium">Address</label>
        <input className="mb-3 w-full rounded border p-2" placeholder="Your address" />

        <button data-testid="place-order" className={buttonClass}>
          Place order
        </button>
      </form>
    </div>
  )
}