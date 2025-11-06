<script lang="ts">
	import { formatCurrency } from '$lib/types';
	import type { Transaction } from '$lib/types';
	import { Separator } from '$lib/components/ui/separator';
	import { ArrowRight } from '@lucide/svelte';

	// Props
	let { transactions, limit = 5 } = $props<{
		transactions: Transaction[];
		limit?: number;
	}>();

	// Sort and limit transactions (create copy to avoid mutation in $derived)
	const recentTransactions = $derived(
		[...transactions]
			.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
			.slice(0, limit)
	);

	// Format date relative to today
	function formatRelativeDate(dateStr: string): string {
		const date = new Date(dateStr);
		const today = new Date();
		const yesterday = new Date(today);
		yesterday.setDate(yesterday.getDate() - 1);

		// Reset time components for comparison
		const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
		const todayOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
		const yesterdayOnly = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate());

		if (dateOnly.getTime() === todayOnly.getTime()) {
			return 'Today';
		} else if (dateOnly.getTime() === yesterdayOnly.getTime()) {
			return 'Yesterday';
		} else {
			return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
		}
	}

	// Get category icon
	function getCategoryIcon(category: string): string {
		const iconMap: Record<string, string> = {
			FOOD_AND_DRINK: '🍽️',
			TRANSPORTATION: '🚗',
			SHOPPING: '🛍️',
			TRANSFER: '💸',
			INCOME: '💰',
			ENTERTAINMENT: '🎬',
			GENERAL_SERVICES: '⚙️',
			HOME_IMPROVEMENT: '🏠',
			MEDICAL: '⚕️',
			TRAVEL: '✈️',
			LOAN_PAYMENTS: '🏦',
			BANK_FEES: '🏦'
		};

		const primary = category.split('_')[0];
		return iconMap[category] || iconMap[primary] || '💳';
	}
</script>

<div class="recent-activity">
	{#if recentTransactions.length === 0}
		<div class="empty-state">
			<p class="text-gray-500 text-sm">No recent transactions</p>
		</div>
	{:else}
		<div class="transactions-list">
			{#each recentTransactions as transaction, index (transaction.id)}
				<div class="transaction-item">
					<div class="transaction-content">
						<!-- Icon + Merchant -->
						<div class="transaction-left">
							<span class="category-icon">{getCategoryIcon(transaction.personal_finance_category_primary)}</span>
							<div class="transaction-details">
								<span class="merchant-name">{transaction.merchant_name || 'Transaction'}</span>
								<span class="transaction-date">{formatRelativeDate(transaction.date)}</span>
							</div>
						</div>

						<!-- Amount -->
						<div class="transaction-amount">
							<span class={transaction.amount < 0 ? 'amount-positive' : 'amount-negative'}>
								{transaction.amount < 0 ? '+' : ''}{formatCurrency(Math.abs(transaction.amount))}
							</span>
						</div>
					</div>

					{#if index < recentTransactions.length - 1}
						<Separator class="my-3" />
					{/if}
				</div>
			{/each}
		</div>

		<!-- View all link -->
		<a href="/transactions" class="view-all-link">
			<span>View All Transactions</span>
			<ArrowRight class="w-4 h-4" />
		</a>
	{/if}
</div>

<style>
	.recent-activity {
		width: 100%;
	}

	.empty-state {
		text-align: center;
		padding: 2rem;
	}

	.transactions-list {
		display: flex;
		flex-direction: column;
	}

	.transaction-item {
		/* Spacing handled by separator */
	}

	.transaction-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.transaction-left {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex: 1;
		min-width: 0; /* Allow text truncation */
	}

	.category-icon {
		font-size: 1.5rem;
		flex-shrink: 0;
	}

	.transaction-details {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
		min-width: 0;
	}

	.merchant-name {
		font-size: 0.875rem;
		font-weight: 500;
		color: #1f2937; /* gray-800 */
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.transaction-date {
		font-size: 0.75rem;
		color: #6b7280; /* gray-500 */
	}

	.transaction-amount {
		flex-shrink: 0;
	}

	.amount-positive {
		font-size: 0.875rem;
		font-weight: 600;
		color: #10b981; /* brand-green */
		font-variant-numeric: tabular-nums;
	}

	.amount-negative {
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151; /* gray-700 */
		font-variant-numeric: tabular-nums;
	}

	.view-all-link {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 1.5rem;
		padding: 0.5rem 1rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: #3b82f6; /* brand-blue */
		border: 1px solid #e5e7eb;
		border-radius: 0.5rem;
		text-decoration: none;
		transition: all 0.15s ease;
	}

	.view-all-link:hover {
		background-color: #f9fafb; /* gray-50 */
		border-color: #3b82f6;
	}

	/* Responsive */
	@media (max-width: 640px) {
		.merchant-name {
			max-width: 150px;
		}
	}
</style>
