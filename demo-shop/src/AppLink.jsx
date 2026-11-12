import { Link, useLocation } from 'react-router-dom'

export default function AppLink({ to, ...props }) {
  const { search } = useLocation()
  return <Link to={{ pathname: to, search }} {...props} />
}