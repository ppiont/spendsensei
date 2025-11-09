import { env } from '$env/dynamic/public';

export function load() {
  // Read PUBLIC_API_BASE_URL at runtime from Railway environment
  // This runs on the SERVER, where process.env is available
  return {
    apiBaseUrl: env.PUBLIC_API_BASE_URL || 'http://localhost:8000'
  };
}
