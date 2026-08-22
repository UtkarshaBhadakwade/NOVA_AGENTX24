// AGENT X - Frontend Application Logic

document.addEventListener('DOMContentLoaded', () => {
    // STATE
    const state = {
        activePage: 'overview',
        maxIterations: 8,
        preferredModel: 'gemini-1.5-flash',
        savedInsights: JSON.parse(localStorage.getItem('agentx_saved_insights') || '[]'),
        activeAgentEventSource: null,
        currentAnalyzingPaper: null,
        charts: {
            trends: null
        }
    };

    // DOM ELEMENTS
    const elements = {
        // Navigation & Sidebar
        navLinks: document.querySelectorAll('.nav-link'),
        pages: document.querySelectorAll('.content-page'),
        mobileMenuToggle: document.getElementById('mobile-menu-toggle'),
        sidebarClose: document.getElementById('sidebar-close'),
        appSidebar: document.getElementById('app-sidebar'),
        
        // Greeting & Header
        greetingText: document.getElementById('greeting-text'),
        
        // Settings page
        badgeGeminiStatus: document.getElementById('badge-gemini-status'),
        badgeTavilyStatus: document.getElementById('badge-tavily-status'),
        settingModel: document.getElementById('setting-model'),
        settingIterations: document.getElementById('setting-iterations'),
        iterationsValue: document.getElementById('iterations-value'),
        btnSaveSettings: document.getElementById('btn-save-settings'),
        summaryIterations: document.getElementById('summary-iterations'),

        // Overview / Agent Run
        agentObjectiveInput: document.getElementById('agent-objective-input'),
        btnRunAgent: document.getElementById('btn-run-agent'),
        agentRunContainer: document.getElementById('agent-run-container'),
        statusPulseDot: document.getElementById('status-pulse-dot'),
        agentStatusText: document.getElementById('agent-status-text'),
        agentIterationsCount: document.getElementById('agent-iterations-count'),
        agentMaxIterationsCount: document.getElementById('agent-max-iterations-count'),
        agentActivityLog: document.getElementById('agent-activity-log'),
        activityEmptyState: document.getElementById('activity-empty-state'),
        workingBadge: document.getElementById('working-badge'),
        intelligenceReportContent: document.getElementById('intelligence-report-content'),
        btnSaveReport: document.getElementById('btn-save-report'),
        suggestionChips: document.querySelectorAll('.suggestion-chip'),

        // Research Explorer
        researchSearchInput: document.getElementById('research-search-input'),
        btnSearchPapers: document.getElementById('btn-search-papers'),
        btnToggleFilters: document.getElementById('btn-toggle-filters'),
        filtersGrid: document.getElementById('filters-grid'),
        filterYear: document.getElementById('filter-year'),
        customYearInputs: document.getElementById('custom-year-inputs'),
        customYearStart: document.getElementById('custom-year-start'),
        customYearEnd: document.getElementById('custom-year-end'),
        filterDomain: document.getElementById('filter-domain'),
        filterSort: document.getElementById('filter-sort'),
        filterType: document.getElementById('filter-type'),
        filterSource: document.getElementById('filter-source'),
        btnApplyFilters: document.getElementById('btn-apply-filters'),
        btnClearFilters: document.getElementById('btn-clear-filters'),
        resultsCountText: document.getElementById('results-count-text'),
        paperCardsGrid: document.getElementById('paper-cards-grid'),

        // Paper Analysis Side Panel
        analysisSidePanel: document.getElementById('analysis-side-panel'),
        btnCloseAnalysis: document.getElementById('btn-close-analysis'),
        analysisLoadingState: document.getElementById('analysis-loading-state'),
        analysisContentView: document.getElementById('analysis-content-view'),
        panelPaperSource: document.getElementById('panel-paper-source'),
        panelPaperTitle: document.getElementById('panel-paper-title'),
        panelPaperAuthors: document.getElementById('panel-paper-authors'),
        panelPaperYearDomain: document.getElementById('panel-paper-year-domain'),
        panelPaperAbstract: document.getElementById('panel-paper-abstract'),
        analysisProblem: document.getElementById('analysis-problem'),
        analysisMethodology: document.getElementById('analysis-methodology'),
        analysisFindings: document.getElementById('analysis-findings'),
        analysisContribution: document.getElementById('analysis-contribution'),
        analysisLimitations: document.getElementById('analysis-limitations'),
        analysisApplications: document.getElementById('analysis-applications'),
        analysisRelevance: document.getElementById('analysis-relevance'),
        analysisConfidencePercent: document.getElementById('analysis-confidence-percent'),
        analysisConfidenceBar: document.getElementById('analysis-confidence-bar'),
        analysisConfidenceJustification: document.getElementById('analysis-confidence-justification'),
        btnSaveInsight: document.getElementById('btn-save-insight'),

        // Competitor Intelligence
        ciObjectiveInput: document.getElementById('ci-objective-input'),
        btnRunCI: document.getElementById('btn-run-ci'),

        // Trends page
        trendsDomainPicker: document.getElementById('trends-domain-picker'),

        // Saved Insights page
        savedInsightsGrid: document.getElementById('saved-insights-grid'),
        savedEmptyState: document.getElementById('saved-empty-state')
    };

    // 1. ROUTING & SHELL INTERACTION
    function setupRouting() {
        elements.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const pageId = link.getAttribute('data-page');
                navigateTo(pageId);
                
                // Close sidebar on mobile
                elements.appSidebar.classList.remove('open');
            });
        });

        // Mobile Menu Toggles
        elements.mobileMenuToggle.addEventListener('click', () => {
            elements.appSidebar.classList.add('open');
        });

        elements.sidebarClose.addEventListener('click', () => {
            elements.appSidebar.classList.remove('open');
        });

        // Close side panels on document clicking outside if appropriate, for now close analysis button is enough
        elements.btnCloseAnalysis.addEventListener('click', closeAnalysisPanel);
    }

    function navigateTo(pageId) {
        state.activePage = pageId;
        
        // Update nav links
        elements.navLinks.forEach(link => {
            if (link.getAttribute('data-page') === pageId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Update sections
        elements.pages.forEach(page => {
            if (page.id === `page-${pageId}`) {
                page.classList.add('active');
            } else {
                page.classList.remove('active');
            }
        });

        // Trigger page-specific loads
        if (pageId === 'trends') {
            loadTrendsChart();
        } else if (pageId === 'saved') {
            renderSavedInsights();
        } else if (pageId === 'settings') {
            checkAPIHealth();
        }
        
        // Lucide icon replacement on page change
        lucide.createIcons();
    }

    // Initialize Greeting
    function updateGreeting() {
        const hr = new Date().getHours();
        let greeting = 'Good morning';
        if (hr >= 12 && hr < 17) {
            greeting = 'Good afternoon';
        } else if (hr >= 17) {
            greeting = 'Good evening';
        }
        if (elements.greetingText) {
            elements.greetingText.textContent = greeting;
        }
    }

    // 2. SETTINGS & HEALTH CHECKS
    async function checkAPIHealth() {
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            
            updateHealthBadge(elements.badgeGeminiStatus, data.gemini_configured);
            updateHealthBadge(elements.badgeTavilyStatus, data.tavily_configured);
        } catch (err) {
            console.error('Health check failed', err);
            updateHealthBadge(elements.badgeGeminiStatus, false, 'Failed connection');
            updateHealthBadge(elements.badgeTavilyStatus, false, 'Failed connection');
        }
    }

    function updateHealthBadge(badgeEl, isConfigured, customText) {
        if (!badgeEl) return;
        badgeEl.className = 'status-badge ' + (isConfigured ? 'active' : 'inactive');
        
        const text = customText || (isConfigured ? 'Configured' : 'Missing API Key');
        badgeEl.innerHTML = `<span class="badge-dot"></span> ${text}`;
    }

    function setupSettingsHandlers() {
        // Sync setting ranges
        if (elements.settingIterations) {
            elements.settingIterations.addEventListener('input', (e) => {
                const val = e.target.value;
                state.maxIterations = parseInt(val);
                elements.iterationsValue.textContent = val;
                elements.summaryIterations.textContent = val;
                elements.agentMaxIterationsCount.textContent = val;
            });
        }

        if (elements.btnSaveSettings) {
            elements.btnSaveSettings.addEventListener('click', () => {
                state.preferredModel = elements.settingModel.value;
                alert('Settings saved successfully!');
            });
        }
    }

    // 3. SUGGESTIONS
    elements.suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const promptText = chip.getAttribute('data-text');
            elements.agentObjectiveInput.value = promptText;
            elements.agentObjectiveInput.focus();
        });
    });

    // 4. AGENT EXECUTION (STREAMING SSE / ReAct LOOP)
    function runAgentLoop(objective) {
        if (!objective || !objective.trim()) {
            alert('Please enter an objective to analyze.');
            return;
        }

        // Cancel previous SSE if running
        if (state.activeAgentEventSource) {
            state.activeAgentEventSource.close();
        }

        // Set UI to Working state
        elements.agentRunContainer.classList.remove('hidden');
        elements.agentActivityLog.innerHTML = '';
        elements.activityEmptyState.classList.add('hidden');
        elements.workingBadge.classList.remove('hidden');
        elements.workingBadge.textContent = '● Active';
        elements.workingBadge.className = 'badge badge-accent animate-pulse';
        elements.statusPulseDot.className = 'status-pulse-dot working';
        elements.agentStatusText.textContent = 'Working';
        elements.agentIterationsCount.textContent = '0';
        elements.btnRunAgent.disabled = true;
        elements.btnSaveReport.disabled = true;
        
        // Reset intelligence brief placeholder
        elements.intelligenceReportContent.innerHTML = `
            <div class="empty-state text-center py-6">
                <i data-lucide="loader" class="empty-icon text-muted animate-spin"></i>
                <p class="empty-text">Intelligence report will appear once the agent finishes synthesis.</p>
            </div>
        `;
        lucide.createIcons();

        // Scroll to container
        elements.agentRunContainer.scrollIntoView({ behavior: 'smooth' });

        // Connect to server SSE endpoint
        const encodedObjective = encodeURIComponent(objective);
        const maxIter = state.maxIterations;
        const sseUrl = `/api/agent/run/stream?objective=${encodedObjective}&max_iterations=${maxIter}`;
        
        const eventSource = new EventSource(sseUrl);
        state.activeAgentEventSource = eventSource;

        let iterations = 0;
        let finalReport = null;

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'step') {
                    const step = data.step;
                    appendActivityLogStep(step);
                    
                    // Increment iterations count if it is a reasoning step
                    if (step.type === 'REASONING_STATUS') {
                        iterations++;
                        elements.agentIterationsCount.textContent = iterations;
                        updateAgentWorkingStatus(step.content);
                    }
                } 
                else if (data.type === 'final_report') {
                    finalReport = data.report;
                    renderIntelligenceReport(data.report, data.analysis_result);
                    
                    // Mark Complete
                    elements.statusPulseDot.className = 'status-pulse-dot complete';
                    elements.agentStatusText.textContent = 'Complete';
                    elements.workingBadge.textContent = '✓ Complete';
                    elements.workingBadge.className = 'badge badge-success';
                    elements.btnRunAgent.disabled = false;
                    elements.btnSaveReport.disabled = false;
                    eventSource.close();
                } 
                else if (data.type === 'error') {
                    appendActivityLogStep({
                        type: 'ERROR',
                        content: data.error
                    });
                    elements.statusPulseDot.className = 'status-pulse-dot error';
                    elements.agentStatusText.textContent = 'Failed';
                    elements.workingBadge.textContent = '✕ Error';
                    elements.workingBadge.className = 'badge badge-error';
                    elements.btnRunAgent.disabled = false;
                    eventSource.close();
                }
            } catch (err) {
                console.error('Error processing SSE stream message', err);
            }
        };

        eventSource.onerror = (err) => {
            console.error('SSE connection error:', err);
            appendActivityLogStep({
                type: 'ERROR',
                content: 'Server connection interrupted or API quota exceeded. Please ensure server is running.'
            });
            elements.statusPulseDot.className = 'status-pulse-dot error';
            elements.agentStatusText.textContent = 'Failed';
            elements.workingBadge.textContent = '✕ Connection Lost';
            elements.workingBadge.className = 'badge badge-error';
            elements.btnRunAgent.disabled = false;
            eventSource.close();
        };
    }

    function appendActivityLogStep(step) {
        if (!elements.agentActivityLog) return;
        
        const stepDiv = document.createElement('div');
        stepDiv.className = `activity-step ${step.type.toLowerCase()}`;
        
        let typeLabel = step.type;
        if (step.type === 'REASONING_STATUS') typeLabel = 'Reasoning';
        if (step.type === 'ACTION') typeLabel = 'Action';
        if (step.type === 'TOOL_RESULT') typeLabel = 'Observation';
        if (step.type === 'DECISION') typeLabel = 'Decision';
        if (step.type === 'TASK_COMPLETE') typeLabel = 'Task Completed';
        if (step.type === 'ERROR') typeLabel = 'System Error';
        
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        
        stepDiv.innerHTML = `
            <div class="step-meta">
                <span>${typeLabel}</span>
                <span>${timestamp}</span>
            </div>
            <div class="step-body">${step.content}</div>
        `;
        
        elements.agentActivityLog.appendChild(stepDiv);
        elements.agentActivityLog.scrollTop = elements.agentActivityLog.scrollHeight;
    }

    function updateAgentWorkingStatus(reasoningContent) {
        const content = reasoningContent.toLowerCase();
        let status = 'Working';
        
        if (content.includes('searching') || content.includes('arxiv') || content.includes('web')) {
            status = 'Researching';
        } else if (content.includes('analyzing') || content.includes('evaluation')) {
            status = 'Analyzing';
        } else if (content.includes('synthesizing') || content.includes('brief') || content.includes('final')) {
            status = 'Synthesizing';
        }
        
        elements.agentStatusText.textContent = status;
    }

    function renderIntelligenceReport(reportMarkdown, analysisResult) {
        // Parse markdown text using Marked.js CDN
        if (typeof marked !== 'undefined') {
            elements.intelligenceReportContent.innerHTML = marked.parse(reportMarkdown);
        } else {
            // Fallback rendering
            elements.intelligenceReportContent.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit;">${reportMarkdown}</pre>`;
        }
        
        // Save current analysis context on the Save Report button
        elements.btnSaveReport.onclick = () => {
            const newInsight = {
                id: 'insight_' + Date.now(),
                title: elements.agentObjectiveInput.value.slice(0, 60) + '...',
                date: new Date().toLocaleDateString(),
                domain: 'Intelligence Brief',
                summary: 'Structured synthesis report covering strategic developments, opportunities, threats and recommendations.',
                source: 'Agent X autonomous synthesis',
                content: reportMarkdown
            };
            saveInsight(newInsight);
        };
    }

    // Overview Button Handler
    elements.btnRunAgent.addEventListener('click', () => {
        const objective = elements.agentObjectiveInput.value;
        runAgentLoop(objective);
    });

    // Competitor Page Run Handler
    elements.btnRunCI.addEventListener('click', () => {
        const competitorObjective = elements.ciObjectiveInput.value;
        navigateTo('overview');
        elements.agentObjectiveInput.value = competitorObjective;
        runAgentLoop(competitorObjective);
    });

    // 5. RESEARCH EXPLORER
    function setupExplorerHandlers() {
        // Toggle filters grid
        elements.btnToggleFilters.addEventListener('click', () => {
            const collapsed = elements.filtersGrid.classList.contains('collapsed');
            if (collapsed) {
                elements.filtersGrid.classList.remove('collapsed');
                elements.filtersGrid.classList.add('expanded');
            } else {
                elements.filtersGrid.classList.remove('expanded');
                elements.filtersGrid.classList.add('collapsed');
            }
        });

        // Toggle custom year input visibility
        elements.filterYear.addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                elements.customYearInputs.classList.remove('hidden');
            } else {
                elements.customYearInputs.classList.add('hidden');
            }
        });

        // Clear filters
        elements.btnClearFilters.addEventListener('click', () => {
            elements.researchSearchInput.value = '';
            elements.filterYear.value = 'any';
            elements.customYearInputs.classList.add('hidden');
            elements.filterDomain.value = 'all';
            elements.filterSort.value = 'relevance';
            elements.filterType.value = 'all';
            elements.filterSource.value = 'all';
            searchResearchPapers();
        });

        // Search Handlers
        elements.btnSearchPapers.addEventListener('click', searchResearchPapers);
        elements.btnApplyFilters.addEventListener('click', searchResearchPapers);
        elements.researchSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchResearchPapers();
            }
        });
    }

    async function searchResearchPapers() {
        const query = elements.researchSearchInput.value;
        if (!query || !query.trim()) {
            alert('Please enter a search query (e.g., "AI cancer detection").');
            return;
        }

        // Calculate years
        let startYear = null;
        let endYear = null;
        const yearVal = elements.filterYear.value;
        
        if (yearVal === 'custom') {
            startYear = parseInt(elements.customYearStart.value) || 2010;
            endYear = parseInt(elements.customYearEnd.value) || 2026;
        } else if (yearVal !== 'any') {
            startYear = parseInt(yearVal);
            endYear = parseInt(yearVal);
        }

        // Show loading state
        elements.resultsCountText.textContent = 'Searching arXiv database...';
        elements.paperCardsGrid.innerHTML = `
            <div class="empty-state text-center py-8">
                <div class="spinner mb-4"></div>
                <p class="empty-text">Searching arXiv for papers matching your filters...</p>
            </div>
        `;

        try {
            const payload = {
                query: query,
                start_year: startYear,
                end_year: endYear,
                domain: elements.filterDomain.value === 'all' ? null : elements.filterDomain.value,
                sort_by: elements.filterSort.value,
                paper_type: elements.filterType.value === 'all' ? null : elements.filterType.value,
                source: elements.filterSource.value === 'all' ? null : elements.filterSource.value
            };

            const response = await fetch('/api/research/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error('Search failed on server.');
            }

            const papers = await response.json();
            renderPapers(papers);
        } catch (err) {
            console.error('Research search failed:', err);
            elements.resultsCountText.textContent = 'Error occurred';
            elements.paperCardsGrid.innerHTML = `
                <div class="empty-state text-center py-8">
                    <i data-lucide="alert-circle" class="empty-icon text-muted" style="color: var(--status-error)"></i>
                    <p class="empty-text">Unable to retrieve research papers.</p>
                    <p class="text-sm text-muted mt-2">Check API status in Settings or try a simpler query.</p>
                    <button class="btn btn-secondary btn-sm mt-4" onclick="location.reload()">Retry</button>
                </div>
            `;
            lucide.createIcons();
        }
    }

    function renderPapers(papers) {
        if (!papers || papers.length === 0) {
            elements.resultsCountText.textContent = '0 papers found';
            elements.paperCardsGrid.innerHTML = `
                <div class="empty-state text-center py-8">
                    <i data-lucide="frown" class="empty-icon text-muted"></i>
                    <p class="empty-text">No research papers found.</p>
                    <p class="text-sm text-muted">Try broadening your search or changing the year range.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        elements.resultsCountText.textContent = `${papers.length} papers found`;
        elements.paperCardsGrid.innerHTML = '';

        papers.forEach(paper => {
            const card = document.createElement('div');
            card.className = 'paper-card';
            
            // Format authors list
            const authorStr = paper.authors.join(', ');
            // Year from published date
            const year = paper.published.split('-')[0];
            const domainText = paper.domain || elements.filterDomain.value !== 'all' ? elements.filterDomain.value : 'Artificial Intelligence';
            
            card.innerHTML = `
                <span class="source-badge-mini">${paper.source.replace(' Research Search', '')}</span>
                <div class="paper-card-meta">${year} · ${domainText}</div>
                <h3 class="paper-card-title">${paper.title}</h3>
                <div class="paper-card-authors">Authors: ${authorStr}</div>
                <p class="paper-card-abstract">${paper.content}</p>
                <div class="paper-card-footer">
                    <span class="relevance-score">Relevance: ${paper.relevance}%</span>
                    <div class="paper-card-actions">
                        <a href="${paper.url}" target="_blank" class="btn btn-secondary btn-sm"><i data-lucide="external-link"></i> View Paper</a>
                        <button class="btn btn-primary btn-sm btn-analyze-paper" data-id="${paper.url}"><i data-lucide="sparkles"></i> Analyze</button>
                    </div>
                </div>
            `;
            
            // Store paper object inside dataset for side panel retrieval
            card.dataset.paper = JSON.stringify(paper);
            elements.paperCardsGrid.appendChild(card);
        });

        // Bind analysis click events
        document.querySelectorAll('.btn-analyze-paper').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const cardEl = btn.closest('.paper-card');
                const paperObj = JSON.parse(cardEl.dataset.paper);
                openAnalysisPanel(paperObj);
            });
        });

        lucide.createIcons();
    }

    // 6. PAPER ANALYSIS SIDE PANEL
    function openAnalysisPanel(paper) {
        state.currentAnalyzingPaper = paper;
        elements.analysisSidePanel.classList.add('open');
        elements.analysisLoadingState.classList.remove('hidden');
        elements.analysisContentView.classList.add('hidden');
        elements.btnSaveInsight.disabled = true;

        // Fetch AI analysis
        fetchPaperAnalysis(paper);
    }

    function closeAnalysisPanel() {
        elements.analysisSidePanel.classList.remove('open');
        state.currentAnalyzingPaper = null;
    }

    async function fetchPaperAnalysis(paper) {
        try {
            const payload = {
                title: paper.title,
                authors: paper.authors,
                published: paper.published,
                source: paper.source,
                abstract: paper.content
            };

            const response = await fetch('/api/research/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error('Analysis request failed.');
            }

            const analysis = await response.json();
            renderPaperAnalysis(analysis, paper);
        } catch (err) {
            console.error('Failed to analyze paper:', err);
            elements.analysisLoadingState.innerHTML = `
                <i data-lucide="alert-octagon" class="empty-icon" style="color: var(--status-error)"></i>
                <p class="status-text font-medium text-charcoal mt-2">Analysis failed</p>
                <p class="text-xs text-muted mt-1">The intelligence agent could not complete this analysis.</p>
                <button class="btn btn-secondary btn-sm mt-4" id="btn-retry-analysis">Try Again</button>
            `;
            lucide.createIcons();
            
            document.getElementById('btn-retry-analysis').onclick = () => {
                elements.analysisLoadingState.innerHTML = `
                    <div class="spinner mb-4"></div>
                    <p class="status-text font-medium text-charcoal">Analyzing research paper...</p>
                `;
                fetchPaperAnalysis(paper);
            };
        }
    }

    function renderPaperAnalysis(analysis, paper) {
        elements.analysisLoadingState.classList.add('hidden');
        elements.analysisContentView.classList.remove('hidden');
        
        elements.panelPaperTitle.textContent = paper.title;
        elements.panelPaperAuthors.textContent = paper.authors.join(', ');
        
        const year = paper.published.split('-')[0];
        const domain = paper.domain || 'Research Domain';
        elements.panelPaperYearDomain.textContent = `${year} · ${domain}`;
        elements.panelPaperAbstract.textContent = paper.content;

        // Structured AI text mappings
        elements.analysisProblem.textContent = analysis.problem;
        elements.analysisMethodology.textContent = analysis.methodology;
        elements.analysisFindings.textContent = analysis.key_findings;
        elements.analysisContribution.textContent = analysis.main_contribution;
        elements.analysisLimitations.textContent = analysis.limitations;
        elements.analysisApplications.textContent = analysis.real_world_applications;
        elements.analysisRelevance.textContent = analysis.competitive_relevance;
        
        // Confidence
        const confidenceVal = analysis.confidence || 90;
        elements.analysisConfidencePercent.textContent = `${confidenceVal}%`;
        elements.analysisConfidenceBar.style.width = `${confidenceVal}%`;
        elements.analysisConfidenceJustification.textContent = analysis.confidence_justification;

        // Save Insight Button Setup
        elements.btnSaveInsight.disabled = false;
        elements.btnSaveInsight.onclick = () => {
            const newInsight = {
                id: 'insight_' + Date.now(),
                title: paper.title,
                date: new Date().toLocaleDateString(),
                domain: domain,
                summary: analysis.competitive_relevance,
                source: paper.source,
                content: `### Problem Addressed\n${analysis.problem}\n\n### Findings\n${analysis.key_findings}`
            };
            saveInsight(newInsight);
        };
        
        lucide.createIcons();
    }

    // 7. TRENDS VISUALIZATION (ECHARTS)
    async function loadTrendsChart() {
        const domain = elements.trendsDomainPicker.value;
        
        if (state.charts.trends) {
            state.charts.trends.showLoading({
                text: 'Loading live trends...',
                color: '#3D4C41'
            });
        } else {
            // Setup ECharts Instance
            const chartDom = document.getElementById('trends-chart');
            state.charts.trends = echarts.init(chartDom);
            state.charts.trends.showLoading({ text: 'Loading live trends...' });
        }

        try {
            const res = await fetch(`/api/research/trends?domain=${encodeURIComponent(domain)}`);
            const data = await res.json();
            
            const years = data.data.map(item => item.year);
            const counts = data.data.map(item => item.count);

            const option = {
                backgroundColor: '#FFFFFF',
                color: ['#3D4C41'],
                tooltip: {
                    trigger: 'axis',
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    borderColor: '#DDD8CF',
                    textStyle: { color: '#242424' }
                },
                grid: {
                    left: '4%',
                    right: '4%',
                    bottom: '8%',
                    top: '12%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: years,
                    axisLine: { lineStyle: { color: '#6B6862' } },
                    axisTick: { show: false }
                },
                yAxis: {
                    type: 'value',
                    name: 'Papers Volume',
                    nameTextStyle: { color: '#6B6862', fontSize: 11 },
                    splitLine: { lineStyle: { color: '#EFEBE3' } },
                    axisLine: { show: false }
                },
                series: [
                    {
                        name: 'Paper Submissions',
                        type: 'line',
                        smooth: true,
                        symbolSize: 8,
                        data: counts,
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: 'rgba(61, 76, 65, 0.4)' },
                                { offset: 1, color: 'rgba(247, 245, 240, 0.1)' }
                            ])
                        },
                        lineStyle: { width: 3 }
                    }
                ]
            };

            state.charts.trends.hideLoading();
            state.charts.trends.setOption(option);
        } catch (err) {
            console.error('Trends charts loading failed:', err);
            state.charts.trends.hideLoading();
            // Render error state on chart
            state.charts.trends.setOption({
                title: {
                    text: 'Trends Service Unavailable',
                    left: 'center',
                    top: 'center',
                    textStyle: { color: '#A63A2B', fontSize: 14 }
                }
            });
        }
    }

    if (elements.trendsDomainPicker) {
        elements.trendsDomainPicker.addEventListener('change', loadTrendsChart);
    }

    // Chart responsiveness
    window.addEventListener('resize', () => {
        if (state.charts.trends) {
            state.charts.trends.resize();
        }
    });

    // 8. SAVED INSIGHTS (LOCAL STORAGE PERSISTENCE)
    function saveInsight(insight) {
        // Prevent duplicate saves
        if (state.savedInsights.some(ins => ins.title === insight.title)) {
            alert('This insight is already saved.');
            return;
        }
        
        state.savedInsights.push(insight);
        localStorage.setItem('agentx_saved_insights', JSON.stringify(state.savedInsights));
        alert('Insight pinned to Saved Insights.');
    }

    function renderSavedInsights() {
        if (!elements.savedInsightsGrid) return;

        if (state.savedInsights.length === 0) {
            elements.savedEmptyState.classList.remove('hidden');
            elements.savedInsightsGrid.innerHTML = '';
            elements.savedInsightsGrid.appendChild(elements.savedEmptyState);
            return;
        }

        elements.savedEmptyState.classList.add('hidden');
        elements.savedInsightsGrid.innerHTML = '';

        state.savedInsights.forEach(insight => {
            const card = document.createElement('div');
            card.className = 'saved-insight-card';
            
            card.innerHTML = `
                <div>
                    <div class="saved-insight-meta">
                        <span>${insight.domain}</span>
                        <span>Saved: ${insight.date}</span>
                    </div>
                    <h3 class="saved-insight-title">${insight.title}</h3>
                    <p class="saved-insight-summary">${insight.summary}</p>
                </div>
                <div class="saved-insight-actions">
                    <span class="text-xs text-muted">Source: ${insight.source.replace(' Research Search', '')}</span>
                    <button class="btn btn-secondary btn-sm btn-remove-insight" data-id="${insight.id}">
                        <i data-lucide="trash-2"></i> Remove
                    </button>
                </div>
            `;
            elements.savedInsightsGrid.appendChild(card);
        });

        // Bind removal buttons
        document.querySelectorAll('.btn-remove-insight').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = btn.getAttribute('data-id');
                removeInsight(id);
            });
        });

        lucide.createIcons();
    }

    function removeInsight(id) {
        state.savedInsights = state.savedInsights.filter(ins => ins.id !== id);
        localStorage.setItem('agentx_saved_insights', JSON.stringify(state.savedInsights));
        renderSavedInsights();
    }

    // INITIALIZATION
    function init() {
        setupRouting();
        updateGreeting();
        setupSettingsHandlers();
        setupExplorerHandlers();
        
        // Load settings values to fields
        if (elements.settingIterations) {
            elements.settingIterations.value = state.maxIterations;
            elements.iterationsValue.textContent = state.maxIterations;
            elements.summaryIterations.textContent = state.maxIterations;
            elements.agentMaxIterationsCount.textContent = state.maxIterations;
        }
        
        // Initial icon load
        lucide.createIcons();
    }

    init();
});
