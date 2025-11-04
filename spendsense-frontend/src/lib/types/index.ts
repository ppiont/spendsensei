/**
 * TypeScript type definitions for SpendSense API
 *
 * These types match the Pydantic schemas from the backend API.
 */

// User types
export interface User {
  id: string;
  name: string;
  email: string;
  consent: boolean;
  created_at: string;
}

export interface UserCreate {
  name: string;
  email: string;
}

// Account types
export interface Account {
  id: string;
  user_id: string;
  type: 'depository' | 'credit';
  subtype: 'checking' | 'savings' | 'credit_card';
  name: string;
  mask: string;
  balance: number; // in cents
  limit?: number; // in cents, credit cards only
  currency: string;
  apr?: number;
  min_payment?: number; // in cents
  is_overdue: boolean;
}

// Transaction types
export interface Transaction {
  id: string;
  account_id: string;
  date: string; // ISO 8601 format
  amount: number; // in cents, positive = debit, negative = credit
  merchant_name?: string;
  category: string;
  pending: boolean;
}

// Insight/Recommendation types
export interface EducationItem {
  id: string;
  title: string;
  summary: string;
  body: string;
  cta: string;
  source: string;
  relevance_score: number;
}

export interface Rationale {
  persona_type: string;
  confidence: number;
  explanation: string;
  key_signals: string[];
}

export interface Recommendation {
  content: EducationItem;
  rationale: Rationale;
  persona: string;
  confidence: number;
}

// API Error type
export interface APIError {
  detail: string;
}

// Helper function to convert cents to dollars
export function centsToDollars(cents: number): number {
  return cents / 100;
}

// Helper function to convert dollars to cents
export function dollarsToCents(dollars: number): number {
  return Math.round(dollars * 100);
}

// Helper function to format currency
export function formatCurrency(cents: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(centsToDollars(cents));
}

// Helper function to format category/subtype strings (snake_case → Title Case)
export function formatCategory(category: string): string {
  return category
    .toLowerCase()
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
