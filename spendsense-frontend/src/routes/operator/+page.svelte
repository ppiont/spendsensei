<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { Recommendation, User } from '$lib/types';

	// Svelte 5 runes for reactive state
	let selectedUserId = $state('');
	let recommendations = $state<Recommendation[]>([]);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let selectedWindow = $state(30);
	let users = $state<User[]>([]);
	let usersLoading = $state(true);
	let usersError = $state<string | null>(null);

	// Get full data from first recommendation
	const fullData = $derived(recommendations.length > 0 ? recommendations[0] : null);

	// Format JSON for display
	function formatJSON(obj: any): string {
		return JSON.stringify(obj, null, 2);
	}

	// Fetch all users
	async function fetchUsers() {
		usersLoading = true;
		usersError = null;

		try {
			const data = await api.users.getUsers();
			users = data;
			// Set first user as selected by default
			if (data.length > 0 && !selectedUserId) {
				selectedUserId = data[0].id;
			}
		} catch (err: any) {
			usersError = err.detail || err.message || 'Failed to load users';
			console.error('Failed to fetch users:', err);
		} finally {
			usersLoading = false;
		}
	}

	// Fetch insights for inspection
	async function inspectUser() {
		if (!selectedUserId) return;

		loading = true;
		error = null;

		try {
			const data = await api.insights.getUserInsights(selectedUserId, selectedWindow);
			recommendations = data;
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to load data';
			console.error('Operator view error:', err);
		} finally {
			loading = false;
		}
	}

	// Load data on mount
	onMount(async () => {
		await fetchUsers();
		if (selectedUserId) {
			await inspectUser();
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
			{#if usersError}
				<div class="bg-destructive/10 border border-destructive/30 rounded-lg p-4 mb-4">
					<strong class="text-destructive block mb-2">Error loading users:</strong>
					<p class="text-destructive/90">{usersError}</p>
				</div>
			{/if}

			<div class="flex flex-col md:flex-row gap-4 items-start md:items-end">
				<div class="flex flex-col gap-2 flex-1">
					<label for="user-select" class="text-sm font-medium text-muted-foreground"
						>Select User ({users.length} total):</label
					>
					<select
						id="user-select"
						bind:value={selectedUserId}
						disabled={usersLoading || users.length === 0}
						class="px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed"
					>
						{#if usersLoading}
							<option>Loading users...</option>
						{:else if users.length === 0}
							<option>No users found</option>
						{:else}
							{#each users as user}
								<option value={user.id}>{user.name}</option>
							{/each}
						{/if}
					</select>
				</div>

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
		{:else if !fullData}
			<div class="bg-card rounded-lg border border-border p-12 text-center">
				<p class="text-muted-foreground">Click "Inspect User" to load recommendation data</p>
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
							<p class="text-xs font-medium text-muted-foreground">User ID</p>
							<p class="text-sm font-mono text-foreground truncate" title={selectedUserId}>
								{selectedUserId.slice(0, 8)}...
							</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Persona</p>
							<p
								class="text-sm font-semibold text-primary px-2 py-1 bg-primary/10 rounded inline-block"
							>
								{fullData.persona}
							</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Confidence</p>
							<p class="text-sm font-semibold text-foreground">
								{(fullData.confidence * 100).toFixed(1)}%
							</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Recommendations</p>
							<p class="text-sm font-semibold text-foreground">{recommendations.length}</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Time Window</p>
							<p class="text-sm font-semibold text-foreground">{selectedWindow} days</p>
						</div>
						<div class="space-y-1">
							<p class="text-xs font-medium text-muted-foreground">Key Signals</p>
							<p class="text-sm font-semibold text-foreground">
								{fullData.rationale.key_signals.length}
							</p>
						</div>
					</div>
				</section>

				<!-- Behavioral Signals -->
				<section class="bg-card rounded-lg border border-border shadow-sm p-6">
					<h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
						<span>🎯</span> Behavioral Signals
					</h2>
					<div class="flex flex-wrap gap-2 mb-4">
						{#each fullData.rationale.key_signals as signal}
							<span class="px-3 py-1 bg-accent text-foreground rounded-full text-sm font-medium">
								{signal}
							</span>
						{/each}
					</div>
					<div class="bg-muted rounded-lg p-4 overflow-x-auto">
						<pre class="text-xs font-mono text-foreground">{formatJSON({
								key_signals: fullData.rationale.key_signals
							})}</pre>
					</div>
				</section>

				<!-- Persona Matching Logic -->
				<section class="bg-card rounded-lg border border-border shadow-sm p-6">
					<h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
						<span>🎭</span> Persona Matching Logic
					</h2>
					<div class="space-y-3 mb-4">
						<div class="flex gap-4 py-2 border-b border-border">
							<span class="text-sm font-medium text-muted-foreground min-w-[140px]"
								>Assigned Persona:</span
							>
							<span class="text-sm text-foreground font-semibold">{fullData.persona}</span>
						</div>
						<div class="flex gap-4 py-2 border-b border-border">
							<span class="text-sm font-medium text-muted-foreground min-w-[140px]"
								>Confidence Score:</span
							>
							<span class="text-sm text-foreground">{(fullData.confidence * 100).toFixed(2)}%</span
							>
						</div>
						<div class="flex gap-4 py-2">
							<span class="text-sm font-medium text-muted-foreground min-w-[140px]">Rationale:</span
							>
							<p class="text-sm text-foreground flex-1">{fullData.rationale.explanation}</p>
						</div>
					</div>
					<div class="bg-muted rounded-lg p-4 overflow-x-auto">
						<pre class="text-xs font-mono text-foreground">{formatJSON({
								persona_type: fullData.rationale.persona_type,
								confidence: fullData.rationale.confidence,
								explanation: fullData.rationale.explanation
							})}</pre>
					</div>
				</section>

				<!-- Recommendations Details -->
				<section class="bg-card rounded-lg border border-border shadow-sm p-6">
					<h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
						<span>💡</span> Recommendations Generated
					</h2>
					<div class="space-y-4">
						{#each recommendations as rec, index}
							<div class="bg-accent/50 rounded-lg p-4">
								<h3 class="text-lg font-semibold text-foreground mb-3">
									Recommendation #{index + 1}
								</h3>
								<div class="space-y-2">
									<div class="flex gap-4 text-sm">
										<span class="font-medium text-muted-foreground min-w-[120px]">Title:</span>
										<span class="text-foreground">{rec.content.title}</span>
									</div>
									<div class="flex gap-4 text-sm">
										<span class="font-medium text-muted-foreground min-w-[120px]">Content ID:</span>
										<span class="text-foreground font-mono">{rec.content.id}</span>
									</div>
									<div class="flex gap-4 text-sm">
										<span class="font-medium text-muted-foreground min-w-[120px]"
											>Relevance Score:</span
										>
										<span class="text-foreground"
											>{(rec.content.relevance_score * 100).toFixed(1)}%</span
										>
									</div>
									<div class="flex gap-4 text-sm">
										<span class="font-medium text-muted-foreground min-w-[120px]">Source:</span>
										<span class="text-foreground">{rec.content.source}</span>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</section>

				<!-- Complete Decision Trace (JSON) -->
				<section class="bg-card rounded-lg border border-border shadow-sm p-6">
					<h2 class="text-xl font-bold text-foreground mb-2 flex items-center gap-2">
						<span>🔍</span> Complete Decision Trace (JSON)
					</h2>
					<p class="text-sm text-muted-foreground mb-4 italic">
						Full recommendation object showing all decision-making data for auditability and debugging.
					</p>
					<div class="bg-muted rounded-lg p-4 overflow-x-auto">
						<pre class="text-xs font-mono text-foreground">{formatJSON(fullData)}</pre>
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
