<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency } from '$lib/types';
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

<div class="dashboard">
	<header class="dashboard-header">
		<h1>Financial Dashboard</h1>

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
		<div class="loading">Loading financial data...</div>
	{:else if error}
		<div class="error">
			<strong>Error:</strong>
			{error}
			<button onclick={() => loadUserData()}>Retry</button>
		</div>
	{:else}
		<!-- Financial Summary -->
		<section class="summary">
			<h2>Financial Summary</h2>
			<div class="summary-cards">
				<div class="card assets">
					<h3>Assets</h3>
					<p class="amount">{formatCurrency(assets)}</p>
					<p class="detail">{accounts.filter((a) => a.type === 'depository').length} accounts</p>
				</div>

				<div class="card liabilities">
					<h3>Liabilities</h3>
					<p class="amount">{formatCurrency(liabilities)}</p>
					<p class="detail">{accounts.filter((a) => a.type === 'credit').length} credit cards</p>
				</div>

				<div class="card net-worth">
					<h3>Net Worth</h3>
					<p class="amount" class:negative={netWorth < 0}>{formatCurrency(netWorth)}</p>
					<p class="detail">Assets - Liabilities</p>
				</div>
			</div>
		</section>

		<!-- Accounts List -->
		<section class="accounts">
			<h2>Accounts</h2>
			<div class="accounts-list">
				{#each accounts as account}
					<div class="account-item" class:credit={account.type === 'credit'}>
						<div class="account-info">
							<h3>{account.name}</h3>
							<p class="account-type">{account.subtype} •••• {account.mask}</p>
						</div>
						<div class="account-balance">
							<p class="balance">{formatCurrency(account.balance)}</p>
							{#if account.type === 'credit' && account.limit}
								<p class="limit">Limit: {formatCurrency(account.limit)}</p>
							{/if}
						</div>
					</div>
				{/each}

				{#if accounts.length === 0}
					<p class="empty">No accounts found</p>
				{/if}
			</div>
		</section>

		<!-- Recent Transactions -->
		<section class="transactions">
			<h2>Recent Transactions</h2>
			<div class="transactions-list">
				{#each transactions as txn}
					<div class="transaction-item">
						<div class="transaction-info">
							<p class="merchant">{txn.merchant_name || 'Unknown'}</p>
							<p class="category">{txn.category}</p>
							<p class="date">{new Date(txn.date).toLocaleDateString()}</p>
						</div>
						<p class="amount" class:income={txn.amount < 0}>
							{txn.amount < 0 ? '+' : ''}{formatCurrency(Math.abs(txn.amount))}
						</p>
					</div>
				{/each}

				{#if transactions.length === 0}
					<p class="empty">No recent transactions</p>
				{/if}
			</div>
		</section>
	{/if}
</div>

<style>
	.dashboard {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	.dashboard-header {
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

	.user-selector {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	select {
		padding: 0.5rem 1rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
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

	.summary {
		margin-bottom: 2rem;
	}

	h2 {
		font-size: 1.5rem;
		color: #333;
		margin-bottom: 1rem;
	}

	.summary-cards {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1rem;
	}

	.card {
		padding: 1.5rem;
		border-radius: 8px;
		background: white;
		border: 1px solid #e0e0e0;
	}

	.card.assets {
		border-left: 4px solid #4caf50;
	}

	.card.liabilities {
		border-left: 4px solid #f44336;
	}

	.card.net-worth {
		border-left: 4px solid #2196f3;
	}

	.card h3 {
		font-size: 0.875rem;
		text-transform: uppercase;
		color: #666;
		margin: 0 0 0.5rem 0;
	}

	.card .amount {
		font-size: 2rem;
		font-weight: bold;
		color: #333;
		margin: 0;
	}

	.card .amount.negative {
		color: #f44336;
	}

	.card .detail {
		font-size: 0.875rem;
		color: #999;
		margin: 0.5rem 0 0 0;
	}

	.accounts,
	.transactions {
		margin-bottom: 2rem;
	}

	.accounts-list,
	.transactions-list {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		overflow: hidden;
	}

	.account-item,
	.transaction-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		border-bottom: 1px solid #f0f0f0;
	}

	.account-item:last-child,
	.transaction-item:last-child {
		border-bottom: none;
	}

	.account-item.credit {
		background: #fff8f8;
	}

	.account-info h3,
	.transaction-info .merchant {
		font-size: 1rem;
		color: #333;
		margin: 0 0 0.25rem 0;
	}

	.account-type,
	.category,
	.date {
		font-size: 0.875rem;
		color: #999;
		margin: 0;
	}

	.account-balance {
		text-align: right;
	}

	.balance,
	.amount {
		font-size: 1.25rem;
		font-weight: bold;
		color: #333;
		margin: 0;
	}

	.limit {
		font-size: 0.875rem;
		color: #999;
		margin: 0.25rem 0 0 0;
	}

	.transaction-info {
		flex: 1;
	}

	.amount.income {
		color: #4caf50;
	}

	.empty {
		padding: 2rem;
		text-align: center;
		color: #999;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.dashboard {
			padding: 1rem;
		}

		.dashboard-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}

		.summary-cards {
			grid-template-columns: 1fr;
		}

		.account-item,
		.transaction-item {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.5rem;
		}

		.account-balance {
			text-align: left;
		}
	}
</style>
