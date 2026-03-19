const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying AuditLog smart contract...\n");

  const [deployer] = await ethers.getSigners();
  console.log(`📍 Deploying from account: ${deployer.address}`);
  console.log(`💰 Account balance: ${ethers.formatEther(await ethers.provider.getBalance(deployer.address))} ETH\n`);

  const AuditLog = await ethers.getContractFactory("AuditLog");
  const auditLog = await AuditLog.deploy();
  await auditLog.waitForDeployment();

  const contractAddress = await auditLog.getAddress();
  console.log(`✅ AuditLog deployed to: ${contractAddress}`);
  console.log(`📝 Transaction hash: ${auditLog.deploymentTransaction().hash}\n`);

  // Save deployment info to a JSON file for the backend to read
  const deploymentInfo = {
    contractAddress,
    deployerAddress: deployer.address,
    network: "localhost",
    chainId: 31337,
    deployedAt: new Date().toISOString(),
  };

  const deploymentPath = path.join(__dirname, "../deployment.json");
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`💾 Deployment info saved to: deployment.json`);

  // Also save to backend directory for easy access
  const backendDeploymentPath = path.join(__dirname, "../backend/deployment.json");
  if (fs.existsSync(path.join(__dirname, "../backend"))) {
    fs.writeFileSync(backendDeploymentPath, JSON.stringify(deploymentInfo, null, 2));
    console.log(`💾 Deployment info also saved to: backend/deployment.json`);
  }

  console.log("\n🎉 Deployment complete!");
  console.log("📋 Next steps:");
  console.log(`   1. Update backend/.env with CONTRACT_ADDRESS=${contractAddress}`);
  console.log(`   2. Start the FastAPI backend: cd backend && uvicorn main:app --reload`);
  console.log(`   3. Run the simulation: cd backend && python simulate_events.py`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
