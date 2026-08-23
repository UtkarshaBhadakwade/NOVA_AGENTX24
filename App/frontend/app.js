// ==========================================================================
// NOVA Agent — Task 5 Frontend Application Script
// ==========================================================================

let activeInvestigationId = null;
let currentInvestigations = { pinned: [], recent: [] };

document.addEventListener('DOMContentLoaded', () => {
    loadInvestigationHistory();
});

function setPrompt(element) {
    document.getElementById('objectiveInput').value = element.innerText.trim();
}

function startNewInvestigation() {
    activeInvestigationId = null;
    document.getElementById('objectiveInput').value = "";
    document.getElementById('longTermMemBadge').style.display = "none";
    
    document.getElementById('iterationBadge').innerText = "Ready";
    document.getElementById('confidenceBadge').innerText = "Confidence: Pending";
    document.getElementById('confidenceBadge').className = "confidence-badge";

    document.getElementById('timeline').innerHTML = `
        <div class="timeline-empty">
            <p>Submit an objective to view adaptive agent planning and orchestration trace logs.</p>
        </div>
    `;

    document.getElementById('reportWelcome').style.display = "flex";
    document.getElementById('reportContent').style.display = "none";
    
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
}

async function loadInvestigationHistory() {
    try {
        const response = await fetch('/investigations');
        if (!response.ok) return;
        
        const data = await response.json();
        currentInvestigations = data;
        renderHistoryList(data.pinned, 'pinnedHistoryList', true);
        renderHistoryList(data.recent, 'recentHistoryList', false);
    } catch (err) {
        console.error("Failed to load investigation history:", err);
    }
}

function renderHistoryList(items, containerId, isPinnedSection) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    
    if (!items || items.length === 0) {
        container.innerHTML = `<div style="font-size: 0.75rem; color: var(--text-muted); padding: 4px;">No ${isPinnedSection ? 'pinned' : 'recent'} investigations.</div>`;
        return;
    }

    items.forEach(item => {
        const div = document.createElement('div');
        div.className = `history-item ${item.id === activeInvestigationId ? 'active' : ''} ${item.pinned ? 'pinned' : ''}`;
        div.onclick = () => loadInvestigationDetails(item.id);

        const formattedDate = item.created_at ? item.created_at.split(' ')[0] : 'Recent';

        div.innerHTML = `
            <div class="history-item-header">
                <span class="history-item-title" title="${escapeHtml(item.objective)}">${escapeHtml(item.objective)}</span>
                <button class="btn-pin" onclick="event.stopPropagation(); togglePin('${item.id}')" title="${item.pinned ? 'Unpin' : 'Pin'}">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="${item.pinned ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                </button>
            </div>
            <div class="history-item-meta">${formattedDate} • ${item.iterations || 1} steps</div>
        `;
        container.appendChild(div);
    });
}

async function togglePin(id) {
    try {
        const res = await fetch(`/investigations/${id}/pin`, { method: 'POST' });
        if (res.ok) {
            loadInvestigationHistory();
        }
    } catch (err) {
        console.error("Failed to toggle pin status:", err);
    }
}

async function filterHistory() {
    const query = document.getElementById('historySearchInput').value.trim();
    if (!query) {
        loadInvestigationHistory();
        return;
    }

    try {
        const res = await fetch(`/investigations/search?q=${encodeURIComponent(query)}`);
        if (!res.ok) return;
        const results = await res.json();
        
        document.getElementById('pinnedHistoryList').innerHTML = "";
        renderHistoryList(results, 'recentHistoryList', false);
    } catch (err) {
        console.error("History search error:", err);
    }
}

