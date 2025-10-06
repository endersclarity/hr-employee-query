const API_BASE_URL = import.meta.env?.VITE_API_URL || '';  // Empty string for relative URLs (same origin)
const API_TIMEOUT = parseInt(import.meta.env?.VITE_API_TIMEOUT || '10000', 10);

const ERROR_MESSAGES = {
  'VALIDATION_ERROR': 'Query validation failed. Only SELECT queries are permitted.',
  'LLM_ERROR': 'Unable to process query. Please try again or rephrase.',
  'DB_ERROR': 'Database query failed. Please check your query and try again.'
};

export async function submitQuery(query) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query}),
      signal: controller.signal
    });

    // Check response status before parsing JSON
    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(ERROR_MESSAGES[data.error_type] || data.error);
    }

    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchQueryStatus(queryLogId) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(`${API_BASE_URL}/api/query/${queryLogId}`, {
      method: 'GET',
      headers: {'Content-Type': 'application/json'},
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchAnalysisReport() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(`${API_BASE_URL}/api/reports/analysis`, {
      method: 'GET',
      headers: {'Content-Type': 'application/json'},
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
