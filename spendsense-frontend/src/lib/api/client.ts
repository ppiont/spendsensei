/**
 * SpendSense API Client
 *
 * Type-safe API client for communicating with the SpendSense backend.
 * Handles errors, timeouts, and JSON parsing automatically.
 */

import { env } from '$env/dynamic/public';
import { browser } from '$app/environment';
import type {
  User,
  UserCreate,
  Account,
  Transaction,
  Recommendation,
  InsightsResponse,
  InspectUserResponse,
  APIError
} from '$lib/types';

// Get API base URL from environment variable
// SvelteKit's $env/dynamic/public works at runtime (not build-time)
// This is critical for adapter-node with SSR
function getApiBaseUrl(): string {
  // Try Railway's auto-provided service URL first
  if (env.PUBLIC_RAILWAY_SERVICE_SPENDSENSEI_URL) {
    return `https://${env.PUBLIC_RAILWAY_SERVICE_SPENDSENSEI_URL}`;
  }

  // Fallback to explicit API base URL
  if (env.PUBLIC_API_BASE_URL) {
    return env.PUBLIC_API_BASE_URL;
  }

  // Development fallback
  return 'http://localhost:8000';
}

const API_BASE_URL = getApiBaseUrl();

// Request timeout in milliseconds
const REQUEST_TIMEOUT = 10000;

/**
 * Custom error class for API errors
 */
export class APIClientError extends Error {
  constructor(
    message: string,
    public status?: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'APIClientError';
  }
}

/**
 * Helper function to make API requests with proper error handling
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeout = REQUEST_TIMEOUT
): Promise<Response> {
  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error && error.name === 'AbortError') {
      throw new APIClientError('Request timeout', undefined, 'The request took too long to complete');
    }

    throw new APIClientError(
      'Network error',
      undefined,
      error instanceof Error ? error.message : 'Unknown network error'
    );
  }
}

/**
 * Helper function to handle API responses
 */
async function handleResponse<T>(response: Response): Promise<T> {
  // Handle non-JSON responses
  const contentType = response.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    throw new APIClientError(
      'Invalid response format',
      response.status,
      'Expected JSON response from server'
    );
  }

  // Parse JSON
  let data: any;
  try {
    data = await response.json();
  } catch (error) {
    throw new APIClientError(
      'Failed to parse response',
      response.status,
      'Invalid JSON in server response'
    );
  }

  // Handle error responses
  if (!response.ok) {
    const apiError = data as APIError;
    throw new APIClientError(
      `API error: ${response.status}`,
      response.status,
      apiError.detail || 'Unknown error'
    );
  }

  return data as T;
}

/**
 * User API
 */
export const userAPI = {
  /**
   * Get all users
   */
  async getUsers(): Promise<User[]> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/users`);
    return handleResponse<User[]>(response);
  },

  /**
   * Create a new user
   */
  async createUser(userData: UserCreate): Promise<User> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/users`, {
      method: 'POST',
      body: JSON.stringify(userData)
    });
    return handleResponse<User>(response);
  },

  /**
   * Update user consent status
   */
  async updateConsent(userId: string, consent: boolean): Promise<User> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/users/consent?user_id=${userId}&consent=${consent}`, {
      method: 'POST'
    });
    return handleResponse<User>(response);
  }
};

/**
 * Account API
 */
export const accountAPI = {
  /**
   * Get all accounts for a user
   */
  async getUserAccounts(userId: string): Promise<Account[]> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/accounts/${userId}`);
    return handleResponse<Account[]>(response);
  }
};

/**
 * Transaction API
 */
export const transactionAPI = {
  /**
   * Get transactions for a user with pagination
   */
  async getUserTransactions(
    userId: string,
    limit = 100,
    offset = 0
  ): Promise<Transaction[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    });

    const response = await fetchWithTimeout(
      `${API_BASE_URL}/transactions/${userId}?${params}`
    );
    return handleResponse<Transaction[]>(response);
  }
};

/**
 * Insights API
 */
export const insightsAPI = {
  /**
   * Get personalized insights and recommendations for a user.
   *
   * Returns education content, partner offers, persona info, and signals summary.
   */
  async getUserInsights(userId: string, window = 30): Promise<InsightsResponse> {
    const params = new URLSearchParams({
      window: window.toString()
    });

    const response = await fetchWithTimeout(
      `${API_BASE_URL}/insights/${userId}?${params}`
    );
    return handleResponse<InsightsResponse>(response);
  }
};

/**
 * Operator API
 */
export const operatorAPI = {
  /**
   * Inspect user data for operator debugging (no consent checks).
   *
   * This endpoint provides comprehensive user data for internal review
   * and debugging purposes. Unlike the insights endpoint, this does NOT
   * check consent and returns all available data.
   */
  async inspectUser(userId: string, window = 30): Promise<InspectUserResponse> {
    const params = new URLSearchParams({
      window: window.toString()
    });

    const response = await fetchWithTimeout(
      `${API_BASE_URL}/operator/inspect/${userId}?${params}`
    );
    return handleResponse<InspectUserResponse>(response);
  }
};

/**
 * Combined API client
 */
export const api = {
  users: userAPI,
  accounts: accountAPI,
  transactions: transactionAPI,
  insights: insightsAPI,
  operator: operatorAPI
};

export default api;
