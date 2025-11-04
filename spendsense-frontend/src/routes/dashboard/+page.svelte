<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency, formatCategory } from '$lib/types';
	import type { Account, Transaction } from '$lib/types';

	// Svelte 5 runes for reactive state
	let selectedUserId = $state('bdd640fb-0667-4ad1-9c80-317fa3b1799d');
	let accounts = $state<Account[]>([]);
	let transactions = $state<Transaction[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Available test users
	const testUsers = [
		{ id: 'bdd640fb-0667-4ad1-9c80-317fa3b1799d', name: 'Daniel Doyle' },
		{ id: '97d7a560-adb1-4670-ad9f-b00d4882d73c', name: 'Mr. Andrew Foster' },
		{ id: '37c86152-beed-4af9-80c5-9f30d1031424', name: 'Amber Cooper' },
		{ id: 'dc268108-7140-41a1-afc2-ccfc9db7284b', name: 'Steven Taylor' },
		{ id: 'c7a9f33c-22d8-49d3-b3e4-f986f18cccdc', name: 'Ashley Garcia' }
	];

	// Derived values using $derived rune
	const assets = $derived(
		accounts
			.filter((a) => a.type === 'depository')
			.reduce((sum, a) => sum + a.balance, 0)
	);

	const liabilities = $derived(
		accounts
			.filter((a) => a.type === 'credit')
			.reduce((sum, a) => sum + a.balance, 0)
	);

	const netWorth = $derived(assets - liabilities);

	// Fetch data for selected user
	async function loadUserData() {
		loading = true;
		error = null;

		try {
			// Fetch accounts and transactions in parallel
			const [accountsData, transactionsData] = await Promise.all([
				api.accounts.getUserAccounts(selectedUserId),
				api.transactions.getUserTransactions(selectedUserId, 10, 0)
			]);

			accounts = accountsData;
			transactions = transactionsData;
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to load data';
			console.error('Dashboard error:', err);
		} finally {
			loading = false;
		}
	}

	// Load data on mount and when user changes
	onMount(() => {
		loadUserData();
	});

	// Reload when user selection changes
	$effect(() => {
		if (selectedUserId) {
			loadUserData();
		}
	});
</script>

<div class="min-h-screen bg-background">
	<div class="container mx-auto px-4 py-8 sm:px-6 lg:px-8 max-w-7xl">
		<!-- Header -->
		<header class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
			<h1 class="text-3xl font-bold text-foreground">Financial Dashboard</h1>

			<div class="flex items-center gap-2">
				<label for="user-select" class="text-sm font-medium text-muted-foreground">User:</label>
				<select
					id="user-select"
					bind:value={selectedUserId}
					class="px-4 py-2 border border-border rounded-lg bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
				>
					{#each testUsers as user}
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
					<p class="text-muted-foreground">Loading financial data...</p>
				</div>
			</div>
		{:else if error}
			<div class="bg-destructive/10 border border-destructive/30 rounded-lg p-6 text-center">
				<strong class="text-destructive block mb-2">Error:</strong>
				<p class="text-destructive/90 mb-4">{error}</p>
				<button
					onclick={() => loadUserData()}
					class="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors"
				>
					Retry
				</button>
			</div>
		{:else}
			<!-- Financial Summary Cards -->
			<section class="mb-8">
				<h2 class="text-xl font-semibold text-foreground mb-4">Financial Summary</h2>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<!-- Assets Card -->
					<div class="bg-card rounded-lg p-6 border-l-4 border-l-chart-2 shadow-sm">
						<h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
							Assets
						</h3>
						<p class="text-3xl font-bold text-foreground">{formatCurrency(assets)}</p>
						<p class="text-sm text-muted-foreground mt-2">
							{accounts.filter((a) => a.type === 'depository').length} accounts
						</p>
					</div>

					<!-- Liabilities Card -->
					<div class="bg-card rounded-lg p-6 border-l-4 border-l-destructive shadow-sm">
						<h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
							Liabilities
						</h3>
						<p class="text-3xl font-bold text-foreground">{formatCurrency(liabilities)}</p>
						<p class="text-sm text-muted-foreground mt-2">
							{accounts.filter((a) => a.type === 'credit').length} credit cards
						</p>
					</div>

					<!-- Net Worth Card -->
					<div class="bg-card rounded-lg p-6 border-l-4 border-l-primary shadow-sm">
						<h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
							Net Worth
						</h3>
						<p class="text-3xl font-bold {netWorth < 0 ? 'text-destructive' : 'text-foreground'}">
							{formatCurrency(netWorth)}
						</p>
						<p class="text-sm text-muted-foreground mt-2">Assets - Liabilities</p>
					</div>
				</div>
			</section>

			<!-- Accounts List -->
			<section class="mb-8">
				<h2 class="text-xl font-semibold text-foreground mb-4">Accounts</h2>
				<div class="bg-card rounded-lg border border-border shadow-sm overflow-hidden">
					{#if accounts.length > 0}
						{#each accounts as account, i}
							<div
								class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 {i !==
								accounts.length - 1
									? 'border-b border-border'
									: ''} {account.type === 'credit'
									? 'bg-destructive/5'
									: ''} hover:bg-accent/50 transition-colors"
							>
								<div class="mb-3 sm:mb-0">
									<h3 class="text-base font-medium text-foreground">{account.name}</h3>
									<p class="text-sm text-muted-foreground">
										{formatCategory(account.subtype)} •••• {account.mask}
									</p>
								</div>
								<div class="text-left sm:text-right">
									<p class="text-lg font-semibold text-foreground">
										{formatCurrency(account.balance)}
									</p>
									{#if account.type === 'credit' && account.limit}
										<p class="text-sm text-muted-foreground">
											Limit: {formatCurrency(account.limit)}
										</p>
									{/if}
								</div>
							</div>
						{/each}
					{:else}
						<p class="text-center py-8 text-muted-foreground">No accounts found</p>
					{/if}
				</div>
			</section>

			<!-- Recent Transactions -->
			<section>
				<h2 class="text-xl font-semibold text-foreground mb-4">Recent Transactions</h2>
				<div class="bg-card rounded-lg border border-border shadow-sm overflow-hidden">
					{#if transactions.length > 0}
						{#each transactions as txn, i}
							<div
								class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 {i !==
								transactions.length - 1
									? 'border-b border-border'
									: ''} hover:bg-accent/50 transition-colors"
							>
								<div class="flex-1 mb-2 sm:mb-0">
									<p class="text-base font-medium text-foreground">
										{txn.merchant_name || 'Unknown'}
									</p>
									<p class="text-sm text-muted-foreground">
										{formatCategory(txn.category)}
									</p>
									<p class="text-xs text-muted-foreground">
										{new Date(txn.date).toLocaleDateString()}
									</p>
								</div>
								<p
									class="text-lg font-semibold {txn.amount < 0
										? 'text-chart-2'
										: 'text-foreground'}"
								>
									{txn.amount < 0 ? '+' : ''}{formatCurrency(Math.abs(txn.amount))}
								</p>
							</div>
						{/each}
					{:else}
						<p class="text-center py-8 text-muted-foreground">No recent transactions</p>
					{/if}
				</div>
			</section>
		{/if}
	</div>
</div>
