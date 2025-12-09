/**
 * Base API fetch utility
 * Handles common request logic, error handling, and timeouts
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_VERSION = "/api/v1";

export async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${API_VERSION}${endpoint}`;
  const defaultOptions = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {}),
    },
  };

  if (config.body && typeof config.body === "object") {
    config.body = JSON.stringify(config.body);
  }

  // Add timeout for long-running requests (like start_competition)
  const timeout = options.timeout || 300000; // 5 minutes default
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  config.signal = controller.signal;

  try {
    const response = await fetch(url, config);
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.message || errorJson.detail || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === "AbortError") {
      throw new Error(
        `Request timeout after ${
          timeout / 1000
        } seconds. The server may be processing a long-running operation.`
      );
    }
    console.error("API request failed:", error);
    throw error;
  }
}

