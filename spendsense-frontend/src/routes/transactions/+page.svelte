<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency, formatCategory } from '$lib/types';
	import type { Transaction } from '$lib/types';
	import { Badge } from '$lib/components/ui/badge';
	import {
		Table,
		TableBody,
		TableCell,
		TableHead,
		TableHeader,
		TableRow
	} from '$lib/components/ui/table';
	import { Search, X } from '@lucide/svelte';

	// User selection from global store
	import { selectedUserId } from '$lib/stores/userStore';
	let currentUserId = $state('');

	// Subscribe to user store
	selectedUserId.subscribe(value => {
		currentUserId = value;
	});

	// State
	let allTransactions = $state<Transaction[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Pagination state (25 per page per story spec)
	let currentPage = $state(1);
	let pageSize = 25;

	// Filter state
	let searchQuery = $state('');
	let selectedCategory = $state('all');
	let selectedDateRange = $state<30 | 90 | 180 | 'all'>(30);

	// Debounced search
	let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;
	let debouncedSearch = $state('');

	// Get unique categories from transactions
	const categories = $derived(
		['all', ...new Set(allTransactions.map((t) => t.personal_finance_category_primary))].sort()
	);

	// Filter by date range
	const dateFilteredTransactions = $derived(() => {
		if (selectedDateRange === 'all') return allTransactions;

		const cutoffDate = new Date();
		cutoffDate.setDate(cutoffDate.getDate() - selectedDateRange);

		return allTransactions.filter((txn) => new Date(txn.date) >= cutoffDate);
	});

	// Filter transactions by search and category
	const filteredTransactions = $derived(() => {
		return dateFilteredTransactions().filter((txn) => {
			const matchesSearch =
				debouncedSearch === '' ||
				txn.merchant_name?.toLowerCase().includes(debouncedSearch.toLowerCase());
			const matchesCategory =
				selectedCategory === 'all' || txn.personal_finance_category_primary === selectedCategory;
			return matchesSearch && matchesCategory;
		});
	});

	// Paginate filtered transactions
	const paginatedTransactions = $derived(
		filteredTransactions().slice((currentPage - 1) * pageSize, currentPage * pageSize)
	);

	// Calculate total pages
	const totalPages = $derived(Math.ceil(filteredTransactions().length / pageSize));

	// Check if any filters are active
	const hasActiveFilters = $derived(
		debouncedSearch !== '' || selectedCategory !== 'all' || selectedDateRange !== 30
	);

	// Calculate category spending breakdown
	const categoryBreakdown = $derived(() => {
		const breakdown = new Map<string, number>();

		filteredTransactions()
			.filter((t) => t.amount > 0) // Only expenses (positive amounts)
			.forEach((t) => {
				const current = breakdown.get(t.personal_finance_category_primary) || 0;
				breakdown.set(t.personal_finance_category_primary, current + t.amount);
			});

		const sorted = Array.from(breakdown.entries())
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);

		const total = sorted.reduce((sum, item) => sum + item.amount, 0);
		return sorted.map((item) => ({ ...item, percentage: (item.amount / total) * 100 }));
	});

	// Get badge variant for category
	function getCategoryBadgeClass(category: string): string {
		if (category.startsWith('INCOME')) return 'bg-brand-blue text-white';
		if (category.startsWith('TRANSFER_IN')) return 'bg-brand-green text-white';
		if (category.startsWith('TRANSFER_OUT')) return 'bg-gray-500 text-white';
		return 'bg-gray-200 text-gray-700';
	}

	// Format date
	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	// Fetch transactions for selected user
	async function loadTransactions() {
		if (!currentUserId) return;

		loading = true;
		error = null;
		currentPage = 1; // Reset to first page

		try {
			// Fetch up to 500 transactions
			const data = await api.transactions.getUserTransactions(currentUserId, 500, 0);
			allTransactions = data;
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to load transactions';
			console.error('Transactions error:', err);
		} finally {
			loading = false;
		}
	}

	// Clear all filters
	function clearFilters() {
		searchQuery = '';
		debouncedSearch = '';
		selectedCategory = 'all';
		selectedDateRange = 30;
		currentPage = 1;
	}

	// Load data on mount
	onMount(() => {
		if (currentUserId) {
			loadTransactions();
		}
	});

	// Reload when user selection changes
	$effect(() => {
		if (currentUserId) {
			loadTransactions();
		}
	});

	// Debounce search input
	$effect(() => {
		if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
		searchDebounceTimer = setTimeout(() => {
			debouncedSearch = searchQuery;
		}, 300);
	});

	// Reset to page 1 when filters change
	$effect(() => {
		if (debouncedSearch || selectedCategory || selectedDateRange) {
			currentPage = 1;
		}
	});

	function goToPage(page: number) {
		if (page >= 1 && page <= totalPages) {
			currentPage = page;
		}
	}
</script>

