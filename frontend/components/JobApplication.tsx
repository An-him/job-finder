// components/JobApplication.tsx
import React, { useState } from 'react';
import { fetchApi } from '../utils/api';

interface JobApplicationProps {
  jobId: number;
}

export const JobApplication: React.FC<JobApplicationProps> = ({ jobId }) => {
  const [coverLetter, setCoverLetter] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetchApi('/applications/apply', {
        method: 'POST',
        body: JSON.stringify({ job_id: jobId, cover_letter: coverLetter }),
      });
      alert('Application submitted successfully!');
    } catch (error) {
      console.error('Failed to submit application:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={coverLetter}
        onChange={(e) => setCoverLetter(e.target.value)}
        placeholder="Cover Letter"
        required
      />
      <button type="submit">Apply</button>
    </form>
  );
};