<script lang="ts">
	import { formatCurrency } from '$lib/types';
	import type { Transaction } from '$lib/types';

	// Props
	let { transactions, window = 30 } = $props<{
		transactions: Transaction[];
		window?: number;
	}>();

	// Calculate current period cash flow
	const currentCashFlow = $derived(() => {
		const windowDate = new Date();
		windowDate.setDate(windowDate.getDate() - window);

		const periodTransactions = transactions.filter((t) => new Date(t.date) >= windowDate);

		const income = periodTransactions
			.filter((t) => t.amount < 0)
			.reduce((sum, t) => sum + Math.abs(t.amount), 0);

		const expenses = periodTransactions
			.filter((t) => t.amount > 0)
			.reduce((sum, t) => sum + t.amount, 0);

		const net = income - expenses;

		return { income, expenses, net };
	});

	// Calculate last 6 months trend for sparkline
	const monthlyTrend = $derived(() => {
		const months: number[] = [];

		for (let i = 5; i >= 0; i--) {
			const endDate = new Date();
			endDate.setMonth(endDate.getMonth() - i);
			endDate.setDate(1);
			const startDate = new Date(endDate);
			startDate.setMonth(startDate.getMonth() - 1);

			const monthTransactions = transactions.filter((t) => {
				const tDate = new Date(t.date);
				return tDate >= startDate && tDate < endDate;
			});

			const income = monthTransactions
				.filter((t) => t.amount < 0)
				.reduce((sum, t) => sum + Math.abs(t.amount), 0);

			const expenses = monthTransactions
				.filter((t) => t.amount > 0)
				.reduce((sum, t) => sum + t.amount, 0);

			months.push(income - expenses);
		}

		return months;
	});

	// Generate SVG sparkline path
	const sparklinePath = $derived(() => {
		const data = monthlyTrend();
		if (data.length === 0) return '';

		const width = 200;
		const height = 40;
		const padding = 4;

		const max = Math.max(...data.map(Math.abs));
		const min = Math.min(...data);

		if (max === 0) {
			// Flat line at middle
			return `M 0,${height / 2} L ${width},${height / 2}`;
		}

		const points = data.map((value, index) => {
			const x = (index / (data.length - 1)) * width;
			// Normalize to 0-1 range, then scale to height with padding
			const normalized = (value - min) / (max - min || 1);
			const y = height - padding - normalized * (height - padding * 2);
			return `${x.toFixed(2)},${y.toFixed(2)}`;
		});

		return `M ${points.join(' L ')}`;
	});

	// Get bar width percentages (max 100%)
	const barWidths = $derived(() => {
		const { income, expenses } = currentCashFlow();
		const max = Math.max(income, expenses);

		return {
			income: max > 0 ? (income / max) * 100 : 0,
			expenses: max > 0 ? (expenses / max) * 100 : 0
		};
	});
</script>

<div class="cash-flow-summary">
	<!-- Main metrics -->
	<div class="metrics-grid">
		<!-- Income -->
		<div class="metric-card income-card">
			<div class="metric-label">Income</div>
			<div class="metric-value income-value">{formatCurrency(currentCashFlow().income)}</div>
			<div class="metric-bar">
				<div class="bar-background">
					<div class="bar-fill income-bar" style="width: {barWidths().income}%"></div>
				</div>
			</div>
		</div>

		<!-- Expenses -->
		<div class="metric-card expenses-card">
			<div class="metric-label">Expenses</div>
			<div class="metric-value expenses-value">{formatCurrency(currentCashFlow().expenses)}</div>
			<div class="metric-bar">
				<div class="bar-background">
					<div class="bar-fill expenses-bar" style="width: {barWidths().expenses}%"></div>
				</div>
			</div>
		</div>

		<!-- Net Cash Flow -->
		<div class="metric-card net-card">
			<div class="metric-label">Net Cash Flow</div>
			<div class="metric-value net-value" class:positive={currentCashFlow().net > 0} class:negative={currentCashFlow().net < 0}>
				{currentCashFlow().net > 0 ? '+' : ''}{formatCurrency(currentCashFlow().net)}
			</div>
			<div class="metric-bar">
				<div class="bar-background">
					<div
						class="bar-fill net-bar"
						class:positive={currentCashFlow().net > 0}
						class:negative={currentCashFlow().net < 0}
						style="width: {Math.min(100, Math.abs(currentCashFlow().net) / Math.max(currentCashFlow().income, currentCashFlow().expenses) * 100)}%"
					></div>
				</div>
			</div>
		</div>
	</div>

	<!-- Sparkline trend -->
	<div class="trend-section">
		<div class="trend-header">
			<span class="trend-label">Last 6 Months Trend</span>
		</div>
		<div class="sparkline-container">
			<svg width="200" height="40" class="sparkline">
				<!-- Zero line -->
				<line x1="0" y1="20" x2="200" y2="20" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="2,2" />
				<!-- Path -->
				<path
					d={sparklinePath()}
					fill="none"
					stroke="#3b82f6"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</div>
	</div>
</div>

<style>
	.cash-flow-summary {
		width: 100%;
	}

	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.metric-card {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.metric-label {
		font-size: 0.75rem;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #6b7280; /* gray-500 */
	}

	.metric-value {
		font-size: 1.5rem;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
	}

	.income-value {
		color: #10b981; /* brand-green */
	}

	.expenses-value {
		color: #f87171; /* brand-coral */
	}

	.net-value {
		color: #3b82f6; /* brand-blue */
	}

	.net-value.positive {
		color: #10b981; /* brand-green */
	}

	.net-value.negative {
		color: #f87171; /* brand-coral */
	}

	.metric-bar {
		margin-top: 0.25rem;
	}

	.bar-background {
		width: 100%;
		height: 8px;
		background-color: #f3f4f6; /* gray-100 */
		border-radius: 9999px;
		overflow: hidden;
	}

	.bar-fill {
		height: 100%;
		border-radius: 9999px;
		transition: width 0.3s ease;
	}

	.income-bar {
		background-color: #10b981; /* brand-green */
	}

	.expenses-bar {
		background-color: #f87171; /* brand-coral */
	}

	.net-bar {
		background-color: #3b82f6; /* brand-blue */
	}

	.net-bar.positive {
		background-color: #10b981; /* brand-green */
	}

	.net-bar.negative {
		background-color: #f87171; /* brand-coral */
	}

	.trend-section {
		padding-top: 1.5rem;
		border-top: 1px solid #e5e7eb; /* gray-200 */
	}

	.trend-header {
		margin-bottom: 0.75rem;
	}

	.trend-label {
		font-size: 0.75rem;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #6b7280; /* gray-500 */
	}

	.sparkline-container {
		display: flex;
		justify-content: center;
	}

	.sparkline {
		display: block;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.metrics-grid {
			grid-template-columns: 1fr;
			gap: 1.25rem;
		}

		.metric-value {
			font-size: 1.25rem;
		}
	}
</style>
