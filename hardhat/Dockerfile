# ── Hardhat Dockerfile ─────────────────────────────────────────────────────────
# Starts a local Ethereum node AND auto-deploys the AuditLog contract.
# Writes the deployed contract address to /shared/contract_address.txt
# so the backend container can read it on startup.
FROM node:20-alpine

WORKDIR /app

# Install Hardhat dependencies
COPY package*.json ./
RUN npm ci

COPY contracts/ contracts/
COPY scripts/ scripts/
COPY hardhat.config.js .

# Entrypoint: start node + deploy in background, keep node running
COPY hardhat-entrypoint.sh /hardhat-entrypoint.sh
RUN chmod +x /hardhat-entrypoint.sh

EXPOSE 8545
ENTRYPOINT ["/hardhat-entrypoint.sh"]
