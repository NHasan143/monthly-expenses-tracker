/**
 * monthly_chart.js
 * Renders a D3 bar chart of monthly expenses (Jan–Dec) on the dashboard.
 *
 * Bar color logic:
 *   - GREEN  (#3bdf91) if monthly total ≤ 80% of salary
 *   - RED    (#f85149) if monthly total >  80% of salary
 *
 * Y-axis always spans $1,000 – $10,000 as specified.
 * Fetches data from /api/monthly-expenses (JSON).
 */

(function () {

  const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun',
                  'Jul','Aug','Sep','Oct','Nov','Dec'];

  const COLOR_SAFE   = '#3bdf91';
  const COLOR_DANGER = '#f85149';
  const COLOR_EMPTY  = '#30363d';

  const Y_MIN = 1000;
  const Y_MAX = 50000;

  function renderChart(salary, monthlyData) {
    const container = document.getElementById('monthly-expenses-chart');
    if (!container) return;

    // ── Dimensions ──────────────────────────────────────────────
    const margin = { top: 20, right: 20, bottom: 50, left: 70 };
    const totalW  = container.clientWidth || 800;
    const width   = totalW - margin.left - margin.right;
    const height  = 320 - margin.top - margin.bottom;

    // Remove any existing SVG (e.g. on resize/refresh)
    d3.select('#monthly-expenses-chart svg').remove();

    // ── SVG canvas ───────────────────────────────────────────────
    const svg = d3.select('#monthly-expenses-chart')
      .append('svg')
        .attr('width',  width  + margin.left + margin.right)
        .attr('height', height + margin.top  + margin.bottom)
      .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // ── Scales ───────────────────────────────────────────────────
    const x = d3.scaleBand()
      .domain(MONTHS)
      .range([0, width])
      .padding(0.3);

    const y = d3.scaleLinear()
      .domain([Y_MIN, Y_MAX])
      .range([height, 0])
      .clamp(true);   // values outside domain won't bleed off chart

    // ── Threshold line at 90% of salary ─────────────────────────
    const threshold = salary * 0.90;
    const thresholdClamped = Math.min(Math.max(threshold, Y_MIN), Y_MAX);

    if (salary > 0 && thresholdClamped > Y_MIN && thresholdClamped < Y_MAX) {
      // Dashed red threshold line
      svg.append('line')
        .attr('x1', 0).attr('x2', width)
        .attr('y1', y(thresholdClamped)).attr('y2', y(thresholdClamped))
        .attr('stroke', COLOR_DANGER)
        .attr('stroke-width', 1.5)
        .attr('stroke-dasharray', '6 4')
        .attr('opacity', 0.6);

      // Label for the threshold line
      svg.append('text')
        .attr('x', width - 4)
        .attr('y', y(thresholdClamped) - 6)
        .attr('text-anchor', 'end')
        .attr('fill', COLOR_DANGER)
        .attr('font-size', '11px')
        .attr('font-family', 'DM Sans, sans-serif')
        .text(`90% limit ($${thresholdClamped.toLocaleString()})`);
    }

    // ── X Axis ───────────────────────────────────────────────────
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).tickSize(0))
      .call(g => g.select('.domain').attr('stroke', '#30363d'))
      .call(g => g.selectAll('text')
        .attr('fill', '#8b949e')
        .attr('font-size', '12px')
        .attr('font-family', 'DM Sans, sans-serif')
        .attr('dy', '1.2em'));

    // ── Y Axis ───────────────────────────────────────────────────
    svg.append('g')
      .call(
        d3.axisLeft(y)
          .tickValues([1000, 5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000])
          .tickFormat(d => `$${(d / 1000).toFixed(0)}k`)
          .tickSize(-width)        // extend ticks across as grid lines
      )
      .call(g => g.select('.domain').remove())
      .call(g => g.selectAll('.tick line')
        .attr('stroke', '#21262d')
        .attr('stroke-dasharray', '3 3'))
      .call(g => g.selectAll('text')
        .attr('fill', '#8b949e')
        .attr('font-size', '11px')
        .attr('font-family', 'DM Sans, sans-serif')
        .attr('dx', '-4px'));

    // ── Tooltip ──────────────────────────────────────────────────
    const tooltip = d3.select('body')
      .append('div')
      .attr('id', 'd3-tooltip')
      .style('position',   'fixed')
      .style('background', '#1c2333')
      .style('border',     '1px solid #30363d')
      .style('border-radius', '8px')
      .style('padding',    '10px 14px')
      .style('font-size',  '13px')
      .style('font-family','DM Sans, sans-serif')
      .style('color',      '#e6edf3')
      .style('pointer-events', 'none')
      .style('opacity',    0)
      .style('z-index',    9999);

    // ── Bars ─────────────────────────────────────────────────────
    const bars = svg.selectAll('.bar')
      .data(monthlyData)
      .join('rect')
        .attr('class', 'bar')
        .attr('x',     d => x(MONTHS[d.month - 1]))
        .attr('width', x.bandwidth())
        .attr('rx', 4)  // rounded top corners
        .attr('ry', 4)
        // Start from bottom for animation
        .attr('y',      height)
        .attr('height', 0)
        .attr('fill', d => {
          if (d.total === 0)             return COLOR_EMPTY;
          if (salary > 0 && d.total > threshold) return COLOR_DANGER;
          return COLOR_SAFE;
        })
        .attr('opacity', d => d.total === 0 ? 0.3 : 0.85)
        .style('cursor', 'pointer');

    // ── Animate bars up on load ───────────────────────────────────
    bars.transition()
      .duration(800)
      .delay((d, i) => i * 60)
      .ease(d3.easeCubicOut)
      .attr('y',      d => {
        const clamped = Math.min(Math.max(d.total, Y_MIN), Y_MAX);
        return d.total === 0 ? height - 4 : y(clamped);
      })
      .attr('height', d => {
        if (d.total === 0) return 4;
        const clamped = Math.min(Math.max(d.total, Y_MIN), Y_MAX);
        return height - y(clamped);
      });

    // ── Tooltip interactions ─────────────────────────────────────
    bars
      .on('mouseover', function (event, d) {
        const overThreshold = salary > 0 && d.total > threshold;
        d3.select(this)
          .transition().duration(100)
          .attr('opacity', 1)
          .attr('filter', 'brightness(1.2)');

        tooltip
          .style('opacity', 1)
          .html(`
            <div style="font-weight:700; margin-bottom:4px; color:${d.total === 0 ? '#8b949e' : overThreshold ? COLOR_DANGER : COLOR_SAFE}">
              ${MONTHS[d.month - 1]}
            </div>
            <div>Spent: <strong>$${d.total.toLocaleString('en-US', {minimumFractionDigits: 2})}</strong></div>
            ${salary > 0 ? `<div style="color:#8b949e; font-size:11px; margin-top:4px;">${((d.total / salary) * 100).toFixed(1)}% of salary</div>` : ''}
            ${overThreshold ? `<div style="color:${COLOR_DANGER}; font-size:11px; margin-top:2px;">⚠ Over 90% limit</div>` : ''}
          `);
      })
      .on('mousemove', function (event) {
        tooltip
          .style('left', (event.clientX + 14) + 'px')
          .style('top',  (event.clientY - 40) + 'px');
      })
      .on('mouseleave', function (event, d) {
        d3.select(this)
          .transition().duration(150)
          .attr('opacity', d.total === 0 ? 0.3 : 0.85)
          .attr('filter', 'none');

        tooltip.style('opacity', 0);
      });

    // ── Value labels on top of each bar ──────────────────────────
    svg.selectAll('.bar-label')
      .data(monthlyData.filter(d => d.total > 0))
      .join('text')
        .attr('class', 'bar-label')
        .attr('text-anchor', 'middle')
        .attr('x', d => x(MONTHS[d.month - 1]) + x.bandwidth() / 2)
        .attr('fill', '#8b949e')
        .attr('font-size', '10px')
        .attr('font-family', 'DM Sans, sans-serif')
        // Appear after bar animation
        .attr('opacity', 0)
        .attr('y', d => {
          const clamped = Math.min(Math.max(d.total, Y_MIN), Y_MAX);
          return y(clamped) - 6;
        })
        .text(d => `$${(d.total / 1000).toFixed(1)}k`)
        .transition()
          .delay((d, i) => 800 + i * 60)
          .duration(300)
          .attr('opacity', 1);

    // Clean up tooltip on page unload
    window.addEventListener('beforeunload', () => {
      document.getElementById('d3-tooltip')?.remove();
    });
  }

  // ── Fetch data and render ─────────────────────────────────────
  async function init() {
    try {
      const res  = await fetch('/api/monthly-expenses');
      const json = await res.json();
      renderChart(json.salary, json.monthly);
    } catch (err) {
      console.error('Monthly chart error:', err);
    }
  }

  document.addEventListener('DOMContentLoaded', init);

  // Re-render on window resize (debounced)
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(init, 250);
  });

})();