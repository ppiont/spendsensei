<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	// Redirect to dashboard immediately on mount
	onMount(() => {
		goto('/dashboard', { replaceState: true });
	});
</script>

<div class="min-h-screen bg-gray-50 flex items-center justify-center">
	<div class="text-center">
		<p class="text-gray-600 text-lg">Redirecting to Dashboard...</p>
	</div>
</div>
