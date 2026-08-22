function setPrompt(element) {
    document.getElementById('objectiveInput').value = element.innerText;
}

async function runAnalysis() {
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

    // UI Loading State
    btn.disabled = true;
    btnText.innerText = "Running...";
    btnSpinner.style.display = "block";
    
    reportWelcome.style.display = "none";
    reportContent.style.display = "none";

    timeline.innerHTML = `
        <div class="timeline-card">
            <div class="event-header">
                <span class="event-type">[INITIATING]</span>
            </div>
            <div class="event-text">Starting NOVAagent ReAct loop for objective...</div>
        </div>
    `;

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ objective: objective })
        });

        if (!response.ok) {
            throw new Error(`Server returned status: ${response.status}`);
        }

        const data = await response.json();
        
        // Render Iterations Badge
        document.getElementById('iterationBadge').innerText = `${data.iterations} Steps | ${data.tools_called.length} Tools`;

        // Render Trace Events
        timeline.innerHTML = "";
        data.trace_events.forEach(item => {
            const card = document.createElement('div');
            card.className = "timeline-card";

            let detailText = typeof item.detail === 'object' ? JSON.stringify(item.detail, null, 2) : item.detail;

            card.innerHTML = `
                <div class="event-header">
                    <span class="event-type">${escapeHtml(item.event)}</span>
                </div>
                <div class="event-text">${escapeHtml(detailText)}</div>
            `;
            timeline.appendChild(card);
        });

        // Render Report Dashboard
        if (data.final_report) {
            renderReport(data.final_report);
            reportContent.style.display = "flex";
            document.getElementById('reportScrollContainer').scrollTop = 0;
        }

    } catch (error) {
        console.error("Error executing agent:", error);
        timeline.innerHTML += `
            <div class="timeline-card" style="border-color: var(--accent-red);">
                <div class="event-header">
                    <span class="event-type" style="color: var(--accent-red);">[ERROR]</span>
                </div>
                <div class="event-text">Execution failed: ${escapeHtml(error.message)}</div>
            </div>
        `;
        reportWelcome.style.display = "flex";
    } finally {
        btn.disabled = false;
        btnText.innerText = "Execute Agent";
        btnSpinner.style.display = "none";
    }
}

function renderReport(report) {
    document.getElementById('execSummary').innerText = report["EXECUTIVE SUMMARY"] || "N/A";
    
    renderList('keyDevelopments', report["KEY DEVELOPMENTS"]);
    renderList('emergingTrends', report["EMERGING TRENDS"]);
    renderList('opportunities', report["OPPORTUNITIES"]);
    renderList('threats', report["THREATS AND RISKS"]);
    renderList('strategicImplications', report["STRATEGIC IMPLICATIONS"]);
    renderList('recommendedActions', report["RECOMMENDED ACTIONS"]);

    // Confidence Level
    const confBadge = document.getElementById('confidenceBadge');
    const confidenceText = report["CONFIDENCE LEVEL"] || "HIGH";
    confBadge.innerText = `CONFIDENCE: ${confidenceText}`;

    // Sources
    const sourcesContainer = document.getElementById('sourcesContainer');
    sourcesContainer.innerHTML = "";
    const sources = report["SOURCES USED"] || [];
    if (sources.length === 0) {
        sourcesContainer.innerHTML = "<p style='color: var(--text-secondary); font-size: 0.85rem;'>No external sources referenced.</p>";
    } else {
        sources.forEach(src => {
            const div = document.createElement('div');
            div.className = "source-box";
            
            const match = src.match(/(Web|Web \(Tavily\)|arXiv|CrossRef):\s*(.*?)\s*\((https?:\/\/[^\s]+)\)/);
            if (match) {
                const type = match[1];
                const title = match[2];
                const url = match[3];
                div.innerHTML = `
                    <a href="${url}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>
                    <span class="type-tag">${type}</span>
                `;
            } else {
                div.innerHTML = `<span>${escapeHtml(src)}</span>`;
            }
            sourcesContainer.appendChild(div);
        });
    }
}

function renderList(elementId, items) {
    const ul = document.getElementById(elementId);
    ul.innerHTML = "";
    if (!items || items.length === 0) {
        ul.innerHTML = "<li>No specific items recorded.</li>";
        return;
    }
    items.forEach(item => {
        const li = document.createElement('li');
        li.innerText = item;
        ul.appendChild(li);
    });
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
