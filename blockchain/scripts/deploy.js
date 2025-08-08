const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying GreenLink Smart Contracts...");
  console.log("==========================================");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying contracts with account:", deployer.address);
  console.log("💰 Account balance:", (await deployer.getBalance()).toString());

  // Deploy CarbonCreditToken
  console.log("\n1️⃣ Deploying CarbonCreditToken...");
  const CarbonCreditToken = await hre.ethers.getContractFactory("CarbonCreditToken");
  const carbonCreditToken = await CarbonCreditToken.deploy("https://api.greenlink.com/metadata/");
  await carbonCreditToken.deployed();
  console.log("✅ CarbonCreditToken deployed to:", carbonCreditToken.address);

  // Deploy CarbonCreditMarket
  console.log("\n2️⃣ Deploying CarbonCreditMarket...");
  const CarbonCreditMarket = await hre.ethers.getContractFactory("CarbonCreditMarket");
  const carbonCreditMarket = await CarbonCreditMarket.deploy(carbonCreditToken.address);
  await carbonCreditMarket.deployed();
  console.log("✅ CarbonCreditMarket deployed to:", carbonCreditMarket.address);

  // Deploy GreenLinkRegistry
  console.log("\n3️⃣ Deploying GreenLinkRegistry...");
  const GreenLinkRegistry = await hre.ethers.getContractFactory("GreenLinkRegistry");
  const greenLinkRegistry = await GreenLinkRegistry.deploy(carbonCreditToken.address);
  await greenLinkRegistry.deployed();
  console.log("✅ GreenLinkRegistry deployed to:", greenLinkRegistry.address);

  // Grant marketplace operator role to registry
  console.log("\n4️⃣ Setting up permissions...");
  await carbonCreditToken.grantRole(await carbonCreditToken.OPERATOR_ROLE(), greenLinkRegistry.address);
  console.log("✅ Granted registry operator role on token contract");

  // Verify contracts on Etherscan (if not on local network)
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\n5️⃣ Verifying contracts on Etherscan...");
    
    try {
      await hre.run("verify:verify", {
        address: carbonCreditToken.address,
        constructorArguments: ["https://api.greenlink.com/metadata/"],
      });
      console.log("✅ CarbonCreditToken verified");
    } catch (error) {
      console.log("⚠️ CarbonCreditToken verification failed:", error.message);
    }

    try {
      await hre.run("verify:verify", {
        address: carbonCreditMarket.address,
        constructorArguments: [carbonCreditToken.address],
      });
      console.log("✅ CarbonCreditMarket verified");
    } catch (error) {
      console.log("⚠️ CarbonCreditMarket verification failed:", error.message);
    }

    try {
      await hre.run("verify:verify", {
        address: greenLinkRegistry.address,
        constructorArguments: [carbonCreditToken.address],
      });
      console.log("✅ GreenLinkRegistry verified");
    } catch (error) {
      console.log("⚠️ GreenLinkRegistry verification failed:", error.message);
    }
  }

  console.log("\n" + "=" * 50);
  console.log("🎉 Deployment Complete!");
  console.log("=" * 50);
  console.log("📋 Contract Addresses:");
  console.log("   CarbonCreditToken:", carbonCreditToken.address);
  console.log("   CarbonCreditMarket:", carbonCreditMarket.address);
  console.log("   GreenLinkRegistry:", greenLinkRegistry.address);
  console.log("\n🌐 Network:", hre.network.name);
  console.log("🔗 Explorer:", getExplorerUrl(hre.network.name, carbonCreditToken.address));
  
  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    deployer: deployer.address,
    contracts: {
      CarbonCreditToken: carbonCreditToken.address,
      CarbonCreditMarket: carbonCreditMarket.address,
      GreenLinkRegistry: greenLinkRegistry.address,
    },
    timestamp: new Date().toISOString(),
  };

  const fs = require("fs");
  fs.writeFileSync(
    `deployment-${hre.network.name}.json`,
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\n💾 Deployment info saved to:", `deployment-${hre.network.name}.json`);

  return {
    carbonCreditToken: carbonCreditToken.address,
    carbonCreditMarket: carbonCreditMarket.address,
    greenLinkRegistry: greenLinkRegistry.address,
  };
}

function getExplorerUrl(network, address) {
  switch (network) {
    case "mumbai":
      return `https://mumbai.polygonscan.com/address/${address}`;
    case "polygon":
      return `https://polygonscan.com/address/${address}`;
    default:
      return `Local network: ${address}`;
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  }); 