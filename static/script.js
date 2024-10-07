// User Registration
document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(event.target);

            const response = await fetch('/api/users/register', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                alert('Registration successful!'); // Handle success
            } else {
                const error = await response.json();
                alert(error.error); // Handle error
            }
        });
    }


    function checkToken() {
        const accessToken = localStorage.getItem('accessToken');
        if (!accessToken || isJwtExpired(accessToken)) {
            localStorage.removeItem('accessToken');
            window.location.href = '/login.html';
        }
    }

    function isJwtExpired(token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
    }

// Call this function before any API call that requires authentication
checkToken();


    // User Login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(event.target);
            const body = {
                email: formData.get('email'),
                password: formData.get('password')
            };

            try {
                const response = await fetch('/api/users/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(body)
                });

                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('accessToken', data.access_token); // Store the token
                    window.location.href = data.redirect_url; // Redirect user to the dashboard
                } else {
                    alert('Login failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while logging in.');
            }
        });
    }

    
    // Job Searching
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function () {
            const query = document.getElementById('search-input').value;
            fetch(`/api/jobs/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    const jobListingsDiv = document.getElementById('job-listings');
                    if (!jobListingsDiv) return; // Ensure the job listings element exists
                    jobListingsDiv.innerHTML = ''; // Clear previous results

                    if (data.error) {
                        alert(data.error);
                        return;
                    }

                    if (!data.hits || data.hits.length === 0) {
                        jobListingsDiv.innerHTML = '<p>No jobs found.</p>';
                        return;
                    }

                    // Render jobs on the page
                    data.hits.forEach(job => {
                        const jobCard = document.createElement('div');
                        jobCard.classList.add('job-card');
                        jobCard.innerHTML = `
                            <h3>${job.title}</h3>
                            <p>${job.description}</p>
                            <p><strong>Location:</strong> ${job.city}, ${job.country}</p>
                            <p><strong>Company:</strong> ${job.hiringOrganizationName}</p>
                            <p><strong>Posted:</strong> ${new Date(job.created_at).toLocaleDateString()}</p>
                            <p><strong>Apply here:</strong> <a href="${job.url}" target="_blank">Link</a></p>
                        `;
                        jobListingsDiv.appendChild(jobCard);
                    });
                })
                .catch(error => console.error('Error fetching job listings:', error));
        });
    }

    // Job Posting

    const postJobForm = document.getElementById('post-job-form');
    if (postJobForm) {
        postJobForm.addEventListener('submit', function (event) {
            event.preventDefault(); 

            const jobData = {
                job_title: document.getElementById('job_title').value,
                description: document.getElementById('description').value,
                job_type: document.getElementById('job_type').value,
                category: document.getElementById('category').value,
                company_id: document.getElementById('company_id').value,
                experience_level: document.getElementById('experience_level').value,
                application_link: document.getElementById('application_link').value
            };

            postJob(jobData);
        });

        function postJob(jobData) {
            fetch('/api/jobs/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}` // Ensure correct token key
                },
                body: JSON.stringify(jobData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert('Job posted successfully!');
                    postJobForm.reset(); 
                }
            })
            .catch(error => console.error('Error posting job:', error));
        }
    }

    // Fetch and render the job seeker dashboard
    const dashboardContainer = document.getElementById('dashboard-container');
    const accessToken = localStorage.getItem('accessToken');
    if (dashboardContainer) {
        fetch('/api/users/job_seeker_dashboard', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        })
        .then(response => {
        if (!response.ok) {
            // Handle errors, e.g., redirect to login page if 401
            if (response.status === 401) {
                window.location.href = '/login.html';
            }
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Process the data from the API
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}
});