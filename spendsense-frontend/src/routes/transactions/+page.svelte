<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency } from '$lib/types';
	import type { Transaction } from '$lib/types';

	// Svelte 5 runes for reactive state
	let selectedUserId = $state('bdd640fb-0667-4ad1-9c80-317fa3b1799d');
	let allTransactions = $state<Transaction[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Pagination state
	let currentPage = $state(1);
	let pageSize = $state(50);

	// Filter state
	let searchQuery = $state('');
	let selectedCategory = $state('all');

	// Available test users
	const testUsers = [
		{ id: 'bdd640fb-0667-4ad1-9c80-317fa3b1799d', name: 'Daniel Doyle' },
		{ id: '97d7a560-adb1-4670-ad9f-b00d4882d73c', name: 'Mr. Andrew Foster' },
		{ id: '37c86152-beed-4af9-80c5-9f30d1031424', name: 'Amber Cooper' },
		{ id: 'dc268108-7140-41a1-afc2-ccfc9db7284b', name: 'Steven Taylor' },
		{ id: 'c7a9f33c-22d8-49d3-b3e4-f986f18cccdc', name: 'Ashley Garcia' }
	];

	// Get unique categories from transactions
	const categories = $derived(
		['all', ...new Set(allTransactions.map((t) => t.category))].sort()
	);

	// Filter transactions by search and category
	const filteredTransactions = $derived(
		allTransactions.filter((txn) => {
			const matchesSearch =
				searchQuery === '' ||
				txn.merchant_name?.toLowerCase().includes(searchQuery.toLowerCase());
			const matchesCategory =
				selectedCategory === 'all' || txn.category === selectedCategory;
			return matchesSearch && matchesCategory;
		})
	);

	// Paginate filtered transactions
	const paginatedTransactions = $derived(
		filteredTransactions.slice((currentPage - 1) * pageSize, currentPage * pageSize)
	);

	// Calculate total pages
	const totalPages = $derived(Math.ceil(filteredTransactions.length / pageSize));

	// Calculate category spending breakdown
	const categoryBreakdown = $derived(() => {
		const breakdown = new Map<string, number>();

		filteredTransactions
			.filter((t) => t.amount > 0) // Only expenses (positive amounts)
			.forEach((t) => {
				const current = breakdown.get(t.category) || 0;
				breakdown.set(t.category, current + t.amount);
			});

		return Array.from(breakdown.entries())
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);
	});

	// Fetch transactions for selected user
	async function loadTransactions() {
		loading = true;
		error = null;
		currentPage = 1; // Reset to first page

		try {
			// Fetch up to 500 transactions (more than we'll display)
			const data = await api.transactions.getUserTransactions(selectedUserId, 500, 0);
			allTransactions = data;
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to load transactions';
			console.error('Transactions error:', err);
		} finally {
			loading = false;
		}
	}

	// Load data on mount
	onMount(() => {
		loadTransactions();
	});

	// Reload when user selection changes
	$effect(() => {
		if (selectedUserId) {
			loadTransactions();
		}
	});

	// Reset to page 1 when filters change
	$effect(() => {
		if (searchQuery || selectedCategory) {
			currentPage = 1;
		}
	});

	function goToPage(page: number) {
		if (page >= 1 && page <= totalPages) {
			currentPage = page;
		}
	}
</script>

