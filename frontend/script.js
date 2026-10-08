/* ============================================================
   AI FEEDBACK SYSTEM — Sprint 2
   Backend API + NLP analysis (US5–US8)
   ============================================================ */

const STORAGE_KEY = 'ai_feedback_data';
const MIGRATION_FLAG = 'ai_feedback_migrated_v1';

function getFeedbacks() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function sentimentBadge(sentiment) {
    const s = (sentiment || 'unknown').toLowerCase();
    const cls = s === 'positive' ? 'badge-positive' : s === 'negative' ? 'badge-negative' : 'badge-neutral';
    const label = s.charAt(0).toUpperCase() + s.slice(1);
    return `<span class="badge ${cls}">${escapeHtml(label)}</span>`;
}

function languageBadge(code, name) {
    return `<span class="badge badge-lang">${escapeHtml(name || code || 'Unknown')}</span>`;
}

function intensityBlock(item) {
    if (item.emotion_intensity == null) {
        return `<p class="intensity-na">Emotion intensity: Not applicable</p>`;
    }
    const pct = Math.min(100, Math.max(0, (item.emotion_intensity / 10) * 100));
    const sentiment = (item.sentiment || 'neutral').toLowerCase();
    const barClass =
        sentiment === 'positive' ? 'bar-positive' : sentiment === 'negative' ? 'bar-negative' : 'bar-neutral';
    return `
        <div class="intensity-card">
            <div class="intensity-head">
                <strong>Emotion Intensity: ${item.emotion_intensity}/10</strong>
                <span class="intensity-level">${escapeHtml(item.intensity_level || '')}</span>
            </div>
            <div class="progress-track"><div class="progress-fill ${barClass}" style="width:${pct}%"></div></div>
            <p class="intensity-note">Level measures emotional strength (not model accuracy).</p>
        </div>
    `;
}

function renderFeedbackCard(fb, detailed = false) {
    const dateStr = fb.created_at
        ? new Date(fb.created_at).toLocaleString('en-GB')
        : fb.date || '';
    const conf =
        fb.sentiment_confidence != null
            ? `<span class="conf">Model score: ${(fb.sentiment_confidence * 100).toFixed(1)}% (calibrated label confidence, not guaranteed accuracy)</span>`
            : '';
    return `
        <div class="feedback-item">
            <div class="meta">
                <span class="name">${escapeHtml(fb.student_name || fb.name || 'Anonymous')}</span>
                <span>${escapeHtml(dateStr)}</span>
            </div>
            <div class="badges-row">
                <span class="topic-tag">${escapeHtml(fb.topic)}</span>
                ${languageBadge(fb.detected_language, fb.language_name)}
                ${sentimentBadge(fb.sentiment)}
                ${conf}
            </div>
            <p class="text">${escapeHtml(fb.feedback_text || fb.text || '')}</p>
            ${detailed ? intensityBlock(fb) : ''}
        </div>
    `;
}

async function tryMigrateLocalStorage() {
    const legacy = getFeedbacks();
    if (!legacy.length || localStorage.getItem(MIGRATION_FLAG) === 'true') return;
    try {
        const session = await AdminAPI.session();
        if (!session?.authenticated) return;
        const result = await AdminAPI.migrate(legacy);
        if (result.imported > 0) {
            localStorage.setItem(MIGRATION_FLAG, 'true');
            console.info('Migrated localStorage feedback:', result);
        }
    } catch {
        /* migration runs after admin login */
    }
}

async function renderRecentFeedbacks() {
    const container = document.getElementById('recentFeedbacks');
    if (!container) return;
    try {
        const list = await FeedbackAPI.recent(3);
        if (!list.length) {
            container.innerHTML = '<p class="empty">No feedback yet. Be the first to submit!</p>';
            return;
        }
        container.innerHTML = list.map((fb) => renderFeedbackCard(fb, true)).join('');
    } catch (err) {
        container.innerHTML = `<p class="empty">Could not load recent feedback: ${escapeHtml(err.message)}</p>`;
    }
}

