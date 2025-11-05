<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { InspectUserResponse } from '$lib/types';

	// User selection from global store
	import { selectedUserId } from '$lib/stores/userStore';
	let currentUserId = $state('');

	// Subscribe to user store
	selectedUserId.subscribe(value => {
		currentUserId = value;
	});

	// Svelte 5 runes for reactive state
	let inspectData = $state<InspectUserResponse | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let selectedWindow = $state(30);

	// Get derived data
	const hasConsent = $derived(inspectData?.consent_status || false);
	const hasPersona = $derived(inspectData?.persona_type !== null && inspectData?.persona_type !== undefined);
	const recommendations = $derived(inspectData?.education_recommendations || []);
	const offers = $derived(inspectData?.offer_recommendations || []);

	// Format JSON for display
	function formatJSON(obj: any): string {
		return JSON.stringify(obj, null, 2);
	}

	// Fetch user data for inspection
	async function inspectUser() {
		if (!currentUserId) return;

		loading = true;
		error = null;

		try {
			const data = await api.operator.inspectUser(currentUserId, selectedWindow);
			inspectData = data;
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to load data';
			console.error('Operator view error:', err);
		} finally {
			loading = false;
		}
	}

	// Load data on mount
	onMount(() => {
		if (currentUserId) {
			inspectUser();
		}
	});

	// Reload when user or window changes
	$effect(() => {
		if (currentUserId) {
			inspectUser();
		}
	});
</script>

