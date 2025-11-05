<script lang="ts">
	import { onMount } from 'svelte';
	import { selectedUserId } from '$lib/stores/userStore';
	import { api } from '$lib/api/client';
	import type { User } from '$lib/types';

	// Only show in development mode
	const isDev = import.meta.env.DEV;

	// State
	let users = $state<User[]>([]);
	let loading = $state(true);
	let currentUserId = $state('');

	// Subscribe to store
	selectedUserId.subscribe(value => {
		currentUserId = value;
	});

	// Fetch users
	async function loadUsers() {
		try {
			const data = await api.users.getUsers();
			users = data;

			// If no user selected, select first user
			if (!currentUserId && users.length > 0) {
				selectedUserId.set(users[0].id);
			}
		} catch (err) {
			console.error('Failed to load users:', err);
		} finally {
			loading = false;
		}
	}

	// Handle user change
	function handleUserChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		selectedUserId.set(target.value);
	}

	// Load users on mount
	onMount(() => {
		loadUsers();
	});
</script>

{#if isDev}
	<div class="user-switcher-strip">
		<div class="container">
			<div class="content">
				<span class="label">DEV MODE: VIEWING AS</span>
				{#if loading}
					<span class="loading">Loading users...</span>
				{:else if users.length > 0}
					<select
						value={currentUserId}
						onchange={handleUserChange}
						class="user-select"
					>
						{#each users as user}
							<option value={user.id}>{user.name}</option>
						{/each}
					</select>
				{:else}
					<span class="error">No users found</span>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	.user-switcher-strip {
		background-color: #1f2937;
		border-bottom: 1px solid #374151;
		position: sticky;
		top: 0;
		z-index: 50;
	}

	.container {
		max-width: 80rem;
		margin: 0 auto;
		padding: 0 1.5rem;
	}

	.content {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem 0;
		gap: 1rem;
	}

	.label {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #9ca3af;
	}

	.loading,
	.error {
		font-size: 0.875rem;
		color: #d1d5db;
	}

	.error {
		color: #fca5a5;
	}

	.user-select {
		padding: 0.5rem 0.75rem;
		background-color: #374151;
		border: 1px solid #4b5563;
		border-radius: 0.5rem;
		color: #f3f4f6;
		font-size: 0.875rem;
		cursor: pointer;
		outline: none;
		transition: all 0.15s ease;
		min-width: 200px;
	}

	.user-select:hover {
		background-color: #4b5563;
	}

	.user-select:focus {
		ring: 2px;
		ring-color: #3b82f6;
		border-color: #3b82f6;
	}

	@media (max-width: 640px) {
		.content {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.5rem;
		}

		.user-select {
			width: 100%;
		}
	}
</style>
