/**
 * User Store - Global state for selected user ID
 *
 * This store manages the currently selected user for demo purposes.
 * It persists the selection in localStorage so the user stays selected
 * across page navigation and browser refreshes.
 */

import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createUserStore() {
	// Load from localStorage if available (browser only)
	const stored = browser ? localStorage.getItem('selectedUserId') : null;
	const { subscribe, set } = writable<string>(stored || '');

	return {
		subscribe,
		set: (value: string) => {
			// Persist to localStorage
			if (browser) {
				localStorage.setItem('selectedUserId', value);
			}
			set(value);
		}
	};
}

export const selectedUserId = createUserStore();
