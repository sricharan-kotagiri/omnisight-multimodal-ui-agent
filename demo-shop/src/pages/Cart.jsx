import AppLink from '../AppLink.jsx'

export default function Cart() {
  return (
    <div data-source="demo-shop/src/pages/Cart.jsx">
      <h1 className="mb-4 text-2xl font-bold">Your Cart</h1>
      <div className="flex items-center justify-between rounded-lg border bg-white p-4">
        <span>Wireless Headphones</span>
        <span className="font-bold">$59</span>
      </div>
      <AppLink
        to="/checkout"
        className="mt-4 inline-block rounded bg-indigo-600 px-4 py-2 text-white"
      >
        Go to checkout
      </AppLink>
    </div>
  )
}