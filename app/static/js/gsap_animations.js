/**
 * Progress Bar Animation Only
 * Animates the colored bars in "By Category" section
 * Everything else stays the same
 */

if (gsap) {
  gsap.registerPlugin(ScrollTrigger);
}

// Animate progress bars
function animateProgressBars() {
  const bars = document.querySelectorAll('[style*="height:6px"] > div');
  
  bars.forEach((bar, index) => {
    const targetWidth = bar.style.width;
    bar.style.width = '0%';
    
    gsap.to(bar, {
      width: targetWidth,
      duration: 1.5,
      ease: "power2.out",
      delay: index * 0.15
    });
  });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  if (!gsap) return;
  animateProgressBars();
});