<script lang="ts">
	import { cn } from '$lib/utils';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { ChevronDown, ChevronUp } from '@lucide/svelte';

	interface Props {
		icon: string;
		title: string;
		body: string;
		rationale: string;
		cta?: string;
		expanded?: boolean;
		onclick?: () => void;
	}

	let { icon, title, body, rationale, cta, expanded = false, onclick }: Props = $props();

	let isHovered = $state(false);
</script>

<button
	class={cn(
		'card-recommendation text-left w-full',
		(isHovered || expanded) && 'active',
		'cursor-pointer'
	)}
	onmouseenter={() => (isHovered = true)}
	onmouseleave={() => (isHovered = false)}
	onclick={onclick}
	role="article"
	aria-expanded={expanded}
>
	<!-- Header with icon and badge -->
	<div class="flex items-start gap-3 mb-4">
		<!-- Icon circle -->
		<div class="icon-circle text-xl flex-shrink-0">
			{icon}
		</div>

		<!-- Badge -->
		<Badge variant="secondary" class="badge-education text-xs font-semibold">
			EDUCATION
		</Badge>
	</div>

	<!-- Title -->
	<h3 class="text-base font-semibold text-gray-800 mb-2">{title}</h3>

	<!-- Body - with line-clamp when not expanded -->
	<p class={cn('text-sm leading-relaxed text-gray-600 mb-4', !expanded && 'line-clamp-3')}>
		{body}
	</p>

	<!-- Rationale box -->
	<div class="bg-gray-50 rounded-lg p-3 mb-4">
		<p class="text-xs text-gray-600 leading-relaxed">
			<span class="font-semibold text-gray-700">Because:</span>
			{rationale}
		</p>
	</div>

	<!-- CTA button (only visible when expanded) -->
	{#if expanded && cta}
		<div class="mt-4 pt-4 border-t border-gray-200">
			<span class="text-brand-blue font-semibold text-sm hover:text-blue-dark transition-colors">
				{cta} →
			</span>
		</div>
	{/if}

	<!-- Expand/Collapse indicator -->
	<div class="flex items-center justify-center gap-2 mt-4 pt-4 border-t border-gray-200 text-gray-600 text-sm">
		{#if expanded}
			<ChevronUp class="w-4 h-4" />
			<span>Show less</span>
		{:else}
			<ChevronDown class="w-4 h-4" />
			<span>Read more</span>
		{/if}
	</div>
</button>
