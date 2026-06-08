// Test script to verify environment variable configuration
console.log("Testing Fable Flux frontend environment configuration...\n");

const requiredVars = ["MODAL_API_KEY", "MODAL_API_URL"];
const missingVars = requiredVars.filter((name) => !process.env[name]);

if (missingVars.length === 0) {
  console.log("Required Modal environment variables are set.");
} else {
  console.log(`Missing required variables: ${missingVars.join(", ")}`);
  console.log("Set them in the system environment or front-end/.env.local.");
}

if (process.env.MODAL_MODEL) {
  console.log("MODAL_MODEL override is set.");
} else {
  console.log("MODAL_MODEL is not set; the API route default will be used.");
}
