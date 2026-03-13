/* ═══════════════════════════════════════
   FIREBASE INITIALIZATION & IMPORTS
═══════════════════════════════════════ */
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-auth.js";
import { getFirestore, doc, setDoc } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyAcB-99MP7Oq9f2vZ979bnjt3Geb6rjrhE",
  authDomain: "database-25a5b.firebaseapp.com",
  projectId: "database-25a5b",
  storageBucket: "database-25a5b.firebasestorage.app",
  messagingSenderId: "562972874228",
  appId: "1:562972874228:web:aee5d889ce153e4f7295a1"
};

// Initialize Firebase Auth & Database
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
console.log("🔥 Firebase initialized. Ready to save data!");

/* ═══════════════════════════════════════
   RAKSHA NETHRA — UI & ANIMATION LOGIC
═══════════════════════════════════════ */

/* ── CUSTOM CURSOR ───────────────────── */
const cursor = document.getElementById('cursor');
const trail  = document.getElementById('cursor-trail');
let mx = 0, my = 0, tx = 0, ty = 0;

if(cursor && trail) {
  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    cursor.style.left = mx + 'px';
    cursor.style.top  = my + 'px';
  });

  (function animTrail() {
    tx += (mx - tx) * 0.14;
    ty += (my - ty) * 0.14;
    trail.style.left = tx + 'px';
    trail.style.top  = ty + 'px';
    requestAnimationFrame(animTrail);
  })();

  document.querySelectorAll('a, button, [onclick], input, select').forEach(el => {
    el.addEventListener('mouseenter', () => {
      cursor.style.transform = 'translate(-50%,-50%) scale(2)';
      cursor.style.opacity = '0.6';
    });
    el.addEventListener('mouseleave', () => {
      cursor.style.transform = 'translate(-50%,-50%) scale(1)';
      cursor.style.opacity = '1';
    });
  });
}

/* ── ANIMATED BACKGROUND CANVAS ─────── */
const canvas = document.getElementById('bg-canvas');
if(canvas) {
  const ctx = canvas.getContext('2d');
  let W, H, particles = [], nebulae = [];

  function initCanvas() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;

    particles = Array.from({ length: 160 }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.4 + 0.3, speed: Math.random() * 0.25 + 0.05,
      phase: Math.random() * Math.PI * 2,
    }));

    nebulae = [
      { x: W * 0.12, y: H * 0.25, r: 420, c: '0,229,255' },
      { x: W * 0.88, y: H * 0.5,  r: 360, c: '155,93,229' },
      { x: W * 0.5,  y: H * 0.85, r: 280, c: '255,59,92' },
    ];
  }

  function drawCanvas(ts) {
    ctx.clearRect(0, 0, W, H);
    nebulae.forEach(n => {
      const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r);
      g.addColorStop(0, `rgba(${n.c},0.055)`);
      g.addColorStop(1, `rgba(${n.c},0)`);
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2); ctx.fill();
    });

    particles.forEach(p => {
      const alpha = 0.3 + 0.5 * Math.sin(p.phase + ts * 0.001 * p.speed);
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(210,225,255,${alpha})`; ctx.fill();
    });

    requestAnimationFrame(drawCanvas);
  }
  initCanvas(); requestAnimationFrame(drawCanvas);
  window.addEventListener('resize', initCanvas);
}

/* ── NAVBAR SCROLL STATE ─────────────── */
const navbar = document.getElementById('navbar');
if(navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 60);
    });
}

/* ── 3D TILT on hero dashboard ───────── */
const dashWrapper = document.getElementById('dashWrapper');
const dash3d      = document.getElementById('dash3d');
if (dashWrapper && dash3d) {
  dashWrapper.addEventListener('mousemove', e => {
    const rect = dashWrapper.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top  + rect.height / 2;
    const rx = ((e.clientY - cy) / (rect.height / 2)) * -7;
    const ry = ((e.clientX - cx) / (rect.width  / 2)) * 7;
    dash3d.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg)`;
  });
  dashWrapper.addEventListener('mouseleave', () => {
    dash3d.style.transform = 'rotateX(0deg) rotateY(0deg)';
  });
}

/* ── STAT COUNTER ANIMATION ──────────── */
function animateCount(el) {
  const target = +el.dataset.count;
  const dur    = 1600;
  const start  = performance.now();
  (function step(now) {
    const p = Math.min((now - start) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(ease * target);
    if (p < 1) requestAnimationFrame(step);
  })(start);
}

/* ── AOS (scroll-reveal) ─────────────── */
const aosItems = document.querySelectorAll('[data-aos]');
if(aosItems.length > 0) {
    const aosObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el   = entry.target;
          const delay = +(el.dataset.aosDelay || 0);
          setTimeout(() => {
            el.classList.add('aosIn');
            // Trigger counter if stat-num
            el.querySelectorAll('.stat-num[data-count]').forEach(animateCount);
          }, delay);
          aosObs.unobserve(el);
        }
      });
    }, { threshold: 0.12 });

    aosItems.forEach(el => aosObs.observe(el));
}

window.addEventListener('load', () => {
  document.querySelectorAll('.stat-num[data-count]').forEach(animateCount);
});

