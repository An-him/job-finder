'use client'

import { useState, useEffect } from 'react'

interface UserProfile {
  id: number;
  name: string;
  email: string;
  bio: string;
}

export default function Profile() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/user/profile')
      .then(response => response.json())
      .then(data => {
        setProfile(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching user profile:', error)
        setLoading(false)
      })
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">My Profile</h1>
      {loading ? (
        <p>Loading profile...</p>
      ) : profile ? (
        <div className="border p-4 rounded-lg">
          <h2 className="text-xl font-semibold">{profile.name}</h2>
          <p className="text-gray-600">{profile.email}</p>
          <p className="mt-2">{profile.bio}</p>
        </div>
      ) : (
        <p>Failed to load profile</p>
      )}
    </div>
  )
}