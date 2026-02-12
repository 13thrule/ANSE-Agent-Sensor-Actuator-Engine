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

    // Replay & Timeline controls
    document.getElementById('replay-refresh')?.addEventListener('click', () => {
        loadAuditTimeline();
    });

    document.getElementById('export-audit-json')?.addEventListener('click', () => {
        exportAuditTrail('json');
    });

    document.getElementById('export-audit-pdf')?.addEventListener('click', () => {
        exportAuditTrail('pdf');
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
    } else if (tabName === 'replay') {
        loadAuditTimeline();
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
// ============================================================================
// AUDIT REPLAY & TIMELINE FUNCTIONS
// ============================================================================

/**
 * Load audit timeline with filtering options
 */
async function loadAuditTimeline() {
    const agentFilter = document.getElementById('replay-filter-agent')?.value || '';
    const toolFilter = document.getElementById('replay-filter-tool')?.value || '';
    const statusFilter = document.getElementById('replay-filter-status')?.value || '';

    try {
        const params = new URLSearchParams();
        params.append('limit', 100);
        if (agentFilter) params.append('agent_id', agentFilter);
        if (toolFilter) params.append('tool', toolFilter);
        if (statusFilter) params.append('status', statusFilter);

        const response = await fetch(`${API_BASE}/audit/timeline?${params}`, {
            headers: AUTH_HEADER
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        renderAuditTimeline(data.timeline || []);
        loadAuditStats();
    } catch (error) {
        console.error('Failed to load audit timeline:', error);
        document.getElementById('audit-timeline').innerHTML =
            '<div style="color: var(--error-color);">Failed to load timeline</div>';
    }
}

/**
 * Render audit timeline with interactive events
 */
function renderAuditTimeline(events) {
    const container = document.getElementById('audit-timeline');

    if (!events || events.length === 0) {
        container.innerHTML = '<div class="empty">No events match the filters</div>';
        return;
    }

    container.innerHTML = events.map((event, idx) => `
        <div class="timeline-event ${event.status}" data-event-id="${event.id}">
            <div class="timeline-marker">
                <div class="timeline-dot"></div>
                ${idx < events.length - 1 ? '<div class="timeline-line"></div>' : ''}
            </div>
            <div class="timeline-content">
                <div class="timeline-header">
                    <span class="timeline-tool">${event.tool}</span>
                    <span class="timeline-timestamp">${new Date(event.timestamp).toLocaleString()}</span>
                </div>
                <div>
                    <span class="timeline-agent">${event.agent_id}</span>
                    <span style="margin-left: 0.5rem; font-size: 0.85rem;">
                        Status: <strong>${event.status === 'success' ? '✓' : '✗'} ${event.status}</strong>
                    </span>
                </div>
                <div class="timeline-details">
                    <div class="timeline-detail">
                        <span class="timeline-label">Severity:</span>
                        <span class="timeline-value">${event.severity || 'normal'}</span>
                    </div>
                    <div class="timeline-detail">
                        <span class="timeline-label">Duration:</span>
                        <span class="timeline-value">-</span>
                    </div>
                </div>
                <div class="timeline-actions">
                    <button class="btn-small" onclick="viewEventDetails(${event.id})">Details</button>
                    <button class="btn-small" onclick="replayEvent(${event.id})">Replay</button>
                </div>
            </div>
        </div>
    `).join('');

    // Add click handlers for timeline events
    document.querySelectorAll('.timeline-event').forEach(el => {
        el.addEventListener('click', (e) => {
            if (!e.target.closest('button')) {
                viewEventDetails(parseInt(el.dataset.eventId));
            }
        });
    });
}

/**
 * Load and display audit statistics
 */
async function loadAuditStats() {
    try {
        const response = await fetch(`${API_BASE}/audit/stats`, {
            headers: AUTH_HEADER
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const stats = await response.json();
        renderAuditStats(stats);
    } catch (error) {
        console.error('Failed to load audit stats:', error);
    }
}

/**
 * Render audit statistics dashboard
 */
function renderAuditStats(stats) {
    const container = document.getElementById('audit-stats');

    const toolUsageHTML = stats.tool_usage
        .slice(0, 5)
        .map(
            (item) => `
        <div class="tool-usage-item">
            <span class="tool-usage-name">${item.tool}</span>
            <span class="tool-usage-count">${item.count} calls</span>
        </div>
    `
        )
        .join('');

    const agentActivityHTML = stats.agent_activity
        .slice(0, 5)
        .map(
            (item) => `
        <div class="tool-usage-item">
            <span class="tool-usage-name">${item.agent}</span>
            <span class="tool-usage-count">${item.count} actions</span>
        </div>
    `
        )
        .join('');

    container.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">Total Events</div>
            <div class="stat-value">${stats.total_events}</div>
            <div class="stat-subtext">${stats.successful_events} successful, ${stats.failed_events} failed</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Success Rate</div>
            <div class="stat-value">${stats.success_rate.toFixed(1)}%</div>
            <div class="stat-subtext">${stats.successful_events}/${stats.total_events}</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Top Tools</div>
            <div class="tool-usage-list">
                ${toolUsageHTML}
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Top Agents</div>
            <div class="tool-usage-list">
                ${agentActivityHTML}
            </div>
        </div>
    `;
}

/**
 * View detailed event information
 */
async function viewEventDetails(eventId) {
    try {
        const response = await fetch(`${API_BASE}/audit/${eventId}`, {
            headers: AUTH_HEADER
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const event = await response.json();

        // Create modal for details
        const modal = document.createElement('div');
        modal.className = 'event-detail-modal active';
        modal.innerHTML = `
            <div class="event-detail-content">
                <button class="event-detail-close" onclick="this.closest('.event-detail-modal').remove()">×</button>
                <div class="event-detail-header">
                    <div class="event-detail-title">${event.tool_name}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">
                        ${new Date(event.timestamp).toLocaleString()}
                    </div>
                </div>
                <div class="event-detail-body">
                    <div class="event-detail-section">
                        <div class="event-detail-label">Agent ID</div>
                        <div class="event-detail-value">${event.agent_id}</div>
                    </div>
                    <div class="event-detail-section">
                        <div class="event-detail-label">Status</div>
                        <div class="event-detail-value">
                            ${event.status === 'success' ? '✓ Success' : '✗ Failed'}
                        </div>
                    </div>
                    <div class="event-detail-section">
                        <div class="event-detail-label">Input Arguments</div>
                        <div class="event-detail-value">${event.input_args ? JSON.stringify(JSON.parse(event.input_args), null, 2) : 'None'}</div>
                    </div>
                    <div class="event-detail-section">
                        <div class="event-detail-label">Output</div>
                        <div class="event-detail-value">${event.output ? JSON.stringify(JSON.parse(event.output), null, 2) : 'None'}</div>
                    </div>
                    <div class="event-detail-section">
                        <button class="btn-primary" onclick="replayEvent(${event.id})">Replay in Simulation</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    } catch (error) {
        console.error('Failed to load event details:', error);
        alert('Failed to load event details');
    }
}

/**
 * Replay an audit event in simulation mode
 */
async function replayEvent(eventId) {
    try {
        const response = await fetch(`${API_BASE}/audit/replay/${eventId}`, {
            method: 'POST',
            headers: AUTH_HEADER,
            body: JSON.stringify({})
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();

        // Show replay result
        const modal = document.createElement('div');
        modal.className = 'event-detail-modal active';
        modal.innerHTML = `
            <div class="event-detail-content">
                <button class="event-detail-close" onclick="this.closest('.event-detail-modal').remove()">×</button>
                <div class="event-detail-header">
                    <div class="event-detail-title">Event Replayed ✓</div>
                </div>
                <div class="event-detail-body">
                    <div class="event-detail-section">
                        <div class="event-detail-label">Replayed At</div>
                        <div class="event-detail-value">${new Date(result.replayed_at).toLocaleString()}</div>
                    </div>
                    <div class="event-detail-section">
                        <div class="event-detail-label">Mode</div>
                        <div class="event-detail-value">🔄 ${result.replay_mode}</div>
                    </div>
                    <div class="event-detail-section">
                        <div class="event-detail-label">Status</div>
                        <div class="event-detail-value">${result.status}</div>
                    </div>
                    <div class="event-detail-section">
                        <div class="event-detail-label">Message</div>
                        <div class="event-detail-value">${result.message}</div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    } catch (error) {
        console.error('Failed to replay event:', error);
        alert('Failed to replay event');
    }
}

/**
 * Export audit trail
 */
async function exportAuditTrail(format) {
    try {
        const agentId = document.getElementById('replay-filter-agent')?.value;

        const params = new URLSearchParams();
        params.append('format', format);
        if (agentId) params.append('agent_id', agentId);

        const response = await fetch(`${API_BASE}/audit/export?${params}`, {
            headers: AUTH_HEADER
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        if (format === 'json') {
            const data = await response.json();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            downloadFile(blob, `audit-export-${new Date().toISOString().split('T')[0]}.json`);
        }
    } catch (error) {
        console.error('Failed to export audit trail:', error);
        alert('Failed to export audit trail');
    }
}

/**
 * Download file utility
 */
function downloadFile(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}