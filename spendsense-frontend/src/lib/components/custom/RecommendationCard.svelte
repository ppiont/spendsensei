<script lang="ts">
	import { cn } from '$lib/utils';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';

	interface Props {
		icon: string;
		title: string;
		body: string;
		rationale: string;
		cta?: string;
		expanded?: boolean;
	}

	let { icon, title, body, rationale, cta, expanded = false }: Props = $props();

	let isHovered = $state(false);
</script>

<div
	class={cn('card-recommendation', (isHovered || expanded) && 'active')}
	onmouseenter={() => (isHovered = true)}
	onmouseleave={() => (isHovered = false)}
	role="article"
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

	<!-- Body -->
	<p class="text-sm leading-relaxed text-gray-600 mb-4 line-clamp-3">{body}</p>

	<!-- Rationale box -->
	<div class="bg-gray-50 rounded-lg p-3 mb-4">
		<p class="text-xs text-gray-600 leading-relaxed">
			<span class="font-semibold text-gray-700">Because:</span>
			{rationale}
		</p>
	</div>

	<!-- CTA button (optional) -->
	{#if cta}
		<Button class="w-full btn-brand">
			{cta}
		</Button>
	{/if}

	<!-- Placeholder for expanded state (Story 7.3) -->
	{#if expanded}
		<div class="mt-4 pt-4 border-t border-gray-200">
			<p class="text-xs text-gray-500 italic">Expanded content will be added in Story 7.3</p>
		</div>
	{/if}
</div>
