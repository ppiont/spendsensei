<script lang="ts">
	import { Progress } from '$lib/components/ui/progress';
	import { Badge } from '$lib/components/ui/badge';
	import { ChevronDown, ChevronUp } from '@lucide/svelte';

	// Props
	let {
		personaType,
		confidence,
		explanation,
		keySignals
	} = $props<{
		personaType: string;
		confidence: number;
		explanation: string;
		keySignals: string[];
	}>();

	// Expandable details state
	let showDetails = $state(false);

	// Persona configuration
	const personaConfig: Record<
		string,
		{
			icon: string;
			gradient: string;
			title: string;
			whatItMeans: string;
			whyItMatters: string;
		}
	> = {
		savings_builder: {
			icon: '🎯',
			gradient: 'from-emerald-50 to-teal-50',
			title: 'Savings Builder',
			whatItMeans:
				'You consistently set aside money each month and maintain low credit utilization. Your financial habits show discipline and long-term thinking.',
			whyItMatters:
				"This persona means you're on track to build wealth over time. We'll focus your education on optimizing savings strategies, investment opportunities, and accelerating your financial goals."
		},
		high_utilization: {
			icon: '⚠️',
			gradient: 'from-red-50 to-orange-50',
			title: 'High Utilization',
			whatItMeans:
				'Your credit cards are carrying high balances relative to your credit limits. This can impact your credit score and lead to significant interest charges.',
			whyItMatters:
				"High utilization is costing you money in interest and may be limiting your credit options. We'll help you understand strategies to pay down balances and improve your credit health."
		},
		variable_income: {
			icon: '📊',
			gradient: 'from-blue-50 to-indigo-50',
			title: 'Variable Income Budgeter',
			whatItMeans:
				'Your income fluctuates from month to month, which can make budgeting and planning more challenging than with a steady paycheck.',
			whyItMatters:
				"Variable income requires different financial strategies than traditional employment. We'll focus on building cash reserves, smoothing expenses, and planning for irregular income patterns."
		},
		subscription_heavy: {
			icon: '💳',
			gradient: 'from-purple-50 to-pink-50',
			title: 'Subscription Heavy',
			whatItMeans:
				'You have multiple recurring subscriptions and services that automatically charge your accounts each month.',
			whyItMatters:
				"Subscriptions can quietly drain your budget. Even small recurring charges add up to significant annual costs. We'll help you audit and optimize your subscriptions to free up money for your priorities."
		},
		balanced: {
			icon: '⚖️',
			gradient: 'from-green-50 to-blue-50',
			title: 'Balanced',
			whatItMeans:
				'Your finances show healthy patterns across multiple areas: manageable credit usage, consistent income, and reasonable spending.',
			whyItMatters:
				"You have a solid financial foundation. We'll focus on fine-tuning your approach, identifying optimization opportunities, and helping you maintain these good habits long-term."
		}
	};

	const config = $derived(personaConfig[personaType] || personaConfig.balanced);
</script>

<div class="persona-card bg-gradient-to-br {config.gradient}">
	<!-- Header -->
	<div class="persona-header">
		<div class="persona-icon">{config.icon}</div>
		<div class="persona-title-section">
			<h3 class="persona-title">{config.title}</h3>
			<div class="confidence-section">
				<span class="confidence-label">Confidence: {(confidence * 100).toFixed(0)}%</span>
				<Progress value={confidence * 100} class="confidence-bar" />
			</div>
		</div>
	</div>

	<!-- Explanation -->
	<p class="persona-explanation">{explanation}</p>

	<!-- Key Signals -->
	{#if keySignals.length > 0}
		<div class="signals-section">
			<span class="signals-label">Behavioral Signals:</span>
			<div class="signals-tags">
				{#each keySignals as signal}
					<Badge variant="secondary" class="signal-badge">
						{signal.replace(/_/g, ' ')}
					</Badge>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Expandable Details -->
	<button onclick={() => (showDetails = !showDetails)} class="expand-button">
		<span class="expand-text">{showDetails ? 'Hide details' : 'What this means for you'}</span>
		{#if showDetails}
			<ChevronUp class="w-4 h-4" />
		{:else}
			<ChevronDown class="w-4 h-4" />
		{/if}
	</button>

	{#if showDetails}
		<div class="details-content">
			<div class="detail-section">
				<h4 class="detail-heading">What it means:</h4>
				<p class="detail-text">{config.whatItMeans}</p>
			</div>
			<div class="detail-section">
				<h4 class="detail-heading">Why it matters:</h4>
				<p class="detail-text">{config.whyItMatters}</p>
			</div>
		</div>
	{/if}
</div>

<style>
	.persona-card {
		width: 100%;
		padding: 2rem;
		border-radius: 0.75rem;
		border: 1px solid #e5e7eb; /* gray-200 */
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}

	.persona-header {
		display: flex;
		align-items: flex-start;
		gap: 1.5rem;
		margin-bottom: 1.5rem;
	}

	.persona-icon {
		font-size: 3rem;
		line-height: 1;
		flex-shrink: 0;
	}

	.persona-title-section {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.persona-title {
		font-size: 1.5rem;
		font-weight: 700;
		color: #1f2937; /* gray-800 */
		margin: 0;
	}

	.confidence-section {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.confidence-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: #6b7280; /* gray-500 */
	}

	:global(.confidence-bar) {
		height: 0.5rem;
	}

	.persona-explanation {
		font-size: 0.9375rem;
		line-height: 1.6;
		color: #374151; /* gray-700 */
		margin: 0 0 1.5rem 0;
	}

	.signals-section {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}

	.signals-label {
		font-size: 0.875rem;
		font-weight: 600;
		color: #4b5563; /* gray-600 */
	}

	.signals-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	:global(.signal-badge) {
		font-size: 0.75rem;
		text-transform: capitalize;
		font-weight: 500;
	}

	.expand-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: #3b82f6; /* brand-blue */
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		transition: color 0.15s ease;
	}

	.expand-button:hover {
		color: #2563eb; /* blue-dark */
	}

	.expand-text {
		line-height: 1;
	}

	.details-content {
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid #e5e7eb; /* gray-200 */
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
		background-color: rgba(255, 255, 255, 0.5);
		padding: 1.5rem;
		border-radius: 0.5rem;
	}

	.detail-section {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.detail-heading {
		font-size: 0.9375rem;
		font-weight: 600;
		color: #1f2937; /* gray-800 */
		margin: 0;
	}

	.detail-text {
		font-size: 0.875rem;
		line-height: 1.6;
		color: #4b5563; /* gray-600 */
		margin: 0;
	}

	/* Responsive */
	@media (max-width: 640px) {
		.persona-card {
			padding: 1.5rem;
		}

		.persona-header {
			flex-direction: column;
			align-items: center;
			text-align: center;
		}

		.persona-icon {
			font-size: 2.5rem;
		}

		.persona-title {
			font-size: 1.25rem;
		}

		.details-content {
			padding: 1rem;
		}
	}
</style>
