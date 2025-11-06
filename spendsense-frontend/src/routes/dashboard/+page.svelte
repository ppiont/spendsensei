<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency } from '$lib/types';
	import type { Account, Transaction, Recommendation, OfferRecommendation } from '$lib/types';

	// Components
	import KpiCard from '$lib/components/custom/KpiCard.svelte';
	import RecommendationCard from '$lib/components/custom/RecommendationCard.svelte';
	import SpendingBreakdown from '$lib/components/custom/SpendingBreakdown.svelte';
	import CashFlowSummary from '$lib/components/custom/CashFlowSummary.svelte';
	import PersonaCard from '$lib/components/custom/PersonaCard.svelte';
	import RecentActivity from '$lib/components/custom/RecentActivity.svelte';
	import ConsentCTA from '$lib/components/ConsentCTA.svelte';
	import { Alert, AlertDescription } from '$lib/components/ui/alert';
	import { Info, ExternalLink, CheckCircle, ChevronDown, ChevronUp } from '@lucide/svelte';

	// User selection from global store
	import { selectedUserId } from '$lib/stores/userStore';
	let currentUserId = $state('');
	selectedUserId.subscribe(value => {
		currentUserId = value;
	});

	// State
	let accounts = $state<Account[]>([]);
	let transactions = $state<Transaction[]>([]);
	let recommendations = $state<Recommendation[]>([]);
	let offers = $state<OfferRecommendation[]>([]);
	let personaType = $state<string | null>(null);
	let personaConfidence = $state<number>(0);
	let personaExplanation = $state<string>('');
	let keySignals = $state<string[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let consentRequired = $state(false);

	// Expandable offer states
	let expandedOfferIds = $state<Set<string>>(new Set());

	function toggleOfferExpanded(id: string) {
		if (expandedOfferIds.has(id)) {
			expandedOfferIds.delete(id);
		} else {
			expandedOfferIds.add(id);
		}
		expandedOfferIds = expandedOfferIds; // Trigger reactivity
	}

	// === KPI CALCULATIONS ===
	const assets = $derived(
		accounts.filter((a) => a.type === 'depository').reduce((sum, a) => sum + a.current_balance, 0)
	);

	const liabilities = $derived(
		accounts.filter((a) => a.type === 'credit').reduce((sum, a) => sum + a.current_balance, 0)
	);

	const netWorth = $derived(assets - liabilities);

	const savingsAccounts = $derived(accounts.filter((a) => a.subtype === 'savings'));
	const totalSavings = $derived(
		savingsAccounts.reduce((sum, a) => sum + a.current_balance, 0)
	);

	// Filter transactions to last 30 days
	const recentTransactions = $derived(() => {
		const now = new Date();
		const windowDate = new Date(now);
		windowDate.setDate(windowDate.getDate() - 30);
		windowDate.setHours(0, 0, 0, 0);

		return transactions.filter((t) => {
			const txDate = new Date(t.date);
			return txDate >= windowDate;
		});
	});

	const incomeTransactions = $derived(
		recentTransactions().filter(
			(t) =>
				t.personal_finance_category_primary === 'INCOME' ||
				t.personal_finance_category_primary.startsWith('INCOME')
		)
	);

	const monthlyIncome = $derived(Math.abs(incomeTransactions.reduce((sum, t) => sum + t.amount, 0)));

	const creditAccounts = $derived(accounts.filter((a) => a.type === 'credit'));
	const totalCreditUsed = $derived(creditAccounts.reduce((sum, a) => sum + a.current_balance, 0));
	const totalCreditLimit = $derived(creditAccounts.reduce((sum, a) => sum + (a.limit || 0), 0));
	const creditUtilization = $derived(
		totalCreditLimit > 0 ? ((totalCreditUsed / totalCreditLimit) * 100).toFixed(1) + '%' : '0%'
	);
	const creditUtilizationValue = $derived(
		totalCreditLimit > 0 ? (totalCreditUsed / totalCreditLimit) * 100 : 0
	);
	const creditVariant = $derived<'standard' | 'success' | 'alert'>(
		creditUtilizationValue < 30 ? 'success' : creditUtilizationValue > 50 ? 'alert' : 'standard'
	);

	const expenseTransactions = $derived(
		recentTransactions().filter(
			(t) =>
				t.amount > 0 &&
				!t.personal_finance_category_primary.startsWith('INCOME') &&
				!t.personal_finance_category_primary.startsWith('TRANSFER')
		)
	);
	const monthlyExpenses = $derived(expenseTransactions.reduce((sum, t) => sum + t.amount, 0));

	// Calculate actual monthly savings rate (income - expenses) / income
	const monthlySavingsRate = $derived(
		monthlyIncome > 0 ? (((monthlyIncome - monthlyExpenses) / monthlyIncome) * 100).toFixed(1) + '%' : '0%'
	);

	// Calculate net worth change over last 30 days
	const netWorthChange = $derived(monthlyIncome - monthlyExpenses);
	const netWorth30DaysAgo = $derived(netWorth - netWorthChange);
	const netWorthChangeDollar = $derived(netWorthChange);
	const netWorthChangePercent = $derived(
		netWorth30DaysAgo !== 0 ? parseFloat(((netWorthChange / Math.abs(netWorth30DaysAgo)) * 100).toFixed(1)) : 0
	);

	const emergencyFundMonths = $derived(
		monthlyExpenses > 0 ? (totalSavings / monthlyExpenses).toFixed(1) + ' months' : '0 months'
	);

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

	// === DATA FETCHING ===
	async function loadUserData() {
		if (!currentUserId) return;

		loading = true;
		error = null;

		try {
			const [accountsData, transactionsData] = await Promise.all([
				api.accounts.getUserAccounts(currentUserId),
				api.transactions.getUserTransactions(currentUserId, 500, 0)
			]);

			accounts = accountsData;
			transactions = transactionsData;

			// Try to fetch insights
			try {
				const insightsData = await api.insights.getUserInsights(currentUserId, 30);
				if (insightsData.consent_required) {
					consentRequired = true;
					recommendations = [];
					offers = [];
					personaType = null;
				} else {
					consentRequired = false;
					recommendations = insightsData.education_recommendations || [];
					offers = insightsData.offer_recommendations || [];
					personaType = insightsData.persona_type;
					personaConfidence = insightsData.confidence;

					if (recommendations.length > 0) {
						personaExplanation = recommendations[0].rationale.explanation;
						keySignals = recommendations[0].rationale.key_signals;
					}
				}
			} catch (err) {
				console.log('Insights not available:', err);
				consentRequired = true;
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

	$effect(() => {
		if (currentUserId) {
			loadUserData();
		}
	});
</script>

<div class="dashboard-page">
	<div class="dashboard-container">
		{#if loading}
			<div class="loading-state">
				<div class="spinner"></div>
				<p>Loading your financial data...</p>
			</div>
		{:else if error}
			<div class="error-state">
				<Alert variant="destructive">
					<AlertDescription>
						<strong>Error:</strong> {error}
						<button onclick={() => loadUserData()} class="retry-button">Retry</button>
					</AlertDescription>
				</Alert>
			</div>
		{:else}
			<!-- SECTION 1: FINANCIAL SNAPSHOT -->
			<section class="dashboard-section">
				<h2 class="section-title">Financial Snapshot</h2>
				<div class="kpi-grid">
					<!-- Net Worth (Featured) -->
					<div class="featured-kpi">
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

			<!-- SECTION 2: SPENDING INSIGHTS -->
			<section class="dashboard-section">
				<h2 class="section-title">Spending Insights</h2>
				<div class="section-card">
					<SpendingBreakdown {transactions} window={30} />
				</div>
			</section>

			<!-- SECTION 3: CASH FLOW -->
			<section class="dashboard-section">
				<h2 class="section-title">Cash Flow</h2>
				<div class="section-card">
					<CashFlowSummary {transactions} window={30} />
				</div>
			</section>

			<!-- SECTION 4: YOUR FINANCIAL PERSONALITY -->
			{#if !consentRequired && personaType}
				<section class="dashboard-section">
					<h2 class="section-title">Your Financial Personality</h2>
					<PersonaCard
						{personaType}
						confidence={personaConfidence}
						explanation={personaExplanation}
						{keySignals}
					/>
				</section>
			{/if}

			<!-- SECTION 5: PARTNER OFFERS -->
			{#if !consentRequired && offers.length > 0}
				<section class="dashboard-section">
					<div class="section-header">
						<h2 class="section-title">Partner Offers</h2>
						<span class="offers-badge">{offers.length} {offers.length === 1 ? 'Offer' : 'Offers'} Available</span>
					</div>
					<div class="offers-grid">
						{#each offers as offerRec}
							{@const offer = offerRec.offer}
							{@const isExpanded = expandedOfferIds.has(offer.id)}
							<div class="offer-card">
								<div class="offer-header">
									<div class="offer-title-section">
										<h3 class="offer-title">{offer.title}</h3>
										<p class="offer-provider">{offer.provider}</p>
									</div>
									<CheckCircle class="w-5 h-5 text-brand-green" />
								</div>
								<p class="offer-summary">{offer.summary}</p>

								<div class="offer-benefits">
									<h4 class="benefits-heading">Key Benefits:</h4>
									<ul class="benefits-list">
										{#each offer.benefits as benefit}
											<li><span class="check-icon">✓</span> {benefit}</li>
										{/each}
									</ul>
								</div>

								<button onclick={() => toggleOfferExpanded(offer.id)} class="eligibility-button">
									<span>Eligibility</span>
									{#if isExpanded}<ChevronUp class="w-4 h-4" />{:else}<ChevronDown class="w-4 h-4" />{/if}
								</button>

								{#if isExpanded}
									<div class="eligibility-content">
										<p>{offer.eligibility_explanation}</p>
									</div>
								{/if}

								<a href={offer.cta_url} target="_blank" rel="noopener noreferrer" class="offer-cta">
									{offer.cta} <ExternalLink class="w-4 h-4" />
								</a>

								<p class="offer-disclaimer">{offer.disclaimer}</p>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- SECTION 6: RECENT ACTIVITY -->
			<section class="dashboard-section">
				<h2 class="section-title">Recent Activity</h2>
				<div class="section-card">
					<RecentActivity {transactions} limit={5} />
				</div>
			</section>

			<!-- SECTION 7: PERSONALIZED EDUCATION -->
			{#if consentRequired}
				<section class="dashboard-section">
					<h2 class="section-title">Personalized Education</h2>
					<ConsentCTA userId={currentUserId} />
				</section>
			{:else if recommendations.length > 0}
				<section class="dashboard-section">
					<h2 class="section-title">Personalized Education</h2>
					<div class="recommendations-grid">
						{#each recommendations.slice(0, 3) as rec}
							<RecommendationCard
								icon="💡"
								title={rec.content.title}
								body={rec.content.summary}
								rationale={rec.rationale.explanation}
								cta="Learn More"
							/>
						{/each}
					</div>
				</section>
			{/if}

			<!-- SECTION 8: DISCLAIMER -->
			<section class="dashboard-section disclaimer-section">
				<Alert>
					<Info class="w-5 h-5" />
					<AlertDescription>
						<p class="disclaimer-text">
							<strong>Educational Content:</strong> This is educational content, not financial advice. Please
							consult with a qualified financial professional before making financial decisions.
						</p>
						{#if offers.length > 0}
							<p class="disclaimer-text mt-2">
								<strong>Partner Offers:</strong> Offers are provided by SpendSense partners and are subject
								to their terms and conditions. Eligibility determinations are estimates based on your financial profile.
							</p>
						{/if}
					</AlertDescription>
				</Alert>
			</section>
		{/if}
	</div>
</div>

<style>
	.dashboard-page {
		min-height: 100vh;
		background-color: #f9fafb; /* gray-50 */
	}

	.dashboard-container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem 1.5rem;
	}

	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem;
		gap: 1rem;
	}

	.spinner {
		width: 3rem;
		height: 3rem;
		border: 4px solid #e5e7eb;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.error-state {
		padding: 2rem;
	}

	.retry-button {
		margin-left: 1rem;
		padding: 0.5rem 1rem;
		background-color: #3b82f6;
		color: white;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
	}

	.dashboard-section {
		margin-bottom: 3rem;
	}

	.section-title {
		font-size: 1.5rem;
		font-weight: 600;
		color: #1f2937;
		margin-bottom: 1.5rem;
	}

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1.5rem;
	}

	.offers-badge {
		padding: 0.5rem 1rem;
		background-color: #d1fae5;
		color: #065f46;
		font-size: 0.875rem;
		font-weight: 600;
		border-radius: 9999px;
	}

	.section-card {
		background: white;
		border-radius: 0.75rem;
		padding: 2rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}

	.kpi-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1.5rem;
	}

	.featured-kpi {
		grid-column: span 2;
	}

	.recommendations-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1.5rem;
	}

	.offers-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1.5rem;
	}

	.offer-card {
		background: white;
		border: 2px solid #d1fae5;
		border-radius: 0.75rem;
		padding: 1.5rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		transition: border-color 0.15s ease;
	}

	.offer-card:hover {
		border-color: #10b981;
	}

	.offer-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1rem;
	}

	.offer-title-section {
		flex: 1;
	}

	.offer-title {
		font-size: 1.125rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0 0 0.25rem 0;
	}

	.offer-provider {
		font-size: 0.875rem;
		color: #6b7280;
		margin: 0;
	}

	.offer-summary {
		font-size: 0.875rem;
		color: #374151;
		margin: 0 0 1rem 0;
		line-height: 1.5;
	}

	.offer-benefits {
		margin-bottom: 1rem;
	}

	.benefits-heading {
		font-size: 0.875rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0 0 0.5rem 0;
	}

	.benefits-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.benefits-list li {
		font-size: 0.875rem;
		color: #374151;
		display: flex;
		align-items: flex-start;
		gap: 0.5rem;
	}

	.check-icon {
		color: #10b981;
		font-weight: bold;
		flex-shrink: 0;
	}

	.eligibility-button {
		width: 100%;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem;
		background-color: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 0.5rem;
		cursor: pointer;
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
		margin-bottom: 1rem;
		transition: background-color 0.15s ease;
	}

	.eligibility-button:hover {
		background-color: #f3f4f6;
	}

	.eligibility-content {
		padding: 0.75rem 1rem;
		background-color: #eff6ff;
		border-radius: 0.5rem;
		margin-bottom: 1rem;
	}

	.eligibility-content p {
		font-size: 0.875rem;
		color: #374151;
		line-height: 1.5;
		margin: 0;
	}

	.offer-cta {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.75rem;
		background-color: #10b981;
		color: white;
		border-radius: 0.5rem;
		text-decoration: none;
		font-weight: 500;
		font-size: 0.875rem;
		transition: background-color 0.15s ease;
		margin-bottom: 0.75rem;
	}

	.offer-cta:hover {
		background-color: #059669;
	}

	.offer-disclaimer {
		font-size: 0.75rem;
		color: #6b7280;
		line-height: 1.4;
		margin: 0;
	}

	.disclaimer-section {
		margin-bottom: 2rem;
	}

	.disclaimer-text {
		font-size: 0.875rem;
		line-height: 1.5;
		margin: 0;
	}

	.mt-2 {
		margin-top: 0.5rem;
	}

	/* Responsive */
	@media (max-width: 1024px) {
		.kpi-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.recommendations-grid,
		.offers-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (max-width: 768px) {
		.dashboard-container {
			padding: 1.5rem 1rem;
		}

		.kpi-grid,
		.recommendations-grid,
		.offers-grid {
			grid-template-columns: 1fr;
		}

		.featured-kpi {
			grid-column: span 1;
		}

		.section-card {
			padding: 1.5rem;
		}
	}
</style>
