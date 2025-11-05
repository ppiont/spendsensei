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

// Account types - Plaid-compliant
export interface Account {
  id: string;
  user_id: string;
  type: 'depository' | 'credit';
  subtype: 'checking' | 'savings' | 'credit_card';
  name: string;
  mask: string;
  current_balance: number; // in cents
  available_balance?: number; // in cents
  limit?: number; // in cents, credit cards only
  currency: string;
  holder_category: string; // 'personal' or 'business'
  apr?: number;
  min_payment?: number; // in cents
  is_overdue: boolean;
  last_payment_amount?: number; // in cents
  last_payment_date?: string; // ISO 8601 format
  next_payment_due_date?: string; // ISO 8601 format
  last_statement_balance?: number; // in cents
  last_statement_date?: string; // ISO 8601 format
  interest_rate?: number;
}

// Transaction types - Plaid-compliant
export interface Transaction {
  id: string;
  account_id: string;
  date: string; // ISO 8601 format
  amount: number; // in cents, positive = debit, negative = credit
  merchant_name?: string;
  merchant_entity_id?: string; // Normalized merchant ID
  personal_finance_category_primary: string; // e.g., FOOD_AND_DRINK, INCOME
  personal_finance_category_detailed?: string; // e.g., RESTAURANTS, GROCERIES
  payment_channel?: string; // 'online', 'in_store', 'other'
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

export interface PartnerOffer {
  id: string;
  title: string;
  provider: string;
  offer_type: string;
  summary: string;
  benefits: string[];
  eligibility_explanation: string;
  cta: string;
  cta_url: string;
  disclaimer: string;
  relevance_score: number;
  eligibility_met: boolean;
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

export interface OfferRecommendation {
  offer: PartnerOffer;
  rationale: Rationale;
  persona: string;
  confidence: number;
}

export interface InsightsResponse {
  persona_type: string;
  confidence: number;
  education_recommendations: Recommendation[];
  offer_recommendations: OfferRecommendation[];
  signals_summary: Record<string, any>;
  disclaimer: string;
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