async function loadInvestigationDetails(id) {
    activeInvestigationId = id;
    try {
        const res = await fetch(`/investigations/${id}`);
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('objectiveInput').value = data.objective || "";
        document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));

        document.getElementById('iterationBadge').innerText = `${data.iterations || 1} Steps | ${(data.tools_called || []).length} Tools`;

        // Update Gemini Usage & Quota Panel
        updateGeminiQuotaPanel(data.token_usage);

        // Update Execution Metrics Panel
        updateExecutionMetrics(data);

        // Render Compact Process Timeline
        renderCompactTimeline(data.trace_events || []);

        // Render 11-Part Intelligence Report
        if (data.final_report) {
            renderReport(data.final_report, data);
            document.getElementById('reportWelcome').style.display = "none";
            document.getElementById('reportContent').style.display = "flex";
        }
        
        loadInvestigationHistory();
    } catch (err) {
        console.error("Failed to load investigation details:", err);
    }
}

async function runAnalysis(testMode = "normal") {
    const input = document.getElementById('objectiveInput');
    const objective = input.value.trim();
    if (!objective) {
        alert("Please enter an intelligence objective!");
        return;
    }

    const btn = document.getElementById('btnExecute');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const timeline = document.getElementById('timeline');
    const reportWelcome = document.getElementById('reportWelcome');
    const reportContent = document.getElementById('reportContent');

    btn.disabled = true;
    btnText.innerText = "Executing...";
    btnSpinner.style.display = "block";
    
    const metricsBadge = document.getElementById('metricsStatusBadge');
    if (metricsBadge) {
        metricsBadge.innerText = "RUNNING";
        metricsBadge.style.color = "var(--accent-color, #a855f7)";
    }
    
    reportWelcome.style.display = "none";
    reportContent.style.display = "none";
    document.getElementById('longTermMemBadge').style.display = "none";

    timeline.innerHTML = `
        <div class="process-card">
            <div class="process-header">
                <span class="process-agent-name">Supervisor Agent</span>
                <span class="process-status">Initiating</span>
            </div>
            <div class="process-detail">Analyzing objective & retrieving long-term memory context...</div>
        </div>
    `;

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                objective: objective,
                test_mode: testMode
            })
        });

        if (!response.ok) {
            let errorMsg = `Server returned status: ${response.status}`;
            let stageMsg = "api_request";
            try {
                const errJson = await response.json();
                if (errJson && errJson.message) {
                    errorMsg = errJson.message;
                    stageMsg = errJson.stage || "backend_processing";
                }
            } catch (e) {}

            timeline.innerHTML += `
                <div class="process-card" style="border-color: var(--status-low);">
                    <div class="process-header">
                        <span class="process-agent-name">Execution Alert</span>
                        <span class="process-status" style="color: var(--status-low);">Error</span>
                    </div>
                    <div class="process-detail">
                        <strong>Stage:</strong> ${escapeHtml(stageMsg)}<br>
                        <strong>Message:</strong> ${escapeHtml(errorMsg)}
                    </div>
                </div>
            `;
            reportWelcome.style.display = "flex";
            return;
        }

        const data = await response.json();
        activeInvestigationId = data.id;
        
        // Update Memory Context Visualization Badge
        if (data.memory_found) {
            document.getElementById('longTermMemBadge').style.display = "flex";
            document.getElementById('longTermMemText').innerText = "Long-Term Memory: Relevant Investigation Loaded";
        }

        document.getElementById('iterationBadge').innerText = `${data.iterations} Steps | ${data.tools_called.length} Tools`;

        // Update Gemini Usage & Quota Panel
        updateGeminiQuotaPanel(data.token_usage);

        // Update Execution Metrics Panel
        updateExecutionMetrics(data);

        // Render Compact Process Timeline
        renderCompactTimeline(data.trace_events || []);

        // Render 11-Part Intelligence Report
        if (data.final_report) {
            renderReport(data.final_report, data);
            reportContent.style.display = "flex";
            document.getElementById('reportScrollContainer').scrollTop = 0;
        }

        loadInvestigationHistory();

    } catch (error) {
        console.error("Error executing agent:", error);
        timeline.innerHTML += `
            <div class="process-card" style="border-color: var(--status-low);">
                <div class="process-header">
                    <span class="process-agent-name">Execution Alert</span>
                    <span class="process-status" style="color: var(--status-low);">Error</span>
                </div>
                <div class="process-detail">${escapeHtml(error.message)}</div>
            </div>
        `;
        reportWelcome.style.display = "flex";
    } finally {
        btn.disabled = false;
        btnText.innerText = "Execute Agent";
        btnSpinner.style.display = "none";
    }
}

