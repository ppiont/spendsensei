<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency } from '$lib/types';
	import type { Account, Transaction, Recommendation } from '$lib/types';
	import KpiCard from '$lib/components/custom/KpiCard.svelte';
	import RecommendationCard from '$lib/components/custom/RecommendationCard.svelte';
	import PersonaBadge from '$lib/components/custom/PersonaBadge.svelte';
	import ConsentCTA from '$lib/components/ConsentCTA.svelte';
	import { ChevronDown, ChevronUp, Info } from '@lucide/svelte';

	// Svelte 5 runes for reactive state
	let accounts = $state<Account[]>([]);
	let transactions = $state<Transaction[]>([]);
	let recommendations = $state<Recommendation[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// User selection from global store
	import { selectedUserId } from '$lib/stores/userStore';
	let currentUserId = $state('');

	// Subscribe to user store
	selectedUserId.subscribe(value => {
		currentUserId = value;
	});

	// Expandable consent prompt state
	let showConsentDetails = $state(false);

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
		if (!currentUserId) return;

		loading = true;
		error = null;

		try {
			// Load accounts and transactions (always available)
			const [accountsData, transactionsData] = await Promise.all([
				api.accounts.getUserAccounts(currentUserId),
				api.transactions.getUserTransactions(currentUserId, 100, 0)
			]);

			accounts = accountsData;
			transactions = transactionsData;

			// Try to fetch insights, but don't fail if consent required
			try {
				const insightsData = await api.insights.getUserInsights(currentUserId, 30);
				if (!insightsData.consent_required) {
					recommendations = insightsData.education_recommendations.slice(0, 3);
				} else {
					recommendations = [];
				}
			} catch (err) {
				console.log('Insights not available:', err);
				recommendations = [];
			}
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to load data';
			console.error('Dashboard error:', err);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		if (currentUserId) {
			loadUserData();
		}
	});

	// Reload data when user changes
	$effect(() => {
		if (currentUserId) {
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

			<!-- Top Bar: Persona Badge (only if have recommendations) -->
			{#if personaData && recommendations.length > 0}
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

			<!-- Recommendations Section: 3-column grid OR consent prompt -->
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
				{:else if currentUserId}
					<!-- Inline Consent Prompt -->
					<div class="bg-gradient-to-br from-brand-blue/5 to-brand-green/5 border-2 border-brand-blue/20 rounded-xl p-8 text-center max-w-3xl mx-auto">
						<div class="w-16 h-16 bg-brand-blue/10 rounded-full flex items-center justify-center mx-auto mb-4">
							<span class="text-3xl">🔓</span>
						</div>
						<h3 class="text-xl font-bold text-gray-800 mb-2">Unlock AI-Powered Insights</h3>
						<p class="text-gray-600 mb-6">
							Enable insights to receive personalized financial recommendations based on your spending patterns
						</p>

						<!-- Quick Benefits -->
						<div class="flex flex-wrap gap-4 justify-center mb-6 text-sm text-gray-700">
							<div class="flex items-center gap-2">
								<span class="text-brand-green">✓</span>
								<span>Your Financial Personality</span>
							</div>
							<div class="flex items-center gap-2">
								<span class="text-brand-green">✓</span>
								<span>3 Tailored Recommendations</span>
							</div>
							<div class="flex items-center gap-2">
								<span class="text-brand-green">✓</span>
								<span>Partner Offers</span>
							</div>
						</div>

						<!-- Expandable Details -->
						<button
							onclick={() => (showConsentDetails = !showConsentDetails)}
							class="flex items-center gap-2 mx-auto mb-6 text-brand-blue font-medium hover:text-blue-dark transition-colors"
						>
							{showConsentDetails ? 'Show less' : 'Learn more about insights'}
							{#if showConsentDetails}
								<ChevronUp class="w-4 h-4" />
							{:else}
								<ChevronDown class="w-4 h-4" />
							{/if}
						</button>

						{#if showConsentDetails}
							<div class="bg-white rounded-lg p-6 mb-6 text-left">
								<h4 class="font-semibold text-gray-800 mb-4 flex items-center gap-2">
									<Info class="w-5 h-5 text-brand-blue" />
									What you'll get:
								</h4>
								<ul class="space-y-3 mb-6">
									<li class="flex items-start gap-3">
										<span class="text-brand-green mt-1">✓</span>
										<span class="text-sm text-gray-700">
											<strong>Your Financial Personality</strong> - Discover your unique spending and saving patterns
										</span>
									</li>
									<li class="flex items-start gap-3">
										<span class="text-brand-green mt-1">✓</span>
										<span class="text-sm text-gray-700">
											<strong>3 Personalized Recommendations</strong> - Education tailored to your financial situation
										</span>
									</li>
									<li class="flex items-start gap-3">
										<span class="text-brand-green mt-1">✓</span>
										<span class="text-sm text-gray-700">
											<strong>Partner Offers You Qualify For</strong> - Vetted products that match your needs
										</span>
									</li>
									<li class="flex items-start gap-3">
										<span class="text-brand-green mt-1">✓</span>
										<span class="text-sm text-gray-700">
											<strong>Plain-Language Explanations</strong> - Clear rationales for every recommendation
										</span>
									</li>
								</ul>

								<div class="p-4 bg-blue-50 border-l-4 border-brand-blue rounded mb-4">
									<p class="text-xs text-gray-600 leading-relaxed">
										<strong>How it works:</strong> We'll analyze your transaction patterns to identify your financial personality
										and provide relevant educational content. You can revoke consent anytime in account settings.
										This is educational content only - not financial advice.
									</p>
								</div>

								<p class="text-xs text-gray-500 text-center italic">
									Note: This is a demo application. All data is synthetic and consent is simulated.
								</p>
							</div>
						{/if}

						<a href="/insights" class="inline-block px-6 py-3 bg-brand-blue text-white rounded-lg font-semibold hover:bg-blue-dark transition-colors">
							Enable Insights
						</a>
						<p class="text-xs text-gray-500 mt-4">This is educational content only - not financial advice</p>
					</div>
				{:else}
					<div class="text-center py-8 text-gray-600">
						<p>No recommendations available at this time.</p>
					</div>
				{/if}
			</section>

		{/if}
	</div>
</div>
