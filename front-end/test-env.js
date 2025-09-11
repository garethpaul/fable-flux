// Test script to verify environment variable configuration
console.log("Testing POE_API_KEY environment variable configuration...\n");

// Check if POE_API_KEY is available from environment
const apiKey = process.env.POE_API_KEY;

if (apiKey) {
  console.log("✅ POE_API_KEY found in environment variables");
  console.log(`   Key starts with: ${apiKey.substring(0, 10)}...`);
  console.log(`   Key length: ${apiKey.length} characters`);
} else {
  console.log("❌ POE_API_KEY not found in environment variables");
  console.log("   Please set POE_API_KEY either:");
  console.log(
    "   1. As a system environment variable: export POE_API_KEY=your_key"
  );
  console.log("   2. In .env.local file: POE_API_KEY=your_key");
}

console.log("\nEnvironment variable precedence:");
console.log("1. System environment variables (highest priority)");
console.log("2. .env.local file (fallback for development)");
