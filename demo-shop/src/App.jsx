import { Routes, Route } from 'react-router-dom'
import AppLink from './AppLink.jsx'
import Home from './pages/Home.jsx'
import Cart from './pages/Cart.jsx'
import Checkout from './pages/Checkout.jsx'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b bg-white p-4">
        <nav className="mx-auto flex max-w-3xl items-center justify-between">
          <AppLink to="/" className="text-xl font-bold text-indigo-700">
            DemoShop
          </AppLink>
          <AppLink to="/cart" className="text-sm font-medium">
            Cart
          </AppLink>
        </nav>
      </header>

      <main className="mx-auto max-w-3xl p-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
        </Routes>
      </main>
    </div>
  )
}