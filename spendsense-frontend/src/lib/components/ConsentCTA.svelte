<script lang="ts">
	import { api } from '$lib/api/client';
	import { CheckCircle, Info } from '@lucide/svelte';

	// Props
	let { userId } = $props<{ userId: string }>();

	// State
	let enabling = $state(false);
	let error = $state<string | null>(null);
	let success = $state(false);

	async function enableConsent() {
		enabling = true;
		error = null;

		try {
			await api.users.updateConsent(userId, true);
			success = true;

			// Reload page after short delay to show updated data
			setTimeout(() => {
				window.location.reload();
			}, 1500);
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to enable insights';
			console.error('Failed to enable consent:', err);
		} finally {
			enabling = false;
		}
	}
</script>

<div class="consent-cta">
	{#if success}
		<!-- Success State -->
		<div class="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
			<CheckCircle class="w-16 h-16 text-green-600 mx-auto mb-4" />
			<h3 class="text-2xl font-semibold text-green-900 mb-2">Insights Enabled!</h3>
			<p class="text-green-700">Refreshing your personalized insights...</p>
		</div>
	{:else}
		<!-- CTA Card -->
		<div class="bg-gradient-to-br from-brand-blue/5 to-brand-green/5 border-2 border-brand-blue/20 rounded-xl p-8">
			<!-- Icon -->
			<div class="flex justify-center mb-6">
				<div class="w-20 h-20 bg-brand-blue/10 rounded-full flex items-center justify-center">
					<span class="text-4xl">🔓</span>
				</div>
			</div>

			<!-- Heading -->
			<h3 class="text-2xl font-bold text-gray-800 text-center mb-3">
				Unlock Personalized Insights
			</h3>
			<p class="text-center text-gray-600 mb-6">
				Enable insights to receive tailored financial education based on your spending patterns
			</p>

			<!-- Benefits List -->
			<div class="bg-white rounded-lg p-6 mb-6">
				<h4 class="font-semibold text-gray-800 mb-4 flex items-center gap-2">
					<Info class="w-5 h-5 text-brand-blue" />
					What you'll get:
				</h4>
				<ul class="space-y-3">
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
			</div>

			<!-- Error Message -->
			{#if error}
				<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
					<p class="text-sm text-red-800">
						<strong>Error:</strong> {error}
					</p>
				</div>
			{/if}

			<!-- CTA Button -->
			<button
				onclick={enableConsent}
				disabled={enabling}
				class="w-full py-4 px-6 bg-brand-blue text-white rounded-lg font-semibold text-lg hover:bg-blue-dark transition-colors disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed"
			>
				{enabling ? 'Enabling...' : 'Enable Insights'}
			</button>

			<!-- Disclaimer -->
			<div class="mt-6 p-4 bg-blue-50 border-l-4 border-brand-blue rounded">
				<p class="text-xs text-gray-600 leading-relaxed">
					<strong>How it works:</strong> We'll analyze your transaction patterns to identify your financial personality
					and provide relevant educational content. You can revoke consent anytime in account settings.
					This is educational content only - not financial advice.
				</p>
			</div>

			<!-- Demo Note -->
			<p class="text-xs text-gray-500 text-center mt-4 italic">
				Note: This is a demo application. All data is synthetic and consent is simulated.
			</p>
		</div>
	{/if}
</div>

<style>
	.consent-cta {
		max-width: 600px;
		margin: 0 auto;
	}
</style>
