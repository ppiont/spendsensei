<script lang="ts">
	import { formatCurrency } from '$lib/types';
	import type { Transaction } from '$lib/types';

	// Props
	let { transactions } = $props<{ transactions: Transaction[] }>();

	// State
	let activeView = $state<'net' | 'income' | 'expenses'>('net');
	let hoveredIndex = $state<number | null>(null);
	let chartWidth = $state(600);
	let tooltipX = $state(0);
	let tooltipY = $state(0);

	// Constants
	const CHART_HEIGHT = 240;
	const PADDING = { top: 20, right: 20, bottom: 40, left: 60 };

	// Derived chart dimensions
	const chartAreaWidth = $derived(chartWidth - PADDING.left - PADDING.right);
	const chartAreaHeight = CHART_HEIGHT - PADDING.top - PADDING.bottom;

	// Types
	interface MonthlyData {
		month: string;
		date: Date;
		income: number;
		expenses: number;
		netFlow: number;
	}

	// === DATA AGGREGATION ===
	const monthlyData = $derived.by(() => {
		const now = new Date();
		const months: MonthlyData[] = [];

		// Generate last 6 COMPLETE months (exclude current partial month)
		for (let i = 6; i >= 1; i--) {
			const monthDate = new Date(now.getFullYear(), now.getMonth() - i, 1);
			const monthEnd = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0);

			// Filter transactions for this month
			const monthTransactions = transactions.filter((t) => {
				const tDate = new Date(t.date);
				return tDate >= monthDate && tDate <= monthEnd;
			});

			// Calculate income (negative amounts in Plaid = money in)
			const income = monthTransactions
				.filter((t) => t.amount < 0)
				.reduce((sum, t) => sum + Math.abs(t.amount), 0);

			// Calculate expenses (positive amounts)
			const expenses = monthTransactions
				.filter((t) => t.amount > 0)
				.reduce((sum, t) => sum + t.amount, 0);

			months.push({
				month: monthDate.toLocaleDateString('en-US', { month: 'short' }).toUpperCase(),
				date: monthDate,
				income,
				expenses,
				netFlow: income - expenses
			});
		}

		return months;
	});

	// === Y-AXIS SCALING ===
	// Use FIXED scale across all views for consistency
	const yAxisBounds = $derived.by(() => {
		if (monthlyData.length === 0) return { min: 0, max: 0, ticks: [] };

		// Collect ALL values from all three views
		const allValues: number[] = [];
		monthlyData.forEach((d) => {
			allValues.push(d.netFlow, d.income, d.expenses);
		});

		const max = Math.max(...allValues, 0);
		const min = Math.min(...allValues, 0);

		// Add 20% padding
		const range = max - min || 1;
		const padding = range * 0.2;

		const adjustedMax = max + padding;
		const adjustedMin = min - padding;

		// Generate 5 tick marks
		const ticks = generateTicks(adjustedMin, adjustedMax, 5);

		return { min: adjustedMin, max: adjustedMax, ticks };
	});

	function generateTicks(min: number, max: number, count: number): number[] {
		const range = max - min;
		const rawStep = range / (count - 1);

		// Round to nice numbers
		const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)));
		const niceStep = Math.ceil(rawStep / magnitude) * magnitude;

		const ticks: number[] = [];
		const start = Math.floor(min / niceStep) * niceStep;

		for (let i = 0; i < count; i++) {
			ticks.push(start + i * niceStep);
		}

		return ticks;
	}

	// Scale value to Y coordinate
	function scaleY(value: number): number {
		const { min, max } = yAxisBounds;
		if (max === min) return chartAreaHeight / 2;
		const normalized = (value - min) / (max - min);
		return chartAreaHeight - normalized * chartAreaHeight;
	}

	// Scale X coordinate
	function scaleX(index: number): number {
		const count = monthlyData.length;
		if (count <= 1) return 0;
		return (index / (count - 1)) * chartAreaWidth;
	}

	// === PATH GENERATION ===
	const linePath = $derived.by(() => {
		if (monthlyData.length === 0) return '';

		const points = monthlyData.map((d, i) => {
			const x = scaleX(i);
			const value = activeView === 'net' ? d.netFlow : activeView === 'income' ? d.income : d.expenses;
			const y = scaleY(value);
			return `${x},${y}`;
		});

		return `M ${points.join(' L ')}`;
	});

	const areaPath = $derived.by(() => {
		if (monthlyData.length === 0) return '';

		const zeroY = scaleY(0);
		const firstX = scaleX(0);
		const lastX = scaleX(monthlyData.length - 1);

		// Close the path at zero line
		return `${linePath} L ${lastX},${zeroY} L ${firstX},${zeroY} Z`;
	});

	// === COLORS ===
	const colors = $derived.by(() => {
		switch (activeView) {
			case 'net':
				return {
					line: '#3b82f6',
					fill: 'rgba(59, 130, 246, 0.15)'
				};
			case 'income':
				return {
					line: '#10b981',
					fill: 'rgba(16, 185, 129, 0.15)'
				};
			case 'expenses':
				return {
					line: '#f87171',
					fill: 'rgba(248, 113, 113, 0.15)'
				};
		}
	});

	// === INTERACTIVITY ===
	function handleMouseMove(event: MouseEvent) {
		if (monthlyData.length === 0) return;

		const svgRect = (event.currentTarget as SVGElement).getBoundingClientRect();
		const mouseX = event.clientX - svgRect.left - PADDING.left;

		// Find nearest data point
		const index = Math.round((mouseX / chartAreaWidth) * (monthlyData.length - 1));
		const clampedIndex = Math.max(0, Math.min(monthlyData.length - 1, index));

		hoveredIndex = clampedIndex;

		// Position tooltip
		const dataX = scaleX(clampedIndex) + PADDING.left;
		const data = monthlyData[clampedIndex];
		const dataY =
			scaleY(activeView === 'net' ? data.netFlow : activeView === 'income' ? data.income : data.expenses) +
			PADDING.top;

		tooltipX = dataX;
		tooltipY = dataY - 80; // Above the point
	}

	function handleMouseLeave() {
		hoveredIndex = null;
	}

	function handleToggle(view: 'net' | 'income' | 'expenses') {
		activeView = view;
	}

	// === CURRENCY FORMATTING ===
	function formatCurrencyShort(cents: number): string {
		const dollars = cents / 100;
		const abs = Math.abs(dollars);

		if (abs >= 1000) {
			return `${dollars < 0 ? '-' : ''}$${(abs / 1000).toFixed(1)}K`;
		}
		return `${dollars < 0 ? '-' : ''}$${abs.toFixed(0)}`;
	}

	// === INSIGHTS ===
	const insight = $derived.by(() => {
		if (monthlyData.length < 2) return 'Not enough data for insights';

		const firstMonth = monthlyData[0];
		const lastMonth = monthlyData[monthlyData.length - 1];

		switch (activeView) {
			case 'net': {
				const change = lastMonth.netFlow - firstMonth.netFlow;
				const percentChange =
					firstMonth.netFlow !== 0 ? ((change / Math.abs(firstMonth.netFlow)) * 100).toFixed(0) : '0';

				if (change > 0) {
					return `Your cash flow improved by ${formatCurrency(Math.abs(change))} (${percentChange}%) since ${firstMonth.month}`;
				} else if (change < 0) {
					return `Your cash flow decreased by ${formatCurrency(Math.abs(change))} (${percentChange}%) since ${firstMonth.month}`;
				} else {
					return `Your cash flow has remained steady over the last 6 months`;
				}
			}
			case 'income': {
				const avg = monthlyData.reduce((sum, d) => sum + d.income, 0) / monthlyData.length;
				return `Your average monthly income is ${formatCurrency(avg)}`;
			}
			case 'expenses': {
				const avg = monthlyData.reduce((sum, d) => sum + d.expenses, 0) / monthlyData.length;
				const maxMonth = monthlyData.reduce((max, d) => (d.expenses > max.expenses ? d : max));
				return `Average monthly expenses: ${formatCurrency(avg)} (highest in ${maxMonth.month})`;
			}
		}
	});

	// Zero line Y position
	const zeroY = $derived(scaleY(0) + PADDING.top);
