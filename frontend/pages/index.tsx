import { useAuth } from '../contexts/AuthContext'
import { Login } from '../components/Login'
import { JobList } from '../components/JobList'

export default function Home() {
  const { user, isLoading } = useAuth()

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      {user ? (
        <>
          <h1>Welcome, {user.fullname}!</h1>
          <JobList />
        </>
      ) : (
        <Login />
      )}
    </div>
  )
}