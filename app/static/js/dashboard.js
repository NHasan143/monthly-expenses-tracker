/**
 * dashboard.js
 * Handles all JavaScript functionality for the Dashboard page.
 *
 * Responsibilities:
 *  1. Render the Chart.js doughnut chart using category spending data
 *  2. Animate stat card values (count up from 0 to real value on load)
 *  3. Animate category progress bars when they scroll into the viewport
 *  4. Launch a confetti burst when the user's savings rate is 20% or above
 *
 * Depends on:
 *  - window.CATEGORY_DATA  → set by an inline <script> in dashboard.html
 *  - Chart.js              → loaded via CDN in base.html
 */


// ── Color palette used for both the doughnut chart and confetti ──────────────
// These match the colors defined in dashboard.html's Jinja template so that
// chart slices, category badges, and progress bars all share the same palette.
const PALETTE = ['#3bdf91', '#58a6ff', '#e3b341', '#f85149', '#bc8cff', '#79c0ff'];


// ── Wait for the full DOM to be ready before running anything ─────────────────
// 'DOMContentLoaded' fires once every HTML element is parsed and available.
// Without this wrapper, querySelector calls would fail on elements not yet rendered.
document.addEventListener('DOMContentLoaded', () => {


  // ── 1. DOUGHNUT CHART (Chart.js) ─────────────────────────────────────────
  // Looks for a <canvas id="expenseChart"> on the page.
  // If the canvas or the data doesn't exist (e.g. no expenses yet), we bail early
  // to avoid JavaScript errors on an empty dashboard.
  const canvas = document.getElementById('expenseChart');
  if (canvas && window.CATEGORY_DATA) {

    // Extract category names (labels) and their totals (values) from the
    // window.CATEGORY_DATA object that was injected by dashboard.html.
    // e.g. { "Groceries": 2300, "Rent": 2000 } → labels=["Groceries","Rent"]
    const labels = Object.keys(window.CATEGORY_DATA);
    const values = Object.values(window.CATEGORY_DATA);

    // Create a new Chart.js doughnut chart instance on the canvas element.
    new Chart(canvas.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,

          // Assign a color from PALETTE to each slice.
          // slice() ensures we never go out of bounds if there are fewer categories than colors.
          backgroundColor: PALETTE.slice(0, labels.length),

          borderWidth: 2,
          borderColor: '#161b22',  // matches --surface CSS variable (dark background)
          hoverOffset: 12           // slices pop outward slightly when hovered
        }]
      },
      options: {
        responsive: true,           // chart resizes with its container
        maintainAspectRatio: false, // allows us to control height via the parent div
        cutout: '68%',              // controls the hole size — higher % = thinner ring

        plugins: {
          // Legend sits below the chart, styled to match the app's dark theme
          legend: {
            position: 'bottom',
            labels: {
              color: '#8b949e',                    // --text-muted
              font: { family: 'DM Sans', size: 12 },
              padding: 16,
              usePointStyle: true,
              pointStyle: 'circle',
              boxWidth: 10,
              boxHeight: 10,
            }
          },

          // Custom tooltip: prefix the value with a $ sign
          tooltip: {
            callbacks: {
              label: ctx => ` $${ctx.parsed.toFixed(2)}`
            }
          }
        }
      }
    });
  }
  // ── End Doughnut Chart ────────────────────────────────────────────────────


  // ── 2. ANIMATED NUMBER COUNTERS ──────────────────────────────────────────
  // When the page loads, each stat card value (salary, expenses, balance,
  // savings rate) counts up from 0 to its real value over ~1.2 seconds.
  // This creates a satisfying "live data loading" effect that draws the user's
  // eye to the key numbers immediately.
  //
  // How it works:
  //   - We read the current text content of each .stat-value element
  //   - Strip the '$' or '%' symbol to get the raw number
  //   - Use setInterval to increment a counter 60 times/sec until it reaches the target
  //   - Each tick we re-write the element's text with the growing number

  /**
   * Animates an element's text from 0 up to `target` over `duration` ms.
   * @param {HTMLElement} el       - The DOM element whose text we're animating
   * @param {number}      target   - The final numeric value to count up to
   * @param {string}      prefix   - Symbol to prepend ('$' for money, '' for %)
   * @param {string}      suffix   - Symbol to append ('' for money, '%' for rate)
   * @param {number}      duration - Total animation time in milliseconds
   */
  function animateCounter(el, target, prefix = '$', suffix = '', duration = 1200) {
    let current = 0;

    // Calculate how much to add each frame so we reach `target` in `duration` ms.
    // 16ms per frame ≈ 60fps
    const increment = target / (duration / 16);

    const timer = setInterval(() => {
      current += increment;

      // Once we've reached or passed the target, snap to exact value and stop
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }

      // Write the formatted number back into the element
      el.textContent = prefix + current.toFixed(2) + suffix;
    }, 16);
  }

  // Apply the counter animation to every stat card value on the page.
  // We detect whether it's a percentage or a dollar amount by checking the text.
  document.querySelectorAll('.stat-value').forEach(el => {
    const text = el.textContent.trim();
    const isPercent = text.includes('%');

    // Parse the raw number, stripping any leading '$' or trailing '%'
    const rawValue = parseFloat(text.replace('$', '').replace('%', ''));

    // Skip elements that don't contain a valid number (e.g. empty cards)
    if (isNaN(rawValue)) return;

    animateCounter(
      el,
      rawValue,
      isPercent ? '' : '$',   // prefix: no symbol for %, dollar sign for money
      isPercent ? '%' : '',   // suffix: % sign for savings rate, nothing for money
    );
  });
  // ── End Animated Counters ─────────────────────────────────────────────────


  // ── 3. SCROLL-TRIGGERED PROGRESS BAR ANIMATION ───────────────────────────
  // The category progress bars (in the "By Category" card) normally render
  // at full width instantly. This enhancement makes each bar animate from 0%
  // to its real width the first time it scrolls into view.
  //
  // We use the IntersectionObserver API — a modern, performant alternative
  // to listening to scroll events. The observer fires a callback whenever
  // a watched element enters or exits the visible viewport.
  //
  // Steps per bar:
  //   1. Save the target width (already set inline by Jinja: e.g. "style='width:72%'")
  //   2. Set width to 0% instantly (no transition yet, so it's invisible)
  //   3. On the next animation frame, re-apply the target width WITH a CSS transition
  //      → the browser smoothly animates from 0 → 72%
  //   4. Stop observing this bar (we only want the animation to play once)

  const progressObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      // Only act when the element has entered the visible area
      if (entry.isIntersecting) {
        const bar = entry.target;

        // Save the target width before we reset it to 0
        const targetWidth = bar.style.width;

        // Instantly collapse to 0 (no animation yet, happens in same paint frame)
        bar.style.width = '0%';

        // requestAnimationFrame defers the width restoration to the next paint.
        // This tiny delay is necessary — without it, the browser may batch both
        // style changes together and skip straight to the final width.
        requestAnimationFrame(() => {
          bar.style.transition = 'width 1s cubic-bezier(0.4, 0, 0.2, 1)';
          bar.style.width = targetWidth;
        });

        // Unobserve so the animation doesn't retrigger on every scroll
        progressObserver.unobserve(bar);
      }
    });
  }, {
    threshold: 0.1  // trigger when at least 10% of the bar is visible
  });

  // Target the inner colored div inside each progress bar container.
  // The container is identified by its inline height style set in dashboard.html.
  document.querySelectorAll('[style*="height:6px"] > div').forEach(bar => {
    progressObserver.observe(bar);
  });
  // ── End Progress Bar Animation ────────────────────────────────────────────


  // ── 4. CONFETTI BURST ON HIGH SAVINGS RATE ───────────────────────────────
  // If the user's savings rate is 20% or above (considered "great" by the app),
  // we fire a short confetti animation from the savings rate stat card.
  //
  // This rewards the user with a moment of visual delight for good budgeting —
  // a subtle gamification element that encourages healthy financial habits.
  //
  // How it works:
  //   - 60 small colored dots are created as absolutely-positioned <div> elements
  //   - Each dot is placed at the center of the savings card
  //   - A CSS animation (confettiFly) translates them outward in random directions
  //   - They fade out and are removed from the DOM after 2 seconds (no memory leaks)

  /**
   * Launches a confetti burst originating from the center-top of `originEl`.
   * @param {HTMLElement} originEl - The element to burst confetti from
   */
  function launchConfetti(originEl) {
    const rect = originEl.getBoundingClientRect();

    for (let i = 0; i < 60; i++) {
      const dot = document.createElement('div');

      // Each dot gets a random color from the app's palette
      dot.style.cssText = `
        position: fixed;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: ${PALETTE[i % PALETTE.length]};
        left: ${rect.left + rect.width / 2}px;
        top: ${rect.top}px;
        pointer-events: none;
        z-index: 9999;
        animation: confettiFly ${0.8 + Math.random() * 0.8}s ease-out forwards;
        --tx: ${(Math.random() - 0.5) * 200}px;
        --ty: ${-(Math.random() * 150 + 50)}px;
      `;
      // --tx and --ty are CSS custom properties consumed by the @keyframes rule
      // They give each dot a unique random trajectory

      document.body.appendChild(dot);

      // Clean up the dot from the DOM after its animation completes
      setTimeout(() => dot.remove(), 2000);
    }
  }

  // ── Inject the confettiFly keyframes into the page dynamically ─────────────
  // We add the @keyframes rule via JavaScript so dashboard.js stays self-contained
  // and you don't need to touch main.css to use this effect.
  const confettiStyle = document.createElement('style');
  confettiStyle.textContent = `
    @keyframes confettiFly {
      to {
        transform: translate(var(--tx), var(--ty));
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(confettiStyle);

  // Find the savings rate card (last .stat-card on the dashboard) and read its value.
  // The stat cards are: Salary | Expenses | Balance | Savings Rate (left to right)
  const savingsCard = document.querySelector('.stat-grid .stat-card:last-child');
  if (savingsCard) {
    const savingsText = savingsCard.querySelector('.stat-value')?.textContent || '';
    const savingsValue = parseFloat(savingsText.replace('%', ''));

    // Only fire confetti if savings rate is genuinely 20% or above
    // Delay by 1.4s so the counter animation finishes first — more dramatic!
    if (!isNaN(savingsValue) && savingsValue >= 20) {
      setTimeout(() => launchConfetti(savingsCard), 1400);
    }
  }
  // ── End Confetti Burst ────────────────────────────────────────────────────

  // ── 5. RECENT EXPENSES TABLE — ROW STAGGER ANIMATION ─────────────────────
  // When the dashboard loads, each row in the Recent Expenses table slides in
  // and fades up one after another with a small delay between each row.
  // This mirrors the exact same cascade entrance effect used on the Expenses
  // page (expenses.js) so both tables feel consistent across the app.
  //
  // We scope the selector to '.card:last-of-type tbody tr' so we only target
  // the Recent Expenses table and don't accidentally affect other elements.
  //
  // How it works:
  //   - Every <tr> starts invisible and shifted down 20px
  //   - Each row gets a slightly longer delay than the previous (i * 60ms)
  //     creating the staggered waterfall effect
  //   - requestAnimationFrame ensures the browser has painted the initial
  //     invisible state before triggering the transition to visible
  const recentRows = document.querySelectorAll('tbody tr');

  recentRows.forEach((row, i) => {
    row.style.opacity    = '0';
    row.style.transform  = 'translateY(20px)';
    row.style.transition = 'opacity 0.4s ease, transform 0.4s ease';

    setTimeout(() => {
      requestAnimationFrame(() => {
        row.style.opacity   = '1';
        row.style.transform = 'translateY(0)';
      });
    }, 60 + i * 60);
  });

  // ── 6. RECENT EXPENSES TABLE — AMOUNT HOVER PULSE ────────────────────────
  // When the user hovers over any row in the Recent Expenses table, the amount
  // cell briefly scales up and turns red — drawing the eye to the cost.
  // Mirrors the identical effect from expenses.js for consistency.
  //
  // The column index differs from the Expenses page because the dashboard table
  // has no leading '#' column:
  //   expenses.html  → # | Description | Category | Amount | Actions → td:nth-child(4)
  //   dashboard.html → Description | Category | Amount | % of Income → td:nth-child(3)
  recentRows.forEach(row => {
    const amountCell = row.querySelector('td:nth-child(3)');
    if (!amountCell) return;

    row.addEventListener('mouseenter', () => {
      amountCell.style.transition = 'transform 0.15s ease, color 0.15s ease';
      amountCell.style.transform  = 'scale(1.15)';
      amountCell.style.color      = '#f85149';
    });

    row.addEventListener('mouseleave', () => {
      amountCell.style.transform = 'scale(1)';
      amountCell.style.color     = '';
    });
  });

  // ── 7. STAT CARD HOVER EFFECTS ────────────────────────────────────────────
// Adds a lift + glow hover effect to each stat card dynamically.
// Each card type (green, red, yellow) gets its own matching glow color
// so the effect feels cohesive with the card's accent color.
//
// We use mouseenter/mouseleave instead of CSS :hover so the effect
// is fully controlled by JavaScript — easier to adjust or extend later.
//
// Effects applied on hover:
//   - Card lifts up 4px (translateY)
//   - Border brightens to accent color
//   - Background lightens slightly
//   - Colored box shadow appears below + glow ring around border

// Define glow colors matching each card type
const glowColors = {
  green:  'rgba(59, 223, 145, 0.15)',   // --accent green
  red:    'rgba(248, 81, 73, 0.15)',    // --danger red
  yellow: 'rgba(227, 179, 65, 0.15)',   // --warning yellow
};

const borderColors = {
  green:  'rgba(59, 223, 145, 0.5)',
  red:    'rgba(248, 81, 73, 0.5)',
  yellow: 'rgba(227, 179, 65, 0.5)',
};

document.querySelectorAll('.stat-card').forEach(card => {

  // Detect which color type this card is (green, red, or yellow)
  const type = ['green', 'red', 'yellow'].find(t => card.classList.contains(t)) || 'green';

  // Set the base transition on the card so all property changes animate smoothly
  card.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease, background 0.3s ease';

  // ── Mouse enters the card ──
  card.addEventListener('mouseenter', () => {
    card.style.transform   = 'translateY(-4px)';                    // lift up
    card.style.background  = 'var(--surface2)';                     // lighten background
    card.style.borderColor = borderColors[type];                    // brighten border
    card.style.boxShadow   = `0 8px 30px ${glowColors[type]}, 0 0 0 1px ${borderColors[type]}`; // glow
  });

  // ── Mouse leaves the card ──
  card.addEventListener('mouseleave', () => {
    card.style.transform   = 'translateY(0)';                       // return to normal
    card.style.background  = 'var(--surface)';                      // restore background
    card.style.borderColor = 'var(--border)';                       // restore border
    card.style.boxShadow   = 'none';                                // remove glow
  });
});
// ── End Stat Card Hover Effects ───────────────────────────────────────────

}); // End DOMContentLoaded

/**
 * Animates the colored bars in "By Category" section
 */

if (gsap) {
  gsap.registerPlugin(ScrollTrigger);
}

// Doughnut chart hover effect
function addChartHoverEffect() {
  const canvas = document.getElementById('expenseChart');
  if (!canvas) return;
  
  canvas.addEventListener('mouseenter', () => {
    canvas.style.cursor = 'pointer';
    
  });
  
  canvas.addEventListener('mouseleave', () => {
    canvas.style.cursor = 'default';
    
    // Scale back to normal
    gsap.to(canvas, {
      scale: 1,
      duration: 0.3,
      ease: "power2.out"
    });
  });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  if (!gsap) return;
  addChartHoverEffect();
});