<div class="min-h-screen bg-gray-50">
	<div class="container mx-auto px-6 py-6 sm:px-8 lg:px-10 max-w-7xl">
		{#if loading}
			<!-- Loading State -->
			<div class="flex items-center justify-center py-16">
				<div class="text-center space-y-3">
					<div
						class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"
					></div>
					<p class="text-gray-600">Loading transactions...</p>
				</div>
			</div>
		{:else if error}
			<!-- Error State -->
			<div class="bg-brand-coral/10 border border-brand-coral/30 rounded-lg p-6 text-center">
				<strong class="text-brand-coral block mb-2">Error:</strong>
				<p class="text-brand-coral/90 mb-4">{error}</p>
				<button
					onclick={() => loadTransactions()}
					class="px-4 py-2 bg-brand-coral text-white rounded-lg hover:opacity-90 transition-opacity"
				>
					Retry
				</button>
			</div>
		{:else}
			<div class="space-y-6">
				<!-- Category Spending Summary Card -->
				{#if categoryBreakdown().length > 0}
					<section class="bg-white rounded-xl p-8 shadow-card">
						<h2 class="text-xl font-semibold text-gray-800 mb-6">Spending by Category</h2>
						<div class="space-y-4">
							{#each categoryBreakdown().slice(0, 5) as { category, amount, percentage }}
								<div class="space-y-2">
									<div class="flex justify-between items-center">
										<span class="text-sm font-medium text-gray-700">{formatCategory(category)}</span>
										<div class="flex items-center gap-3">
											<span class="text-xs text-gray-500">{percentage.toFixed(1)}%</span>
											<span class="text-sm font-semibold text-gray-800">{formatCurrency(amount)}</span>
										</div>
									</div>
									<div class="h-2 bg-gray-100 rounded-full overflow-hidden">
										<div
											class="h-full bg-brand-blue rounded-full transition-all duration-300"
											style="width: {percentage}%"
										></div>
									</div>
								</div>
							{/each}
						</div>
					</section>
				{/if}

				<!-- Filter Controls -->
				<section class="bg-white rounded-xl p-6 shadow-card">
					<div class="flex flex-col lg:flex-row gap-4">
						<!-- Search Input -->
						<div class="flex-1">
							<label for="search" class="block text-sm font-medium text-gray-700 mb-2">
								Search Merchants
							</label>
							<div class="relative">
								<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
								<input
									id="search"
									type="text"
									placeholder="Search merchants..."
									bind:value={searchQuery}
									class="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-brand-blue"
								/>
							</div>
						</div>

						<!-- Category Dropdown -->
						<div class="w-full lg:w-48">
							<label for="category" class="block text-sm font-medium text-gray-700 mb-2">
								Category
							</label>
							<select
								id="category"
								bind:value={selectedCategory}
								class="w-full px-4 py-2 border border-gray-200 rounded-lg bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-brand-blue"
							>
								{#each categories as category}
									<option value={category}>
										{category === 'all' ? 'All Categories' : formatCategory(category)}
									</option>
								{/each}
							</select>
						</div>

						<!-- Date Range Buttons -->
						<div class="w-full lg:w-auto">
							<label class="block text-sm font-medium text-gray-700 mb-2">Period</label>
							<div class="flex bg-gray-100 rounded-lg p-1">
								<button
									onclick={() => (selectedDateRange = 30)}
									class={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
										selectedDateRange === 30
											? 'bg-brand-blue text-white shadow-sm'
											: 'text-gray-600 hover:text-gray-800'
									}`}
								>
									30d
								</button>
								<button
									onclick={() => (selectedDateRange = 90)}
									class={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
										selectedDateRange === 90
											? 'bg-brand-blue text-white shadow-sm'
											: 'text-gray-600 hover:text-gray-800'
									}`}
								>
									90d
								</button>
								<button
									onclick={() => (selectedDateRange = 180)}
									class={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
										selectedDateRange === 180
											? 'bg-brand-blue text-white shadow-sm'
											: 'text-gray-600 hover:text-gray-800'
									}`}
								>
									180d
								</button>
								<button
									onclick={() => (selectedDateRange = 'all')}
									class={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
										selectedDateRange === 'all'
											? 'bg-brand-blue text-white shadow-sm'
											: 'text-gray-600 hover:text-gray-800'
									}`}
								>
									All
								</button>
							</div>
						</div>

						<!-- Clear Filters Button -->
						{#if hasActiveFilters}
							<div class="w-full lg:w-auto">
								<label class="block text-sm font-medium text-gray-700 mb-2 opacity-0">Clear</label>
								<button
									onclick={clearFilters}
									class="w-full lg:w-auto px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors flex items-center gap-2"
								>
									<X class="w-4 h-4" />
									Clear Filters
								</button>
							</div>
						{/if}
					</div>

					<!-- Results Count -->
					<div class="mt-4 pt-4 border-t border-gray-100">
						<p class="text-sm text-gray-600">
							Showing {(currentPage - 1) * pageSize + 1}-{Math.min(
								currentPage * pageSize,
								filteredTransactions().length
							)} of {filteredTransactions().length} transactions
						</p>
					</div>
				</section>

				<!-- Transactions Table (Desktop/Tablet) -->
				<section class="hidden md:block bg-white rounded-xl shadow-card overflow-hidden">
					<Table>
						<TableHeader>
							<TableRow>
								<TableHead class="text-gray-700">Date</TableHead>
								<TableHead class="text-gray-700">Merchant</TableHead>
								<TableHead class="text-gray-700">Category</TableHead>
								<TableHead class="text-right text-gray-700">Amount</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{#each paginatedTransactions as txn, index}
								<TableRow class={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
									<TableCell class="text-sm text-gray-600 py-3 px-4">
										{formatDate(txn.date)}
									</TableCell>
									<TableCell class="font-semibold text-gray-800 py-3 px-4">
										{txn.merchant_name || 'Unknown'}
									</TableCell>
									<TableCell class="py-3 px-4">
										<Badge class={`${getCategoryBadgeClass(txn.personal_finance_category_primary)} text-xs uppercase`}>
											{formatCategory(txn.personal_finance_category_primary)}
										</Badge>
									</TableCell>
									<TableCell class="text-right font-mono py-3 px-4">
										<span class={txn.amount < 0 ? 'text-brand-green font-semibold' : 'text-red-600'}>
											{txn.amount < 0 ? '+' : ''}{formatCurrency(Math.abs(txn.amount))}
										</span>
									</TableCell>
								</TableRow>
							{/each}
						</TableBody>
					</Table>

					{#if paginatedTransactions.length === 0}
						<!-- Empty State -->
						<div class="py-16 text-center">
							<div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
								<Search class="w-8 h-8 text-gray-400" />
							</div>
							<h3 class="text-lg font-semibold text-gray-800 mb-2">No transactions match your filters</h3>
							<p class="text-gray-600 mb-4">Try adjusting your search or filter criteria</p>
							<button
								onclick={clearFilters}
								class="px-4 py-2 bg-brand-blue text-white rounded-lg hover:bg-blue-dark transition-colors"
							>
								Reset Filters
							</button>
						</div>
					{/if}
				</section>

				<!-- Transactions Card View (Mobile) -->
				<section class="md:hidden space-y-3">
					{#each paginatedTransactions as txn}
						<div class="bg-white rounded-lg p-4 shadow-card">
							<div class="flex items-start justify-between mb-2">
								<div class="flex-1">
									<h3 class="font-semibold text-gray-800">{txn.merchant_name || 'Unknown'}</h3>
									<Badge class={`${getCategoryBadgeClass(txn.personal_finance_category_primary)} text-xs uppercase mt-1`}>
										{formatCategory(txn.personal_finance_category_primary)}
									</Badge>
								</div>
								<span class={`font-mono font-semibold ${txn.amount < 0 ? 'text-brand-green' : 'text-red-600'}`}>
									{txn.amount < 0 ? '+' : ''}{formatCurrency(Math.abs(txn.amount))}
								</span>
							</div>
							<p class="text-sm text-gray-600">{formatDate(txn.date)}</p>
						</div>
					{/each}

					{#if paginatedTransactions.length === 0}
						<!-- Empty State (Mobile) -->
						<div class="bg-white rounded-lg p-8 text-center shadow-card">
							<div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
								<Search class="w-8 h-8 text-gray-400" />
							</div>
							<h3 class="text-lg font-semibold text-gray-800 mb-2">No transactions found</h3>
							<p class="text-gray-600 mb-4">Try adjusting your filters</p>
							<button
								onclick={clearFilters}
								class="px-4 py-2 bg-brand-blue text-white rounded-lg hover:bg-blue-dark transition-colors"
							>
								Reset Filters
							</button>
						</div>
					{/if}
				</section>

				<!-- Pagination -->
				{#if totalPages > 1 && paginatedTransactions.length > 0}
					<section class="flex justify-center items-center gap-4 py-4">
						<button
							onclick={() => goToPage(currentPage - 1)}
							disabled={currentPage === 1}
							class="px-4 py-2 bg-brand-blue text-white rounded-lg hover:bg-blue-dark transition-colors disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed"
						>
							Previous
						</button>

						<span class="text-sm text-gray-600">
							Page {currentPage} of {totalPages}
						</span>

						<button
							onclick={() => goToPage(currentPage + 1)}
							disabled={currentPage === totalPages}
							class="px-4 py-2 bg-brand-blue text-white rounded-lg hover:bg-blue-dark transition-colors disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed"
						>
							Next
						</button>
					</section>
				{/if}
			</div>

		{/if}
	</div>
</div>
