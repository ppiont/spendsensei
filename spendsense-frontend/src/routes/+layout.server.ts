import { PUBLIC_API_BASE_URL } from '$env/static/public';

export function load() {
  // Railway sets PUBLIC_API_BASE_URL at runtime
  // Pass it to all pages via layout
  return {
    apiBaseUrl: PUBLIC_API_BASE_URL || 'http://localhost:8000'
  };
}
