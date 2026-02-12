/**
 * ANSE Operator UI Dashboard
 * Handles agent monitoring, audit log, and approval token management
 */

// API Configuration
const API_BASE = '/api';
const POLL_INTERVAL_MS = 2000; // Poll every 2 seconds
const AUTH_HEADER = {
    'Authorization': 'Basic ' + btoa('admin:admin'), // Dev only
    'Content-Type': 'application/json'
};

// State
let currentSelectedAgent = null;
let agents = [];
let auditEvents = [];
let pollIntervalId = null;

// DOM Elements
const agentsList = document.getElementById('agents-list');
const agentDetails = document.getElementById('agent-details');
const systemHealth = document.getElementById('system-health');
const recentEvents = document.getElementById('recent-events');
const auditStream = document.getElementById('audit-stream');
const approvalForm = document.getElementById('approval-form');
const tokenResult = document.getElementById('token-result');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const timestampEl = document.getElementById('timestamp');
const tabButtons = document.querySelectorAll('.tab-button');
const tabPanes = document.querySelectorAll('.tab-pane');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    startPolling();
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
});

// Setup event listeners
function setupEventListeners() {
    // Tab switching
    tabButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });

    // Refresh agents button
    document.getElementById('refresh-agents').addEventListener('click', () => {
        loadAgents();
    });

    // Audit controls
    document.getElementById('audit-filter-tool').addEventListener('input', (e) => {
        filterAuditEvents(e.target.value);
    });

    document.getElementById('audit-refresh').addEventListener('click', () => {
        loadAuditEvents();
    });

    // Approval form
    approvalForm.addEventListener('submit', (e) => {
        e.preventDefault();
        issueApprovalToken();
    });

    // Token copy button
    document.getElementById('token-copy')?.addEventListener('click', () => {
        const tokenText = document.getElementById('token-value').textContent;
        navigator.clipboard.writeText(tokenText).then(() => {
            alert('Token copied to clipboard');
        });
    });
}

// Tab switching
function switchTab(tabName) {
    // Update buttons
    tabButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update panes
    tabPanes.forEach(pane => {
        pane.classList.toggle('active', pane.id === `${tabName}-tab`);
    });

    // Load data for specific tabs
    if (tabName === 'audit') {
        loadAuditEvents();
    }
}

// Polling loop
function startPolling() {
    loadAgents();
    loadSystemHealth();
    
    pollIntervalId = setInterval(() => {
        loadAgents();
        loadSystemHealth();
        if (currentSelectedAgent) {
            loadRecentEvents();
        }
    }, POLL_INTERVAL_MS);
}

