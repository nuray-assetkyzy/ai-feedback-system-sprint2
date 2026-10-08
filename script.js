/* ============================================================
   AI FEEDBACK SYSTEM — Sprint 1
   Features:
   1. Feedback Submission Form
   2. Save Feedback to Database (LocalStorage)
   3. Select Feedback Topic
   4. Admin Login Panel
   ============================================================ */

// ================== DATABASE (LocalStorage) ==================
const STORAGE_KEY = 'ai_feedback_data';
const ADMIN_USER = 'admin';
const ADMIN_PASS = '1234';

function getFeedbacks() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
}

function saveFeedbacks(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

function addFeedback(feedback) {
    const list = getFeedbacks();
    list.unshift(feedback);
    saveFeedbacks(list);
}

// ================== SECURITY ==================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ================== 1. FEEDBACK FORM ==================
const feedbackForm = document.getElementById('feedbackForm');

if (feedbackForm) {
    feedbackForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const name = document.getElementById('studentName').value.trim();
        const topic = document.getElementById('topic').value;
        const text = document.getElementById('feedbackText').value.trim();

        if (!name || !topic || !text) {
            alert('Please fill all fields!');
            return;
        }

        const feedback = {
            id: Date.now(),
            name: name,
            topic: topic,
            text: text,
            date: new Date().toLocaleString('en-GB')
        };

        addFeedback(feedback);

        const successMsg = document.getElementById('successMsg');
        successMsg.textContent = '✅ Your feedback has been saved! Thank you!';
        successMsg.style.display = 'block';

        feedbackForm.reset();
        renderRecentFeedbacks();

        setTimeout(() => {
            successMsg.style.display = 'none';
        }, 4000);
    });
}

// ================== SHOW RECENT 3 FEEDBACKS ==================
function renderRecentFeedbacks() {
    const container = document.getElementById('recentFeedbacks');
    if (!container) return;

    const list = getFeedbacks().slice(0, 3);

    if (list.length === 0) {
        container.innerHTML = '<p class="empty">No feedback yet. Be the first to submit!</p>';
        return;
    }

    container.innerHTML = list.map(fb => `
        <div class="feedback-item">
            <div class="meta">
                <span class="name">${escapeHtml(fb.name)}</span>
                <span>${fb.date}</span>
            </div>
            <span class="topic-tag">${escapeHtml(fb.topic)}</span>
            <p class="text">${escapeHtml(fb.text)}</p>
        </div>
    `).join('');
}

// ================== 2. ADMIN PANEL ==================
const loginForm = document.getElementById('loginForm');
const logoutBtn = document.getElementById('logoutBtn');
const filterTopic = document.getElementById('filterTopic');

// Login
if (loginForm) {
    if (sessionStorage.getItem('adminLogged') === 'true') {
        showAdminPanel();
    }

    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const user = document.getElementById('loginUser').value.trim();
        const pass = document.getElementById('loginPass').value.trim();

        if (user === ADMIN_USER && pass === ADMIN_PASS) {
            sessionStorage.setItem('adminLogged', 'true');
            showAdminPanel();
        } else {
            document.getElementById('loginError').textContent = '❌ Wrong username or password!';
        }
    });
}

// Show panel
function showAdminPanel() {
    document.getElementById('loginSection').classList.add('hidden');
    document.getElementById('adminPanel').classList.remove('hidden');
    renderAdminFeedbacks();
    updateStats();
}

// Logout
if (logoutBtn) {
    logoutBtn.addEventListener('click', function () {
        sessionStorage.removeItem('adminLogged');
        window.location.href = 'admin.html';
    });
}

// Filter
if (filterTopic) {
    filterTopic.addEventListener('change', renderAdminFeedbacks);
}

// ================== SHOW ALL FEEDBACKS ==================
function renderAdminFeedbacks() {
    const container = document.getElementById('feedbackList');
    if (!container) return;

    let list = getFeedbacks();
    const filter = filterTopic ? filterTopic.value : '';

    if (filter) {
        list = list.filter(fb => fb.topic === filter);
    }

    if (list.length === 0) {
        container.innerHTML = '<div class="card"><p class="empty">No feedback found.</p></div>';
        return;
    }

    container.innerHTML = list.map(fb => `
        <div class="card">
            <div class="meta" style="display:flex;justify-content:space-between;margin-bottom:10px;color:#888;font-size:13px;">
                <span><b style="color:#2c3e50;">${escapeHtml(fb.name)}</b></span>
                <span>${fb.date}</span>
            </div>
            <span class="topic-tag">${escapeHtml(fb.topic)}</span>
            <p style="margin-top:10px;line-height:1.6;color:#444;">${escapeHtml(fb.text)}</p>
        </div>
    `).join('');
}

// ================== STATISTICS ==================
function updateStats() {
    const list = getFeedbacks();

    const totalEl = document.getElementById('totalCount');
    const todayEl = document.getElementById('todayCount');
    const topicEl = document.getElementById('topicCount');

    if (!totalEl) return;

    totalEl.textContent = list.length;

    const today = new Date().toLocaleDateString('en-GB');
    const todayCount = list.filter(fb => fb.date.includes(today)).length;
    todayEl.textContent = todayCount;

    const uniqueTopics = new Set(list.map(fb => fb.topic));
    topicEl.textContent = uniqueTopics.size;
}

// ================== PAGE LOAD ==================
document.addEventListener('DOMContentLoaded', function () {
    renderRecentFeedbacks();
});