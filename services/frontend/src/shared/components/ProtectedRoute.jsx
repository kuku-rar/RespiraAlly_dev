import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from './LoadingSpinner'

const ProtectedRoute = ({ requireStaff = false }) => {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingSpinner fullScreen message="驗證身份中..." />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (requireStaff && !user.is_staff) {
    return <Navigate to="/liff" replace />
  }

  return <Outlet />
}

export default ProtectedRoute