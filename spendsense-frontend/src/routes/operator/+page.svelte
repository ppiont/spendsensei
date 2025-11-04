<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { Recommendation } from '$lib/types';

	// Svelte 5 runes for reactive state
	let selectedUserId = $state('bdd640fb-0667-4ad1-9c80-317fa3b1799d');
	let recommendations = $state<Recommendation[]>([]);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let selectedWindow = $state(30);

	// Available test users
	const testUsers = [
		{ id: 'bdd640fb-0667-4ad1-9c80-317fa3b1799d', name: 'Daniel Doyle' },
		{ id: '97d7a560-adb1-4670-ad9f-b00d4882d73c', name: 'Mr. Andrew Foster' },
		{ id: '37c86152-beed-4af9-80c5-9f30d1031424', name: 'Amber Cooper' },
		{ id: 'dc268108-7140-41a1-afc2-ccfc9db7284b', name: 'Steven Taylor' },
		{ id: 'c7a9f33c-22d8-49d3-b3e4-f986f18cccdc', name: 'Ashley Garcia' }
	];

	// Get full data from first recommendation
	const fullData = $derived(recommendations.length > 0 ? recommendations[0] : null);

	// Format JSON for display
	function formatJSON(obj: any): string {
		return JSON.stringify(obj, null, 2);
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
	onMount(() => {
		inspectUser();
	});
</script>

<div class="operator-view">
	<header class="page-header">
		<div>
			<h1>🔧 Operator View</h1>
			<p class="subtitle">Internal inspection tool for verifying recommendation system</p>
		</div>
	</header>

	<section class="controls">
		<div class="control-group">
			<label for="user-select">Select User:</label>
			<select id="user-select" bind:value={selectedUserId}>
				{#each testUsers as user}
					<option value={user.id}>{user.name}</option>
				{/each}
			</select>
		</div>

		<div class="control-group">
			<label for="window-select">Time Window:</label>
			<select id="window-select" bind:value={selectedWindow}>
				<option value={30}>30 Days</option>
				<option value={180}>180 Days</option>
			</select>
		</div>

		<button class="inspect-button" onclick={() => inspectUser()} disabled={loading}>
			{loading ? 'Loading...' : '🔍 Inspect User'}
		</button>
	</section>

	{#if loading}
		<div class="loading">Fetching data...</div>
	{:else if error}
		<div class="error">
			<strong>Error:</strong>
			{error}
		</div>
	{:else if !fullData}
		<div class="empty">
			<p>Click "Inspect User" to load data</p>
		</div>
	{:else}
		<div class="inspection-content">
			<!-- Summary Card -->
			<section class="summary-card">
				<h2>📊 Summary</h2>
				<div class="summary-grid">
					<div class="summary-item">
						<span class="label">User ID:</span>
						<span class="value">{selectedUserId}</span>
					</div>
					<div class="summary-item">
						<span class="label">Persona:</span>
						<span class="value persona-badge">{fullData.persona}</span>
					</div>
					<div class="summary-item">
						<span class="label">Confidence:</span>
						<span class="value">{(fullData.confidence * 100).toFixed(1)}%</span>
					</div>
					<div class="summary-item">
						<span class="label">Recommendations:</span>
						<span class="value">{recommendations.length}</span>
					</div>
					<div class="summary-item">
						<span class="label">Time Window:</span>
						<span class="value">{selectedWindow} days</span>
					</div>
					<div class="summary-item">
						<span class="label">Key Signals:</span>
						<span class="value">{fullData.rationale.key_signals.length}</span>
					</div>
				</div>
			</section>

			<!-- Behavioral Signals -->
			<section class="section-card">
				<h2>🎯 Behavioral Signals</h2>
				<div class="signals-list">
					{#each fullData.rationale.key_signals as signal}
						<div class="signal-badge">{signal}</div>
					{/each}
				</div>
				<div class="code-block">
					<pre>{formatJSON({ key_signals: fullData.rationale.key_signals })}</pre>
				</div>
			</section>

			<!-- Persona Matching Logic -->
			<section class="section-card">
				<h2>🎭 Persona Matching Logic</h2>
				<div class="matching-info">
					<div class="info-row">
						<strong>Assigned Persona:</strong>
						<span>{fullData.persona}</span>
					</div>
					<div class="info-row">
						<strong>Confidence Score:</strong>
						<span>{(fullData.confidence * 100).toFixed(2)}%</span>
					</div>
					<div class="info-row">
						<strong>Rationale:</strong>
						<p>{fullData.rationale.explanation}</p>
					</div>
				</div>
				<div class="code-block">
					<pre>{formatJSON({
							persona_type: fullData.rationale.persona_type,
							confidence: fullData.rationale.confidence,
							explanation: fullData.rationale.explanation
						})}</pre>
				</div>
			</section>

			<!-- Recommendations Details -->
			<section class="section-card">
				<h2>💡 Recommendations Generated</h2>
				{#each recommendations as rec, index}
					<div class="recommendation-detail">
						<h3>Recommendation #{index + 1}</h3>
						<div class="rec-info">
							<div class="info-row">
								<strong>Title:</strong>
								<span>{rec.content.title}</span>
							</div>
							<div class="info-row">
								<strong>Content ID:</strong>
								<span>{rec.content.id}</span>
							</div>
							<div class="info-row">
								<strong>Relevance Score:</strong>
								<span>{(rec.content.relevance_score * 100).toFixed(1)}%</span>
							</div>
							<div class="info-row">
								<strong>Source:</strong>
								<span>{rec.content.source}</span>
							</div>
						</div>
					</div>
				{/each}
			</section>

			<!-- Complete Decision Trace (JSON) -->
			<section class="section-card">
				<h2>🔍 Complete Decision Trace (JSON)</h2>
				<p class="description">
					Full traceability of the recommendation system's decision-making process
				</p>
				<div class="code-block">
					<pre>{formatJSON(recommendations)}</pre>
				</div>
			</section>
		</div>
	{/if}

	<nav class="back-nav">
		<a href="/dashboard">← Back to Dashboard</a>
	</nav>
</div>

<style>
	.operator-view {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
		background: #f5f5f5;
		min-height: 100vh;
	}

	.page-header {
		background: white;
		padding: 2rem;
		border-radius: 8px;
		margin-bottom: 2rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	h1 {
		font-size: 2rem;
		color: #333;
		margin: 0 0 0.5rem 0;
	}

	.subtitle {
		color: #666;
		margin: 0;
		font-size: 0.9rem;
	}

	.controls {
		background: white;
		padding: 1.5rem;
		border-radius: 8px;
		margin-bottom: 2rem;
		display: flex;
		gap: 1rem;
		align-items: flex-end;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.control-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.control-group label {
		font-size: 0.875rem;
		color: #666;
		font-weight: 500;
	}

	select {
		padding: 0.625rem 1rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
		min-width: 250px;
	}

	.inspect-button {
		padding: 0.625rem 1.5rem;
		background: #2196f3;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
		font-weight: 500;
		transition: background 0.2s;
	}

	.inspect-button:hover:not(:disabled) {
		background: #1976d2;
	}

	.inspect-button:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	.loading,
	.error,
	.empty {
		background: white;
		padding: 3rem;
		text-align: center;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.loading {
		color: #666;
	}

	.error {
		color: #c33;
		background: #fee;
		border: 1px solid #fcc;
	}

	.empty {
		color: #999;
	}

	.inspection-content {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.summary-card,
	.section-card {
		background: white;
		padding: 1.5rem;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	h2 {
		font-size: 1.25rem;
		color: #333;
		margin: 0 0 1rem 0;
		padding-bottom: 0.75rem;
		border-bottom: 2px solid #f0f0f0;
	}

	h3 {
		font-size: 1rem;
		color: #555;
		margin: 0 0 0.75rem 0;
	}

	.summary-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
	}

	.summary-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.summary-item .label {
		font-size: 0.75rem;
		color: #999;
		text-transform: uppercase;
		font-weight: 600;
	}

	.summary-item .value {
		font-size: 1.125rem;
		color: #333;
		font-weight: 600;
	}

	.persona-badge {
		background: #e3f2fd;
		color: #1976d2;
		padding: 0.25rem 0.75rem;
		border-radius: 16px;
		display: inline-block;
	}

	.signals-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}

	.signal-badge {
		background: #f0f0f0;
		color: #555;
		padding: 0.5rem 1rem;
		border-radius: 20px;
		font-size: 0.875rem;
		font-weight: 500;
	}

	.code-block {
		background: #1e1e1e;
		color: #d4d4d4;
		padding: 1rem;
		border-radius: 4px;
		overflow-x: auto;
		margin-top: 1rem;
	}

	.code-block pre {
		margin: 0;
		font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
		font-size: 0.875rem;
		line-height: 1.5;
	}

	.matching-info,
	.rec-info {
		margin-bottom: 1rem;
	}

	.info-row {
		display: flex;
		gap: 1rem;
		padding: 0.75rem 0;
		border-bottom: 1px solid #f0f0f0;
	}

	.info-row:last-child {
		border-bottom: none;
	}

	.info-row strong {
		min-width: 150px;
		color: #666;
		font-size: 0.875rem;
	}

	.info-row span,
	.info-row p {
		flex: 1;
		color: #333;
		margin: 0;
	}

	.recommendation-detail {
		padding: 1rem;
		background: #f9f9f9;
		border-radius: 6px;
		margin-bottom: 1rem;
	}

	.recommendation-detail:last-child {
		margin-bottom: 0;
	}

	.description {
		color: #666;
		font-size: 0.875rem;
		margin: 0 0 1rem 0;
		font-style: italic;
	}

	.back-nav {
		margin-top: 2rem;
		padding-top: 2rem;
		border-top: 1px solid #ddd;
	}

	.back-nav a {
		color: #2196f3;
		text-decoration: none;
		font-weight: 500;
	}

	.back-nav a:hover {
		text-decoration: underline;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.operator-view {
			padding: 1rem;
		}

		.controls {
			flex-direction: column;
			align-items: stretch;
		}

		select {
			width: 100%;
		}

		.summary-grid {
			grid-template-columns: 1fr;
		}

		.info-row {
			flex-direction: column;
			gap: 0.25rem;
		}

		.info-row strong {
			min-width: auto;
		}

		.code-block {
			font-size: 0.75rem;
		}
	}
</style>
