<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { formatCurrency } from '$lib/types';
	import type { Recommendation } from '$lib/types';

	// Svelte 5 runes for reactive state
	let selectedUserId = $state('bdd640fb-0667-4ad1-9c80-317fa3b1799d');
	let recommendations = $state<Recommendation[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedWindow = $state(30);
	let expandedCard = $state<number | null>(null);

	// Available test users
	const testUsers = [
		{ id: 'bdd640fb-0667-4ad1-9c80-317fa3b1799d', name: 'Daniel Doyle' },
		{ id: '97d7a560-adb1-4670-ad9f-b00d4882d73c', name: 'Mr. Andrew Foster' },
		{ id: '37c86152-beed-4af9-80c5-9f30d1031424', name: 'Amber Cooper' },
		{ id: 'dc268108-7140-41a1-afc2-ccfc9db7284b', name: 'Steven Taylor' },
		{ id: 'c7a9f33c-22d8-49d3-b3e4-f986f18cccdc', name: 'Ashley Garcia' }
	];

	// Get persona from first recommendation
	const persona = $derived(recommendations.length > 0 ? recommendations[0].persona : null);
	const confidence = $derived(recommendations.length > 0 ? recommendations[0].confidence : 0);

	// Format persona name for display
	function formatPersona(persona: string): string {
		return persona
			.split('_')
			.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
			.join(' ');
	}

	// Get persona description
	function getPersonaDescription(persona: string): string {
		const descriptions: Record<string, string> = {
			high_utilization:
				'You have high credit card utilization. This affects your credit score and can lead to high interest charges.',
			variable_income:
				'You have variable or irregular income patterns. Building an emergency fund can help smooth out cash flow.',
			subscription_heavy:
				'You have multiple recurring subscriptions. Reviewing and canceling unused subscriptions can save money.',
			savings_builder:
				'You are actively building savings. Keep up the good work and consider optimizing your savings strategy.',
			balanced:
				'Your finances appear balanced. Focus on maintaining good habits and optimizing where possible.'
		};
		return descriptions[persona] || 'Financial profile analysis based on your transaction patterns.';
	}

	// Fetch insights for selected user
	async function loadInsights() {
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

	// Load data on mount
	onMount(() => {
		loadInsights();
	});

	// Reload when user or window selection changes
	$effect(() => {
		if (selectedUserId || selectedWindow) {
			loadInsights();
		}
	});

	function toggleCard(index: number) {
		expandedCard = expandedCard === index ? null : index;
	}
</script>

<div class="min-h-screen bg-background">
	<div class="container mx-auto px-4 py-8 sm:px-6 lg:px-8 max-w-7xl">
		<!-- Header -->
		<header class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
			<h1 class="text-3xl font-bold text-foreground">Financial Insights</h1>

			<div class="flex flex-col sm:flex-row gap-4">
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

				<div class="flex items-center gap-2">
					<label for="window-select" class="text-sm font-medium text-muted-foreground">Period:</label>
					<select
						id="window-select"
						bind:value={selectedWindow}
						class="px-4 py-2 border border-border rounded-lg bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
					>
						<option value={30}>Last 30 Days</option>
						<option value={180}>Last 180 Days</option>
					</select>
				</div>
			</div>
		</header>

		{#if loading}
			<div class="flex items-center justify-center py-16">
				<div class="text-center space-y-3">
					<div
						class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"
					></div>
					<p class="text-muted-foreground">Analyzing your financial patterns...</p>
				</div>
			</div>
		{:else if error}
			<div class="bg-destructive/10 border border-destructive/30 rounded-lg p-6 text-center">
				<strong class="text-destructive block mb-2">Error:</strong>
				<p class="text-destructive/90 mb-4">{error}</p>
				<button
					onclick={() => loadInsights()}
					class="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors"
				>
					Retry
				</button>
			</div>
		{:else if recommendations.length === 0}
			<div class="bg-card rounded-lg border border-border p-12 text-center">
				<h2 class="text-xl font-semibold text-foreground mb-2">No Insights Available</h2>
				<p class="text-muted-foreground">
					We need more transaction data to generate personalized recommendations.
				</p>
			</div>
		{:else}
			<div class="space-y-8">
				<!-- Persona Display -->
				{#if persona}
					<section class="bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg border border-primary/20 p-8 shadow-sm">
						<div class="flex items-start justify-between mb-4">
							<h2 class="text-2xl font-bold text-foreground">Your Financial Persona</h2>
							<span class="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm font-medium">
								{Math.round(confidence * 100)}% Confidence
							</span>
						</div>

						<h3 class="text-3xl font-bold text-primary mb-3">{formatPersona(persona)}</h3>
						<p class="text-lg text-foreground/80 mb-6">{getPersonaDescription(persona)}</p>

						{#if recommendations[0].rationale.key_signals.length > 0}
							<div class="border-t border-primary/20 pt-4 mt-4">
								<p class="text-sm font-medium text-muted-foreground mb-2">Based on:</p>
								<ul class="flex flex-wrap gap-2">
									{#each recommendations[0].rationale.key_signals as signal}
										<li class="px-3 py-1 bg-card border border-border rounded-full text-sm">
											{signal.replace(/_/g, ' ')}
										</li>
									{/each}
								</ul>
							</div>
						{/if}
					</section>
				{/if}

				<!-- Recommendations Grid -->
				<section>
					<h2 class="text-2xl font-bold text-foreground mb-6">Personalized Recommendations</h2>

					<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
						{#each recommendations as rec, index}
							<article class="bg-card rounded-lg border border-border shadow-sm overflow-hidden flex flex-col">
								<div class="p-6 flex-1">
									<div class="flex items-start justify-between mb-3">
										<h3 class="text-lg font-semibold text-foreground flex-1 pr-2">{rec.content.title}</h3>
										<span class="px-2 py-1 bg-primary/10 text-primary rounded text-xs font-medium whitespace-nowrap">
											{Math.round(rec.content.relevance_score * 100)}% Match
										</span>
									</div>

									<p class="text-sm text-muted-foreground mb-4">{rec.content.summary}</p>

									{#if expandedCard === index}
										<div class="space-y-4">
											<div class="text-sm text-foreground/90">
												{rec.content.body}
											</div>

											<div class="bg-accent/50 rounded-lg p-4">
												<h4 class="text-sm font-semibold text-foreground mb-2">Why this matters for you:</h4>
												<p class="text-sm text-foreground/80">{rec.rationale.explanation}</p>
											</div>

											<div class="border-t border-border pt-4">
												<strong class="text-sm text-primary">{rec.content.cta}</strong>
											</div>

											<div class="text-xs text-muted-foreground">
												Source: {rec.content.source}
											</div>
										</div>
									{/if}
								</div>

								<button
									onclick={() => toggleCard(index)}
									class="w-full px-6 py-3 bg-muted hover:bg-accent text-foreground font-medium transition-colors border-t border-border"
								>
									{expandedCard === index ? 'Show Less ↑' : 'Read More ↓'}
								</button>
							</article>
						{/each}
					</div>
				</section>
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
