// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./CarbonCreditToken.sol";

/**
 * @title GreenLinkRegistry
 * @dev Registry for tracking submissions and their blockchain representations
 */
contract GreenLinkRegistry is Ownable {

    CarbonCreditToken public carbonCreditToken;
    
    // Submission structure
    struct Submission {
        uint256 submissionId;
        address user;
        string imageHash; // IPFS hash or similar
        uint256 greeneryPercentage;
        uint256 carbonValue; // in grams of CO2
        string location; // GPS coordinates
        uint256 timestamp;
        uint256 tokenId; // Associated carbon credit token
        bool isVerified;
        bool isTokenized;
    }
    
    // Mapping from submission ID to submission
    mapping(uint256 => Submission) public submissions;
    
    // Mapping from user address to their submissions
    mapping(address => uint256[]) public userSubmissions;
    
    // Mapping from image hash to submission ID (prevent duplicates)
    mapping(string => uint256) public imageHashToSubmission;
    
    // Counter for submission IDs
    uint256 private _submissionIdCounter;
    
    // Verification threshold (minimum greenery percentage for tokenization)
    uint256 public verificationThreshold = 20; // 20%
    
    // Events
    event SubmissionRegistered(
        uint256 indexed submissionId,
        address indexed user,
        string imageHash,
        uint256 greeneryPercentage,
        uint256 carbonValue,
        string location
    );
    
    event SubmissionVerified(uint256 indexed submissionId, bool verified);
    
    event SubmissionTokenized(
        uint256 indexed submissionId,
        uint256 indexed tokenId,
        address indexed user
    );
    
    event VerificationThresholdUpdated(uint256 newThreshold);

    constructor(address _carbonCreditToken) Ownable(msg.sender) {
        carbonCreditToken = CarbonCreditToken(_carbonCreditToken);
    }

    /**
     * @dev Register a new submission
     * @param imageHash IPFS hash or similar identifier
     * @param greeneryPercentage Greenery percentage from AI analysis
     * @param carbonValue Carbon value in grams of CO2
     * @param location GPS coordinates
     */
    function registerSubmission(
        string memory imageHash,
        uint256 greeneryPercentage,
        uint256 carbonValue,
        string memory location
    ) external returns (uint256) {
        require(bytes(imageHash).length > 0, "Image hash cannot be empty");
        require(greeneryPercentage <= 100, "Greenery percentage must be <= 100");
        require(carbonValue > 0, "Carbon value must be greater than 0");
        require(
            imageHashToSubmission[imageHash] == 0,
            "Image already registered"
        );
        
        _submissionIdCounter++;
        uint256 submissionId = _submissionIdCounter;
        
        submissions[submissionId] = Submission({
            submissionId: submissionId,
            user: msg.sender,
            imageHash: imageHash,
            greeneryPercentage: greeneryPercentage,
            carbonValue: carbonValue,
            location: location,
            timestamp: block.timestamp,
            tokenId: 0,
            isVerified: greeneryPercentage >= verificationThreshold,
            isTokenized: false
        });
        
        userSubmissions[msg.sender].push(submissionId);
        imageHashToSubmission[imageHash] = submissionId;
        
        emit SubmissionRegistered(
            submissionId,
            msg.sender,
            imageHash,
            greeneryPercentage,
            carbonValue,
            location
        );
        
        if (greeneryPercentage >= verificationThreshold) {
            emit SubmissionVerified(submissionId, true);
        }
        
        return submissionId;
    }

    /**
     * @dev Tokenize a verified submission
     * @param submissionId The submission ID to tokenize
     */
    function tokenizeSubmission(uint256 submissionId) external {
        Submission storage submission = submissions[submissionId];
        require(submission.user == msg.sender, "Only submission owner can tokenize");
        require(submission.isVerified, "Submission must be verified");
        require(!submission.isTokenized, "Submission already tokenized");
        
        // Mint carbon credit token
        uint256 tokenId = carbonCreditToken.mintCarbonCredit(
            msg.sender,
            submission.carbonValue,
            submission.greeneryPercentage,
            submission.location,
            submission.imageHash
        );
        
        submission.tokenId = tokenId;
        submission.isTokenized = true;
        
        emit SubmissionTokenized(submissionId, tokenId, msg.sender);
    }

    /**
     * @dev Get submission by ID
     */
    function getSubmission(uint256 submissionId) 
        external 
        view 
        returns (Submission memory) 
    {
        return submissions[submissionId];
    }

    /**
     * @dev Get all submissions by user
     */
    function getUserSubmissions(address user) 
        external 
        view 
        returns (uint256[] memory) 
    {
        return userSubmissions[user];
    }

    /**
     * @dev Get submission by image hash
     */
    function getSubmissionByImageHash(string memory imageHash) 
        external 
        view 
        returns (Submission memory) 
    {
        uint256 submissionId = imageHashToSubmission[imageHash];
        require(submissionId != 0, "Image not found");
        return submissions[submissionId];
    }

    /**
     * @dev Get all verified submissions
     */
    function getVerifiedSubmissions() external view returns (uint256[] memory) {
        uint256 totalSubmissions = _submissionIdCounter;
        uint256 verifiedCount = 0;
        
        // Count verified submissions
        for (uint256 i = 1; i <= totalSubmissions; i++) {
            if (submissions[i].isVerified) {
                verifiedCount++;
            }
        }
        
        // Create array of verified submissions
        uint256[] memory verifiedSubmissions = new uint256[](verifiedCount);
        uint256 index = 0;
        
        for (uint256 i = 1; i <= totalSubmissions; i++) {
            if (submissions[i].isVerified) {
                verifiedSubmissions[index] = i;
                index++;
            }
        }
        
        return verifiedSubmissions;
    }

    /**
     * @dev Get all tokenized submissions
     */
    function getTokenizedSubmissions() external view returns (uint256[] memory) {
        uint256 totalSubmissions = _submissionIdCounter;
        uint256 tokenizedCount = 0;
        
        // Count tokenized submissions
        for (uint256 i = 1; i <= totalSubmissions; i++) {
            if (submissions[i].isTokenized) {
                tokenizedCount++;
            }
        }
        
        // Create array of tokenized submissions
        uint256[] memory tokenizedSubmissions = new uint256[](tokenizedCount);
        uint256 index = 0;
        
        for (uint256 i = 1; i <= totalSubmissions; i++) {
            if (submissions[i].isTokenized) {
                tokenizedSubmissions[index] = i;
                index++;
            }
        }
        
        return tokenizedSubmissions;
    }

    /**
     * @dev Get total number of submissions
     */
    function getTotalSubmissions() external view returns (uint256) {
        return _submissionIdCounter;
    }

    /**
     * @dev Update verification threshold (owner only)
     */
    function updateVerificationThreshold(uint256 newThreshold) external onlyOwner {
        require(newThreshold <= 100, "Threshold cannot exceed 100%");
        verificationThreshold = newThreshold;
        emit VerificationThresholdUpdated(newThreshold);
    }

    /**
     * @dev Get registry statistics
     */
    function getRegistryStats() external view returns (
        uint256 totalSubmissions,
        uint256 verifiedSubmissions,
        uint256 tokenizedSubmissions,
        uint256 totalCarbonValue
    ) {
        totalSubmissions = _submissionIdCounter;
        uint256 verified = 0;
        uint256 tokenized = 0;
        uint256 totalCarbon = 0;
        
        for (uint256 i = 1; i <= totalSubmissions; i++) {
            if (submissions[i].isVerified) {
                verified++;
            }
            if (submissions[i].isTokenized) {
                tokenized++;
            }
            totalCarbon += submissions[i].carbonValue;
        }
        
        return (totalSubmissions, verified, tokenized, totalCarbon);
    }

    /**
     * @dev Get submissions by date range
     */
    function getSubmissionsByDateRange(uint256 startTime, uint256 endTime) 
        external 
        view 
        returns (uint256[] memory) 
    {
        uint256 totalSubmissions = _submissionIdCounter;
        uint256 count = 0;
        
        // Count submissions in range
        for (uint256 i = 1; i <= totalSubmissions; i++) {
            if (submissions[i].timestamp >= startTime && 
                submissions[i].timestamp <= endTime) {
                count++;
            }
        }
        
        // Create array of submissions in range
        uint256[] memory submissionsInRange = new uint256[](count);
        uint256 index = 0;
        
        for (uint256 i = 1; i <= totalSubmissions; i++) {
            if (submissions[i].timestamp >= startTime && 
                submissions[i].timestamp <= endTime) {
                submissionsInRange[index] = i;
                index++;
            }
        }
        
        return submissionsInRange;
    }

    /**
     * @dev Emergency function to update submission (owner only)
     */
    function emergencyUpdateSubmission(
        uint256 submissionId,
        uint256 greeneryPercentage,
        uint256 carbonValue
    ) external onlyOwner {
        require(submissionId <= _submissionIdCounter, "Invalid submission ID");
        
        submissions[submissionId].greeneryPercentage = greeneryPercentage;
        submissions[submissionId].carbonValue = carbonValue;
        submissions[submissionId].isVerified = greeneryPercentage >= verificationThreshold;
        
        if (greeneryPercentage >= verificationThreshold) {
            emit SubmissionVerified(submissionId, true);
        }
    }
} 