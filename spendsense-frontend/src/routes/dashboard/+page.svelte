<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency } from '$lib/types';
	import type { Account, Transaction, Recommendation } from '$lib/types';
	import KpiCard from '$lib/components/custom/KpiCard.svelte';
	import RecommendationCard from '$lib/components/custom/RecommendationCard.svelte';
	import PersonaBadge from '$lib/components/custom/PersonaBadge.svelte';

	// Svelte 5 runes for reactive state
	let accounts = $state<Account[]>([]);
	let transactions = $state<Transaction[]>([]);
	let recommendations = $state<Recommendation[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Dev mode user switching (only in development)
	const isDev = import.meta.env.DEV;
	let users = $state<Array<{ id: string; name: string }>>([]);
	let selectedUserId = $state('');

	// === KPI CALCULATIONS ===

	// 1. Net Worth (Featured KPI)
	const assets = $derived(
		accounts
			.filter((a) => a.type === 'depository')
			.reduce((sum, a) => sum + a.current_balance, 0)
	);

	const liabilities = $derived(
		accounts
			.filter((a) => a.type === 'credit')
			.reduce((sum, a) => sum + a.current_balance, 0)
	);

	const netWorth = $derived(assets - liabilities);

	// Calculate month-over-month change (placeholder: assume 1.9% change, $240 increase)
	const netWorthChangePercent = $derived(1.9);
	const netWorthChangeDollar = $derived(240); // In the future, calculate from historical data

	// 2. Monthly Savings Rate
	const savingsAccounts = $derived(accounts.filter((a) => a.subtype === 'savings'));
	const totalSavings = $derived(
		savingsAccounts.reduce((sum, a) => sum + a.current_balance, 0)
	);

	const incomeTransactions = $derived(
		transactions.filter(
			(t) =>
				t.personal_finance_category_primary === 'INCOME' ||
				t.personal_finance_category_primary.startsWith('INCOME')
		)
	);

	const monthlyIncome = $derived(
		Math.abs(incomeTransactions.reduce((sum, t) => sum + t.amount, 0))
	);

	const monthlySavingsRate = $derived(
		monthlyIncome > 0 ? ((totalSavings / monthlyIncome) * 100).toFixed(1) + '%' : '0%'
	);

	// 3. Credit Health
	const creditAccounts = $derived(accounts.filter((a) => a.type === 'credit'));
	const totalCreditUsed = $derived(
		creditAccounts.reduce((sum, a) => sum + a.current_balance, 0)
	);
	const totalCreditLimit = $derived(
		creditAccounts.reduce((sum, a) => sum + (a.limit || 0), 0)
	);

	const creditUtilization = $derived(
		totalCreditLimit > 0 ? ((totalCreditUsed / totalCreditLimit) * 100).toFixed(1) + '%' : '0%'
	);

	const creditUtilizationValue = $derived(
		totalCreditLimit > 0 ? (totalCreditUsed / totalCreditLimit) * 100 : 0
	);

	const creditVariant = $derived<'standard' | 'success' | 'alert'>(
		creditUtilizationValue < 30 ? 'success' : creditUtilizationValue > 50 ? 'alert' : 'standard'
	);

	// 4. Emergency Fund
	const expenseTransactions = $derived(
		transactions.filter(
			(t) =>
				t.amount > 0 &&
				!t.personal_finance_category_primary.startsWith('INCOME') &&
				!t.personal_finance_category_primary.startsWith('TRANSFER')
		)
	);

	const monthlyExpenses = $derived(expenseTransactions.reduce((sum, t) => sum + t.amount, 0));

	const emergencyFundMonths = $derived(
		monthlyExpenses > 0 ? (totalSavings / monthlyExpenses).toFixed(1) + ' months' : '0 months'
	);

	// 5. Subscriptions
	const merchantCounts = $derived(() => {
		const counts = new Map<string, number>();
		transactions.forEach((t) => {
			if (t.merchant_name) {
				counts.set(t.merchant_name, (counts.get(t.merchant_name) || 0) + 1);
			}
		});
		return counts;
	});

	const subscriptionCount = $derived(() => {
		const counts = merchantCounts();
		return Array.from(counts.values()).filter((count) => count >= 2).length;
	});

	// Persona data for badge
	const personaData = $derived(
		recommendations.length > 0
			? {
					name: recommendations[0].rationale.persona_type
						.split('_')
						.map((w) => w.charAt(0).toUpperCase() + w.slice(1))
						.join(' '),
					type: recommendations[0].rationale.persona_type
				}
			: null
	);

	// === DATA FETCHING ===

	async function loadUserData() {
		if (!selectedUserId) return;

		loading = true;
		error = null;

		try {
			const [accountsData, transactionsData, insightsData] = await Promise.all([
				api.accounts.getUserAccounts(selectedUserId),
				api.transactions.getUserTransactions(selectedUserId, 100, 0),
				api.insights.getUserInsights(selectedUserId, 30)
			]);

			accounts = accountsData;
			transactions = transactionsData;
			recommendations = insightsData.slice(0, 3);
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to load data';
			console.error('Dashboard error:', err);
		} finally {
			loading = false;
		}
	}

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

	onMount(async () => {
		await loadUsers();
		if (selectedUserId) {
			loadUserData();
		}
	});

	// Reload data when user changes (dev mode only)
	$effect(() => {
		if (selectedUserId) {
			loadUserData();
		}
	});
</script>

<div class="min-h-screen bg-gray-50">
	<div class="container mx-auto px-6 py-6 sm:px-8 lg:px-10 max-w-7xl">
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
			<div class="bg-brand-coral/10 border border-brand-coral/30 rounded-lg p-6 text-center">
				<strong class="text-brand-coral block mb-2">Error:</strong>
				<p class="text-brand-coral/90 mb-4">{error}</p>
				<button
					onclick={() => loadUserData()}
					class="px-4 py-2 bg-brand-coral text-white rounded-lg hover:opacity-90 transition-opacity"
				>
					Retry
				</button>
			</div>
		{:else}
			<!-- Direction 6 Layout: Clean Top Bar + Metrics Grid + Recommendations -->

			<!-- Top Bar: Persona Badge (left) + View All Insights button (right) -->
			{#if personaData}
				<div class="bg-white rounded-xl p-6 mb-6 shadow-card flex items-center justify-between">
					<PersonaBadge personaName={personaData.name} personaType={personaData.type} />
					<a href="/insights" class="btn-brand px-5 py-2 rounded-lg text-sm font-medium text-white transition-all hover:shadow-soft">
						View All Insights
					</a>
				</div>
			{/if}

			<!-- Metrics Grid: Featured KPI (2 cols) + 4 supporting KPIs -->
			<section class="mb-12">
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
					<!-- Featured KPI: Net Worth (spans 2 columns) -->
					<div class="col-span-1 md:col-span-2">
						<KpiCard
							variant="featured"
							label="NET WORTH"
							value={formatCurrency(netWorth)}
							change={netWorthChangePercent}
							changeAmount={formatCurrency(netWorthChangeDollar)}
						/>
					</div>

					<!-- Supporting KPIs -->
					<KpiCard label="MONTHLY SAVINGS" value={monthlySavingsRate} />

					<KpiCard variant={creditVariant} label="CREDIT HEALTH" value={creditUtilization} />

					<KpiCard label="EMERGENCY FUND" value={emergencyFundMonths} />

					<KpiCard label="SUBSCRIPTIONS" value={subscriptionCount().toString()} />
				</div>
			</section>

			<!-- Recommendations Section: 3-column grid -->
			<section class="bg-white rounded-xl p-8 shadow-card">
				<h2 class="text-2xl font-semibold text-gray-800 mb-6">Personalized Recommendations</h2>

				{#if recommendations.length > 0}
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						{#each recommendations as rec}
							<RecommendationCard
								icon="💡"
								title={rec.content.title}
								body={rec.content.summary}
								rationale={rec.rationale.explanation}
								cta="Learn More"
							/>
						{/each}
					</div>
				{:else}
					<div class="text-center py-8 text-gray-600">
						<p>No recommendations available at this time.</p>
					</div>
				{/if}
			</section>

			<!-- Dev-only user switcher (bottom of page) -->
			{#if isDev && users.length > 0}
				<div class="mt-8 p-4 bg-gray-800 text-white rounded-lg">
					<div class="flex items-center justify-between">
						<span class="text-xs uppercase tracking-wider font-semibold opacity-75">Dev Mode: Switch User</span>
						<select
							bind:value={selectedUserId}
							class="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							{#each users as user}
								<option value={user.id}>{user.name}</option>
							{/each}
						</select>
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>
