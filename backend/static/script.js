// Navigation and page management
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    loadDashboard();
    loadInitialData();
});

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateToPage(page);
        });
    });

    // Also handle plugin card clicks
    const pluginCards = document.querySelectorAll('.plugin-card');
    pluginCards.forEach(card => {
        card.addEventListener('click', () => {
            const page = card.dataset.page;
            navigateToPage(page);
        });
    });
}

function navigateToPage(pageName) {
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');

    // Update page title
    const titles = {
        dashboard: 'Dashboard',
        github: 'GitHub Integration',
        aws: 'AWS Integration',
        postman: 'Postman Integration',
        'ai-assistant': 'AI Assistant'
    };
    document.getElementById('page-title').textContent = titles[pageName];

    // Show/hide pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.add('hidden');
    });
    const targetPage = document.getElementById(`page-${pageName}`);
    targetPage.classList.remove('hidden');
    targetPage.classList.add('active');

    // Load page-specific data
    switch(pageName) {
        case 'github':
            loadGitHubData();
            break;
        case 'aws':
            loadAWSData();
            break;
        case 'postman':
            loadPostmanData();
            break;
        case 'ai-assistant':
            // Initialize AI chat if needed
            break;
    }
}

function loadDashboard() {
    navigateToPage('dashboard');
}

// ========== INITIAL DATA LOADING ==========
async function loadInitialData() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        updateDashboardMetrics(data);
        updateActivityLog(data.activities || []);
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

function updateDashboardMetrics(data) {
    if (data.cost) {
        document.getElementById('cost-value').textContent = data.cost;
    }
    if (data.incidents !== undefined) {
        document.getElementById('incidents-value').textContent = data.incidents;
    }
    if (data.insights !== undefined) {
        document.getElementById('insights-value').textContent = data.insights;
    }
}

function updateActivityLog(activities) {
    const activityLog = document.getElementById('activity-log');
    if (activities.length === 0) return;

    const activityHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-time">${activity.time || 'Recently'}</div>
            <div class="activity-content">
                <span class="activity-badge ${activity.type.toLowerCase()}">${activity.type}</span>
                <span>${activity.message}</span>
            </div>
        </div>
    `).join('');

    activityLog.innerHTML = activityHTML;
}

// ========== GITHUB PLUGIN ==========
async function loadGitHubData() {
    const commitsContainer = document.getElementById('github-commits');
    const workflowsContainer = document.getElementById('github-workflows');
    const statsContainer = document.getElementById('github-stats');

    try {
        // Load stats
        try {
            const statsRes = await fetch('/api/plugins/github/stats');
            const statsData = await statsRes.json();
            if (statsData) {
                statsContainer.innerHTML = `
                    <div class="data-item">
                        <strong>${statsData.full_name}</strong>
                        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                            ⭐ ${statsData.stars} stars | 🍴 ${statsData.forks} forks | 👁️ ${statsData.watchers} watchers
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                            📝 ${statsData.description || 'No description'}
                        </div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">
                            Language: ${statsData.language || 'Unknown'} | Open Issues: ${statsData.open_issues}
                        </div>
                    </div>
                `;
            }
        } catch (e) {
            console.error('Error loading GitHub stats:', e);
        }

        // Load commits
        const response = await fetch('/api/plugins/github/data');
        const data = await response.json();

        // Display commits
        if (data.commits && data.commits.length > 0) {
            commitsContainer.innerHTML = data.commits.map(commit => `
                <div class="data-item">
                    <strong>${commit.message}</strong>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                        by <strong>${commit.author}</strong> • ${new Date(commit.date).toLocaleDateString()}
                    </div>
                    <div style="font-size: 11px; color: var(--primary); margin-top: 2px;">
                        Commit: ${commit.sha} ${commit.verified ? '✓' : ''}
                    </div>
                </div>
            `).join('');
        } else {
            commitsContainer.innerHTML = '<div class="loading">No recent commits</div>';
        }

        // Display workflows
        if (data.workflows && data.workflows.length > 0) {
            workflowsContainer.innerHTML = data.workflows.map(workflow => {
                const statusColor = workflow.conclusion === 'success' ? 'var(--success)' : 
                                    workflow.conclusion === 'failure' ? 'var(--error)' : 
                                    'var(--warning)';
                return `
                    <div class="data-item">
                        <strong>${workflow.name}</strong>
                        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                            Status: <span style="color: ${statusColor}; text-transform: capitalize;">${workflow.conclusion || workflow.status}</span>
                            | Event: ${workflow.event}
                        </div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">
                            Branch: ${workflow.head_branch} • Run #${workflow.run_number}
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            workflowsContainer.innerHTML = '<div class="loading">No recent workflows</div>';
        }

        // Load other tabs
        loadGitHubPRs();
        loadGitHubIssues();
        loadGitHubBranches();
    } catch (error) {
        console.error('Error loading GitHub data:', error);
        commitsContainer.innerHTML = '<div class="loading">Error loading data</div>';
        workflowsContainer.innerHTML = '<div class="loading">Error loading data</div>';
    }
}

