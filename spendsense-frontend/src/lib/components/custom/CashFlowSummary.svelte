<script lang="ts">
	import { formatCurrency } from '$lib/types';
	import type { Transaction } from '$lib/types';
	import CashFlowChart from './CashFlowChart.svelte';

	// Props
	let { transactions, window = 30 } = $props<{
		transactions: Transaction[];
		window?: number;
	}>();

	// Calculate current period cash flow
	const currentCashFlow = $derived.by(() => {
		// Create cutoff date (start of day, X days ago)
		const now = new Date();
		const windowDate = new Date(now);
		windowDate.setDate(windowDate.getDate() - window);
		// Set to start of day to include full 30 days
		windowDate.setHours(0, 0, 0, 0);

		// Filter transactions within window
		const periodTransactions = transactions.filter((t: Transaction) => {
			const txDate = new Date(t.date);
			return txDate >= windowDate;
		});

		const income = periodTransactions
			.filter((t: Transaction) => t.amount < 0)
			.reduce((sum: number, t: Transaction) => sum + Math.abs(t.amount), 0);

		const expenses = periodTransactions
			.filter((t: Transaction) => t.amount > 0)
			.reduce((sum: number, t: Transaction) => sum + t.amount, 0);

		const net = income - expenses;

		return { income, expenses, net };
	});

	// Get bar width percentages (max 100%)
	const barWidths = $derived.by(() => {
		const { income, expenses } = currentCashFlow;
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
			<div class="metric-label">Income (Last 30 Days)</div>
			<div class="metric-value income-value">{formatCurrency(currentCashFlow.income)}</div>
			<div class="metric-bar">
				<div class="bar-background">
					<div class="bar-fill income-bar" style="width: {barWidths.income}%"></div>
				</div>
			</div>
		</div>

		<!-- Expenses -->
		<div class="metric-card expenses-card">
			<div class="metric-label">Expenses (Last 30 Days)</div>
			<div class="metric-value expenses-value">{formatCurrency(currentCashFlow.expenses)}</div>
			<div class="metric-bar">
				<div class="bar-background">
					<div class="bar-fill expenses-bar" style="width: {barWidths.expenses}%"></div>
				</div>
			</div>
		</div>

		<!-- Net Cash Flow -->
		<div class="metric-card net-card">
			<div class="metric-label">Net Cash Flow (Last 30 Days)</div>
			<div class="metric-value net-value" class:positive={currentCashFlow.net > 0} class:negative={currentCashFlow.net < 0}>
				{currentCashFlow.net > 0 ? '+' : ''}{formatCurrency(currentCashFlow.net)}
			</div>
			<div class="metric-bar">
				<div class="bar-background">
					<div
						class="bar-fill net-bar"
						class:positive={currentCashFlow.net > 0}
						class:negative={currentCashFlow.net < 0}
						style="width: {Math.min(100, Math.abs(currentCashFlow.net) / Math.max(currentCashFlow.income, currentCashFlow.expenses) * 100)}%"
					></div>
				</div>
			</div>
		</div>
	</div>

	<!-- Interactive Cash Flow Chart -->
	<div class="chart-section">
		<CashFlowChart {transactions} />
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

	.chart-section {
		padding-top: 1.5rem;
		margin-top: 1.5rem;
		border-top: 1px solid #e5e7eb; /* gray-200 */
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