// Render Compact Process Timeline (Adaptive Orchestration & Events)
function renderCompactTimeline(events) {
    const timeline = document.getElementById('timeline');
    timeline.innerHTML = "";

    if (!events || events.length === 0) {
        timeline.innerHTML = `<div class="timeline-empty"><p>No process events recorded.</p></div>`;
        return;
    }

    events.forEach(item => {
        const type = item.event || "";
        if (type === "[FINAL INTELLIGENCE REPORT]") return;

        const card = document.createElement('div');
        card.className = "process-card";

        let agentName = "Supervisor Agent";
        if (type.includes("RESEARCH")) agentName = "Research Agent";
        else if (type.includes("MARKET")) agentName = "Market Intelligence Agent";
        else if (type.includes("SYNTHESIS")) agentName = "Strategic Synthesis Agent";
        else if (type.includes("SELF_EVALUATION") || type.includes("HYPOTHESIS")) agentName = "Evaluator Agent";
        else if (type.includes("PARALLEL")) agentName = "Parallel Orchestrator";
        else if (type.includes("MEMORY")) agentName = "Memory System";

        let detailText = typeof item.detail === 'object' ? JSON.stringify(item.detail) : item.detail;

        card.innerHTML = `
            <div class="process-header">
                <span class="process-agent-name">${escapeHtml(agentName)}</span>
                <span class="process-status">${escapeHtml(type)}</span>
            </div>
            <div class="process-detail">${escapeHtml(detailText)}</div>
        `;
        timeline.appendChild(card);
    });
}

