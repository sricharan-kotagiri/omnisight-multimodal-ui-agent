import AppLink from '../AppLink.jsx'
import { useBug } from '../bugs/useBug.js'

const products = [
  { id: 1, name: 'Wireless Headphones', price: '$59' },
  { id: 2, name: 'Smart Watch', price: '$129' },
  { id: 3, name: 'Travel Backpack', price: '$45' },
]

export default function Home() {
  const bug = useBug()

  return (
    <div data-source="demo-shop/src/pages/Home.jsx">
      <h1 className="mb-4 text-2xl font-bold">Products</h1>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {products.map((p) => (
          <div key={p.id} className="rounded-lg border bg-white p-4 shadow-sm">
            <div className="h-32 rounded bg-indigo-200" />
            <h2 className="mt-3 text-lg font-semibold">{p.name}</h2>
            <p
              className={
                bug === 'overlap'
                  ? '-mt-6 font-bold text-indigo-700'
                  : bug === 'low-contrast'
                  ? 'mt-1 font-bold text-gray-300'
                  : 'mt-1 font-bold text-indigo-700'
              }
            >
              {p.price}
            </p>
            <AppLink
              to="/cart"
              className="mt-3 block rounded bg-indigo-600 px-3 py-2 text-center text-sm text-white"
            >
              Add to cart
            </AppLink>
          </div>
        ))}
      </div>
    </div>
  )
}