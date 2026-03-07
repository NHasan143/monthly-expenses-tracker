/**
 * modals.js
 * Shared JavaScript loaded on EVERY page via base.html.
 *
 * Responsibilities:
 *  1. Open and close modal dialogs (used on dashboard, expenses, settings)
 *  2. Close modals when the dark backdrop is clicked
 *  3. Close modals when the Escape key is pressed
 *  4. Add a ripple wave effect to all buttons on click
 *  5. Auto-dismiss flash notification messages after a short delay
 *  6. Smooth page fade-in on load and fade-out before navigation
 */


// ── 1. OPEN MODAL ─────────────────────────────────────────────────────────────
// Adds the CSS class 'open' to the modal overlay element.
// The .modal-overlay selector in main.css uses display:none by default,
// and display:flex when the 'open' class is present.
//
// After opening, we focus the first input field inside the modal automatically.
// This improves accessibility and saves the user an extra click.
//
// @param {string} id - The HTML id attribute of the modal overlay to open
function openModal(id) {
  document.getElementById(id).classList.add('open');

  // Move keyboard focus to the first input in the modal so the user can
  // start typing immediately without needing to click into the field
  const firstInput = document.querySelector(`#${id} input`);
  if (firstInput) firstInput.focus();
}


// ── 2. CLOSE MODAL ───────────────────────────────────────────────────────────
// Removes the 'open' class from the modal overlay, hiding it.
// Called by Cancel buttons and the Escape key handler below.
//
// @param {string} id - The HTML id attribute of the modal overlay to close
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}


// ── Wait for the full DOM to load before attaching any event listeners ────────
// Without this, elements like buttons and overlays won't exist yet when
// the script runs, causing silent failures.
document.addEventListener('DOMContentLoaded', () => {


  // ── 3. CLOSE MODAL ON BACKDROP CLICK ───────────────────────────────────────
  // When a user clicks the dark semi-transparent area OUTSIDE the modal box,
  // the modal should close — this is standard UX behavior users expect.
  //
  // We check that the click target IS the overlay itself (not a child element
  // inside the modal box). This prevents clicks on the modal content from
  // accidentally closing it.

  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      // e.target is the element that was actually clicked
      // overlay is the outer dark backdrop
      // If they're the same, the user clicked the backdrop — close the modal
      if (e.target === overlay) overlay.classList.remove('open');
    });
  });
  // ── End Backdrop Click ──────────────────────────────────────────────────────


  // ── 4. CLOSE MODAL ON ESCAPE KEY ───────────────────────────────────────────
  // Pressing Escape is a universal keyboard shortcut for dismissing dialogs.
  // We listen globally on the document for any keydown event and check if
  // the key is 'Escape', then close all currently open modals.
  //
  // querySelectorAll returns all modals with the 'open' class at that moment.

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.open').forEach(m => {
        m.classList.remove('open');
      });
    }
  });
  // ── End Escape Key Handler ──────────────────────────────────────────────────


  // ── 5. BUTTON RIPPLE EFFECT ─────────────────────────────────────────────────
  // Adds a material-design-style ripple wave to every button when clicked.
  // The ripple starts at the exact point the user's cursor hit the button
  // and expands outward before fading — making clicks feel physical and responsive.
  //
  // How it works:
  //   - On click, a new <span> element is created and inserted into the button
  //   - The span is positioned at the click coordinates (relative to the button)
  //   - A CSS animation (rippleEffect) scales it from 0 to 4x size while fading out
  //   - After 600ms the span is removed from the DOM (no clutter builds up)
  //
  // We also inject the required @keyframes CSS rule dynamically so this file
  // stays completely self-contained — no changes needed in main.css.

  // Inject the ripple keyframes rule into the document's <head>
  const rippleStyle = document.createElement('style');
  rippleStyle.textContent = `
    @keyframes rippleEffect {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(rippleStyle);

  // Attach a click listener to every element with the .btn class
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function (e) {

      // Create the ripple circle element
      const ripple = document.createElement('span');

      // Get the button's position on screen so we can calculate
      // where the click happened relative to the button's top-left corner
      const rect = this.getBoundingClientRect();

      // The ripple is 100x100px — we offset by 50px to center it on the click point
      ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.25);
        width: 100px;
        height: 100px;
        transform: scale(0);
        left: ${e.clientX - rect.left - 50}px;
        top: ${e.clientY - rect.top - 50}px;
        animation: rippleEffect 0.6s linear;
        pointer-events: none;
      `;

      // The button needs relative positioning so the ripple is contained inside it
      this.style.position = 'relative';
      this.style.overflow = 'hidden';

      this.appendChild(ripple);

      // Remove the ripple element after the animation finishes to keep the DOM clean
      setTimeout(() => ripple.remove(), 600);
    });
  });
  // ── End Button Ripple ────────────────────────────────────────────────────────


  // ── 6. AUTO-DISMISSING FLASH NOTIFICATIONS ───────────────────────────────────
  // Flask flash messages (success/error banners) normally stay on screen until
  // the user navigates away. This enhancement makes them automatically slide out
  // and disappear after 3 seconds — keeping the UI clean and uncluttered.
  //
  // Behavior:
  //   - Each flash message fades out and slides to the right after 3 seconds
  //   - If there are multiple messages, they dismiss one-by-one with 500ms gaps
  //     (staggered using the loop index `i`) so they don't all vanish at once
  //   - After the CSS transition finishes (400ms), the element is fully removed
  //     from the DOM so it no longer takes up space

  document.querySelectorAll('.flash').forEach((flash, i) => {

    // Set up the initial transition properties on the element
    flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    flash.style.transform = 'translateX(0)';

    // Schedule the dismiss — stagger multiple messages by 500ms each
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(40px)';  // slides right as it fades

      // Remove from DOM after the CSS transition completes (0.4s = 400ms)
      setTimeout(() => flash.remove(), 400);
    }, 3000 + i * 500);
  });
  // ── End Auto-dismiss Flash ────────────────────────────────────────────────────

}); // End DOMContentLoaded

