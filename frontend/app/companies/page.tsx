'use client'

import { useState, useEffect } from 'react'

interface Company {
  id: number;
  name: string;
  description: string;
}

export default function Companies() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/companies')
      .then(response => response.json())
      .then(data => {
        setCompanies(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching companies:', error)
        setLoading(false)
      })
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Companies</h1>
      {loading ? (
        <p>Loading companies...</p>
      ) : (
        <ul className="space-y-4">
          {companies.map((company) => (
            <li key={company.id} className="border p-4 rounded-lg">
              <h2 className="text-xl font-semibold">{company.name}</h2>
              <p className="mt-2">{company.description}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}