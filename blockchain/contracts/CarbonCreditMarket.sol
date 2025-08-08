// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155Receiver.sol";
import "./CarbonCreditToken.sol";

/**
 * @title CarbonCreditMarket
 * @dev Marketplace for trading carbon credit tokens
 */
contract CarbonCreditMarket is ReentrancyGuard, Ownable, IERC1155Receiver {

    CarbonCreditToken public carbonCreditToken;
    
    // Listing structure
    struct Listing {
        uint256 listingId;
        uint256 tokenId;
        address seller;
        uint256 price;
        bool isActive;
        uint256 createdAt;
    }
    
    // Mapping from listing ID to listing
    mapping(uint256 => Listing) public listings;
    
    // Mapping from token ID to listing ID
    mapping(uint256 => uint256) public tokenToListing;
    
    // Counter for listing IDs
    uint256 private _listingIdCounter;
    
    // Platform fee (2.5% = 250 basis points)
    uint256 public platformFee = 250; // 2.5%
    uint256 public constant BASIS_POINTS = 10000;
    
    // Events
    event ListingCreated(
        uint256 indexed listingId,
        uint256 indexed tokenId,
        address indexed seller,
        uint256 price
    );
    
    event ListingUpdated(
        uint256 indexed listingId,
        uint256 newPrice
    );
    
    event ListingCancelled(uint256 indexed listingId);
    
    event TokenSold(
        uint256 indexed listingId,
        uint256 indexed tokenId,
        address indexed seller,
        address buyer,
        uint256 price
    );
    
    event PlatformFeeUpdated(uint256 newFee);

    constructor(address _carbonCreditToken) Ownable(msg.sender) ReentrancyGuard() {
        carbonCreditToken = CarbonCreditToken(_carbonCreditToken);
    }

    /**
     * @dev Create a new listing
     * @param tokenId The token ID to list
     * @param price Price in wei
     */
    function createListing(uint256 tokenId, uint256 price) external {
        require(price > 0, "Price must be greater than 0");
        require(
            carbonCreditToken.balanceOf(msg.sender, tokenId) > 0,
            "You don't own this token"
        );
        require(
            tokenToListing[tokenId] == 0,
            "Token already listed"
        );
        
        // Transfer token to marketplace (escrow)
        carbonCreditToken.safeTransferFrom(
            msg.sender,
            address(this),
            tokenId,
            1,
            ""
        );
        
        _listingIdCounter++;
        uint256 listingId = _listingIdCounter;
        
        listings[listingId] = Listing({
            listingId: listingId,
            tokenId: tokenId,
            seller: msg.sender,
            price: price,
            isActive: true,
            createdAt: block.timestamp
        });
        
        tokenToListing[tokenId] = listingId;
        
        emit ListingCreated(listingId, tokenId, msg.sender, price);
    }

    /**
     * @dev Buy a listed token
     * @param listingId The listing ID to buy
     */
    function buyToken(uint256 listingId) external payable nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.isActive, "Listing is not active");
        require(msg.value == listing.price, "Incorrect price");
        require(msg.sender != listing.seller, "Cannot buy your own token");
        
        // Calculate platform fee
        uint256 platformFeeAmount = (listing.price * platformFee) / BASIS_POINTS;
        uint256 sellerAmount = listing.price - platformFeeAmount;
        
        // Transfer token to buyer
        carbonCreditToken.safeTransferFrom(
            address(this),
            msg.sender,
            listing.tokenId,
            1,
            ""
        );
        
        // Transfer funds to seller
        payable(listing.seller).transfer(sellerAmount);
        
        // Transfer platform fee to owner
        payable(owner()).transfer(platformFeeAmount);
        
        // Update listing
        listing.isActive = false;
        tokenToListing[listing.tokenId] = 0;
        
        emit TokenSold(
            listingId,
            listing.tokenId,
            listing.seller,
            msg.sender,
            listing.price
        );
    }

    /**
     * @dev Update listing price
     * @param listingId The listing ID to update
     * @param newPrice New price in wei
     */
    function updateListing(uint256 listingId, uint256 newPrice) external {
        Listing storage listing = listings[listingId];
        require(listing.isActive, "Listing is not active");
        require(msg.sender == listing.seller, "Only seller can update");
        require(newPrice > 0, "Price must be greater than 0");
        
        listing.price = newPrice;
        
        emit ListingUpdated(listingId, newPrice);
    }

    /**
     * @dev Cancel a listing
     * @param listingId The listing ID to cancel
     */
    function cancelListing(uint256 listingId) external {
        Listing storage listing = listings[listingId];
        require(listing.isActive, "Listing is not active");
        require(msg.sender == listing.seller, "Only seller can cancel");
        
        // Return token to seller
        carbonCreditToken.safeTransferFrom(
            address(this),
            listing.seller,
            listing.tokenId,
            1,
            ""
        );
        
        // Update listing
        listing.isActive = false;
        tokenToListing[listing.tokenId] = 0;
        
        emit ListingCancelled(listingId);
    }

    /**
     * @dev Get all active listings
     */
    function getActiveListings() external view returns (Listing[] memory) {
        uint256 totalListings = _listingIdCounter;
        uint256 activeCount = 0;
        
        // Count active listings
        for (uint256 i = 1; i <= totalListings; i++) {
            if (listings[i].isActive) {
                activeCount++;
            }
        }
        
        // Create array of active listings
        Listing[] memory activeListings = new Listing[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 1; i <= totalListings; i++) {
            if (listings[i].isActive) {
                activeListings[index] = listings[i];
                index++;
            }
        }
        
        return activeListings;
    }

    /**
     * @dev Get listing by ID
     */
    function getListing(uint256 listingId) external view returns (Listing memory) {
        return listings[listingId];
    }

    /**
     * @dev Get listing by token ID
     */
    function getListingByToken(uint256 tokenId) external view returns (Listing memory) {
        uint256 listingId = tokenToListing[tokenId];
        require(listingId != 0, "Token not listed");
        return listings[listingId];
    }

    /**
     * @dev Get total number of listings
     */
    function getTotalListings() external view returns (uint256) {
        return _listingIdCounter;
    }

    /**
     * @dev Update platform fee (owner only)
     */
    function updatePlatformFee(uint256 newFee) external onlyOwner {
        require(newFee <= 1000, "Fee cannot exceed 10%");
        platformFee = newFee;
        emit PlatformFeeUpdated(newFee);
    }

    /**
     * @dev Withdraw platform fees (owner only)
     */
    function withdrawFees() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No fees to withdraw");
        payable(owner()).transfer(balance);
    }

    /**
     * @dev Emergency function to return tokens to sellers
     */
    function emergencyReturnToken(uint256 listingId) external onlyOwner {
        Listing storage listing = listings[listingId];
        require(listing.isActive, "Listing is not active");
        
        // Return token to seller
        carbonCreditToken.safeTransferFrom(
            address(this),
            listing.seller,
            listing.tokenId,
            1,
            ""
        );
        
        // Update listing
        listing.isActive = false;
        tokenToListing[listing.tokenId] = 0;
        
        emit ListingCancelled(listingId);
    }

    /**
     * @dev Get marketplace statistics
     */
    function getMarketplaceStats() external view returns (
        uint256 totalListings,
        uint256 activeListings,
        uint256 totalVolume,
        uint256 platformFees
    ) {
        totalListings = _listingIdCounter;
        uint256 volume = 0;
        uint256 fees = 0;
        
        for (uint256 i = 1; i <= totalListings; i++) {
            if (!listings[i].isActive) {
                volume += listings[i].price;
                fees += (listings[i].price * platformFee) / BASIS_POINTS;
            }
        }
        
        activeListings = 0;
        for (uint256 i = 1; i <= totalListings; i++) {
            if (listings[i].isActive) {
                activeListings++;
            }
        }
        
        return (totalListings, activeListings, volume, fees);
    }

    /**
     * @dev Required implementation for IERC1155Receiver
     */
    function onERC1155Received(
        address operator,
        address from,
        uint256 id,
        uint256 value,
        bytes calldata data
    ) external override returns (bytes4) {
        return this.onERC1155Received.selector;
    }

    /**
     * @dev Required implementation for IERC1155Receiver
     */
    function onERC1155BatchReceived(
        address operator,
        address from,
        uint256[] calldata ids,
        uint256[] calldata values,
        bytes calldata data
    ) external override returns (bytes4) {
        return this.onERC1155BatchReceived.selector;
    }

    /**
     * @dev Required implementation for IERC165
     */
    function supportsInterface(bytes4 interfaceId) external pure override returns (bool) {
        return interfaceId == type(IERC1155Receiver).interfaceId;
    }
} 