const feedbackForm = document.getElementById('feedbackForm');
if (feedbackForm) {
    feedbackForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const name = document.getElementById('studentName').value.trim();
        const topic = document.getElementById('topic').value;
        const text = document.getElementById('feedbackText').value.trim();
        const successMsg = document.getElementById('successMsg');
        const analysisBox = document.getElementById('analysisResult');
        const submitBtn = feedbackForm.querySelector('button[type="submit"]');

        if (!name || !topic || !text) {
            alert('Please fill all fields!');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Analyzing...';
        successMsg.style.display = 'none';
        if (analysisBox) analysisBox.innerHTML = '<p class="loading">Running language detection, sentiment, and intensity analysis...</p>';

        try {
            const saved = await FeedbackAPI.submit({
                student_name: name,
                topic,
                feedback_text: text,
            });

            if (analysisBox) {
                analysisBox.innerHTML = `
                    <div class="analysis-panel">
                        <h4>AI Analysis Result</h4>
                        <p>Language: ${escapeHtml(saved.language_name)} (${escapeHtml(saved.detected_language)})</p>
                        <p>Sentiment: ${sentimentBadge(saved.sentiment)} ${saved.sentiment_confidence != null ? `<span class="conf">(${(saved.sentiment_confidence * 100).toFixed(1)}% label score)</span>` : ''}</p>
                        ${intensityBlock(saved)}
                        <p class="saved-ok">✅ Saved to database (ID #${saved.id})</p>
                    </div>
                `;
            }

            successMsg.textContent = '✅ Your feedback was analyzed and saved. Thank you!';
            successMsg.style.display = 'block';
            feedbackForm.reset();
            await renderRecentFeedbacks();
        } catch (err) {
            if (analysisBox) analysisBox.innerHTML = `<p class="error-msg">${escapeHtml(err.message)}</p>`;
            successMsg.textContent = '';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = '📤 Submit Feedback';
        }
    });
}

const loginForm = document.getElementById('loginForm');
const logoutBtn = document.getElementById('logoutBtn');
const filterTopic = document.getElementById('filterTopic');
const filterSentiment = document.getElementById('filterSentiment');
const filterLanguage = document.getElementById('filterLanguage');

async function showAdminPanel() {
    document.getElementById('loginSection').classList.add('hidden');
    document.getElementById('adminPanel').classList.remove('hidden');
    await tryMigrateLocalStorage();
    await renderAdminFeedbacks();
    await updateStats();
}

if (loginForm) {
    (async () => {
        try {
            const session = await AdminAPI.session();
            if (session?.authenticated) await showAdminPanel();
        } catch {
            /* not logged in */
        }
    })();

    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const user = document.getElementById('loginUser').value.trim();
        const pass = document.getElementById('loginPass').value;
        const errEl = document.getElementById('loginError');
        errEl.textContent = '';
        try {
            await AdminAPI.login(user, pass);
            await showAdminPanel();
        } catch {
            errEl.textContent = '❌ Wrong username or password!';
        }
    });
}

if (logoutBtn) {
    logoutBtn.addEventListener('click', async function () {
        try {
            await AdminAPI.logout();
        } finally {
            window.location.href = 'admin.html';
        }
    });
}

function bindFilter(el, handler) {
    if (el) el.addEventListener('change', handler);
}

bindFilter(filterTopic, renderAdminFeedbacks);
bindFilter(filterSentiment, renderAdminFeedbacks);
bindFilter(filterLanguage, renderAdminFeedbacks);

async function renderAdminFeedbacks() {
    const container = document.getElementById('feedbackList');
    if (!container) return;
    try {
        const list = await AdminAPI.feedback({
            topic: filterTopic?.value || '',
            sentiment: filterSentiment?.value || '',
            language: filterLanguage?.value || '',
        });
        if (!list.length) {
            container.innerHTML = '<div class="card"><p class="empty">No feedback found.</p></div>';
            return;
        }
        container.innerHTML = list.map((fb) => `<div class="card">${renderFeedbackCard(fb, true)}</div>`).join('');
    } catch (err) {
        container.innerHTML = `<div class="card"><p class="empty">${escapeHtml(err.message)}</p></div>`;
    }
}

async function updateStats() {
    const totalEl = document.getElementById('totalCount');
    if (!totalEl) return;
    try {
        const stats = await AdminAPI.stats();
        totalEl.textContent = stats.total;
        document.getElementById('todayCount').textContent = stats.today;
        document.getElementById('positiveCount').textContent = stats.positive;
        document.getElementById('negativeCount').textContent = stats.negative;
        document.getElementById('neutralCount').textContent = stats.neutral;
        const avgEl = document.getElementById('avgIntensity');
        if (avgEl) {
            avgEl.textContent =
                stats.average_emotion_intensity != null ? stats.average_emotion_intensity.toFixed(1) : '—';
        }
        const topicEl = document.getElementById('topicCount');
        if (topicEl) topicEl.textContent = Object.keys(stats.by_topic || {}).length;
    } catch (err) {
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    renderRecentFeedbacks();
});
