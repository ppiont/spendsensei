<script lang="ts">
	import { formatCurrency, formatCategory } from '$lib/types';
	import type { Transaction } from '$lib/types';
	import { TrendingUp, TrendingDown, Minus } from '@lucide/svelte';

	// Props
	let { transactions, window = 30 } = $props<{
		transactions: Transaction[];
		window?: number;
	}>();

	// Calculate category spending
	const categorySpending = $derived(() => {
		// Filter to only expenses (positive amounts) in the window
		const windowDate = new Date();
		windowDate.setDate(windowDate.getDate() - window);

		const expenses = transactions.filter(
			(t) => t.amount > 0 && new Date(t.date) >= windowDate
		);

		// Group by category
		const groups = new Map<string, number>();
		expenses.forEach((t) => {
			const category = t.personal_finance_category_primary;
			groups.set(category, (groups.get(category) || 0) + t.amount);
		});

		// Calculate total
		const total = Array.from(groups.values()).reduce((sum, amount) => sum + amount, 0);

		// Convert to array and sort by amount
		const categories = Array.from(groups.entries())
			.map(([category, amount]) => ({
				category,
				amount,
				percentage: total > 0 ? (amount / total) * 100 : 0
			}))
			.sort((a, b) => b.amount - a.amount)
			.slice(0, 5); // Top 5

		return { categories, total };
	});

	// Calculate previous period for comparison
	const previousPeriodSpending = $derived(() => {
		const previousWindowDate = new Date();
		previousWindowDate.setDate(previousWindowDate.getDate() - window * 2);
		const currentWindowDate = new Date();
		currentWindowDate.setDate(currentWindowDate.getDate() - window);

		const previousExpenses = transactions.filter(
			(t) =>
				t.amount > 0 &&
				new Date(t.date) >= previousWindowDate &&
				new Date(t.date) < currentWindowDate
		);

		const groups = new Map<string, number>();
		previousExpenses.forEach((t) => {
			const category = t.personal_finance_category_primary;
			groups.set(category, (groups.get(category) || 0) + t.amount);
		});

		return groups;
	});

	// Get trend for a category
	function getTrend(category: string, currentAmount: number): {
		direction: 'up' | 'down' | 'flat';
		percentage: number;
	} {
		const previousAmount = previousPeriodSpending().get(category) || 0;

		if (previousAmount === 0) {
			return { direction: 'flat', percentage: 0 };
		}

		const change = ((currentAmount - previousAmount) / previousAmount) * 100;

		if (Math.abs(change) < 5) {
			return { direction: 'flat', percentage: 0 };
		}

		return {
			direction: change > 0 ? 'up' : 'down',
			percentage: Math.abs(change)
		};
	}

	// Get insight (top spending increase)
	const insight = $derived(() => {
		const { categories } = categorySpending();
		if (categories.length === 0) return null;

		let maxIncrease = 0;
		let maxIncreaseCategory = '';

		categories.forEach(({ category, amount }) => {
			const trend = getTrend(category, amount);
			if (trend.direction === 'up' && trend.percentage > maxIncrease) {
				maxIncrease = trend.percentage;
				maxIncreaseCategory = category;
			}
		});

		if (maxIncrease > 20) {
			return {
				category: formatCategory(maxIncreaseCategory),
				percentage: Math.round(maxIncrease)
			};
		}

		return null;
	});
</script>

<div class="spending-breakdown">
	{#if categorySpending().categories.length === 0}
		<div class="empty-state">
			<p class="text-gray-500 text-sm">No expense data available for this period</p>
		</div>
	{:else}
		<!-- Insight bubble (if applicable) -->
		{#if insight()}
			<div class="insight-bubble">
				<span class="insight-icon">💡</span>
				<span class="insight-text">
					You spent <strong>{insight()?.percentage}% more</strong> on {insight()?.category} this period
				</span>
			</div>
		{/if}

		<!-- Category bars -->
		<div class="categories-list">
			{#each categorySpending().categories as { category, amount, percentage }}
				{@const trend = getTrend(category, amount)}
				<div class="category-row">
					<!-- Category name -->
					<div class="category-name">
						{formatCategory(category)}
					</div>

					<!-- Bar -->
					<div class="bar-container">
						<div class="bar-background">
							<div class="bar-fill" style="width: {percentage}%"></div>
						</div>
					</div>

					<!-- Stats -->
					<div class="category-stats">
						<span class="percentage">{percentage.toFixed(0)}%</span>
						<span class="amount">{formatCurrency(amount)}</span>
						<span class="trend">
							{#if trend.direction === 'up'}
								<TrendingUp class="w-3 h-3 text-brand-coral" />
								<span class="trend-text text-brand-coral">+{trend.percentage.toFixed(0)}%</span>
							{:else if trend.direction === 'down'}
								<TrendingDown class="w-3 h-3 text-brand-green" />
								<span class="trend-text text-brand-green">-{trend.percentage.toFixed(0)}%</span>
							{:else}
								<Minus class="w-3 h-3 text-gray-400" />
								<span class="trend-text text-gray-400">0%</span>
							{/if}
						</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.spending-breakdown {
		width: 100%;
	}

	.empty-state {
		text-align: center;
		padding: 2rem;
	}

	.insight-bubble {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		background: linear-gradient(to right, #eff6ff, #f0fdf4); /* blue-50 to green-50 */
		border-left: 3px solid #3b82f6; /* brand-blue */
		border-radius: 0.5rem;
		margin-bottom: 1.5rem;
	}

	.insight-icon {
		font-size: 1.25rem;
		flex-shrink: 0;
	}

	.insight-text {
		font-size: 0.875rem;
		color: #374151; /* gray-700 */
		line-height: 1.5;
	}

	.insight-text strong {
		color: #1f2937; /* gray-800 */
		font-weight: 600;
	}

	.categories-list {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.category-row {
		display: grid;
		grid-template-columns: minmax(120px, 1fr) 2fr 200px;
		gap: 1rem;
		align-items: center;
	}

	.category-name {
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151; /* gray-700 */
	}

	.bar-container {
		width: 100%;
	}

	.bar-background {
		width: 100%;
		height: 24px;
		background-color: #f3f4f6; /* gray-100 */
		border-radius: 9999px;
		overflow: hidden;
		position: relative;
	}

	.bar-fill {
		height: 100%;
		background: linear-gradient(to right, #3b82f6, #60a5fa); /* brand-blue gradient */
		border-radius: 9999px;
		transition: width 0.3s ease;
	}

	.category-stats {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		justify-content: flex-end;
	}

	.percentage {
		font-size: 0.75rem;
		color: #6b7280; /* gray-500 */
		font-variant-numeric: tabular-nums;
		min-width: 40px;
		width: 40px;
		text-align: right;
		flex-shrink: 0;
	}

	.amount {
		font-size: 0.875rem;
		font-weight: 600;
		color: #1f2937; /* gray-800 */
		font-variant-numeric: tabular-nums;
		min-width: 90px;
		width: 90px;
		text-align: right;
		flex-shrink: 0;
	}

	.trend {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		min-width: 60px;
		width: 60px;
		justify-content: flex-end;
		flex-shrink: 0;
	}

	.trend-text {
		font-size: 0.75rem;
		font-weight: 500;
		font-variant-numeric: tabular-nums;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.category-row {
			grid-template-columns: 1fr;
			gap: 0.5rem;
		}

		.category-name {
			font-size: 0.8125rem;
		}

		.category-stats {
			justify-content: space-between;
		}
	}
</style>
