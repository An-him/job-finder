'use client'

import { useState, useEffect } from 'react'

interface Application {
  id: number;
  job_title: string;
  company: string;
  status: string;
}

export default function Applications() {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/applications')
      .then(response => response.json())
      .then(data => {
        setApplications(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching applications:', error)
        setLoading(false)
      })
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">My Applications</h1>
      {loading ? (
        <p>Loading applications...</p>
      ) : (
        <ul className="space-y-4">
          {applications.map((application) => (
            <li key={application.id} className="border p-4 rounded-lg">
              <h2 className="text-xl font-semibold">{application.job_title}</h2>
              <p className="text-gray-600">{application.company}</p>
              <p className="mt-2">Status: {application.status}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}