<div class="min-h-screen bg-background">
	<div class="container mx-auto px-4 py-8 sm:px-6 lg:px-8 max-w-7xl">
		<!-- Header -->
		<header class="mb-8">
			<div class="flex items-center gap-3 mb-2">
				<span class="text-4xl">🔧</span>
				<h1 class="text-3xl font-bold text-foreground">Operator View</h1>
			</div>
			<p class="text-muted-foreground">
				Internal inspection tool for verifying recommendation system traceability
			</p>
		</header>

		<!-- Controls -->
		<section class="bg-card rounded-lg border border-border shadow-sm p-6 mb-6">
			<div class="flex flex-col md:flex-row gap-4 items-start md:items-end">

				<div class="flex flex-col gap-2">
					<label for="window-select" class="text-sm font-medium text-muted-foreground"
						>Time Window:</label
					>
					<select
						id="window-select"
						bind:value={selectedWindow}
						class="px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
					>
						<option value={30}>30 Days</option>
						<option value={180}>180 Days</option>
					</select>
				</div>

				<button
					onclick={() => inspectUser()}
					disabled={loading}
					class="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed font-medium whitespace-nowrap"
				>
					{loading ? 'Loading...' : '🔍 Inspect User'}
				</button>
			</div>
		</section>

		{#if loading}
			<div class="flex items-center justify-center py-16">
				<div class="text-center space-y-3">
					<div
						class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"
					></div>
					<p class="text-muted-foreground">Fetching recommendation data...</p>
				</div>
			</div>
		{:else if error}
			<div class="bg-destructive/10 border border-destructive/30 rounded-lg p-6 text-center">
				<strong class="text-destructive block mb-2">Error:</strong>
				<p class="text-destructive/90">{error}</p>
			</div>
		{:else if !inspectData}
			<div class="bg-card rounded-lg border border-border p-12 text-center">
				<p class="text-muted-foreground">Select a user from the top bar to inspect their data</p>
			</div>
		{:else}
			<div class="space-y-6">
				<!-- Summary Card -->
				<section class="bg-card rounded-lg border border-border shadow-sm p-6">
					<h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
						<span>📊</span> Summary
					</h2>
					<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">User Name</p>
							<p class="text-sm font-semibold text-foreground">
								{inspectData.user_name}
							</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Consent Status</p>
							<p class={`text-sm font-semibold px-2 py-1 rounded inline-block ${
								hasConsent ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
							}`}>
								{hasConsent ? 'Granted' : 'Not Granted'}
							</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Persona</p>
							{#if hasPersona}
								<p class="text-sm font-semibold text-primary px-2 py-1 bg-primary/10 rounded inline-block">
									{inspectData.persona_type}
								</p>
							{:else}
								<p class="text-sm text-muted-foreground">Not assigned</p>
							{/if}
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Accounts</p>
							<p class="text-sm font-semibold text-foreground">{inspectData.account_count}</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Transactions</p>
							<p class="text-sm font-semibold text-foreground">{inspectData.transaction_count}</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Time Window</p>
							<p class="text-sm font-semibold text-foreground">{selectedWindow} days</p>
						</div>
					</div>
				</section>

				<!-- Behavioral Signals -->
				<section class="bg-card rounded-lg border border-border shadow-sm p-6">
					<h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
						<span>🎯</span> Behavioral Signals
					</h2>
					<div class="bg-muted rounded-lg p-4 overflow-x-auto">
						<pre class="text-xs font-mono text-foreground">{formatJSON(inspectData.signals_summary)}</pre>
					</div>
				</section>

				<!-- Persona Assignment -->
				<section class="bg-card rounded-lg border border-border shadow-sm p-6">
					<h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
						<span>🎭</span> Persona Assignment
					</h2>
					{#if hasConsent && hasPersona}
						<div class="space-y-3">
							<div class="flex gap-4 py-2 border-b border-border">
								<span class="text-sm font-medium text-muted-foreground min-w-[140px]">Assigned Persona:</span>
								<span class="text-sm text-foreground font-semibold">{inspectData.persona_type}</span>
							</div>
							<div class="flex gap-4 py-2">
								<span class="text-sm font-medium text-muted-foreground min-w-[140px]">Confidence Score:</span>
								<span class="text-sm text-foreground">{((inspectData.confidence || 0) * 100).toFixed(2)}%</span>
							</div>
						</div>
					{:else if !hasConsent}
						<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
							<p class="text-sm text-yellow-800">
								<strong>User has not consented to data analysis.</strong><br />
								Persona assignment requires explicit consent.
							</p>
						</div>
					{:else}
						<div class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
							<p class="text-sm text-gray-600">
								No persona assigned (insufficient data or error during analysis).
							</p>
						</div>
					{/if}
				</section>

				<!-- Recommendations Details -->
				{#if recommendations.length > 0}
					<section class="bg-card rounded-lg border border-border shadow-sm p-6">
						<h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
							<span>💡</span> Education Recommendations ({recommendations.length})
						</h2>
						<div class="space-y-4">
							{#each recommendations as rec, index}
								<div class="bg-accent/50 rounded-lg p-4">
									<h3 class="text-lg font-semibold text-foreground mb-3">
										#{index + 1}: {rec.title}
									</h3>
									<div class="space-y-2">
										<div class="flex gap-4 text-sm">
											<span class="font-medium text-muted-foreground min-w-[120px]">ID:</span>
											<span class="text-foreground font-mono">{rec.id}</span>
										</div>
										<div class="flex gap-4 text-sm">
											<span class="font-medium text-muted-foreground min-w-[120px]">Summary:</span>
											<span class="text-foreground">{rec.summary}</span>
										</div>
										<div class="flex gap-4 text-sm">
											<span class="font-medium text-muted-foreground min-w-[120px]">Relevance:</span>
											<span class="text-foreground">{(rec.relevance_score * 100).toFixed(1)}%</span>
										</div>
									</div>
								</div>
							{/each}
						</div>
					</section>
				{/if}

				<!-- Partner Offers -->
				{#if offers.length > 0}
					<section class="bg-card rounded-lg border border-border shadow-sm p-6">
						<h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
							<span>🎁</span> Partner Offers ({offers.length})
						</h2>
						<div class="space-y-4">
							{#each offers as offer, index}
								<div class="bg-accent/50 rounded-lg p-4">
									<h3 class="text-lg font-semibold text-foreground mb-3">
										#{index + 1}: {offer.title}
									</h3>
									<div class="space-y-2">
										<div class="flex gap-4 text-sm">
											<span class="font-medium text-muted-foreground min-w-[120px]">Provider:</span>
											<span class="text-foreground">{offer.provider}</span>
										</div>
										<div class="flex gap-4 text-sm">
											<span class="font-medium text-muted-foreground min-w-[120px]">Eligible:</span>
											<span class={`text-foreground font-semibold ${
												offer.eligibility_met ? 'text-green-600' : 'text-red-600'
											}`}>
												{offer.eligibility_met ? 'Yes' : 'No'}
											</span>
										</div>
									</div>
								</div>
							{/each}
						</div>
					</section>
				{/if}

				<!-- Complete Data Dump (JSON) -->
				<section class="bg-card rounded-lg border border-border shadow-sm p-6">
					<h2 class="text-xl font-bold text-foreground mb-2 flex items-center gap-2">
						<span>🔍</span> Complete Data Dump (JSON)
					</h2>
					<p class="text-sm text-muted-foreground mb-4 italic">
						Full inspection data showing all fields returned by the operator inspect endpoint.
					</p>
					<div class="bg-muted rounded-lg p-4 overflow-x-auto">
						<pre class="text-xs font-mono text-foreground">{formatJSON(inspectData)}</pre>
					</div>
				</section>
			</div>
		{/if}

		<!-- Back Navigation -->
		<nav class="mt-8 pt-6 border-t border-border">
			<a
				href="/"
				class="inline-flex items-center text-primary hover:text-primary/80 font-medium transition-colors"
			>
				← Back to Home
			</a>
		</nav>
	</div>
</div>
