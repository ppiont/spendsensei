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

<div class="insights-page">
	<header class="page-header">
		<h1>Financial Insights</h1>

		<div class="controls">
			<div class="user-selector">
				<label for="user-select">User:</label>
				<select id="user-select" bind:value={selectedUserId}>
					{#each testUsers as user}
						<option value={user.id}>{user.name}</option>
					{/each}
				</select>
			</div>

			<div class="window-selector">
				<label for="window-select">Time Period:</label>
				<select id="window-select" bind:value={selectedWindow}>
					<option value={30}>Last 30 Days</option>
					<option value={180}>Last 180 Days</option>
				</select>
			</div>
		</div>
	</header>

	{#if loading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Analyzing your financial patterns...</p>
		</div>
	{:else if error}
		<div class="error">
			<strong>Error:</strong>
			{error}
			<button onclick={() => loadInsights()}>Retry</button>
		</div>
	{:else if recommendations.length === 0}
		<div class="empty">
			<h2>No Insights Available</h2>
			<p>We need more transaction data to generate personalized recommendations.</p>
		</div>
	{:else}
		<div class="content">
			<!-- Persona Display -->
			{#if persona}
				<section class="persona-card">
					<div class="persona-header">
						<h2>Your Financial Persona</h2>
						<span class="confidence-badge">
							{Math.round(confidence * 100)}% Confidence
						</span>
					</div>

					<div class="persona-content">
						<h3 class="persona-name">{formatPersona(persona)}</h3>
						<p class="persona-description">{getPersonaDescription(persona)}</p>

						{#if recommendations[0].rationale.key_signals.length > 0}
							<div class="signals">
								<p class="signals-label">Based on:</p>
								<ul class="signals-list">
									{#each recommendations[0].rationale.key_signals as signal}
										<li>{signal.replace(/_/g, ' ')}</li>
									{/each}
								</ul>
							</div>
						{/if}
					</div>
				</section>
			{/if}

			<!-- Recommendations -->
			<section class="recommendations">
				<h2>Personalized Recommendations</h2>

				<div class="recommendations-grid">
					{#each recommendations as rec, index}
						<article class="recommendation-card" class:expanded={expandedCard === index}>
							<div class="card-header">
								<h3>{rec.content.title}</h3>
								<span class="relevance-badge">
									{Math.round(rec.content.relevance_score * 100)}% Relevant
								</span>
							</div>

							<p class="summary">{rec.content.summary}</p>

							{#if expandedCard === index}
								<div class="expanded-content">
									<div class="body">
										{rec.content.body}
									</div>

									<div class="rationale">
										<h4>Why this matters for you:</h4>
										<p>{rec.rationale.explanation}</p>
									</div>

									<div class="cta-section">
										<strong>{rec.content.cta}</strong>
									</div>

									<div class="source">
										<small>Source: {rec.content.source}</small>
									</div>
								</div>
							{/if}

							<button class="expand-button" onclick={() => toggleCard(index)}>
								{expandedCard === index ? 'Show Less' : 'Read More'}
							</button>
						</article>
					{/each}
				</div>
			</section>

			<!-- Disclaimer -->
			<section class="disclaimer">
				<h3>Important Disclaimer</h3>
				<p>
					These insights are educational recommendations based on analysis of your transaction
					patterns over the selected time period. They are not financial advice. Please consult
					with a qualified financial advisor for personalized financial planning.
				</p>
				<p>
					Data shown is based on transactions from the past {selectedWindow} days. Results may vary
					with different time periods.
				</p>
			</section>
		</div>
	{/if}

	<nav class="back-nav">
		<a href="/dashboard">← Back to Dashboard</a>
	</nav>
</div>

<style>
	.insights-page {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	.page-header {
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

	.controls {
		display: flex;
		gap: 1rem;
	}

	.user-selector,
	.window-selector {
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

	.loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		text-align: center;
	}

	.spinner {
		width: 50px;
		height: 50px;
		border: 4px solid #f0f0f0;
		border-top: 4px solid #2196f3;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.loading p {
		color: #666;
		font-size: 1.1rem;
	}

	.error,
	.empty {
		padding: 2rem;
		text-align: center;
		border-radius: 8px;
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

	.empty {
		background: #f5f5f5;
		color: #666;
	}

	.content {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.persona-card {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 2rem;
		border-radius: 12px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.persona-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.5rem;
	}

	.persona-header h2 {
		font-size: 1.25rem;
		margin: 0;
		opacity: 0.9;
	}

	.confidence-badge {
		background: rgba(255, 255, 255, 0.2);
		padding: 0.375rem 0.75rem;
		border-radius: 20px;
		font-size: 0.875rem;
		font-weight: 600;
	}

	.persona-content h3 {
		font-size: 2rem;
		margin: 0 0 1rem 0;
	}

	.persona-description {
		font-size: 1.125rem;
		line-height: 1.6;
		margin: 0 0 1.5rem 0;
		opacity: 0.95;
	}

	.signals {
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid rgba(255, 255, 255, 0.2);
	}

	.signals-label {
		font-size: 0.875rem;
		opacity: 0.8;
		margin: 0 0 0.5rem 0;
	}

	.signals-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.signals-list li {
		background: rgba(255, 255, 255, 0.2);
		padding: 0.375rem 0.75rem;
		border-radius: 16px;
		font-size: 0.875rem;
	}

	.recommendations h2 {
		font-size: 1.5rem;
		color: #333;
		margin: 0 0 1.5rem 0;
	}

	.recommendations-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
		gap: 1.5rem;
	}

	.recommendation-card {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 1.5rem;
		transition: box-shadow 0.2s;
	}

	.recommendation-card:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.recommendation-card.expanded {
		grid-column: 1 / -1;
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.card-header h3 {
		font-size: 1.25rem;
		color: #333;
		margin: 0;
		flex: 1;
	}

	.relevance-badge {
		background: #e3f2fd;
		color: #1976d2;
		padding: 0.25rem 0.625rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 600;
		white-space: nowrap;
	}

	.summary {
		color: #666;
		line-height: 1.6;
		margin: 0 0 1rem 0;
	}

	.expanded-content {
		margin: 1.5rem 0;
		padding-top: 1.5rem;
		border-top: 1px solid #f0f0f0;
	}

	.body {
		color: #333;
		line-height: 1.7;
		margin-bottom: 1.5rem;
		white-space: pre-wrap;
	}

	.rationale {
		background: #f9f9f9;
		padding: 1rem;
		border-radius: 6px;
		margin-bottom: 1.5rem;
	}

	.rationale h4 {
		font-size: 1rem;
		color: #333;
		margin: 0 0 0.5rem 0;
	}

	.rationale p {
		color: #666;
		line-height: 1.6;
		margin: 0;
	}

	.cta-section {
		background: #e8f5e9;
		padding: 1rem;
		border-radius: 6px;
		margin-bottom: 1rem;
	}

	.cta-section strong {
		color: #2e7d32;
	}

	.source {
		text-align: right;
		color: #999;
	}

	.expand-button {
		width: 100%;
		padding: 0.75rem;
		background: #2196f3;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
		transition: background 0.2s;
	}

	.expand-button:hover {
		background: #1976d2;
	}

	.disclaimer {
		background: #fff8e1;
		border: 1px solid #ffe082;
		border-radius: 8px;
		padding: 1.5rem;
	}

	.disclaimer h3 {
		font-size: 1rem;
		color: #f57c00;
		margin: 0 0 0.75rem 0;
	}

	.disclaimer p {
		color: #666;
		line-height: 1.6;
		margin: 0 0 0.75rem 0;
		font-size: 0.9rem;
	}

	.disclaimer p:last-child {
		margin-bottom: 0;
	}

	.back-nav {
		margin-top: 2rem;
		padding-top: 2rem;
		border-top: 1px solid #e0e0e0;
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
		.insights-page {
			padding: 1rem;
		}

		.page-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}

		.controls {
			flex-direction: column;
			width: 100%;
		}

		.user-selector,
		.window-selector {
			width: 100%;
		}

		select {
			width: 100%;
		}

		.recommendations-grid {
			grid-template-columns: 1fr;
		}

		.persona-content h3 {
			font-size: 1.5rem;
		}
	}
</style>
