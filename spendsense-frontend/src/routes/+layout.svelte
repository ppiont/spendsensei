<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import UserSwitcher from '$lib/components/UserSwitcher.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="description" content="SpendSense - Personalized financial education based on your spending patterns" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
</svelte:head>

<!-- Skip to main content link (WCAG 2.1 AA) -->
<a
	href="#main-content"
	class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-brand-blue focus:text-white focus:rounded-lg focus:shadow-lg"
>
	Skip to main content
</a>

<!-- Global User Switcher (dev mode only) -->
<UserSwitcher />

<main id="main-content">
	{@render children()}
</main>
