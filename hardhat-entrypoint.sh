#!/bin/sh
# Hardhat entrypoint
# Starts the node, waits for it to be ready, deploys the contract,
# and writes the address to a shared volume for the backend to read.

set -e
SHARED_DIR="/shared"
mkdir -p "$SHARED_DIR"

echo "[HARDHAT] Starting local Ethereum node..."
npx hardhat node --hostname 0.0.0.0 &
NODE_PID=$!

# Wait for node to be ready
echo "[HARDHAT] Waiting for node to be ready on port 8545..."
sleep 5
until npx hardhat --network localhost run scripts/check_node.js 2>/dev/null; do
  echo "[HARDHAT] Node not ready -- retrying in 2s"
  sleep 2
done

echo "[HARDHAT] Deploying AuditLog contract..."
DEPLOY_OUTPUT=$(npx hardhat run scripts/deploy.js --network localhost 2>&1)
echo "$DEPLOY_OUTPUT"

# Extract contract address (deploy.js prints it)
CONTRACT_ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oE '0x[a-fA-F0-9]{40}' | tail -1)
if [ -n "$CONTRACT_ADDR" ]; then
  echo "$CONTRACT_ADDR" > "$SHARED_DIR/contract_address.txt"
  echo "[HARDHAT] Contract deployed at: $CONTRACT_ADDR"
  echo "[HARDHAT] Address written to /shared/contract_address.txt"
else
  echo "[HARDHAT] WARNING: Could not extract contract address from deploy output"
fi

# Keep node running
echo "[HARDHAT] Node running. Waiting..."
wait $NODE_PID