// ── 7. DARK TO LIGHT MODE TRANSITION ───────────────────────────────────────────
// Toggles between dark mode (default) and light mode by adding/removing
// the 'light-mode' class on the <body> element.
//
// The user's preference is saved to localStorage so it persists across
// page refreshes and navigation — they won't have to toggle every time.
//
// The button label and emoji update to reflect the current mode:
//   🌙 Dark  — currently in dark mode  (click to switch to light)
//   ☀️ Light — currently in light mode (click to switch to dark)

const moonSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3bdf91" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v2"/><path d="M14.837 16.385a6 6 0 1 1-7.223-7.222c.624-.147.97.66.715 1.248a4 4 0 0 0 5.26 5.259c.589-.255 1.396.09 1.248.715"/><path d="M16 12a4 4 0 0 0-4-4"/><path d="m19 5-1.256 1.256"/><path d="M20 12h2"/></svg>`;

const sunSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e3b341" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`;

function toggleTheme() {
  const body    = document.body;
  const btn     = document.getElementById('themeToggle');
  const isLight = body.classList.toggle('light-mode');

  btn.innerHTML = isLight ? sunSVG : moonSVG;
  localStorage.setItem('theme', isLight ? 'light' : 'dark');
}

// ── 8. CLICK RIPPLE + PARTICLE BURST ─────────────────────────────────────────
// On every click, two effects fire simultaneously from the click point:
//   1. A ripple ring expands outward and fades — like a water drop
//   2. 20 small particles explode outward in random directions and shrink away
//
// Both are pure CSS + JS — no libraries needed. All elements are created,
// animated, and removed from the DOM automatically so there's no memory leak.
// pointer-events: none on everything ensures clicks are never blocked.
//
// All 5 app accent colors are used — the ripple and each particle independently
// pick a random color from the palette on every click.

document.addEventListener('click', e => {
  const x = e.clientX;
  const y = e.clientY;
  const CLICK_COLORS = ['#3bdf91', '#58a6ff', '#e3b341', '#f85149', '#bc8cff'];

  // ── Ripple ring ──────────────────────────────────────────────────────────
  const rippleColor = CLICK_COLORS[Math.floor(Math.random() * CLICK_COLORS.length)];
  const ripple = document.createElement('div');
  ripple.style.cssText = `
    position: fixed;
    left: ${x}px;
    top: ${y}px;
    width: 0px;
    height: 0px;
    border-radius: 50%;
    border: 2px solid ${rippleColor};
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 9998;
    animation: rippleExpand 0.6s ease-out forwards;
  `;
  document.body.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);

  // ── Particle burst ───────────────────────────────────────────────────────
  for (let i = 0; i < 20; i++) {
    const particle = document.createElement('div');
    const color    = CLICK_COLORS[Math.floor(Math.random() * CLICK_COLORS.length)];
    const size     = Math.random() * 6+3;          // 3px – 9px
    const angle    = Math.random() * 360;             // random direction
    const distance = Math.random() * 40 + 20;        // 40px – 120px spread
    const tx       = Math.cos(angle * Math.PI / 180) * distance;
    const ty       = Math.sin(angle * Math.PI / 180) * distance;
    const duration = Math.random() * 400 + 500;      // 500ms – 900ms

    particle.style.cssText = `
      position: fixed;
      left: ${x}px;
      top: ${y}px;
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      background: ${color};
      transform: translate(-50%, -50%);
      pointer-events: none;
      z-index: 9998;
      animation: particleFly ${duration}ms ease-out forwards;
      --tx: ${tx}px;
      --ty: ${ty}px;
    `;
    document.body.appendChild(particle);
    setTimeout(() => particle.remove(), duration);
  }
});

// ── Keyframes ─────────────────────────────────────────────────────────────────
const clickEffectStyle = document.createElement('style');
clickEffectStyle.textContent = `
  @keyframes rippleExpand {
    to {
      width: 120px;
      height: 120px;
      opacity: 0;
    }
  }
  @keyframes particleFly {
    to {
      transform: translate(calc(-50% + var(--tx)), calc(-50% + var(--ty)));
      opacity: 0;
      width: 0px;
      height: 0px;
    }
  }
`;
document.head.appendChild(clickEffectStyle);
// ── End Click Ripple + Particle Burst ─────────────────────────────────────────

// ── Apply saved theme preference on every page load ───────────────────────────
// Runs immediately (not inside DOMContentLoaded) so the theme is applied
// as early as possible — prevents a flash of the wrong theme on load.
(function applyStoredTheme() {
  const saved = localStorage.getItem('theme');
  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('themeToggle');
    if (saved === 'light') {
      document.body.classList.add('light-mode');
      if (btn) btn.innerHTML = sunSVG;
    } else {
      if (btn) btn.innerHTML = moonSVG;
    }
  });
})();
// ── End Dark / Light Mode Toggle ──────────────────────────────────────────────

// ── 9. PASSWORD VISIBILITY TOGGLE ────────────────────────────────────────────────
// Toggles the input type between 'password' and 'text' so the user can
// verify what they've typed. The eye icon updates to reflect the current state.
//
// @param {string} inputId - The id of the password input field
// @param {HTMLElement} btn - The toggle button element (to update its icon)

function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  const isHidden = input.type === 'password';
  input.type     = isHidden ? 'text' : 'password';
  btn.textContent = isHidden ? '🔐' : '👁';
}
// ── End Password Visibility Toggle ────────────────────────────────────────────