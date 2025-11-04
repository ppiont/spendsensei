<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency, formatCategory } from '$lib/types';
	import type { Transaction } from '$lib/types';

	// Svelte 5 runes for reactive state
	let users = $state<Array<{ id: string; name: string }>>([]);
	let selectedUserId = $state('');
	let allTransactions = $state<Transaction[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Pagination state
	let currentPage = $state(1);
	let pageSize = $state(50);

	// Filter state
	let searchQuery = $state('');
	let selectedCategory = $state('all');

	// Get unique categories from transactions
	const categories = $derived(
		['all', ...new Set(allTransactions.map((t) => t.personal_finance_category_primary))].sort()
	);

	// Filter transactions by search and category
	const filteredTransactions = $derived(
		allTransactions.filter((txn) => {
			const matchesSearch =
				searchQuery === '' ||
				txn.merchant_name?.toLowerCase().includes(searchQuery.toLowerCase());
			const matchesCategory =
				selectedCategory === 'all' || txn.personal_finance_category_primary === selectedCategory;
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
				const current = breakdown.get(t.personal_finance_category_primary) || 0;
				breakdown.set(t.personal_finance_category_primary, current + t.amount);
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

	// Fetch all users
	async function loadUsers() {
		try {
			const data = await api.users.getUsers();
			users = data.map((u) => ({ id: u.id, name: u.name }));
			if (users.length > 0 && !selectedUserId) {
				selectedUserId = users[0].id;
			}
		} catch (err: any) {
			console.error('Error loading users:', err);
		}
	}

	// Load data on mount
	onMount(async () => {
		await loadUsers();
		if (selectedUserId) {
			loadTransactions();
		}
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

<div class="min-h-screen bg-background">
	<div class="container mx-auto px-4 py-8 sm:px-6 lg:px-8 max-w-7xl">
		<!-- Header -->
		<header class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
			<h1 class="text-3xl font-bold text-foreground">Transaction History</h1>

			<div class="flex items-center gap-2">
				<label for="user-select" class="text-sm font-medium text-muted-foreground">User:</label>
				<select
					id="user-select"
					bind:value={selectedUserId}
					class="px-4 py-2 border border-border rounded-lg bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
				>
					{#each users as user}
						<option value={user.id}>{user.name}</option>
					{/each}
				</select>
			</div>
		</header>

		{#if loading}
			<div class="flex items-center justify-center py-16">
				<div class="text-center space-y-3">
					<div
						class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"
					></div>
					<p class="text-muted-foreground">Loading transactions...</p>
				</div>
			</div>
		{:else if error}
			<div class="bg-destructive/10 border border-destructive/30 rounded-lg p-6 text-center">
				<strong class="text-destructive block mb-2">Error:</strong>
				<p class="text-destructive/90 mb-4">{error}</p>
				<button
					onclick={() => loadTransactions()}
					class="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors"
				>
					Retry
				</button>
			</div>
		{:else}
			<div class="space-y-6">
				<!-- Filters and Search -->
				<section
					class="bg-card rounded-lg border border-border shadow-sm p-6 flex flex-col lg:flex-row gap-4 items-start lg:items-end"
				>
					<div class="flex flex-col gap-2 w-full lg:w-auto lg:min-w-[300px]">
						<label for="search" class="text-sm font-medium text-muted-foreground"
							>Search Merchant:</label
						>
						<input
							id="search"
							type="text"
							placeholder="Search by merchant name..."
							bind:value={searchQuery}
							class="px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
						/>
					</div>

					<div class="flex flex-col gap-2 w-full lg:w-auto">
						<label for="category" class="text-sm font-medium text-muted-foreground">Category:</label>
						<select
							id="category"
							bind:value={selectedCategory}
							class="px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
						>
							{#each categories as category}
								<option value={category}>
									{category === 'all' ? 'All Categories' : formatCategory(category)}
								</option>
							{/each}
						</select>
					</div>

					<div class="lg:ml-auto flex items-center">
						<p class="text-sm text-muted-foreground">
							Showing {paginatedTransactions.length} of {filteredTransactions.length} transactions
						</p>
					</div>
				</section>

				<!-- Category Breakdown -->
				{#if categoryBreakdown.length > 0}
					<section class="bg-card rounded-lg border border-border shadow-sm p-6">
						<h2 class="text-xl font-semibold text-foreground mb-4">Spending by Category</h2>
						<div class="space-y-4">
							{#each categoryBreakdown.slice(0, 5) as { category, amount }}
								<div class="space-y-2">
									<div class="flex justify-between text-sm">
										<span class="font-medium text-foreground">{formatCategory(category)}</span>
										<span class="text-muted-foreground">{formatCurrency(amount)}</span>
									</div>
									<div class="h-2 bg-muted rounded-full overflow-hidden">
										<div
											class="h-full bg-primary rounded-full transition-all duration-300"
											style="width: {(amount / categoryBreakdown[0].amount) * 100}%"
										></div>
									</div>
								</div>
							{/each}
						</div>
					</section>
				{/if}

				<!-- Transactions Table -->
				<section class="bg-card rounded-lg border border-border shadow-sm overflow-hidden">
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead class="bg-muted">
								<tr>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
										>Date</th
									>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
										>Merchant</th
									>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
										>Category</th
									>
									<th
										class="px-4 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider"
										>Amount</th
									>
								</tr>
							</thead>
							<tbody class="divide-y divide-border">
								{#each paginatedTransactions as txn}
									<tr class="hover:bg-accent/50 transition-colors">
										<td class="px-4 py-3 text-sm text-muted-foreground">
											{new Date(txn.date).toLocaleDateString()}
										</td>
										<td class="px-4 py-3 text-sm font-medium text-foreground truncate max-w-xs">
											{txn.merchant_name || 'Unknown'}
										</td>
										<td class="px-4 py-3 text-sm text-muted-foreground">
											{formatCategory(txn.personal_finance_category_primary)}
										</td>
										<td
											class="px-4 py-3 text-sm font-semibold text-right {txn.amount < 0
												? 'text-chart-2'
												: 'text-destructive'}"
										>
											{txn.amount < 0 ? '+' : ''}{formatCurrency(Math.abs(txn.amount))}
										</td>
									</tr>
								{/each}

								{#if paginatedTransactions.length === 0}
									<tr>
										<td colspan="4" class="px-4 py-12 text-center text-muted-foreground">
											No transactions found
										</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</section>

				<!-- Pagination -->
				{#if totalPages > 1}
					<section class="flex justify-center items-center gap-4 py-4">
						<button
							onclick={() => goToPage(currentPage - 1)}
							disabled={currentPage === 1}
							class="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed"
						>
							Previous
						</button>

						<span class="text-sm text-muted-foreground">
							Page {currentPage} of {totalPages}
						</span>

						<button
							onclick={() => goToPage(currentPage + 1)}
							disabled={currentPage === totalPages}
							class="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed"
						>
							Next
						</button>
					</section>
				{/if}
			</div>
		{/if}

		<!-- Back Navigation -->
		<nav class="mt-8 pt-6 border-t border-border">
			<a
				href="/dashboard"
				class="inline-flex items-center text-primary hover:text-primary/80 font-medium transition-colors"
			>
				← Back to Dashboard
			</a>
		</nav>
	</div>
</div>
