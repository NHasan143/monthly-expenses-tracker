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


  // ── 7. SMOOTH PAGE FADE TRANSITION ───────────────────────────────────────────
  // By default, clicking a navigation link causes a hard instant page reload
  // which feels abrupt. This enhancement adds a smooth fade-out before navigation
  // and a fade-in when the new page loads — making the app feel like a SPA
  // (Single Page Application) even though it's a standard multi-page Flask app.
  //
  // How it works:
  //   FADE IN:  The page starts invisible (opacity:0) and fades to fully visible
  //             as soon as the browser fires the 'load' event.
  //
  //   FADE OUT: When the user clicks an internal navigation link, we:
  //               1. Prevent the default browser navigation (e.preventDefault)
  //               2. Fade the page out with a CSS transition (opacity → 0)
  //               3. After 300ms (when fade is complete), navigate to the new URL
  //
  // We exclude links that start with '#' (anchor links on the same page),
  // and '/export' download links, to avoid interfering with those behaviours.

  // Start the page as invisible — it will fade in once fully loaded
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.3s ease';

  // Fade in once everything (images, fonts, scripts) has loaded
  window.addEventListener('load', () => {
    document.body.style.opacity = '1';
  });

  // Attach fade-out to all internal navigation links
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');

    // Skip anchor links, export downloads, external URLs, and _blank links
    if (
      !href ||
      href.startsWith('#') ||
      href.includes('/export') ||
      href.startsWith('http') ||        // ← skip all external links
      link.getAttribute('target') === '_blank'  // ← skip all new-tab links
    ) return;

    link.addEventListener('click', function (e) {
      e.preventDefault();
      const target = this.href;
      document.body.style.opacity = '0';
      setTimeout(() => {
        window.location.href = target;
      }, 300);
    });
  });
  // ── End Page Fade Transition ──────────────────────────────────────────────────

}); // End DOMContentLoaded

// ── 8. DARK TO LIGHT MODE TRANSITION ───────────────────────────────────────────
// Toggles between dark mode (default) and light mode by adding/removing
// the 'light-mode' class on the <body> element.
//
// The user's preference is saved to localStorage so it persists across
// page refreshes and navigation — they won't have to toggle every time.
//
// The button label and emoji update to reflect the current mode:
//   🌙 Dark  — currently in dark mode  (click to switch to light)
//   ☀️ Light — currently in light mode (click to switch to dark)

function toggleTheme() {
  const body    = document.body;
  const btn     = document.getElementById('themeToggle');
  const isLight = body.classList.toggle('light-mode'); // toggle and check new state

  // Update button label to reflect the CURRENT active mode
  btn.textContent = isLight ? '☀️ Light' : '🌙 Dark';

  // Save preference to localStorage so it survives page navigation
  localStorage.setItem('theme', isLight ? 'light' : 'dark');
}

// ── Apply saved theme preference on every page load ───────────────────────────
// Runs immediately (not inside DOMContentLoaded) so the theme is applied
// as early as possible — prevents a flash of the wrong theme on load.
(function applyStoredTheme() {
  const saved = localStorage.getItem('theme');
  if (saved === 'light') {
    document.body.classList.add('light-mode');

    // Wait for the DOM to be ready before updating the button label
    document.addEventListener('DOMContentLoaded', () => {
      const btn = document.getElementById('themeToggle');
      if (btn) btn.textContent = '☀️ Light';
    });
  }
})();
// ── End Dark / Light Mode Toggle ──────────────────────────────────────────────