</script>

<div class="cash-flow-chart">
	<!-- Chart Title -->
	<div class="chart-header">
		<h3 class="chart-title">Cash Flow Trends</h3>
	</div>

	<!-- SVG Chart -->
	<div class="chart-container" bind:clientWidth={chartWidth}>
		<svg
			width={chartWidth}
			height={CHART_HEIGHT}
			onmousemove={handleMouseMove}
			onmouseleave={handleMouseLeave}
			role="img"
			aria-label="Cash flow trends over the last 6 months"
		>
			<g transform="translate({PADDING.left}, {PADDING.top})">
				<!-- Grid lines and Y-axis labels -->
				{#each yAxisBounds.ticks as tick}
					<line
						x1="0"
						y1={scaleY(tick)}
						x2={chartAreaWidth}
						y2={scaleY(tick)}
						stroke="#e5e7eb"
						stroke-width="1"
					/>
					<text
						x="-10"
						y={scaleY(tick)}
						text-anchor="end"
						dominant-baseline="middle"
						class="axis-label"
					>
						{formatCurrencyShort(tick)}
					</text>
				{/each}

				<!-- Zero line (emphasized) -->
				<line
					x1="0"
					y1={scaleY(0)}
					x2={chartAreaWidth}
					y2={scaleY(0)}
					stroke="#9ca3af"
					stroke-width="2"
					stroke-dasharray="4,4"
				/>

				<!-- Area fill -->
				<path d={areaPath} fill={colors.fill} class="area-path" />

				<!-- Line -->
				<path d={linePath} fill="none" stroke={colors.line} stroke-width="2.5" class="line-path" />

				<!-- Hover elements -->
				{#if hoveredIndex !== null}
					{@const data = monthlyData[hoveredIndex]}
					{@const x = scaleX(hoveredIndex)}
					{@const y = scaleY(
						activeView === 'net' ? data.netFlow : activeView === 'income' ? data.income : data.expenses
					)}

					<!-- Crosshair -->
					<line x1={x} y1="0" x2={x} y2={chartAreaHeight} stroke="#9ca3af" stroke-width="1" opacity="0.5" />

					<!-- Hover point -->
					<circle cx={x} cy={y} r="5" fill="white" stroke={colors.line} stroke-width="2.5" />
				{/if}

				<!-- X-axis labels -->
				{#each monthlyData as month, i}
					<text
						x={scaleX(i)}
						y={chartAreaHeight + 20}
						text-anchor={i === 0 ? 'start' : i === monthlyData.length - 1 ? 'end' : 'middle'}
						class="axis-label month-label"
					>
						{month.month}
					</text>
				{/each}
			</g>
		</svg>

		<!-- Tooltip -->
		{#if hoveredIndex !== null}
			{@const data = monthlyData[hoveredIndex]}
			<div
				class="tooltip"
				style="left: {tooltipX}px; top: {tooltipY}px;"
				role="tooltip"
			>
				<div class="tooltip-month">{data.month} {data.date.getFullYear()}</div>
				<div class="tooltip-divider"></div>
				<div class="tooltip-row net">
					<span class="tooltip-label">Net Flow</span>
					<span class="tooltip-value" class:positive={data.netFlow > 0} class:negative={data.netFlow < 0}>
						{data.netFlow > 0 ? '+' : ''}{formatCurrency(data.netFlow)}
					</span>
				</div>
				<div class="tooltip-row income">
					<span class="tooltip-label">Income</span>
					<span class="tooltip-value">{formatCurrency(data.income)}</span>
				</div>
				<div class="tooltip-row expenses">
					<span class="tooltip-label">Expenses</span>
					<span class="tooltip-value">{formatCurrency(data.expenses)}</span>
				</div>
			</div>
		{/if}
	</div>

	<!-- Legend / Toggle Controls -->
	<div class="legend" role="group" aria-label="Chart view selector">
		<button
			onclick={() => handleToggle('net')}
			class="legend-button"
			class:active={activeView === 'net'}
			aria-pressed={activeView === 'net'}
		>
			<span class="indicator net"></span>
			Net Flow
		</button>
		<button
			onclick={() => handleToggle('income')}
			class="legend-button"
			class:active={activeView === 'income'}
			aria-pressed={activeView === 'income'}
		>
			<span class="indicator income"></span>
			Income
		</button>
		<button
			onclick={() => handleToggle('expenses')}
			class="legend-button"
			class:active={activeView === 'expenses'}
			aria-pressed={activeView === 'expenses'}
		>
			<span class="indicator expenses"></span>
			Expenses
		</button>
	</div>

	<!-- Insight Badge -->
	<div class="insight-badge">
		<span class="insight-icon">💡</span>
		<span class="insight-text">{insight}</span>
	</div>
</div>

<style>
	.cash-flow-chart {
		width: 100%;
	}

	.chart-header {
		margin-bottom: 1rem;
	}

	.chart-title {
		font-size: 1rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0;
	}

	.chart-container {
		position: relative;
		width: 100%;
		margin-bottom: 1rem;
	}

	svg {
		display: block;
		overflow: visible;
	}

	.axis-label {
		font-size: 0.75rem;
		font-weight: 500;
		color: #6b7280;
		font-variant-numeric: tabular-nums;
		user-select: none;
	}

	.month-label {
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.area-path {
		transition: fill 0.3s ease-in-out;
	}

	.line-path {
		transition:
			stroke 0.3s ease-in-out,
			d 0.3s ease-in-out;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	/* Tooltip */
	.tooltip {
		position: absolute;
		background: #1f2937;
		color: white;
		padding: 0.75rem;
		border-radius: 0.5rem;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
		pointer-events: none;
		transform: translateX(-50%);
		min-width: 180px;
		z-index: 10;
	}

	.tooltip-month {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #9ca3af;
		margin-bottom: 0.5rem;
	}

	.tooltip-divider {
		height: 1px;
		background: #374151;
		margin-bottom: 0.5rem;
	}

	.tooltip-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		margin-bottom: 0.25rem;
		font-size: 0.875rem;
	}

	.tooltip-row:last-child {
		margin-bottom: 0;
	}

	.tooltip-label {
		color: #d1d5db;
		font-weight: 500;
	}

	.tooltip-value {
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: white;
	}

	.tooltip-value.positive {
		color: #10b981;
	}

	.tooltip-value.negative {
		color: #f87171;
	}

	/* Legend */
	.legend {
		display: flex;
		justify-content: center;
		gap: 1rem;
		padding: 0.75rem;
		background: #f9fafb;
		border-radius: 0.5rem;
		margin-bottom: 1rem;
	}

	.legend-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: white;
		border: 2px solid transparent;
		border-radius: 0.375rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: #6b7280;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.legend-button:hover {
		border-color: #e5e7eb;
		color: #374151;
	}

	.legend-button.active {
		border-color: #3b82f6;
		color: #1f2937;
		font-weight: 600;
	}

	.legend-button:focus-visible {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	.indicator {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.indicator.net {
		background: #3b82f6;
	}

	.indicator.income {
		background: #10b981;
	}

	.indicator.expenses {
		background: #f87171;
	}

	/* Insight Badge */
	.insight-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
		border-left: 4px solid #3b82f6;
		border-radius: 0.5rem;
	}

	.insight-icon {
		font-size: 1.25rem;
		flex-shrink: 0;
	}

	.insight-text {
		font-size: 0.875rem;
		color: #1e40af;
		line-height: 1.5;
		font-weight: 500;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.chart-title {
			font-size: 0.875rem;
		}

		.legend {
			flex-direction: column;
			gap: 0.5rem;
		}

		.legend-button {
			justify-content: center;
		}

		.tooltip {
			min-width: 150px;
			font-size: 0.75rem;
		}

		.insight-badge {
			flex-direction: column;
			text-align: center;
		}
	}
</style>