<div class="transactions-page">
	<header class="page-header">
		<h1>Transaction History</h1>

		<div class="user-selector">
			<label for="user-select">User:</label>
			<select id="user-select" bind:value={selectedUserId}>
				{#each testUsers as user}
					<option value={user.id}>{user.name}</option>
				{/each}
			</select>
		</div>
	</header>

	{#if loading}
		<div class="loading">Loading transactions...</div>
	{:else if error}
		<div class="error">
			<strong>Error:</strong>
			{error}
			<button onclick={() => loadTransactions()}>Retry</button>
		</div>
	{:else}
		<div class="content">
			<!-- Filters and Search -->
			<section class="filters">
				<div class="filter-group">
					<label for="search">Search Merchant:</label>
					<input
						id="search"
						type="text"
						placeholder="Search by merchant name..."
						bind:value={searchQuery}
					/>
				</div>

				<div class="filter-group">
					<label for="category">Category:</label>
					<select id="category" bind:value={selectedCategory}>
						{#each categories as category}
							<option value={category}>
								{category === 'all' ? 'All Categories' : category.replace(/_/g, ' ')}
							</option>
						{/each}
					</select>
				</div>

				<div class="stats">
					<p>
						Showing {paginatedTransactions.length} of {filteredTransactions.length} transactions
					</p>
				</div>
			</section>

			<!-- Category Breakdown -->
			{#if categoryBreakdown.length > 0}
				<section class="breakdown">
					<h2>Spending by Category</h2>
					<div class="breakdown-bars">
						{#each categoryBreakdown.slice(0, 5) as { category, amount }}
							<div class="breakdown-item">
								<div class="breakdown-label">
									<span class="category-name">{category.replace(/_/g, ' ')}</span>
									<span class="category-amount">{formatCurrency(amount)}</span>
								</div>
								<div class="breakdown-bar-container">
									<div
										class="breakdown-bar"
										style="width: {(amount / categoryBreakdown[0].amount) * 100}%"
									></div>
								</div>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- Transactions Table -->
			<section class="transactions-table">
				<table>
					<thead>
						<tr>
							<th>Date</th>
							<th>Merchant</th>
							<th>Category</th>
							<th class="amount-col">Amount</th>
						</tr>
					</thead>
					<tbody>
						{#each paginatedTransactions as txn}
							<tr>
								<td class="date-col">{new Date(txn.date).toLocaleDateString()}</td>
								<td class="merchant-col">{txn.merchant_name || 'Unknown'}</td>
								<td class="category-col">{txn.category.replace(/_/g, ' ')}</td>
								<td class="amount-col" class:income={txn.amount < 0} class:expense={txn.amount > 0}>
									{txn.amount < 0 ? '+' : ''}{formatCurrency(Math.abs(txn.amount))}
								</td>
							</tr>
						{/each}

						{#if paginatedTransactions.length === 0}
							<tr>
								<td colspan="4" class="empty">No transactions found</td>
							</tr>
						{/if}
					</tbody>
				</table>
			</section>

			<!-- Pagination -->
			{#if totalPages > 1}
				<section class="pagination">
					<button onclick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>
						Previous
					</button>

					<span class="page-info">
						Page {currentPage} of {totalPages}
					</span>

					<button onclick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>
						Next
					</button>
				</section>
			{/if}
		</div>
	{/if}

	<nav class="back-nav">
		<a href="/dashboard">← Back to Dashboard</a>
	</nav>
</div>

<style>
	.transactions-page {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 2rem;
		color: #333;
		margin: 0;
	}

	h2 {
		font-size: 1.25rem;
		color: #333;
		margin: 0 0 1rem 0;
	}

	.user-selector {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	select,
	input[type='text'] {
		padding: 0.5rem 1rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	input[type='text'] {
		width: 300px;
	}

	.loading,
	.error {
		padding: 2rem;
		text-align: center;
		border-radius: 8px;
	}

	.loading {
		background: #f5f5f5;
		color: #666;
	}

	.error {
		background: #fee;
		color: #c33;
		border: 1px solid #fcc;
	}

	.error button {
		margin-top: 1rem;
		padding: 0.5rem 1rem;
		background: #c33;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}

	.content {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.filters {
		display: flex;
		gap: 1rem;
		align-items: flex-end;
		padding: 1.5rem;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
	}

	.filter-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.filter-group label {
		font-size: 0.875rem;
		color: #666;
	}

	.stats {
		margin-left: auto;
		display: flex;
		align-items: center;
	}

	.stats p {
		margin: 0;
		color: #666;
		font-size: 0.875rem;
	}

	.breakdown {
		padding: 1.5rem;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
	}

	.breakdown-bars {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.breakdown-item {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.breakdown-label {
		display: flex;
		justify-content: space-between;
		font-size: 0.875rem;
	}

	.category-name {
		color: #333;
		font-weight: 500;
	}

	.category-amount {
		color: #666;
	}

	.breakdown-bar-container {
		height: 8px;
		background: #f0f0f0;
		border-radius: 4px;
		overflow: hidden;
	}

	.breakdown-bar {
		height: 100%;
		background: #2196f3;
		border-radius: 4px;
		transition: width 0.3s ease;
	}

	.transactions-table {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		overflow: hidden;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	thead {
		background: #f5f5f5;
	}

	th {
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		color: #666;
		font-size: 0.875rem;
		text-transform: uppercase;
	}

	td {
		padding: 1rem;
		border-top: 1px solid #f0f0f0;
	}

	.date-col {
		color: #666;
		font-size: 0.875rem;
	}

	.merchant-col {
		color: #333;
		font-weight: 500;
	}

	.category-col {
		color: #666;
		font-size: 0.875rem;
	}

	.amount-col {
		text-align: right;
		font-weight: 600;
	}

	.amount-col.income {
		color: #4caf50;
	}

	.amount-col.expense {
		color: #f44336;
	}

	.empty {
		text-align: center;
		color: #999;
		padding: 3rem;
	}

	.pagination {
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
	}

	.pagination button {
		padding: 0.5rem 1rem;
		background: #2196f3;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
	}

	.pagination button:hover:not(:disabled) {
		background: #1976d2;
	}

	.pagination button:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	.page-info {
		color: #666;
		font-size: 0.875rem;
	}

	.back-nav {
		margin-top: 2rem;
		padding-top: 2rem;
		border-top: 1px solid #e0e0e0;
	}

	.back-nav a {
		color: #2196f3;
		text-decoration: none;
		font-weight: 500;
	}

	.back-nav a:hover {
		text-decoration: underline;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.transactions-page {
			padding: 1rem;
		}

		.page-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}

		.filters {
			flex-direction: column;
			align-items: stretch;
		}

		input[type='text'] {
			width: 100%;
		}

		.stats {
			margin-left: 0;
		}

		table {
			font-size: 0.875rem;
		}

		th,
		td {
			padding: 0.75rem 0.5rem;
		}

		.merchant-col {
			max-width: 150px;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}
	}
</style>
