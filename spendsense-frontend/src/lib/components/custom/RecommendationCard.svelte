<script lang="ts">
	import { cn } from '$lib/utils';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { ChevronDown, ChevronUp } from '@lucide/svelte';
	import { marked } from 'marked';

	interface Props {
		icon: string;
		title: string;
		summary: string;
		body: string;
		rationale: string;
		cta?: string;
		expanded?: boolean;
		onclick?: () => void;
	}

	let { icon, title, summary, body, rationale, cta, expanded = false, onclick }: Props = $props();

	let isHovered = $state(false);

	// Convert markdown to HTML for body content
	const bodyHtml = $derived(marked.parse(body, { async: false }) as string);
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

	<!-- Summary (always visible, but line-clamped when collapsed) -->
	<p class={cn('text-sm leading-relaxed text-gray-600 mb-4', !expanded && 'line-clamp-3')}>
		{summary}
	</p>

	<!-- Full body content (only visible when expanded) -->
	{#if expanded}
		<div class="prose prose-sm max-w-none mb-4 text-gray-700">
			{@html bodyHtml}
		</div>
	{/if}

	<!-- Rationale box -->
	<div class="bg-gray-50 rounded-lg p-3 mb-4">
		<p class="text-xs text-gray-600 leading-relaxed">
			<span class="font-semibold text-gray-700">Because:</span>
			{rationale}
		</p>
	</div>

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

<style>
	/* Markdown prose styling */
	:global(.prose) {
		color: #374151;
		max-width: none;
	}

	:global(.prose p) {
		margin-bottom: 0.75rem;
		line-height: 1.6;
	}

	:global(.prose strong) {
		font-weight: 600;
		color: #1f2937;
	}

	:global(.prose ul) {
		list-style-type: disc;
		padding-left: 1.5rem;
		margin-bottom: 0.75rem;
	}

	:global(.prose ol) {
		list-style-type: decimal;
		padding-left: 1.5rem;
		margin-bottom: 0.75rem;
	}

	:global(.prose li) {
		margin-bottom: 0.25rem;
		line-height: 1.5;
	}

	:global(.prose h3) {
		font-size: 1rem;
		font-weight: 600;
		color: #1f2937;
		margin-top: 1rem;
		margin-bottom: 0.5rem;
	}

	:global(.prose h4) {
		font-size: 0.9rem;
		font-weight: 600;
		color: #374151;
		margin-top: 0.75rem;
		margin-bottom: 0.5rem;
	}

	:global(.prose blockquote) {
		border-left: 3px solid #d1d5db;
		padding-left: 1rem;
		font-style: italic;
		color: #6b7280;
		margin: 0.75rem 0;
	}

	:global(.prose code) {
		background-color: #f3f4f6;
		padding: 0.125rem 0.25rem;
		border-radius: 0.25rem;
		font-size: 0.875em;
		font-family: ui-monospace, monospace;
	}

	:global(.prose hr) {
		border-color: #e5e7eb;
		margin: 1rem 0;
	}
</style>
