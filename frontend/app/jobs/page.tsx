'use client'

import { useState, useEffect } from 'react'

interface Job {
  id: number;
  title: string;
  company: string;
  description: string;
}

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/jobs')
      .then(response => response.json())
      .then(data => {
        setJobs(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching jobs:', error)
        setLoading(false)
      })
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Available Jobs</h1>
      {loading ? (
        <p>Loading jobs...</p>
      ) : (
        <ul className="space-y-4">
          {jobs.map((job) => (
            <li key={job.id} className="border p-4 rounded-lg">
              <h2 className="text-xl font-semibold">{job.title}</h2>
              <p className="text-gray-600">{job.company}</p>
              <p className="mt-2">{job.description}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}