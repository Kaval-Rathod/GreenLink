// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title CarbonCreditToken
 * @dev ERC-1155 token for carbon credits with metadata support
 */
contract CarbonCreditToken is ERC1155, AccessControl, Pausable {
    using Strings for uint256;

    // Token metadata structure
    struct TokenMetadata {
        string name;
        string description;
        uint256 carbonValue; // in grams of CO2
        uint256 greeneryPercentage;
        string imageUri;
        uint256 timestamp;
        string location; // GPS coordinates
    }

    // Mapping from token ID to metadata
    mapping(uint256 => TokenMetadata) public tokenMetadata;
    
    // Counter for token IDs
    uint256 private _tokenIdCounter;
    
    // Base URI for token metadata
    string private _baseUri;
    
    // Role definitions
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    
    // Events
    event TokenMinted(
        uint256 indexed tokenId,
        address indexed owner,
        uint256 carbonValue,
        uint256 greeneryPercentage,
        string location
    );
    
    event MetadataUpdated(uint256 indexed tokenId, string newUri);

    constructor(string memory baseUri) ERC1155("") AccessControl() Pausable() {
        _baseUri = baseUri;
        _tokenIdCounter = 1;
        
        // Grant roles to deployer
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
    }

    /**
     * @dev Internal function to mint carbon credit tokens
     */
    function _mintCarbonCredit(
        address to,
        uint256 carbonValue,
        uint256 greeneryPercentage,
        string memory location,
        string memory imageUri
    ) internal returns (uint256) {
        require(carbonValue > 0, "Carbon value must be greater than 0");
        require(greeneryPercentage <= 100, "Greenery percentage must be <= 100");
        
        uint256 tokenId = _tokenIdCounter++;
        
        // Create metadata
        tokenMetadata[tokenId] = TokenMetadata({
            name: string(abi.encodePacked("Carbon Credit #", tokenId.toString())),
            description: string(abi.encodePacked(
                "Carbon credit token representing ", 
                carbonValue.toString(), 
                " grams of CO2 equivalent from greenery analysis"
            )),
            carbonValue: carbonValue,
            greeneryPercentage: greeneryPercentage,
            imageUri: imageUri,
            timestamp: block.timestamp,
            location: location
        });
        
        // Mint 1 token (carbon credits are unique)
        _mint(to, tokenId, 1, "");
        
        emit TokenMinted(tokenId, to, carbonValue, greeneryPercentage, location);
        
        return tokenId;
    }

    /**
     * @dev Mint new carbon credit tokens
     * @param to Address to mint tokens to
     * @param carbonValue Carbon value in grams of CO2
     * @param greeneryPercentage Greenery percentage from AI analysis
     * @param location GPS coordinates
     * @param imageUri URI to the image
     */
    function mintCarbonCredit(
        address to,
        uint256 carbonValue,
        uint256 greeneryPercentage,
        string memory location,
        string memory imageUri
    ) external onlyRole(MINTER_ROLE) returns (uint256) {
        return _mintCarbonCredit(to, carbonValue, greeneryPercentage, location, imageUri);
    }

    /**
     * @dev Batch mint multiple carbon credits
     */
    function batchMintCarbonCredits(
        address[] memory recipients,
        uint256[] memory carbonValues,
        uint256[] memory greeneryPercentages,
        string[] memory locations,
        string[] memory imageUris
    ) external onlyRole(MINTER_ROLE) returns (uint256[] memory) {
        require(
            recipients.length == carbonValues.length &&
            carbonValues.length == greeneryPercentages.length &&
            greeneryPercentages.length == locations.length &&
            locations.length == imageUris.length,
            "Arrays must have same length"
        );
        
        uint256[] memory tokenIds = new uint256[](recipients.length);
        
        for (uint256 i = 0; i < recipients.length; i++) {
            tokenIds[i] = _mintCarbonCredit(
                recipients[i],
                carbonValues[i],
                greeneryPercentages[i],
                locations[i],
                imageUris[i]
            );
        }
        
        return tokenIds;
    }

    /**
     * @dev Get token metadata
     */
    function getTokenMetadata(uint256 tokenId) 
        external 
        view 
        returns (TokenMetadata memory) 
    {
        require(tokenMetadata[tokenId].timestamp != 0, "Token does not exist");
        return tokenMetadata[tokenId];
    }

    /**
     * @dev Get total carbon credits minted
     */
    function getTotalCarbonCredits() external view returns (uint256) {
        return _tokenIdCounter - 1;
    }

    /**
     * @dev Get carbon credits owned by an address
     */
    function getCarbonCreditsByOwner(address owner) 
        external 
        view 
        returns (uint256[] memory) 
    {
        uint256 totalTokens = _tokenIdCounter - 1;
        uint256[] memory temp = new uint256[](totalTokens);
        uint256 count = 0;
        
        for (uint256 i = 1; i <= totalTokens; i++) {
            if (balanceOf(owner, i) > 0) {
                temp[count] = i;
                count++;
            }
        }
        
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = temp[i];
        }
        
        return result;
    }

    /**
     * @dev Update base URI
     */
    function setBaseUri(string memory newBaseUri) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _baseUri = newBaseUri;
    }

    /**
     * @dev Get base URI
     */
    function getBaseUri() external view returns (string memory) {
        return _baseUri;
    }

    /**
     * @dev Override uri function for metadata
     */
    function uri(uint256 tokenId) public view override returns (string memory) {
        return string(abi.encodePacked(_baseUri, tokenId.toString()));
    }

    /**
     * @dev Pause/unpause contract (emergency function)
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Override _update to add pausing
     */
    function _update(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts
    ) internal virtual override {
        super._update(from, to, ids, amounts);
        require(!paused(), "Token transfer while paused");
    }

    /**
     * @dev Override supportsInterface to resolve conflicts
     */
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC1155, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
} 