/**
 * expenses.js — populates and opens the edit modal on the Expenses page.
 * Depends on modals.js (openModal) being loaded first via base.html.
 */

function openEditModal(index, description, category, amount) {
  document.getElementById('editForm').action = `/edit/${index}`;
  document.getElementById('editDescription').value = description;
  document.getElementById('editCategory').value = category;
  document.getElementById('editAmount').value = amount;
  openModal('editExpenseModal');
}
