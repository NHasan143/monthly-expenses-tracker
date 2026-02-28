/**
 * expenses.js
 * JavaScript for the Expenses page (/expenses).
 *
 * Responsibilities:
 *  1. Populate and open the Edit Expense modal with the correct expense data
 *  2. Animate expense table rows in sequentially on page load
 *  3. Add a hover pulse effect on the amount cell of each table row
 *
 * Depends on:
 *  - modals.js (openModal function) — loaded first via base.html
 *  - The expenses table rendered by Jinja in expenses.html
 */


// ── 1. OPEN EDIT MODAL WITH PRE-FILLED DATA ──────────────────────────────────
// Called by the "Edit" button on each expense row in expenses.html.
// The Jinja template passes the expense's current values directly as
// function arguments via an onclick attribute, e.g:
//   onclick="openEditModal(0, 'House Rent', 'Accommodation', 2000)"
//
// This function:
//   - Sets the edit form's POST action URL to the correct /edit/<index> route
//   - Pre-fills the Description, Category, and Amount input fields
//   - Opens the modal so the user sees their current values ready to change
//
// @param {number} index       - Zero-based position of the expense in the list
// @param {string} description - Current description text of the expense
// @param {string} category    - Current category of the expense
// @param {number} amount      - Current amount of the expense
function openEditModal(index, description, category, amount) {

  // Point the form's action to the correct Flask route for this specific expense.
  // Flask's edit route is: POST /edit/<index>
  document.getElementById('editForm').action = `/edit/${index}`;

  // Pre-fill each input with the expense's existing values so the user
  // only needs to change what they want — not retype everything from scratch
  document.getElementById('editDescription').value = description;
  document.getElementById('editCategory').value = category;
  document.getElementById('editAmount').value = amount;

  // Open the modal overlay (openModal is defined in modals.js)
  openModal('editExpenseModal');
}
// ── End Edit Modal ─────────────────────────────────────────────────────────────


// ── Wait for the full DOM to be ready before querying any elements ────────────
document.addEventListener('DOMContentLoaded', () => {


  // ── 2. TABLE ROW STAGGER ANIMATION ─────────────────────────────────────────
  // When the expenses page loads, each table row slides in and fades up
  // one after another with a small delay between each row.
  // This "cascade" entrance makes the list feel dynamic rather than
  // just appearing all at once as a static block.
  //
  // How it works:
  //   - Every <tr> in the table body starts invisible and shifted down 20px
  //   - We loop through them and apply a CSS transition + inline style change
  //   - Each row gets a slightly longer delay than the previous one (i * 60ms)
  //     creating the staggered waterfall effect
  //   - requestAnimationFrame is used to ensure the browser has painted the
  //     initial "invisible" state before we trigger the transition to "visible"

  const rows = document.querySelectorAll('tbody tr');

  rows.forEach((row, i) => {

    // Start each row invisible and nudged down so it can animate upward
    row.style.opacity = '0';
    row.style.transform = 'translateY(20px)';
    row.style.transition = 'opacity 0.4s ease, transform 0.4s ease';

    // Delay each row's entrance by 60ms more than the previous one
    // Row 0 → 60ms, Row 1 → 120ms, Row 2 → 180ms, etc.
    setTimeout(() => {
      requestAnimationFrame(() => {
        row.style.opacity = '1';
        row.style.transform = 'translateY(0)';
      });
    }, 60 + i * 60);
  });
  // ── End Row Stagger Animation ──────────────────────────────────────────────


  // ── 3. EXPENSE AMOUNT HOVER PULSE ──────────────────────────────────────────
  // When the user hovers over any expense row, the amount in that row
  // briefly scales up and turns red — drawing the eye to the cost.
  //
  // This subtle interaction serves two purposes:
  //   1. Visual feedback — confirms which row is currently selected
  //   2. Emphasis — nudging the user to notice the monetary value
  //
  // We use mouseenter/mouseleave instead of CSS :hover on the <td> so that
  // we can combine the transform scale with a color change in one listener,
  // and reset it cleanly when the mouse leaves.
  //
  // The amount cell is the 4th <td> in each row (index 3), which contains
  // the formatted dollar value like "$2,300.00"

  document.querySelectorAll('tbody tr').forEach(row => {

    // Select the amount cell — 4th column in the expense table
    // (columns: #, Description, Category, Amount, Actions)
    const amountCell = row.querySelector('td:nth-child(4)');

    // Skip rows that don't have an amount cell (e.g. "No expenses" empty state row)
    if (!amountCell) return;

    // When the mouse enters the row — scale up and redden the amount
    row.addEventListener('mouseenter', () => {
      amountCell.style.transition = 'transform 0.15s ease, color 0.15s ease';
      amountCell.style.transform = 'scale(1.15)'; // grow 15% larger
      amountCell.style.color = '#f85149';          // --danger red from main.css
    });

    // When the mouse leaves the row — smoothly return to normal
    row.addEventListener('mouseleave', () => {
      amountCell.style.transform = 'scale(1)';
      amountCell.style.color = '';  // revert to the color defined by CSS
    });
  });
  // ── End Amount Hover Pulse ──────────────────────────────────────────────────

// ── 4. STAT CARD HOVER EFFECTS ────────────────────────────────────────────
// Same hover effect as the dashboard page — lifts each stat card on hover
// with a colored glow matching the card's accent type (green, red, yellow).
//
// The expenses page has 3 stat cards: Monthly Salary, Total Spent, Balance.
// Each gets its own glow color matching its class (green, red, or dynamic).

// Define glow colors matching each card type
const glowColors = {
  green:  'rgba(59, 223, 145, 0.15)',  // --accent green
  red:    'rgba(248, 81, 73, 0.15)',   // --danger red
  yellow: 'rgba(227, 179, 65, 0.15)', // --warning yellow
};

const borderColors = {
  green:  'rgba(59, 223, 145, 0.5)',
  red:    'rgba(248, 81, 73, 0.5)',
  yellow: 'rgba(227, 179, 65, 0.5)',
};

document.querySelectorAll('.stat-card').forEach(card => {

  // Detect which color type this card is (green, red, or yellow)
  const type = ['green', 'red', 'yellow'].find(t => card.classList.contains(t)) || 'green';

  // Set base transition so all property changes animate smoothly
  card.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease, background 0.3s ease';

  // ── Mouse enters the card ──
  card.addEventListener('mouseenter', () => {
    card.style.transform   = 'translateY(-4px)';                                                 // lift up
    card.style.background  = 'var(--surface2)';                                                  // lighten background
    card.style.borderColor = borderColors[type];                                                 // brighten border
    card.style.boxShadow   = `0 8px 30px ${glowColors[type]}, 0 0 0 1px ${borderColors[type]}`; // glow
  });

  // ── Mouse leaves the card ──
  card.addEventListener('mouseleave', () => {
    card.style.transform   = 'translateY(0)';       // return to normal position
    card.style.background  = 'var(--surface)';      // restore original background
    card.style.borderColor = 'var(--border)';       // restore original border
    card.style.boxShadow   = 'none';                // remove glow
  });
});
// ── End Stat Card Hover Effects ───────────────────────────────────────────

}); // End DOMContentLoaded