import { useLocation } from 'react-router-dom'

// Reads the bug name from the URL, e.g. /checkout?bug=hidden-button
export function useBug() {
  const { search } = useLocation()
  return new URLSearchParams(search).get('bug')
}