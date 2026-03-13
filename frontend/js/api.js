/* ═══════════════════════════════════════════════════════════
   RAKSHA NETHRA — Shared API Client
   All API calls go through this file.
   Exposes global object: window.RN
═══════════════════════════════════════════════════════════ */

(function() {
  const API_BASE = 'http://127.0.0.1:8000';

  // ── Token helpers ──────────────────────────────────────────
  function getToken() { return localStorage.getItem('rn_token'); }
  function getUser()  { try { return JSON.parse(localStorage.getItem('rn_user') || 'null'); } catch { return null; } }
  function setAuth(token, user) {
    localStorage.setItem('rn_token', token);
    localStorage.setItem('rn_user', JSON.stringify(user));
  }
  function clearAuth() {
    localStorage.removeItem('rn_token');
    localStorage.removeItem('rn_user');
  }

  // ── Auth guard (call on each protected page's load) ─────────
  function requireAuth() {
    if (!getToken()) {
      window.location.href = '/frontend/login.html';
      return false;
    }
    return true;
  }

  // ── Core fetch ─────────────────────────────────────────────
  async function apiFetch(path, opts = {}) {
    const token = getToken();
    const headers = { ...(opts.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!(opts.body instanceof FormData)) {
      if (opts.body && typeof opts.body !== 'string') {
        opts.body = JSON.stringify(opts.body);
      }
      if (opts.body) headers['Content-Type'] = 'application/json';
    }
    const res = await fetch(API_BASE + path, { ...opts, headers });
    if (res.status === 401) {
      clearAuth();
      window.location.href = '/frontend/login.html';
      return null;
    }
    if (res.status === 204) return null;
    const data = await res.json().catch(() => ({ detail: res.statusText }));
    if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
    return data;
  }

  // ── Toast helper (requires #toast-container in DOM) ─────────
  function toast(msg, type = 'info') {
    let tc = document.getElementById('toast-container');
    if (!tc) {
      tc = document.createElement('div');
      tc.id = 'toast-container';
      document.body.appendChild(tc);
    }
    const t = document.createElement('div');
    const icons = { success: '✓', error: '✗', info: 'ℹ' };
    t.className = `toast ${type}`;
    t.innerHTML = `<span>${icons[type]||'ℹ'}</span><span>${msg}</span>`;
    tc.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(100%)'; t.style.transition = '0.3s'; setTimeout(() => t.remove(), 300); }, 3500);
  }

  // ── Populate sidebar user info ──────────────────────────────
  function populateSidebar() {
    const user = getUser();
    if (!user) return;
    const nameEl = document.getElementById('sidebar-user-name');
    const roleEl = document.getElementById('sidebar-user-role');
    const avatarEl = document.getElementById('sidebar-user-avatar');
    if (nameEl) nameEl.textContent = user.name || user.email;
    if (roleEl) roleEl.textContent = user.role || 'citizen';
    if (avatarEl) avatarEl.textContent = (user.name || user.email || '?')[0].toUpperCase();
  }

  // ── Format helpers ──────────────────────────────────────────
  function timeAgo(dateStr) {
    const d = new Date(dateStr);
    const diff = Date.now() - d.getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return 'just now';
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h/24)}d ago`;
  }
  function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g,' ') : ''; }
  function issueColor(type) {
    const map = { pothole:'red', garbage:'yellow', streetlight:'#aaa', water_leak:'#64b5f6' };
    return map[type] || '#888';
  }
  function issueEmoji(type) {
    const map = { pothole:'🛣️', garbage:'🗑️', streetlight:'💡', water_leak:'💧' };
    return map[type] || '📍';
  }

  // ── API endpoints ───────────────────────────────────────────
  const auth = {
    register: (payload) => apiFetch('/auth/register', { method: 'POST', body: payload }),
    login:    (payload) => apiFetch('/auth/login',    { method: 'POST', body: payload }),
  };

  const complaints = {
    create:       (form)  => apiFetch('/complaints/create', { method: 'POST', body: form }),
    all:          ()      => apiFetch('/complaints/all'),
    feed:         ()      => apiFetch('/complaints/feed'),
    updateStatus: (id, s) => apiFetch(`/complaints/${id}/status`, { method: 'PUT', body: { status: s } }),
    delete:       (id)    => apiFetch(`/complaints/${id}`, { method: 'DELETE' }),
    aiDetect:     (p)     => apiFetch('/ai/convert-detection', { method: 'POST', body: p }),
  };

  const map = {
    complaints: () => apiFetch('/map/complaints'),
    heatmap:    () => apiFetch('/map/heatmap'),
  };

  const analytics = {
    dashboard: () => apiFetch('/analytics/dashboard'),
    types:     () => apiFetch('/analytics/types'),
    timeline:  () => apiFetch('/analytics/timeline'),
    locations: () => apiFetch('/analytics/locations'),
  };

  const alerts = {
    list: () => apiFetch('/alerts'),
    sos:  (p) => apiFetch('/alerts/sos', { method: 'POST', body: p }),
  };

  // Expose on window
  window.RN = {
    API_BASE,
    getToken, getUser, setAuth, clearAuth,
    requireAuth, populateSidebar,
    toast, timeAgo, capitalize, issueColor, issueEmoji,
    auth, complaints, map, analytics, alerts,
  };
})();
