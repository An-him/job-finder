import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';

interface Company {
  id: number;
  company_name: string;
  description: string;
  website_url: string;
}

export const CompanyManagement: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [newCompany, setNewCompany] = useState({
    company_name: '',
    description: '',
    website_url: '',
    company_size: '',
    industry: '',
    contact_email: '',
  });

  useEffect(() => {
    fetchApi('/companies')
      .then(data => setCompanies(data))
      .catch(error => console.error('Failed to fetch companies:', error));
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewCompany({ ...newCompany, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const createdCompany = await fetchApi('/companies', {
        method: 'POST',
        body: JSON.stringify(newCompany),
      });
      setCompanies([...companies, createdCompany]);
      setNewCompany({
        company_name: '',
        description: '',
        website_url: '',
        company_size: '',
        industry: '',
        contact_email: '',
      });
    } catch (error) {
      console.error('Failed to create company:', error);
    }
  };

  return (
    <div>
      <h1>Company Management</h1>
      <form onSubmit={handleSubmit}>
        <input
          name="company_name"
          value={newCompany.company_name}
          onChange={handleInputChange}
          placeholder="Company Name"
          required
        />
        <input
          name="description"
          value={newCompany.description}
          onChange={handleInputChange}
          placeholder="Description"
          required
        />
        <input
          name="website_url"
          value={newCompany.website_url}
          onChange={handleInputChange}
          placeholder="Website URL"
          required
        />
        <input
          name="company_size"
          value={newCompany.company_size}
          onChange={handleInputChange}
          placeholder="Company Size"
          required
        />
        <input
          name="industry"
          value={newCompany.industry}
          onChange={handleInputChange}
          placeholder="Industry"
          required
        />
        <input
          name="contact_email"
          value={newCompany.contact_email}
          onChange={handleInputChange}
          placeholder="Contact Email"
          required
        />
        <button type="submit">Create Company</button>
      </form>
      <div>
        <h2>Existing Companies</h2>
        {companies.map(company => (
          <div key={company.id}>
            <h3>{company.company_name}</h3>
            <p>{company.description}</p>
            <a href={company.website_url} target="_blank" rel="noopener noreferrer">Website</a>
          </div>
        ))}
      </div>
    </div>
  );
};