async function loadGitHubPRs() {
    const prsContainer = document.getElementById('github-prs');
    try {
        const response = await fetch('/api/plugins/github/pull-requests');
        const data = await response.json();

        if (data.pull_requests && data.pull_requests.length > 0) {
            prsContainer.innerHTML = data.pull_requests.map(pr => {
                const stateColor = pr.state === 'open' ? 'var(--warning)' : 'var(--success)';
                return `
                    <div class="data-item">
                        <strong>#${pr.number}: ${pr.title}</strong>
                        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                            by ${pr.author} | Status: <span style="color: ${stateColor}; text-transform: capitalize;">${pr.state}</span>
                        </div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">
                            📝 +${pr.additions}/-${pr.deletions} | ${pr.changed_files} files changed
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            prsContainer.innerHTML = '<div class="loading">No pull requests</div>';
        }
    } catch (error) {
        console.error('Error loading PRs:', error);
        prsContainer.innerHTML = '<div class="loading">Error loading data</div>';
    }
}

async function loadGitHubIssues() {
    const issuesContainer = document.getElementById('github-issues');
    try {
        const response = await fetch('/api/plugins/github/issues');
        const data = await response.json();

        if (data.issues && data.issues.length > 0) {
            issuesContainer.innerHTML = data.issues.map(issue => `
                <div class="data-item">
                    <strong>#${issue.number}: ${issue.title}</strong>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                        by ${issue.author} | State: <span style="color: var(--warning); text-transform: capitalize;">${issue.state}</span>
                    </div>
                    ${issue.labels.length > 0 ? `
                        <div style="font-size: 11px; margin-top: 4px;">
                            ${issue.labels.map(label => `<span style="background: rgba(139, 92, 246, 0.2); color: #a78bfa; padding: 2px 6px; border-radius: 3px; margin-right: 4px;">${label}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        } else {
            issuesContainer.innerHTML = '<div class="loading">No issues</div>';
        }
    } catch (error) {
        console.error('Error loading issues:', error);
        issuesContainer.innerHTML = '<div class="loading">Error loading data</div>';
    }
}

async function loadGitHubBranches() {
    const branchesContainer = document.getElementById('github-branches');
    try {
        const response = await fetch('/api/plugins/github/branches');
        const data = await response.json();

        if (data.branches && data.branches.length > 0) {
            branchesContainer.innerHTML = data.branches.map(branch => `
                <div class="data-item">
                    <strong>${branch.name}</strong>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                        Commit: <span style="color: var(--primary);">${branch.commit}</span>
                        ${branch.protected ? ' | 🔒 Protected' : ''}
                    </div>
                </div>
            `).join('');
        } else {
            branchesContainer.innerHTML = '<div class="loading">No branches</div>';
        }
    } catch (error) {
        console.error('Error loading branches:', error);
        branchesContainer.innerHTML = '<div class="loading">Error loading data</div>';
    }
}

function switchGitHubTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.github-tab-content').forEach(tab => {
        tab.classList.remove('active');
        tab.classList.add('hidden');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    const tabId = `github-${tabName}-tab`;
    const tabElement = document.getElementById(tabId);
    if (tabElement) {
        tabElement.classList.remove('hidden');
        tabElement.classList.add('active');
    }
    
    // Add active class to clicked button
    event.target.classList.add('active');
}


// ========== AWS PLUGIN ==========
async function loadAWSData() {
    const resourcesContainer = document.getElementById('aws-resources');
    const costsContainer = document.getElementById('aws-costs');

    try {
        const response = await fetch('/api/plugins/aws/data');
        const data = await response.json();

        // Display resources
        if (data.resources && data.resources.length > 0) {
            resourcesContainer.innerHTML = data.resources.map(resource => `
                <div class="data-item">
                    <strong>${resource.name}</strong>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                        Type: ${resource.type} • Status: <span style="color: var(--success)">${resource.status}</span>
                    </div>
                </div>
            `).join('');
        } else {
            resourcesContainer.innerHTML = '<div class="loading">No resources found</div>';
        }

        // Display costs
        if (data.costs) {
            costsContainer.innerHTML = `
                <div class="data-item">
                    <strong>Monthly Cost</strong>
                    <div style="font-size: 20px; color: var(--primary); font-weight: bold; margin-top: 8px;">
                        ${data.costs.monthly}
                    </div>
                </div>
                <div class="data-item">
                    <strong>Services</strong>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                        ${data.costs.services.map(s => `${s.name}: ${s.cost}`).join(' • ')}
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading AWS data:', error);
        resourcesContainer.innerHTML = '<div class="loading">Error loading data</div>';
        costsContainer.innerHTML = '<div class="loading">Error loading data</div>';
    }
}

// ========== POSTMAN PLUGIN ==========
async function loadPostmanData() {
    const collectionsContainer = document.getElementById('postman-collections');
    const testsContainer = document.getElementById('postman-tests');

    try {
        const response = await fetch('/api/plugins/postman/data');
        const data = await response.json();

        // Display collections
        if (data.collections && data.collections.length > 0) {
            collectionsContainer.innerHTML = data.collections.map(collection => `
                <div class="data-item">
                    <strong>${collection.name}</strong>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                        ${collection.requests} requests • Last updated: ${collection.updated}
                    </div>
                </div>
            `).join('');
        } else {
            collectionsContainer.innerHTML = '<div class="loading">No collections found</div>';
        }

        // Display test results
        if (data.tests && data.tests.length > 0) {
            testsContainer.innerHTML = data.tests.map(test => `
                <div class="data-item">
                    <strong>${test.name}</strong>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                        Result: <span style="color: ${test.passed ? 'var(--success)' : 'var(--error)'}">${test.passed ? 'Passed' : 'Failed'}</span> • ${test.timestamp}
                    </div>
                </div>
            `).join('');
        } else {
            testsContainer.innerHTML = '<div class="loading">No test results</div>';
        }
    } catch (error) {
        console.error('Error loading Postman data:', error);
        collectionsContainer.innerHTML = '<div class="loading">Error loading data</div>';
        testsContainer.innerHTML = '<div class="loading">Error loading data</div>';
    }
}

// ========== AI ASSISTANT ==========
async function sendAIMessage() {
    const input = document.getElementById('ai-input');
    const chatArea = document.getElementById('chat-area');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'chat-message user';
    userMessageDiv.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
    chatArea.appendChild(userMessageDiv);

    input.value = '';
    chatArea.scrollTop = chatArea.scrollHeight;

    try {
        // Send to AI Assistant endpoint
        const response = await fetch('/api/ai/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message })
        });

        const data = await response.json();

        // Add bot response
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'chat-message bot';
        botMessageDiv.innerHTML = `<div class="message-content">${escapeHtml(data.response)}</div>`;
        chatArea.appendChild(botMessageDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
    } catch (error) {
        console.error('Error sending AI message:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-message bot';
        errorDiv.innerHTML = `<div class="message-content">Sorry, I encountered an error. Please try again.</div>`;
        chatArea.appendChild(errorDiv);
    }
}

// ========== UTILITIES ==========
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Keyboard shortcut for sending messages
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.getElementById('ai-input') === document.activeElement) {
        sendAIMessage();
    }
});

// ========== SETTINGS PAGE FUNCTIONS ==========
function testGitHubConnection() {
    const statusDiv = document.getElementById('github-status');
    statusDiv.innerHTML = '<span style="color: var(--warning);">Testing...</span>';
    
    fetch('/api/plugins/github/data')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'connected' || data.commits.length > 0) {
                statusDiv.innerHTML = '<span style="color: var(--success);">✓ GitHub connected successfully!</span>';
            } else {
                statusDiv.innerHTML = '<span style="color: var(--error);">✗ Connection failed. Check your token and repository.</span>';
            }
        })
        .catch(err => {
            statusDiv.innerHTML = '<span style="color: var(--error);">✗ Connection error: ' + err.message + '</span>';
        });
}

function saveGitHubSettings() {
    const token = document.getElementById('github-token').value;
    const repo = document.getElementById('github-repo').value;
    
    if (!token || !repo) {
        alert('Please fill in GitHub token and repository');
        return;
    }
    
    // Save to localStorage for demo (in production, this would go to backend)
    localStorage.setItem('github_token', token);
    localStorage.setItem('github_repo', repo);
    
    alert('Settings saved! You may need to restart the backend for changes to take effect.');
}

function testAWSConnection() {
    const statusDiv = document.getElementById('aws-status');
    statusDiv.innerHTML = '<span style="color: var(--warning);">Testing...</span>';
    
    fetch('/api/plugins/aws/data')
        .then(res => res.json())
        .then(data => {
            if (data.resources && data.resources.length > 0) {
                statusDiv.innerHTML = '<span style="color: var(--success);">✓ AWS connected successfully!</span>';
            } else {
                statusDiv.innerHTML = '<span style="color: var(--warning);">⚠ AWS connected but no resources found.</span>';
            }
        })
        .catch(err => {
            statusDiv.innerHTML = '<span style="color: var(--error);">✗ Connection error: ' + err.message + '</span>';
        });
}

function saveAWSSettings() {
    const key = document.getElementById('aws-key').value;
    const secret = document.getElementById('aws-secret').value;
    const region = document.getElementById('aws-region').value;
    
    if (!key || !secret || !region) {
        alert('Please fill in all AWS credentials');
        return;
    }
    
    localStorage.setItem('aws_key', key);
    localStorage.setItem('aws_secret', secret);
    localStorage.setItem('aws_region', region);
    
    alert('Settings saved! You may need to restart the backend for changes to take effect.');
}

function testPostmanConnection() {
    const statusDiv = document.getElementById('postman-status');
    statusDiv.innerHTML = '<span style="color: var(--warning);">Testing...</span>';
    
    fetch('/api/plugins/postman/data')
        .then(res => res.json())
        .then(data => {
            if (data.collections && data.collections.length > 0) {
                statusDiv.innerHTML = '<span style="color: var(--success);">✓ Postman connected successfully!</span>';
            } else {
                statusDiv.innerHTML = '<span style="color: var(--warning);">⚠ Postman connected but no collections found.</span>';
            }
        })
        .catch(err => {
            statusDiv.innerHTML = '<span style="color: var(--error);">✗ Connection error: ' + err.message + '</span>';
        });
}

function savePostmanSettings() {
    const key = document.getElementById('postman-key').value;
    const workspace = document.getElementById('postman-workspace').value;
    
    if (!key || !workspace) {
        alert('Please fill in Postman API key and workspace ID');
        return;
    }
    
    localStorage.setItem('postman_key', key);
    localStorage.setItem('postman_workspace', workspace);
    
    alert('Settings saved! You may need to restart the backend for changes to take effect.');
}

function savePortalSettings() {
    const darkMode = document.getElementById('dark-mode-toggle').checked;
    const refreshInterval = document.getElementById('refresh-interval').value;
    
    localStorage.setItem('dark_mode', darkMode);
    localStorage.setItem('refresh_interval', refreshInterval);
    
    alert('Portal settings saved!');
    
    // You can add auto-refresh functionality here
    if (refreshInterval > 0) {
        // Auto-refresh dashboard every N seconds
        // setInterval(() => loadInitialData(), refreshInterval * 1000);
    }
}

// Load saved settings on page load
function loadSavedSettings() {
    const githubToken = localStorage.getItem('github_token');
    const githubRepo = localStorage.getItem('github_repo');
    const awsKey = localStorage.getItem('aws_key');
    const awsSecret = localStorage.getItem('aws_secret');
    const awsRegion = localStorage.getItem('aws_region');
    const postmanKey = localStorage.getItem('postman_key');
    const postmanWorkspace = localStorage.getItem('postman_workspace');
    
    if (githubToken) document.getElementById('github-token').value = githubToken;
    if (githubRepo) document.getElementById('github-repo').value = githubRepo;
    if (awsKey) document.getElementById('aws-key').value = awsKey;
    if (awsSecret) document.getElementById('aws-secret').value = awsSecret;
    if (awsRegion) document.getElementById('aws-region').value = awsRegion;
    if (postmanKey) document.getElementById('postman-key').value = postmanKey;
    if (postmanWorkspace) document.getElementById('postman-workspace').value = postmanWorkspace;
}

// Call loadSavedSettings on page load
window.addEventListener('load', loadSavedSettings);