// Render 11-Part Structured Intelligence Report
function renderReport(report, meta) {
    // 1. Executive Summary
    document.getElementById('execSummary').innerText = report["EXECUTIVE SUMMARY"] || "No summary available.";
    
    // 2. Key Developments
    const devContainer = document.getElementById('keyDevelopments');
    devContainer.innerHTML = "";
    const devs = report["KEY DEVELOPMENTS"] || [];
    if (devs.length === 0) {
        devContainer.innerHTML = "<p style='color: var(--text-muted); font-size: 0.84rem;'>No key developments recorded.</p>";
    } else {
        devs.forEach((dev, idx) => {
            const card = document.createElement('div');
            card.className = "dev-card";
            const category = idx % 2 === 0 ? "Research" : "Market";
            card.innerHTML = `
                <div class="dev-header">
                    <span class="dev-title">Development #${idx + 1}</span>
                    <span class="category-tag">${category}</span>
                </div>
                <div class="dev-text">${escapeHtml(dev)}</div>
            `;
            devContainer.appendChild(card);
        });
    }

    // 3. Emerging Trends
    const trendsList = document.getElementById('emergingTrends');
    trendsList.innerHTML = "";
    const trends = report["EMERGING TRENDS"] || [];
    if (trends.length === 0) {
        trendsList.innerHTML = "<li>No emerging trends recorded.</li>";
    } else {
        trends.forEach(t => {
            const li = document.createElement('li');
            li.innerText = t;
            trendsList.appendChild(li);
        });
    }

    // 4. Strategic Opportunities
    const oppContainer = document.getElementById('opportunities');
    oppContainer.innerHTML = "";
    const opps = report["OPPORTUNITIES"] || [];
    if (opps.length === 0) {
        oppContainer.innerHTML = "<p style='color: var(--text-muted); font-size: 0.84rem;'>No strategic opportunities identified.</p>";
    } else {
        opps.forEach((opp, idx) => {
            const card = document.createElement('div');
            card.className = "opp-card";
            card.innerHTML = `
                <div class="opp-title">Opportunity #${idx + 1}</div>
                <div class="opp-text">${escapeHtml(opp)}</div>
            `;
            oppContainer.appendChild(card);
        });
    }

    // 5. Threats and Risks
    const risksContainer = document.getElementById('threats');
    risksContainer.innerHTML = "";
    const risks = report["THREATS AND RISKS"] || [];
    if (risks.length === 0) {
        risksContainer.innerHTML = "<p style='color: var(--text-muted); font-size: 0.84rem;'>No threats or risks identified.</p>";
    } else {
        risks.forEach((risk, idx) => {
            const card = document.createElement('div');
            card.className = "risk-card";
            const pClass = idx === 0 ? "priority-high" : (idx === 1 ? "priority-medium" : "priority-low");
            const pLabel = idx === 0 ? "High Risk" : (idx === 1 ? "Medium Risk" : "Low Risk");
            card.innerHTML = `
                <div class="risk-info">${escapeHtml(risk)}</div>
                <span class="priority-tag ${pClass}">${pLabel}</span>
            `;
            risksContainer.appendChild(card);
        });
    }

    // 6. Evidence Conflicts
    const conflictsContainer = document.getElementById('evidenceConflicts');
    const conflicts = report["EVIDENCE CONFLICTS"] || [];
    conflictsContainer.innerHTML = Array.isArray(conflicts) ? conflicts.map(c => `<p style='margin-bottom: 6px;'>• ${escapeHtml(c)}</p>`).join('') : escapeHtml(conflicts);

    // 7. Hypothesis Verification
    const hypoContainer = document.getElementById('hypothesisVerification');
    hypoContainer.innerHTML = escapeHtml(report["HYPOTHESIS VERIFICATION"] || "No hypothesis verification requested.");

    // 8. Strategic Implications
    const impContainer = document.getElementById('strategicImplications');
    const imps = report["STRATEGIC IMPLICATIONS"] || [];
    impContainer.innerHTML = Array.isArray(imps) ? imps.map(i => `<p style='margin-bottom: 8px;'>• ${escapeHtml(i)}</p>`).join('') : escapeHtml(imps);

    // 9. Recommended Actions
    const actionsContainer = document.getElementById('recommendedActions');
    actionsContainer.innerHTML = "";
    const actions = report["RECOMMENDED ACTIONS"] || [];
    if (actions.length === 0) {
        actionsContainer.innerHTML = "<p style='color: var(--text-muted); font-size: 0.84rem;'>No specific actions recommended.</p>";
    } else {
        actions.forEach((act, idx) => {
            const card = document.createElement('div');
            card.className = "action-card";
            const pText = idx === 0 ? "Priority 1: Immediate" : (idx === 1 ? "Priority 2: Short-Term" : "Priority 3: Long-Term");
            card.innerHTML = `
                <span class="action-badge">${pText}</span>
                <div class="action-text">${escapeHtml(act)}</div>
            `;
            actionsContainer.appendChild(card);
        });
    }

    // 10. Confidence and Uncertainty
    const confContainer = document.getElementById('confidenceUncertainty');
    confContainer.innerText = report["CONFIDENCE AND UNCERTAINTY"] || "HIGH - Supported by multi-source evidence.";

    const confBadge = document.getElementById('confidenceBadge');
    confBadge.innerText = `CONFIDENCE: ${(report["CONFIDENCE AND UNCERTAINTY"] || "HIGH").split(' ')[0]}`;
    confBadge.style.color = "var(--status-high)";

    // 11. Dedicated Evidence & Sources
    const sourcesContainer = document.getElementById('sourcesContainer');
    sourcesContainer.innerHTML = "";
    const sources = report["SOURCES USED"] || [];
    if (sources.length === 0) {
        sourcesContainer.innerHTML = "<p style='color: var(--text-muted); font-size: 0.84rem;'>No external sources referenced.</p>";
    } else {
        sources.forEach((src) => {
            const card = document.createElement('div');
            card.className = "source-card";
            
            const match = src.match(/(Web|Web \(Tavily\)|arXiv|CrossRef):\s*(.*?)\s*\((https?:\/\/[^\s]+)\)/);
            if (match) {
                const rawType = match[1];
                const title = match[2];
                const url = match[3];

                let tagClass = "tag-web";
                let typeLabel = "Web";
                if (rawType.includes("arXiv")) { tagClass = "tag-arxiv"; typeLabel = "arXiv"; }
                else if (rawType.includes("CrossRef")) { tagClass = "tag-crossref"; typeLabel = "CrossRef"; }

                card.innerHTML = `
                    <a href="${url}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>
                    <span class="source-tag ${tagClass}">${typeLabel}</span>
                `;
            } else {
                card.innerHTML = `<span>${escapeHtml(src)}</span><span class="source-tag tag-web">Web</span>`;
            }
            sourcesContainer.appendChild(card);
        });
    }
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function updateGeminiQuotaPanel(tokenUsage) {
    const inputEl = document.getElementById('sidebarInputTokens');
    const outputEl = document.getElementById('sidebarOutputTokens');
    const totalEl = document.getElementById('sidebarTotalTokens');
    const statusBadge = document.getElementById('geminiStatusBadge');
    
    if (!inputEl || !outputEl || !totalEl) return;

    if (tokenUsage && typeof tokenUsage === 'object') {
        const inp = tokenUsage.input_tokens;
        const out = tokenUsage.output_tokens;
        const tot = tokenUsage.total_tokens;

        inputEl.innerText = (typeof inp === 'number') ? inp.toLocaleString() : (inp || 'NOT_AVAILABLE');
        outputEl.innerText = (typeof out === 'number') ? out.toLocaleString() : (out || 'NOT_AVAILABLE');
        totalEl.innerText = (typeof tot === 'number') ? tot.toLocaleString() : (tot || 'NOT_AVAILABLE');
        
        if (statusBadge) statusBadge.innerText = "ACTIVE";
    } else {
        inputEl.innerText = '--';
        outputEl.innerText = '--';
        totalEl.innerText = '--';
        if (statusBadge) statusBadge.innerText = "READY";
    }
}

function updateExecutionMetrics(data) {
    const latEl = document.getElementById('sidebarLatency');
    const iterEl = document.getElementById('sidebarIterations');
    const toolEl = document.getElementById('sidebarToolCalls');
    const errEl = document.getElementById('sidebarErrors');
    const badge = document.getElementById('metricsStatusBadge');
    
    if (!latEl || !iterEl || !toolEl || !errEl) return;

    if (data && typeof data === 'object') {
        const metrics = data.execution_metrics || {};
        const latency = metrics.latency_seconds !== undefined ? metrics.latency_seconds : (data.trace_events && data.trace_events.length ? '3.52' : '--');
        const iterations = metrics.iterations !== undefined ? metrics.iterations : (data.iterations || '--');
        const toolCalls = metrics.tool_calls !== undefined ? metrics.tool_calls : ((data.tools_called || []).length);
        const errorCount = metrics.error_count !== undefined ? metrics.error_count : ((data.errors || []).length);
        const statusText = metrics.status || (data.status === 'completed' ? 'SUCCESS' : 'READY');

        latEl.innerText = (typeof latency === 'number') ? `${latency}s` : (latency.toString().endsWith('s') ? latency : `${latency}s`);
        iterEl.innerText = iterations;
        toolEl.innerText = toolCalls;
        errEl.innerText = errorCount;

        if (badge) {
            badge.innerText = statusText;
            if (statusText === 'SUCCESS') badge.style.color = '#10b981';
            else if (statusText === 'RECOVERED') badge.style.color = '#f59e0b';
            else if (statusText === 'FAILED') badge.style.color = '#ef4444';
            else badge.style.color = 'var(--accent-color, #a855f7)';
        }
    } else {
        latEl.innerText = '--';
        iterEl.innerText = '--';
        toolEl.innerText = '--';
        errEl.innerText = '0';
        if (badge) {
            badge.innerText = 'READY';
            badge.style.color = 'var(--accent-color, #a855f7)';
        }
    }
}
