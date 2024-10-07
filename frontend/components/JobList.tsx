import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';

interface Job {
  id: number;
  job_title: string;
  description: string;
  job_type: string;
  location: string;
  company_id: number;
}

export const JobList: React.FC = () => {
    const [jobs, setJobs] = useState<Job[]>([]);

    useEffect(() => {
        fetchApi('/jobs')
            .then(data => setJobs(data))
            .catch(error => console.error('Failed to fetch jobs:', error));
    }, []);

    return (
        <div>
            <h1>Job Listings</h1>
            {jobs.map(job => (
                <div key={job.id}>
                    <h2>{job.job_title}</h2>
                    <p>{job.description}</p>
                    <p>Type: {job.job_type}</p>
                    <p>Location: {job.location}</p>
                </div>
            ))}
        </div>

    );
};