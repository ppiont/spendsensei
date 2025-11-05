<script lang="ts">
	import { cn } from '$lib/utils';

	interface Props {
		label: string;
		value: string | number;
		change?: number;
		changeAmount?: string; // e.g., "$240"
		variant?: 'standard' | 'featured' | 'alert' | 'success';
	}

	let { label, value, change, changeAmount, variant = 'standard' }: Props = $props();

	// Determine change color class
	const changeColorClass = $derived(
		change !== undefined ? (change >= 0 ? 'text-brand-green' : 'text-brand-coral') : ''
	);
	const changeIcon = $derived(change !== undefined ? (change >= 0 ? '↑' : '↓') : undefined);
</script>

<div
	class={cn(
		'rounded-xl p-8 transition-all duration-150',
		variant === 'standard' && 'card-standard',
		variant === 'featured' && 'card-featured',
		variant === 'alert' && 'card-alert',
		variant === 'success' && 'card-success'
	)}
>
	<!-- Label -->
	<div class="text-xs font-semibold uppercase tracking-wider mb-3 text-gray-600">
		{label}
	</div>

	<!-- Value -->
	<div class="text-3xl font-semibold mb-2 text-gray-800">
		{value}
	</div>

	<!-- Change indicator (optional) -->
	{#if change !== undefined}
		<div class={cn('text-sm font-medium', changeColorClass)}>
			{#if changeAmount}
				<!-- Direction 6 format: ↑ $240 this month (+1.9%) -->
				<span>{changeIcon} {changeAmount} this month ({change >= 0 ? '+' : ''}{change}%)</span>
			{:else}
				<!-- Simple format: ↑ 5.2% -->
				<span>{changeIcon} {Math.abs(change)}%</span>
			{/if}
		</div>
	{/if}
</div>
