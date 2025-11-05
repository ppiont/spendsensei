<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency } from '$lib/types';
	import type { Recommendation } from '$lib/types';
	import PersonaBadge from '$lib/components/custom/PersonaBadge.svelte';
	import RecommendationCard from '$lib/components/custom/RecommendationCard.svelte';
	import { ChevronDown, ChevronUp, Info } from '@lucide/svelte';

	// Dev mode user switching (only in development)
	const isDev = import.meta.env.DEV;
	let users = $state<Array<{ id: string; name: string }>>([]);
	let selectedUserId = $state('');

	// State
	let recommendations = $state<Recommendation[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedWindow = $state(30);
	let expandedIds = $state<Set<string>>(new Set());
	let showPersonaDetails = $state(false);

	// Derived persona data
	const personaData = $derived(
		recommendations.length > 0
			? {
					name: recommendations[0].rationale.persona_type
						.split('_')
						.map((w) => w.charAt(0).toUpperCase() + w.slice(1))
						.join(' '),
					type: recommendations[0].rationale.persona_type,
					explanation: recommendations[0].rationale.explanation,
					confidence: recommendations[0].rationale.confidence,
					keySignals: recommendations[0].rationale.key_signals
				}
			: null
	);

	// Get detailed persona description
	function getPersonaDetails(type: string): { whatItMeans: string; whyItMatters: string } {
		const details: Record<string, { whatItMeans: string; whyItMatters: string }> = {
			savings_builder: {
				whatItMeans:
					'You consistently set aside money each month and maintain low credit utilization. Your financial habits show discipline and long-term thinking.',
				whyItMatters:
					'This persona means you're on track to build wealth over time. We'll focus your education on optimizing savings strategies, investment opportunities, and accelerating your financial goals.'
			},
			high_utilization: {
				whatItMeans:
					'Your credit cards are carrying high balances relative to your credit limits. This can impact your credit score and lead to significant interest charges.',
				whyItMatters:
					'High utilization is costing you money in interest and may be limiting your credit options. We'll help you understand strategies to pay down balances and improve your credit health.'
			},
			variable_income: {
				whatItMeans:
					'Your income fluctuates from month to month, which can make budgeting and planning more challenging than with a steady paycheck.',
				whyItMatters:
					'Variable income requires different financial strategies than traditional employment. We'll focus on building cash reserves, smoothing expenses, and planning for irregular income patterns.'
			},
			subscription_heavy: {
				whatItMeans:
					'You have multiple recurring subscriptions and services that automatically charge your accounts each month.',
				whyItMatters:
					'Subscriptions can quietly drain your budget. Even small recurring charges add up to significant annual costs. We'll help you audit and optimize your subscriptions to free up money for your priorities.'
			},
			balanced: {
				whatItMeans:
					'Your finances show healthy patterns across multiple areas: manageable credit usage, consistent income, and reasonable spending.',
				whyItMatters:
					'You have a solid financial foundation. We'll focus on fine-tuning your approach, identifying optimization opportunities, and helping you maintain these good habits long-term.'
			}
		};
		return (
			details[type] || {
				whatItMeans: 'Your financial profile is based on analysis of your transaction patterns.',
				whyItMatters:
					'We use behavioral signals to provide relevant financial education tailored to your situation.'
			}
		);
	}

	// Toggle expanded card
	function toggleExpanded(id: string) {
		if (expandedIds.has(id)) {
			expandedIds.delete(id);
			expandedIds = expandedIds; // Trigger reactivity
		} else {
			expandedIds.add(id);
			expandedIds = expandedIds; // Trigger reactivity
		}
	}

	// Fetch insights for selected user
	async function loadInsights() {
		if (!selectedUserId) return;

		loading = true;
		error = null;

		try {
			const data = await api.insights.getUserInsights(selectedUserId, selectedWindow);
			recommendations = data;
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to load insights';
			console.error('Insights error:', err);
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
			loadInsights();
		}
	});

	// Reload when user or window selection changes
	$effect(() => {
		if (selectedUserId) {
			loadInsights();
		}
	});
</script>

