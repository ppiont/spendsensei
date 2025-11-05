<script lang="ts">
	import {
		TrendingUp,
		CreditCard,
		DollarSign,
		Layers,
		CheckCircle2
	} from '@lucide/svelte';

	interface Props {
		personaName: string;
		personaType?: string;
	}

	let { personaName, personaType = '' }: Props = $props();

	// Map persona types to icons and subtitles
	const type = $derived(personaType.toLowerCase());

	const Icon = $derived(
		type === 'savings_builder'
			? TrendingUp
			: type === 'high_utilization'
				? CreditCard
				: type === 'variable_income'
					? DollarSign
					: type === 'subscription_heavy'
						? Layers
						: CheckCircle2
	);

	const subtitle = $derived(
		type === 'savings_builder'
			? 'Building wealth consistently'
			: type === 'high_utilization'
				? 'Managing credit actively'
				: type === 'variable_income'
					? 'Navigating income variability'
					: type === 'subscription_heavy'
						? 'Optimizing recurring expenses'
						: type === 'balanced'
							? 'Maintaining financial health'
							: 'Building financial wellness'
	);

	const color = $derived(
		type === 'savings_builder' || type === 'balanced'
			? 'text-brand-green'
			: type === 'high_utilization'
				? 'text-brand-coral'
				: type === 'variable_income'
					? 'text-yellow'
					: 'text-brand-blue'
	);
</script>

<div class="flex items-center gap-3">
	<!-- Icon circle (48px) -->
	<div class="w-12 h-12 rounded-full flex-shrink-0 bg-blue-50 flex items-center justify-center">
		<Icon class={`w-6 h-6 ${color}`} />
	</div>

	<!-- Persona info -->
	<div class="flex flex-col">
		<h3 class="text-lg font-semibold text-gray-800">{personaName}</h3>
		<p class="text-sm text-gray-600">{subtitle}</p>
	</div>
</div>
