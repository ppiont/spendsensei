<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { selectedUserId } from '$lib/stores/userStore';
	import { ChevronDown, TrendingUp } from '@lucide/svelte';
	import type { User } from '$lib/types';

	// State
	let users = $state<User[]>([]);
	let showUserMenu = $state(false);

	// Get current user ID from store (reactive)
	let currentUserId = $derived($selectedUserId);

	// Fetch users on mount
	onMount(async () => {
		try {
			const response = await fetch('http://localhost:8000/users');
			users = await response.json();

			// Set first user if none selected
			if (!$selectedUserId && users.length > 0) {
				selectedUserId.set(users[0].id);
			}
		} catch (err) {
			console.error('Failed to load users:', err);
		}
	});

	// Get current user
	const currentUser = $derived(users.find((u) => u.id === currentUserId));

	// Handle user selection
	function selectUser(userId: string) {
		selectedUserId.set(userId);
		showUserMenu = false;
	}

	// Check if route is active
	function isActive(path: string): boolean {
		return $page.url.pathname === path || $page.url.pathname.startsWith(path + '/');
	}

	// Close menu when clicking outside
	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.user-menu-container')) {
			showUserMenu = false;
		}
	}
</script>

<svelte:window onclick={handleClickOutside} />

<nav class="navigation">
	<div class="nav-container">
		<!-- Logo/Brand -->
		<a href="/" class="brand">
			<TrendingUp class="brand-icon" />
			<span class="brand-text">SpendSense</span>
		</a>

		<!-- Main Navigation Links -->
		<div class="nav-links">
			<a href="/dashboard" class="nav-link" class:active={isActive('/dashboard')}>
				Dashboard
			</a>
			<a href="/transactions" class="nav-link" class:active={isActive('/transactions')}>
				Transactions
			</a>
		</div>

		<!-- User Switcher (Dev Mode) -->
		<div class="user-menu-container">
			<button onclick={() => (showUserMenu = !showUserMenu)} class="user-button">
				<span class="dev-badge">DEV</span>
				<span class="user-name">{currentUser?.name || 'Select User'}</span>
				<ChevronDown class={`w-4 h-4 chevron ${showUserMenu ? 'open' : ''}`} />
			</button>

			{#if showUserMenu}
				<div class="user-dropdown">
					{#each users as user (user.id)}
						<button
							onclick={() => selectUser(user.id)}
							class="user-option"
							class:selected={user.id === currentUserId}
						>
							<div class="user-info">
								<span class="user-option-name">{user.name}</span>
								<span class="user-option-email">{user.email}</span>
							</div>
							{#if user.id === currentUserId}
								<span class="checkmark">✓</span>
							{/if}
						</button>
					{/each}

					<!-- Operator link -->
					<div class="dropdown-divider"></div>
					<a href="/operator" class="operator-link" onclick={() => (showUserMenu = false)}>
						<span class="operator-icon">🔧</span>
						<span>Operator View</span>
					</a>
				</div>
			{/if}
		</div>
	</div>
</nav>

<style>
	.navigation {
		width: 100%;
		background: white;
		border-bottom: 1px solid #e5e7eb; /* gray-200 */
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
		position: sticky;
		top: 0;
		z-index: 50;
	}

	.nav-container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 1.5rem;
		height: 4rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 2rem;
	}

	/* Brand */
	.brand {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		text-decoration: none;
		font-weight: 600;
		font-size: 1.125rem;
		color: #1f2937; /* gray-800 */
		transition: color 0.15s ease;
		flex-shrink: 0;
	}

	.brand:hover {
		color: #3b82f6; /* brand-blue */
	}

	.brand-icon {
		width: 1.5rem;
		height: 1.5rem;
		color: #3b82f6; /* brand-blue */
	}

	.brand-text {
		font-size: 1.25rem;
		letter-spacing: -0.025em;
	}

	/* Nav Links */
	.nav-links {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex: 1;
	}

	.nav-link {
		position: relative;
		padding: 0.75rem 1rem;
		font-size: 0.9375rem;
		font-weight: 500;
		color: #6b7280; /* gray-500 */
		text-decoration: none;
		border-radius: 0.5rem;
		transition: all 0.15s ease;
	}

	.nav-link:hover {
		color: #1f2937; /* gray-800 */
		background-color: #f9fafb; /* gray-50 */
	}

	.nav-link.active {
		color: #3b82f6; /* brand-blue */
		background-color: #eff6ff; /* blue-50 */
	}

	.nav-link.active::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 1rem;
		right: 1rem;
		height: 2px;
		background-color: #3b82f6; /* brand-blue */
		border-radius: 2px 2px 0 0;
	}

	/* User Menu */
	.user-menu-container {
		position: relative;
		flex-shrink: 0;
	}

	.user-button {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.5rem 0.875rem;
		background: #f9fafb; /* gray-50 */
		border: 1px solid #e5e7eb; /* gray-200 */
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.15s ease;
		font-size: 0.875rem;
	}

	.user-button:hover {
		background: #f3f4f6; /* gray-100 */
		border-color: #d1d5db; /* gray-300 */
	}

	.dev-badge {
		padding: 0.125rem 0.375rem;
		background: #3b82f6; /* brand-blue */
		color: white;
		font-size: 0.625rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		border-radius: 0.25rem;
	}

	.user-name {
		font-weight: 500;
		color: #374151; /* gray-700 */
		max-width: 150px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	:global(.chevron) {
		color: #9ca3af; /* gray-400 */
		transition: transform 0.15s ease;
	}

	:global(.chevron.open) {
		transform: rotate(180deg);
	}

	/* Dropdown */
	.user-dropdown {
		position: absolute;
		top: calc(100% + 0.5rem);
		right: 0;
		min-width: 280px;
		max-height: min(400px, 60vh); /* Responsive max height */
		background: white;
		border: 1px solid #e5e7eb; /* gray-200 */
		border-radius: 0.5rem;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
		overflow-y: auto; /* Enable vertical scrolling */
		overflow-x: hidden;
		z-index: 100;
	}

	.user-option {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem 1rem;
		background: white;
		border: none;
		cursor: pointer;
		text-align: left;
		transition: background-color 0.15s ease;
	}

	.user-option:hover {
		background-color: #f9fafb; /* gray-50 */
	}

	.user-option.selected {
		background-color: #eff6ff; /* blue-50 */
	}

	.user-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		flex: 1;
	}

	.user-option-name {
		font-size: 0.875rem;
		font-weight: 500;
		color: #1f2937; /* gray-800 */
	}

	.user-option-email {
		font-size: 0.75rem;
		color: #6b7280; /* gray-500 */
	}

	.checkmark {
		color: #3b82f6; /* brand-blue */
		font-weight: 700;
		font-size: 1rem;
	}

	.dropdown-divider {
		height: 1px;
		background-color: #e5e7eb; /* gray-200 */
		margin: 0.25rem 0;
	}

	.operator-link {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: #6b7280; /* gray-500 */
		text-decoration: none;
		transition: all 0.15s ease;
	}

	.operator-link:hover {
		background-color: #f9fafb; /* gray-50 */
		color: #1f2937; /* gray-800 */
	}

	.operator-icon {
		font-size: 1rem;
	}

	/* Mobile Responsive */
	@media (max-width: 640px) {
		.nav-container {
			padding: 0 1rem;
			gap: 1rem;
		}

		.brand-text {
			display: none;
		}

		.nav-links {
			gap: 0.25rem;
		}

		.nav-link {
			padding: 0.5rem 0.75rem;
			font-size: 0.875rem;
		}

		.nav-link.active::after {
			left: 0.75rem;
			right: 0.75rem;
		}

		.user-name {
			max-width: 100px;
		}

		.user-dropdown {
			min-width: 240px;
		}
	}
</style>
