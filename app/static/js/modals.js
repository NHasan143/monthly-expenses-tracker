/**
 * modals.js — shared modal open/close helpers used on every page.
 * Loaded once via base.html.
 */

function openModal(id) {
  document.getElementById(id).classList.add('open');
  const firstInput = document.querySelector(`#${id} input`);
  if (firstInput) firstInput.focus();
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

// Close any open modal when clicking the dark backdrop
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) overlay.classList.remove('open');
    });
  });
});

// Close any open modal on Escape key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
  }
});
