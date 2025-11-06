<script lang="ts">
	import { api } from '$lib/api/client';
	import { AlertCircle, Lock, Info } from '@lucide/svelte';

	// Props
	let { userId, onConsentChange } = $props<{
		userId: string;
		onConsentChange?: () => void;
	}>();

	// State
	let revoking = $state(false);
	let showConfirmDialog = $state(false);
	let error = $state<string | null>(null);

	async function revokeConsent() {
		revoking = true;
		error = null;

		try {
			await api.users.updateConsent(userId, false);

			// Notify parent component
			if (onConsentChange) {
				onConsentChange();
			}

			// Reload page after short delay
			setTimeout(() => {
				window.location.reload();
			}, 1000);
		} catch (err: any) {
			error = err.detail || err.message || 'Failed to revoke consent';
			console.error('Failed to revoke consent:', err);
		} finally {
			revoking = false;
			showConfirmDialog = false;
		}
	}
</script>

<div class="consent-manager">
	{#if showConfirmDialog}
		<!-- Confirmation Dialog -->
		<div class="confirmation-overlay" onclick={() => showConfirmDialog = false}>
			<div class="confirmation-dialog" onclick={(e) => e.stopPropagation()}>
				<div class="dialog-icon">
					<AlertCircle class="w-12 h-12 text-orange-500" />
				</div>
				<h3 class="dialog-title">Revoke Insights Consent?</h3>
				<p class="dialog-message">
					This will immediately stop all personalized insights, recommendations, and partner offers.
					Your financial data will remain stored but will no longer be analyzed for insights.
				</p>
				<p class="dialog-note">
					You can re-enable insights anytime to resume personalized recommendations.
				</p>

				{#if error}
					<div class="error-message">
						<strong>Error:</strong> {error}
					</div>
				{/if}

				<div class="dialog-actions">
					<button
						onclick={() => showConfirmDialog = false}
						disabled={revoking}
						class="btn-cancel"
					>
						Cancel
					</button>
					<button
						onclick={revokeConsent}
						disabled={revoking}
						class="btn-revoke"
					>
						{revoking ? 'Revoking...' : 'Yes, Revoke Consent'}
					</button>
				</div>
			</div>
		</div>
	{:else}
		<!-- Consent Status Banner -->
		<div class="consent-banner">
			<div class="banner-content">
				<div class="banner-icon">
					<Info class="w-5 h-5 text-blue-600" />
				</div>
				<div class="banner-text">
					<strong>Insights Enabled</strong>
					<span class="banner-description">
						Your financial data is being analyzed to provide personalized recommendations.
					</span>
				</div>
			</div>
			<button
				onclick={() => showConfirmDialog = true}
				class="revoke-button"
				title="Revoke insights consent"
			>
				<Lock class="w-4 h-4" />
				Revoke Consent
			</button>
		</div>
	{/if}
</div>

<style>
	.consent-manager {
		width: 100%;
	}

	/* Banner Styles */
	.consent-banner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 1rem 1.25rem;
		background: linear-gradient(to right, #eff6ff, #f0fdf4);
		border: 1px solid #bfdbfe;
		border-radius: 0.75rem;
	}

	.banner-content {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex: 1;
	}

	.banner-icon {
		flex-shrink: 0;
	}

	.banner-text {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.banner-text strong {
		font-size: 0.9375rem;
		color: #1f2937;
	}

	.banner-description {
		font-size: 0.8125rem;
		color: #6b7280;
	}

	.revoke-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1rem;
		background: white;
		border: 1px solid #d1d5db;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
		cursor: pointer;
		transition: all 0.15s ease;
		white-space: nowrap;
	}

	.revoke-button:hover {
		background: #f9fafb;
		border-color: #9ca3af;
		color: #1f2937;
	}

	/* Confirmation Dialog Styles */
	.confirmation-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 1rem;
	}

	.confirmation-dialog {
		background: white;
		border-radius: 1rem;
		padding: 2rem;
		max-width: 480px;
		width: 100%;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
	}

	.dialog-icon {
		display: flex;
		justify-content: center;
		margin-bottom: 1.5rem;
	}

	.dialog-title {
		font-size: 1.5rem;
		font-weight: 600;
		color: #1f2937;
		text-align: center;
		margin-bottom: 1rem;
	}

	.dialog-message {
		font-size: 0.9375rem;
		color: #4b5563;
		line-height: 1.6;
		margin-bottom: 1rem;
		text-align: center;
	}

	.dialog-note {
		font-size: 0.8125rem;
		color: #6b7280;
		padding: 0.75rem;
		background: #f9fafb;
		border-radius: 0.5rem;
		margin-bottom: 1.5rem;
		text-align: center;
	}

	.error-message {
		padding: 0.75rem;
		background: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 0.5rem;
		color: #991b1b;
		font-size: 0.875rem;
		margin-bottom: 1.5rem;
	}

	.dialog-actions {
		display: flex;
		gap: 0.75rem;
	}

	.btn-cancel,
	.btn-revoke {
		flex: 1;
		padding: 0.75rem 1.5rem;
		border-radius: 0.5rem;
		font-weight: 500;
		font-size: 0.9375rem;
		cursor: pointer;
		transition: all 0.15s ease;
		border: none;
	}

	.btn-cancel {
		background: #f3f4f6;
		color: #374151;
	}

	.btn-cancel:hover:not(:disabled) {
		background: #e5e7eb;
	}

	.btn-revoke {
		background: #ef4444;
		color: white;
	}

	.btn-revoke:hover:not(:disabled) {
		background: #dc2626;
	}

	.btn-cancel:disabled,
	.btn-revoke:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.consent-banner {
			flex-direction: column;
			align-items: stretch;
		}

		.banner-content {
			flex-direction: column;
			align-items: flex-start;
		}

		.revoke-button {
			justify-content: center;
		}

		.dialog-actions {
			flex-direction: column-reverse;
		}
	}
</style>