// Load agents
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/agents`, { headers: AUTH_HEADER });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        agents = data.agents || [];
        
        renderAgentsList();
        setConnected(true);
    } catch (error) {
        console.error('Failed to load agents:', error);
        setConnected(false);
        agentsList.innerHTML = `<div class="empty">Error loading agents</div>`;
    }
}

// Render agents list
function renderAgentsList() {
    if (agents.length === 0) {
        agentsList.innerHTML = '<div class="empty">No active agents</div>';
        return;
    }

    agentsList.innerHTML = agents.map(agent => `
        <div class="agent-item ${agent.id === currentSelectedAgent ? 'active' : ''}" 
             onclick="selectAgent('${agent.id}')">
            <span class="agent-id">${agent.id}</span>
            <span class="agent-type">${agent.agent_type}</span>
        </div>
    `).join('');

    // Auto-select first agent if none selected
    if (!currentSelectedAgent && agents.length > 0) {
        selectAgent(agents[0].id);
    }
}

// Select agent
function selectAgent(agentId) {
    currentSelectedAgent = agentId;
    renderAgentsList();
    loadAgentDetails();
    loadRecentEvents();
    updateApprovalForm();
}

// Load agent details
async function loadAgentDetails() {
    if (!currentSelectedAgent) {
        agentDetails.innerHTML = '<p class="empty">No agent selected</p>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/agents/${currentSelectedAgent}`, { headers: AUTH_HEADER });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const agent = await response.json();
        
        agentDetails.innerHTML = `
            <div class="detail-row">
                <span class="detail-label">Agent ID</span>
                <span class="detail-value">${agent.id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Type</span>
                <span class="detail-value">${agent.agent_type}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status</span>
                <span class="detail-value">${agent.status}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Created</span>
                <span class="detail-value">${new Date(agent.created_at).toLocaleString()}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Last Heartbeat</span>
                <span class="detail-value">${new Date(agent.last_heartbeat).toLocaleString()}</span>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load agent details:', error);
        agentDetails.innerHTML = '<p class="empty">Error loading agent details</p>';
    }
}

// Load system health
async function loadSystemHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`, { headers: AUTH_HEADER });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const health = await response.json();
        
        systemHealth.innerHTML = `
            <div class="health-item">
                <span class="health-label">Status</span>
                <span class="health-value">
                    <span class="health-indicator" style="background-color: #4ade80;"></span>
                    ${health.status}
                </span>
            </div>
            <div class="health-item">
                <span class="health-label">Operator UI</span>
                <span class="health-value">Running</span>
            </div>
            <div class="health-item">
                <span class="health-label">Timestamp</span>
                <span class="health-value">${new Date(health.timestamp).toLocaleString()}</span>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load system health:', error);
        systemHealth.innerHTML = '<p class="empty">Error loading system health</p>';
    }
}

// Load recent events
async function loadRecentEvents() {
    if (!currentSelectedAgent) {
        recentEvents.innerHTML = '<p class="empty">No agent selected</p>';
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE}/audit?agent_id=${currentSelectedAgent}&limit=5`,
            { headers: AUTH_HEADER }
        );
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        const events = data.events || [];
        
        if (events.length === 0) {
            recentEvents.innerHTML = '<p class="empty">No recent events</p>';
            return;
        }

        recentEvents.innerHTML = events.map(event => `
            <div class="event-item">
                <div class="event-time">${new Date(event.timestamp).toLocaleTimeString()}</div>
                <div class="event-text">
                    ${event.tool_name} → <strong>${event.status}</strong>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load recent events:', error);
        recentEvents.innerHTML = '<p class="empty">Error loading events</p>';
    }
}

// Load audit events
async function loadAuditEvents() {
    try {
        const response = await fetch(
            `${API_BASE}/audit?limit=50`,
            { headers: AUTH_HEADER }
        );
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        auditEvents = data.events || [];
        
        renderAuditEvents(auditEvents);
    } catch (error) {
        console.error('Failed to load audit events:', error);
        auditStream.innerHTML = '<p class="empty">Error loading audit log</p>';
    }
}

// Render audit events
function renderAuditEvents(events) {
    if (events.length === 0) {
        auditStream.innerHTML = '<p class="empty">No audit events</p>';
        return;
    }

    auditStream.innerHTML = events.map(event => `
        <div class="audit-event ${event.status}">
            <div class="audit-meta">
                <div>
                    <span class="audit-tool">${event.tool_name}</span>
                    <span> @ ${new Date(event.timestamp).toLocaleTimeString()}</span>
                </div>
                <span class="audit-status">${event.status}</span>
            </div>
            <div style="color: var(--text-secondary); font-size: 0.75rem;">
                Agent: ${event.agent_id}
            </div>
        </div>
    `).join('');
}

// Filter audit events
function filterAuditEvents(toolName) {
    if (!toolName.trim()) {
        renderAuditEvents(auditEvents);
        return;
    }

    const filtered = auditEvents.filter(event =>
        event.tool_name.toLowerCase().includes(toolName.toLowerCase())
    );
    renderAuditEvents(filtered);
}

// Issue approval token
async function issueApprovalToken() {
    const agentId = document.getElementById('approve-agent').value;
    const scope = document.getElementById('approve-scope').value;
    const ttlSeconds = parseInt(document.getElementById('approve-ttl').value);

    if (!agentId || !scope) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/approve`, {
            method: 'POST',
            headers: AUTH_HEADER,
            body: JSON.stringify({
                agent_id: agentId,
                scope: scope,
                ttl_seconds: ttlSeconds
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Error: ${error.error || 'Failed to issue token'}`);
            return;
        }

        const result = await response.json();

        // Show token result
        document.getElementById('token-value').textContent = result.token;
        document.getElementById('token-expires').textContent = new Date(result.expires_at).toLocaleString();
        tokenResult.classList.remove('hidden');

        // Reset form
        approvalForm.reset();
    } catch (error) {
        console.error('Failed to issue token:', error);
        alert('Error issuing token');
    }
}

// Update approval form with selected agent
function updateApprovalForm() {
    if (currentSelectedAgent) {
        document.getElementById('approve-agent').value = currentSelectedAgent;
    }
}

// Connection status
function setConnected(isConnected) {
    if (isConnected) {
        statusIndicator.className = 'status-indicator status-connected';
        statusText.textContent = 'Connected';
    } else {
        statusIndicator.className = 'status-indicator status-disconnected';
        statusText.textContent = 'Disconnected';
    }
}

// Update timestamp
function updateTimestamp() {
    const now = new Date();
    timestampEl.textContent = now.toLocaleTimeString();
}
