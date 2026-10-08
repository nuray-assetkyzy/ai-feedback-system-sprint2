const API_BASE = window.location.origin;

async function apiFetch(path, options = {}) {
    const config = {
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
        },
        ...options,
    };
    const response = await fetch(`${API_BASE}${path}`, config);
    let data = null;
    const text = await response.text();
    if (text) {
        try {
            data = JSON.parse(text);
        } catch {
            data = { detail: text };
        }
    }
    if (!response.ok) {
        const message = data?.detail || data?.message || `Request failed (${response.status})`;
        throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
    }
    return data;
}

const FeedbackAPI = {
    health: () => apiFetch('/api/health'),
    submit: (body) => apiFetch('/api/feedback', { method: 'POST', body: JSON.stringify(body) }),
    recent: (limit = 3) => apiFetch(`/api/feedback/recent?limit=${limit}`),
};

const AdminAPI = {
    login: (username, password) =>
        apiFetch('/api/admin/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        }),
    logout: () => apiFetch('/api/admin/logout', { method: 'POST' }),
    session: () => apiFetch('/api/admin/session'),
    feedback: (params = {}) => {
        const q = new URLSearchParams();
        if (params.topic) q.set('topic', params.topic);
        if (params.sentiment) q.set('sentiment', params.sentiment);
        if (params.language) q.set('language', params.language);
        const qs = q.toString();
        return apiFetch(`/api/admin/feedback${qs ? `?${qs}` : ''}`);
    },
    stats: () => apiFetch('/api/admin/stats'),
    migrate: (records) =>
        apiFetch('/api/admin/migrate', {
            method: 'POST',
            body: JSON.stringify({ records }),
        }),
};
