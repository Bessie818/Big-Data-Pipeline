const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  const RentalIncomeToken = await hre.ethers.getContractFactory("RentalIncomeToken");
  const token = await RentalIncomeToken.deploy(deployer.address);
  await token.waitForDeployment();

  const address = await token.getAddress();
  console.log("RentalIncomeToken deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
