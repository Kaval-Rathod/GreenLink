const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("GreenLink Smart Contracts", function () {
  let carbonCreditToken;
  let carbonCreditMarket;
  let greenLinkRegistry;
  let owner;
  let user1;
  let user2;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    // Deploy contracts
    const CarbonCreditToken = await ethers.getContractFactory("CarbonCreditToken");
    carbonCreditToken = await CarbonCreditToken.deploy("https://api.greenlink.com/metadata/");
    await carbonCreditToken.waitForDeployment();

    const CarbonCreditMarket = await ethers.getContractFactory("CarbonCreditMarket");
    carbonCreditMarket = await CarbonCreditMarket.deploy(await carbonCreditToken.getAddress());
    await carbonCreditMarket.waitForDeployment();

    const GreenLinkRegistry = await ethers.getContractFactory("GreenLinkRegistry");
    greenLinkRegistry = await GreenLinkRegistry.deploy(await carbonCreditToken.getAddress());
    await greenLinkRegistry.waitForDeployment();

    // Grant minter role to registry
    await carbonCreditToken.grantRole(await carbonCreditToken.MINTER_ROLE(), await greenLinkRegistry.getAddress());
  });

  describe("CarbonCreditToken", function () {
    it("Should mint carbon credit tokens", async function () {
      const carbonValue = ethers.parseEther("0.5"); // 0.5 tonnes CO2
      const greeneryPercentage = 75;
      const location = "40.7128,-74.0060";
      const imageUri = "ipfs://QmTestHash";

      await carbonCreditToken.mintCarbonCredit(
        user1.address,
        carbonValue,
        greeneryPercentage,
        location,
        imageUri
      );

      expect(await carbonCreditToken.balanceOf(user1.address, 1)).to.equal(1);
      
      const metadata = await carbonCreditToken.getTokenMetadata(1);
      expect(metadata.carbonValue).to.equal(carbonValue);
      expect(metadata.greeneryPercentage).to.equal(greeneryPercentage);
      expect(metadata.location).to.equal(location);
    });

    it("Should get carbon credits by owner", async function () {
      // Mint multiple tokens
      await carbonCreditToken.mintCarbonCredit(
        user1.address,
        ethers.parseEther("0.5"),
        75,
        "40.7128,-74.0060",
        "ipfs://QmTest1"
      );

      await carbonCreditToken.mintCarbonCredit(
        user1.address,
        ethers.parseEther("0.3"),
        60,
        "40.7129,-74.0061",
        "ipfs://QmTest2"
      );

      const userTokens = await carbonCreditToken.getCarbonCreditsByOwner(user1.address);
      expect(userTokens.length).to.equal(2);
      expect(userTokens[0]).to.equal(1);
      expect(userTokens[1]).to.equal(2);
    });

    it("Should get total carbon credits", async function () {
      expect(await carbonCreditToken.getTotalCarbonCredits()).to.equal(0);

      await carbonCreditToken.mintCarbonCredit(
        user1.address,
        ethers.parseEther("0.5"),
        75,
        "40.7128,-74.0060",
        "ipfs://QmTest"
      );

      expect(await carbonCreditToken.getTotalCarbonCredits()).to.equal(1);
    });
  });

  describe("CarbonCreditMarket", function () {
    beforeEach(async function () {
      // Mint a token for testing
      await carbonCreditToken.mintCarbonCredit(
        user1.address,
        ethers.parseEther("0.5"),
        75,
        "40.7128,-74.0060",
        "ipfs://QmTest"
      );
    });

    it("Should create a listing", async function () {
      const price = ethers.parseEther("0.1"); // 0.1 ETH

      await carbonCreditToken.connect(user1).setApprovalForAll(await carbonCreditMarket.getAddress(), true);
      await carbonCreditMarket.connect(user1).createListing(1, price);

      const listing = await carbonCreditMarket.getListing(1);
      expect(listing.tokenId).to.equal(1);
      expect(listing.seller).to.equal(user1.address);
      expect(listing.price).to.equal(price);
      expect(listing.isActive).to.be.true;
    });

    it("Should buy a listed token", async function () {
      const price = ethers.parseEther("0.1");

      // Create listing
      await carbonCreditToken.connect(user1).setApprovalForAll(await carbonCreditMarket.getAddress(), true);
      await carbonCreditMarket.connect(user1).createListing(1, price);

      // Buy token
      await carbonCreditMarket.connect(user2).buyToken(1, { value: price });

      // Check ownership
      expect(await carbonCreditToken.balanceOf(user2.address, 1)).to.equal(1);
      expect(await carbonCreditToken.balanceOf(user1.address, 1)).to.equal(0);

      // Check listing is inactive
      const listing = await carbonCreditMarket.getListing(1);
      expect(listing.isActive).to.be.false;
    });

    it("Should update listing price", async function () {
      const initialPrice = ethers.parseEther("0.1");
      const newPrice = ethers.parseEther("0.15");

      await carbonCreditToken.connect(user1).setApprovalForAll(await carbonCreditMarket.getAddress(), true);
      await carbonCreditMarket.connect(user1).createListing(1, initialPrice);
      await carbonCreditMarket.connect(user1).updateListing(1, newPrice);

      const listing = await carbonCreditMarket.getListing(1);
      expect(listing.price).to.equal(newPrice);
    });

    it("Should cancel a listing", async function () {
      const price = ethers.parseEther("0.1");

      await carbonCreditToken.connect(user1).setApprovalForAll(await carbonCreditMarket.getAddress(), true);
      await carbonCreditMarket.connect(user1).createListing(1, price);
      await carbonCreditMarket.connect(user1).cancelListing(1);

      // Token should be returned to seller
      expect(await carbonCreditToken.balanceOf(user1.address, 1)).to.equal(1);

      // Listing should be inactive
      const listing = await carbonCreditMarket.getListing(1);
      expect(listing.isActive).to.be.false;
    });

    it("Should get marketplace statistics", async function () {
      const price = ethers.parseEther("0.1");

      // Create and sell a listing
      await carbonCreditToken.connect(user1).setApprovalForAll(await carbonCreditMarket.getAddress(), true);
      await carbonCreditMarket.connect(user1).createListing(1, price);
      await carbonCreditMarket.connect(user2).buyToken(1, { value: price });

      const stats = await carbonCreditMarket.getMarketplaceStats();
      expect(stats.totalListings).to.equal(1);
      expect(stats.activeListings).to.equal(0);
      expect(stats.totalVolume).to.equal(price);
    });
  });

  describe("GreenLinkRegistry", function () {
    it("Should register a submission", async function () {
      const imageHash = "ipfs://QmTestHash";
      const greeneryPercentage = 75;
      const carbonValue = ethers.parseEther("0.5");
      const location = "40.7128,-74.0060";

      await greenLinkRegistry.connect(user1).registerSubmission(
        imageHash,
        greeneryPercentage,
        carbonValue,
        location
      );

      const submission = await greenLinkRegistry.getSubmission(1);
      expect(submission.user).to.equal(user1.address);
      expect(submission.imageHash).to.equal(imageHash);
      expect(submission.greeneryPercentage).to.equal(greeneryPercentage);
      expect(submission.carbonValue).to.equal(carbonValue);
      expect(submission.location).to.equal(location);
      expect(submission.isVerified).to.be.true; // 75% > 20% threshold
    });

    it("Should tokenize a verified submission", async function () {
      const imageHash = "ipfs://QmTestHash";
      const greeneryPercentage = 75;
      const carbonValue = ethers.parseEther("0.5");
      const location = "40.7128,-74.0060";

      await greenLinkRegistry.connect(user1).registerSubmission(
        imageHash,
        greeneryPercentage,
        carbonValue,
        location
      );

      await greenLinkRegistry.connect(user1).tokenizeSubmission(1);

      const submission = await greenLinkRegistry.getSubmission(1);
      expect(submission.isTokenized).to.be.true;
      expect(submission.tokenId).to.be.gt(0);

      // Check token was minted
      expect(await carbonCreditToken.balanceOf(user1.address, submission.tokenId)).to.equal(1);
    });

    it("Should not tokenize unverified submission", async function () {
      const imageHash = "ipfs://QmTestHash";
      const greeneryPercentage = 15; // Below 20% threshold
      const carbonValue = ethers.parseEther("0.5");
      const location = "40.7128,-74.0060";

      await greenLinkRegistry.connect(user1).registerSubmission(
        imageHash,
        greeneryPercentage,
        carbonValue,
        location
      );

      await expect(
        greenLinkRegistry.connect(user1).tokenizeSubmission(1)
      ).to.be.revertedWith("Submission must be verified");
    });

    it("Should get user submissions", async function () {
      const imageHash1 = "ipfs://QmTestHash1";
      const imageHash2 = "ipfs://QmTestHash2";

      await greenLinkRegistry.connect(user1).registerSubmission(
        imageHash1,
        75,
        ethers.parseEther("0.5"),
        "40.7128,-74.0060"
      );

      await greenLinkRegistry.connect(user1).registerSubmission(
        imageHash2,
        80,
        ethers.parseEther("0.6"),
        "40.7129,-74.0061"
      );

      const userSubmissions = await greenLinkRegistry.getUserSubmissions(user1.address);
      expect(userSubmissions.length).to.equal(2);
      expect(userSubmissions[0]).to.equal(1);
      expect(userSubmissions[1]).to.equal(2);
    });

    it("Should get registry statistics", async function () {
      // Register multiple submissions
      await greenLinkRegistry.connect(user1).registerSubmission(
        "ipfs://QmTest1",
        75,
        ethers.parseEther("0.5"),
        "40.7128,-74.0060"
      );

      await greenLinkRegistry.connect(user2).registerSubmission(
        "ipfs://QmTest2",
        15, // Below threshold
        ethers.parseEther("0.3"),
        "40.7129,-74.0061"
      );

      await greenLinkRegistry.connect(user1).registerSubmission(
        "ipfs://QmTest3",
        85,
        ethers.parseEther("0.7"),
        "40.7130,-74.0062"
      );

      // Tokenize one submission
      await greenLinkRegistry.connect(user1).tokenizeSubmission(3);

      const stats = await greenLinkRegistry.getRegistryStats();
      expect(stats.totalSubmissions).to.equal(3);
      expect(stats.verifiedSubmissions).to.equal(2); // 75% and 85%
      expect(stats.tokenizedSubmissions).to.equal(1);
      expect(stats.totalCarbonValue).to.equal(ethers.parseEther("1.5"));
    });
  });

  describe("Integration Tests", function () {
    it("Should complete full workflow: register -> tokenize -> list -> buy", async function () {
      // 1. Register submission
      await greenLinkRegistry.connect(user1).registerSubmission(
        "ipfs://QmTestHash",
        75,
        ethers.parseEther("0.5"),
        "40.7128,-74.0060"
      );

      // 2. Tokenize submission
      await greenLinkRegistry.connect(user1).tokenizeSubmission(1);
      const submission = await greenLinkRegistry.getSubmission(1);
      const tokenId = submission.tokenId;

      // 3. Create listing
      const price = ethers.parseEther("0.1");
      await carbonCreditToken.connect(user1).setApprovalForAll(await carbonCreditMarket.getAddress(), true);
      await carbonCreditMarket.connect(user1).createListing(tokenId, price);

      // 4. Buy token
      await carbonCreditMarket.connect(user2).buyToken(1, { value: price });

      // Verify final state
      expect(await carbonCreditToken.balanceOf(user2.address, tokenId)).to.equal(1);
      expect(await carbonCreditToken.balanceOf(user1.address, tokenId)).to.equal(0);
      
      const listing = await carbonCreditMarket.getListing(1);
      expect(listing.isActive).to.be.false;
    });
  });
}); 