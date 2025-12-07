// Test script to verify frontend-backend connection
// Run this with: node test-connection.js

const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_VERSION = "/api/v1";

async function testConnection() {
  console.log("🔍 Testing Frontend-Backend Connection...\n");
  console.log(`Backend URL: ${API_BASE_URL}${API_VERSION}\n`);

  const endpoints = [
    { name: "Health Check", url: `${API_BASE_URL}/api/health`, method: "GET" },
    { name: "Root", url: `${API_BASE_URL}/`, method: "GET" },
    { name: "Get All Accounts", url: `${API_BASE_URL}${API_VERSION}/accounts`, method: "GET" },
    { name: "Get Stock Prices", url: `${API_BASE_URL}${API_VERSION}/stocks/prices`, method: "GET" },
    { name: "Competition Status", url: `${API_BASE_URL}${API_VERSION}/competition/status`, method: "GET" },
  ];

  for (const endpoint of endpoints) {
    try {
      console.log(`Testing: ${endpoint.name}`);
      const response = await fetch(endpoint.url, {
        method: endpoint.method,
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log(`✅ ${endpoint.name}: SUCCESS`);
        console.log(`   Response:`, JSON.stringify(data, null, 2).substring(0, 200));
      } else {
        console.log(`❌ ${endpoint.name}: FAILED (Status: ${response.status})`);
      }
    } catch (error) {
      console.log(`❌ ${endpoint.name}: ERROR - ${error.message}`);
    }
    console.log("");
  }
}

// Run the test
testConnection().catch(console.error);