/* ── UI FUNCTIONS ───────────────────── */
function toggleMenu() { document.getElementById('mobileMenu').classList.toggle('open'); }
function scroll2(id) { document.getElementById(id).scrollIntoView({ behavior: 'smooth' }); }
function openModal(tab) {
  const overlay = document.getElementById('authOverlay');
  if(overlay) { overlay.classList.add('open'); switchTab(tab); }
}
function closeModal() { document.getElementById('authOverlay').classList.remove('open'); }
function overlayClick(e) { if (e.target === e.currentTarget) closeModal(); }

function switchTab(tab) {
  const isLogin = tab === 'login';
  document.getElementById('tabLogin').classList.toggle('active', isLogin);
  document.getElementById('tabRegister').classList.toggle('active', !isLogin);
  document.getElementById('panelLogin').style.display    = isLogin ? 'block' : 'none';
  document.getElementById('panelRegister').style.display = isLogin ? 'none'  : 'block';
  clearAlert('alertLogin'); clearAlert('alertRegister');
}

function showAlert(id, msg, type) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg; el.className = `modal-alert show ${type}`;
}
function clearAlert(id) {
  const el = document.getElementById(id);
  if (el) el.className = 'modal-alert';
}

function togglePw(id, btn) {
  const inp = document.getElementById(id);
  inp.type = inp.type === 'password' ? 'text' : 'password';
  btn.textContent = inp.type === 'password' ? '👁' : '🙈';
}

function checkStrength(val) {
  let score = 0;
  if (val.length >= 6) score++;
  if (val.length >= 10) score++;
  if (/[A-Z]/.test(val) && /\d/.test(val)) score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;
  const colors = ['#ff3b5c', '#ff3b5c', '#ffc107', '#00ff88'];
  [1, 2, 3, 4].forEach(i => {
    const sb = document.getElementById('sb' + i);
    if(sb) sb.style.background = i <= score ? colors[score - 1] : 'rgba(255,255,255,0.08)';
  });
}

/* ═══════════════════════════════════════
   FIREBASE DATABASE LOGIC (SAVE & LOGIN)
═══════════════════════════════════════ */

async function doRegister() {
  const first = document.getElementById('rFirst').value.trim();
  const last  = document.getElementById('rLast').value.trim();
  const email = document.getElementById('rEmail').value.trim();
  const phone = document.getElementById('rPhone').value.trim();
  const city  = document.getElementById('rCity').value.trim();
  const role  = document.getElementById('rRole').value;
  const pass  = document.getElementById('rPass').value;

  if (!first || !last || !email || !phone || !city || !role || !pass) {
    showAlert('alertRegister', '⚠ Please complete all fields.', 'er'); return;
  }
  
  // Show loading state
  const btn = document.querySelector('#panelRegister .btn-modal-submit');
  btn.textContent = "Creating Account...";

  try {
    // 1. Create User in Firebase Auth
    const userCredential = await createUserWithEmailAndPassword(auth, email, pass);
    const user = userCredential.user;

    // 2. Save User Details to Firestore Database
    await setDoc(doc(db, "users", user.uid), {
      firstName: first,
      lastName: last,
      email: email,
      phone: phone,
      city: city,
      role: role,
      createdAt: new Date()
    });

    showAlert('alertRegister', `✓ Success! Account created for ${first}.`, 'ok');
    
    // Switch to login tab after success
    setTimeout(() => { 
      switchTab('login'); 
      btn.textContent = "Create My Account";
      document.getElementById('lEmail').value = email; // Auto-fill email for login
    }, 2000);

  } catch (error) {
    console.error("Firebase Auth Error:", error);
    btn.textContent = "Create My Account"; // Reset button
    
    // Make errors user-friendly
    if(error.code === 'auth/email-already-in-use') {
      showAlert('alertRegister', '⚠ This email is already registered.', 'er');
    } else {
      showAlert('alertRegister', `⚠ Error: ${error.message}`, 'er');
    }
  }
}

async function doLogin() {
  const email = document.getElementById('lEmail').value.trim();
  const pass  = document.getElementById('lPass').value;
  
  if (!email || !pass) { showAlert('alertLogin', '⚠ Please fill in all fields.', 'er'); return; }

  const btn = document.querySelector('#panelLogin .btn-modal-submit');
  btn.textContent = "Signing In...";

  try {
    // Attempt to log in with Firebase
    await signInWithEmailAndPassword(auth, email, pass);
    
    showAlert('alertLogin', '✓ Signed in successfully! Redirecting...', 'ok');
    
    // In a real app, you would redirect to a dashboard here:
    // window.location.href = "dashboard.html";
    
    setTimeout(() => {
        closeModal();
        btn.textContent = "Sign In to Platform";
    }, 1500);

  } catch (error) {
    console.error("Firebase Login Error:", error);
    btn.textContent = "Sign In to Platform"; // Reset button
    showAlert('alertLogin', '⚠ Invalid email or password.', 'er');
  }
}

/* ═══════════════════════════════════════
   GLOBAL BINDINGS (REQUIRED FOR ES MODULES)
═══════════════════════════════════════ */
window.toggleMenu = toggleMenu;
window.scroll2 = scroll2;
window.openModal = openModal;
window.closeModal = closeModal;
window.overlayClick = overlayClick;
window.switchTab = switchTab;
window.togglePw = togglePw;
window.checkStrength = checkStrength;
window.doLogin = doLogin;
window.doRegister = doRegister;