<div class="min-h-screen bg-gray-50">
	<div class="container mx-auto px-6 py-6 sm:px-8 lg:px-10 max-w-7xl">
		{#if loading}
			<!-- Loading Skeletons -->
			<div class="space-y-8 animate-pulse">
				<!-- Persona skeleton -->
				<div class="bg-white rounded-xl p-12 shadow-card">
					<div class="flex items-center gap-4 mb-6">
						<div class="w-18 h-18 rounded-full bg-gray-200"></div>
						<div class="flex-1">
							<div class="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
							<div class="h-4 bg-gray-200 rounded w-1/2"></div>
						</div>
					</div>
					<div class="space-y-2">
						<div class="h-4 bg-gray-200 rounded w-full"></div>
						<div class="h-4 bg-gray-200 rounded w-5/6"></div>
					</div>
				</div>

				<!-- Recommendation card skeletons -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{#each [1, 2, 3] as _}
						<div class="bg-white rounded-lg p-8 shadow-card">
							<div class="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
							<div class="space-y-2 mb-4">
								<div class="h-4 bg-gray-200 rounded w-full"></div>
								<div class="h-4 bg-gray-200 rounded w-full"></div>
								<div class="h-4 bg-gray-200 rounded w-2/3"></div>
							</div>
							<div class="h-16 bg-gray-100 rounded"></div>
						</div>
					{/each}
				</div>
			</div>
		{:else if error}
			<div class="bg-brand-coral/10 border border-brand-coral/30 rounded-lg p-6 text-center">
				<strong class="text-brand-coral block mb-2">Error:</strong>
				<p class="text-brand-coral/90 mb-4">{error}</p>
				<button
					onclick={() => loadInsights()}
					class="px-4 py-2 bg-brand-coral text-white rounded-lg hover:opacity-90 transition-opacity"
				>
					Retry
				</button>
			</div>
		{:else if recommendations.length === 0}
			<div class="bg-white rounded-lg p-12 text-center shadow-card">
				<h2 class="text-xl font-semibold text-gray-800 mb-2">No Insights Available</h2>
				<p class="text-gray-600">
					We need more transaction data to generate personalized recommendations.
				</p>
			</div>
		{:else}
			<!-- Direction 6 Layout: Hero Persona Section + Recommendations -->

			<!-- Hero Persona Section -->
			{#if personaData}
				<section class="bg-white rounded-xl p-12 mb-12 shadow-card">
					<!-- Top row: PersonaBadge (left) + Window selector tabs (right) -->
					<div class="flex items-start justify-between mb-8">
						<div class="flex-1">
							<PersonaBadge personaName={personaData.name} personaType={personaData.type} />
						</div>

						<!-- Window selector tabs -->
						<div class="flex bg-gray-100 rounded-lg p-1">
							<button
								onclick={() => (selectedWindow = 30)}
								class={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
									selectedWindow === 30
										? 'bg-brand-blue text-white shadow-sm'
										: 'text-gray-600 hover:text-gray-800'
								}`}
							>
								30 Days
							</button>
							<button
								onclick={() => (selectedWindow = 180)}
								class={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
									selectedWindow === 180
										? 'bg-brand-blue text-white shadow-sm'
										: 'text-gray-600 hover:text-gray-800'
								}`}
							>
								180 Days
							</button>
						</div>
					</div>

					<!-- Persona description -->
					<p class="text-base text-gray-600 leading-relaxed mb-6 max-w-3xl">
						{personaData.explanation}
					</p>

					<!-- "What this means" expandable accordion -->
					<button
						onclick={() => (showPersonaDetails = !showPersonaDetails)}
						class="flex items-center gap-2 text-brand-blue font-medium hover:text-blue-dark transition-colors"
					>
						{showPersonaDetails ? 'Hide details' : 'What this means for you'}
						{#if showPersonaDetails}
							<ChevronUp class="w-4 h-4" />
						{:else}
							<ChevronDown class="w-4 h-4" />
						{/if}
					</button>

					{#if showPersonaDetails}
						<div class="mt-6 p-6 bg-gray-50 rounded-lg space-y-4">
							<div>
								<h4 class="font-semibold text-gray-800 mb-2">What it means:</h4>
								<p class="text-gray-600 leading-relaxed">
									{getPersonaDetails(personaData.type).whatItMeans}
								</p>
							</div>
							<div>
								<h4 class="font-semibold text-gray-800 mb-2">Why it matters:</h4>
								<p class="text-gray-600 leading-relaxed">
									{getPersonaDetails(personaData.type).whyItMatters}
								</p>
							</div>

							{#if personaData.keySignals && personaData.keySignals.length > 0}
								<div>
									<h4 class="font-semibold text-gray-800 mb-2">Based on these signals:</h4>
									<ul class="flex flex-wrap gap-2">
										{#each personaData.keySignals as signal}
											<li class="px-3 py-1 bg-white border border-gray-200 rounded-full text-sm text-gray-700">
												{signal.replace(/_/g, ' ')}
											</li>
										{/each}
									</ul>
								</div>
							{/if}
						</div>
					{/if}
				</section>
			{/if}

			<!-- Recommendations Section -->
			<section class="mb-12">
				<h2 class="text-2xl font-semibold text-gray-800 mb-6">Personalized Recommendations</h2>

				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{#each recommendations as rec}
						<RecommendationCard
							icon="💡"
							title={rec.content.title}
							body={rec.content.summary}
							rationale={rec.rationale.explanation}
							cta="Learn More"
							expanded={expandedIds.has(rec.recommendation_id)}
							onclick={() => toggleExpanded(rec.recommendation_id)}
						/>
					{/each}
				</div>
			</section>

			<!-- Educational Disclaimer -->
			<div class="bg-blue-50 border-l-4 border-brand-blue rounded-lg p-6 flex items-start gap-3">
				<Info class="w-5 h-5 text-brand-blue flex-shrink-0 mt-0.5" />
				<p class="text-sm text-gray-700">
					<strong class="font-semibold">Educational Content:</strong> This is educational content, not
					financial advice. Please consult with a qualified financial professional before making
					financial decisions.
				</p>
			</div>

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
