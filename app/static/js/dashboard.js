/**
 * dashboard.js — Chart.js doughnut chart for the dashboard page.
 *
 * Depends on window.CATEGORY_DATA being set by a small inline <script> in
 * dashboard.html before this file is loaded. That inline script is the only
 * place Jinja template data crosses into JavaScript.
 */

const PALETTE = ['#3bdf91', '#58a6ff', '#e3b341', '#f85149', '#bc8cff', '#79c0ff'];

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('expenseChart');
  if (!canvas || !window.CATEGORY_DATA) return;

  const labels = Object.keys(window.CATEGORY_DATA);
  const values = Object.values(window.CATEGORY_DATA);

  new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: PALETTE.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#161b22',
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#8b949e',
            font: { family: 'DM Sans', size: 12 },
            padding: 16,
            usePointStyle: true,
            pointStyleWidth: 8
          }
        },
        tooltip: {
          callbacks: {
            label: ctx => ` $${ctx.parsed.toFixed(2)}`
          }
        }
      }
    }
  });
});
