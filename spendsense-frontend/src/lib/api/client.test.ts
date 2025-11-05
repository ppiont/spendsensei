/**
 * API Client Tests
 *
 * Basic tests to verify the API client works correctly.
 * Run these manually or integrate with a test framework later.
 */

import { api, APIClientError } from './client';

/**
 * Test helper to log results
 */
function logTest(name: string, passed: boolean, details?: string) {
  const symbol = passed ? '✅' : '❌';
  console.log(`${symbol} ${name}`);
  if (details) {
    console.log(`   ${details}`);
  }
}

/**
 * Test: Fetch user accounts (assumes user exists)
 */
export async function testGetUserAccounts(userId: string) {
  console.log('\n=== Testing getUserAccounts ===');
  try {
    const accounts = await api.accounts.getUserAccounts(userId);
    logTest('Fetch user accounts', true, `Found ${accounts.length} accounts`);

    if (accounts.length > 0) {
      const account = accounts[0];
      logTest('Account has required fields',
        !!(account.id && account.type && account.current_balance !== undefined),
        `Sample: ${account.name} (${account.type}/${account.subtype})`
      );
    }

    return true;
  } catch (error) {
    if (error instanceof APIClientError) {
      logTest('Fetch user accounts', false, `${error.status}: ${error.detail}`);
    } else {
      logTest('Fetch user accounts', false, String(error));
    }
    return false;
  }
}

/**
 * Test: Fetch user transactions
 */
export async function testGetUserTransactions(userId: string) {
  console.log('\n=== Testing getUserTransactions ===');
  try {
    const transactions = await api.transactions.getUserTransactions(userId, 10, 0);
    logTest('Fetch user transactions', true, `Found ${transactions.length} transactions`);

    if (transactions.length > 0) {
      const txn = transactions[0];
      logTest('Transaction has required fields',
        !!(txn.id && txn.date && txn.amount !== undefined),
        `Sample: ${txn.merchant_name || 'Unknown'} - $${txn.amount / 100}`
      );
    }

    return true;
  } catch (error) {
    if (error instanceof APIClientError) {
      logTest('Fetch user transactions', false, `${error.status}: ${error.detail}`);
    } else {
      logTest('Fetch user transactions', false, String(error));
    }
    return false;
  }
}

/**
 * Test: Fetch user insights
 */
export async function testGetUserInsights(userId: string) {
  console.log('\n=== Testing getUserInsights ===');
  try {
    const insights = await api.insights.getUserInsights(userId, 30);
    logTest('Fetch user insights', true,
      `Persona: ${insights.persona_type}, ${insights.education_recommendations.length} education, ${insights.offer_recommendations.length} offers`
    );

    if (insights.education_recommendations.length > 0) {
      const rec = insights.education_recommendations[0];
      logTest('Recommendation has required fields',
        !!(rec.persona && rec.content && rec.rationale),
        `Persona: ${rec.persona} (confidence: ${rec.confidence})`
      );
      logTest('Content has title and body',
        !!(rec.content.title && rec.content.body),
        `Title: ${rec.content.title.substring(0, 50)}...`
      );
    }

    return true;
  } catch (error) {
    if (error instanceof APIClientError) {
      logTest('Fetch user insights', false, `${error.status}: ${error.detail}`);
    } else {
      logTest('Fetch user insights', false, String(error));
    }
    return false;
  }
}

/**
 * Test: Handle 404 error
 */
export async function testUserNotFound() {
  console.log('\n=== Testing 404 Error Handling ===');
  try {
    await api.accounts.getUserAccounts('user_does_not_exist_12345');
    logTest('404 error handling', false, 'Should have thrown an error');
    return false;
  } catch (error) {
    if (error instanceof APIClientError && error.status === 404) {
      logTest('404 error handling', true, 'Correctly caught 404 error');
      return true;
    } else {
      logTest('404 error handling', false, 'Wrong error type');
      return false;
    }
  }
}

/**
 * Run all tests
 */
export async function runAllTests(testUserId: string) {
  console.log('==========================================');
  console.log('API Client Test Suite');
  console.log('==========================================');
  console.log(`Test User ID: ${testUserId}`);
  console.log(`API Base URL: ${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}`);

  const results = {
    accounts: await testGetUserAccounts(testUserId),
    transactions: await testGetUserTransactions(testUserId),
    insights: await testGetUserInsights(testUserId),
    notFound: await testUserNotFound()
  };

  const passed = Object.values(results).filter(Boolean).length;
  const total = Object.values(results).length;

  console.log('\n==========================================');
  console.log(`Tests passed: ${passed}/${total}`);
  console.log('==========================================\n');

  return passed === total;
}
