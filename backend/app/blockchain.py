"""
Blockchain integration service for GreenLink
Handles smart contract interactions and token minting
"""

import os
import json
from typing import Optional, Dict, Any
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound
import logging

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for interacting with GreenLink smart contracts"""
    
    def __init__(self):
        # Initialize Web3 connection
        self.w3 = None
        self.contracts = {}
        self.owner_account = None
        self.initialize_web3()
    
    def initialize_web3(self):
        """Initialize Web3 connection and load contracts"""
        try:
            # Get RPC URL from environment (default to local Hardhat)
            rpc_url = os.getenv("POLYGON_RPC_URL", "http://localhost:8545")
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not self.w3.is_connected():
                logger.warning("Failed to connect to blockchain network")
                return
            
            # Get private key from environment
            private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
            if not private_key:
                logger.warning("No blockchain private key found")
                return
            
            # Create account from private key
            self.owner_account = self.w3.eth.account.from_key(private_key)
            
            # Load contract addresses from deployment file
            self.load_contracts()
            
            logger.info("Blockchain service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain service: {e}")
    
    def load_contracts(self):
        """Load deployed contract addresses and ABIs"""
        try:
            # Try to load deployment info
            deployment_file = "blockchain/deployment-hardhat.json"
            if os.path.exists(deployment_file):
                with open(deployment_file, 'r') as f:
                    deployment = json.load(f)
                
                # Load contract ABIs
                self.load_contract_abi("CarbonCreditToken", deployment["contracts"]["CarbonCreditToken"])
                self.load_contract_abi("CarbonCreditMarket", deployment["contracts"]["CarbonCreditMarket"])
                self.load_contract_abi("GreenLinkRegistry", deployment["contracts"]["GreenLinkRegistry"])
                
                logger.info("Contracts loaded successfully")
            else:
                logger.warning("Deployment file not found, using default addresses")
                # Use default addresses for development
                self.load_contract_abi("CarbonCreditToken", "0x5FbDB2315678afecb367f032d93F642f64180aa3")
                self.load_contract_abi("CarbonCreditMarket", "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512")
                self.load_contract_abi("GreenLinkRegistry", "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0")
                
        except Exception as e:
            logger.error(f"Failed to load contracts: {e}")
    
    def load_contract_abi(self, contract_name: str, address: str):
        """Load contract ABI and create contract instance"""
        try:
            # Load ABI from compiled contract
            abi_file = f"blockchain/artifacts/contracts/{contract_name}.sol/{contract_name}.json"
            if os.path.exists(abi_file):
                with open(abi_file, 'r') as f:
                    contract_data = json.load(f)
                    abi = contract_data["abi"]
                
                # Create contract instance
                contract = self.w3.eth.contract(address=address, abi=abi)
                self.contracts[contract_name] = contract
                logger.info(f"Loaded {contract_name} contract at {address}")
            else:
                logger.warning(f"ABI file not found for {contract_name}")
                
        except Exception as e:
            logger.error(f"Failed to load {contract_name} contract: {e}")
    
    def mint_carbon_credit(
        self, 
        to_address: str, 
        carbon_value: float, 
        greenery_percentage: float, 
        location: str, 
        image_uri: str
    ) -> Optional[str]:
        """Mint a new carbon credit token"""
        try:
            if not self.contracts.get("CarbonCreditToken"):
                logger.error("CarbonCreditToken contract not loaded")
                return None
            
            contract = self.contracts["CarbonCreditToken"]
            
            # Convert carbon value to wei (assuming carbon_value is in tonnes)
            carbon_value_wei = self.w3.to_wei(carbon_value, 'ether')
            
            # Prepare transaction
            transaction = contract.functions.mintCarbonCredit(
                to_address,
                carbon_value_wei,
                int(greenery_percentage),
                location,
                image_uri
            ).build_transaction({
                'from': self.owner_account.address,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.owner_account.address),
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.owner_account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Carbon credit minted successfully: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error(f"Transaction failed: {tx_hash.hex()}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to mint carbon credit: {e}")
            return None
    
    def register_submission(
        self,
        user_address: str,
        image_hash: str,
        greenery_percentage: float,
        carbon_value: float,
        location: str
    ) -> Optional[str]:
        """Register a submission on the blockchain"""
        try:
            if not self.contracts.get("GreenLinkRegistry"):
                logger.error("GreenLinkRegistry contract not loaded")
                return None
            
            contract = self.contracts["GreenLinkRegistry"]
            
            # Convert carbon value to wei
            carbon_value_wei = self.w3.to_wei(carbon_value, 'ether')
            
            # Prepare transaction
            transaction = contract.functions.registerSubmission(
                image_hash,
                int(greenery_percentage),
                carbon_value_wei,
                location
            ).build_transaction({
                'from': user_address,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(user_address),
            })
            
            # For now, we'll use the owner account to pay for gas
            # In production, users would sign their own transactions
            transaction['from'] = self.owner_account.address
            transaction['nonce'] = self.w3.eth.get_transaction_count(self.owner_account.address)
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.owner_account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Submission registered successfully: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error(f"Transaction failed: {tx_hash.hex()}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to register submission: {e}")
            return None
    
    def get_token_metadata(self, token_id: int) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific token"""
        try:
            if not self.contracts.get("CarbonCreditToken"):
                return None
            
            contract = self.contracts["CarbonCreditToken"]
            metadata = contract.functions.getTokenMetadata(token_id).call()
            
            return {
                "name": metadata[0],
                "description": metadata[1],
                "carbon_value": self.w3.from_wei(metadata[2], 'ether'),
                "greenery_percentage": metadata[3],
                "image_uri": metadata[4],
                "timestamp": metadata[5],
                "location": metadata[6]
            }
            
        except Exception as e:
            logger.error(f"Failed to get token metadata: {e}")
            return None
    
    def get_user_tokens(self, user_address: str) -> list:
        """Get all tokens owned by a user"""
        try:
            if not self.contracts.get("CarbonCreditToken"):
                return []
            
            contract = self.contracts["CarbonCreditToken"]
            token_ids = contract.functions.getCarbonCreditsByOwner(user_address).call()
            
            tokens = []
            for token_id in token_ids:
                metadata = self.get_token_metadata(token_id)
                if metadata:
                    tokens.append({
                        "token_id": token_id,
                        **metadata
                    })
            
            return tokens
            
        except Exception as e:
            logger.error(f"Failed to get user tokens: {e}")
            return []
    
    def get_marketplace_listings(self) -> list:
        """Get all active marketplace listings"""
        try:
            if not self.contracts.get("CarbonCreditMarket"):
                return []
            
            contract = self.contracts["CarbonCreditMarket"]
            listings = contract.functions.getActiveListings().call()
            
            return [
                {
                    "listing_id": listing[0],
                    "token_id": listing[1],
                    "seller": listing[2],
                    "price": self.w3.from_wei(listing[3], 'ether'),
                    "is_active": listing[4],
                    "created_at": listing[5]
                }
                for listing in listings
            ]
            
        except Exception as e:
            logger.error(f"Failed to get marketplace listings: {e}")
            return []
    
    def is_connected(self) -> bool:
        """Check if blockchain connection is active"""
        return self.w3 is not None and self.w3.is_connected()
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get blockchain network information"""
        if not self.is_connected():
            return {"connected": False}
        
        try:
            return {
                "connected": True,
                "network_id": self.w3.eth.chain_id,
                "latest_block": self.w3.eth.block_number,
                "gas_price": self.w3.from_wei(self.w3.eth.gas_price, 'gwei'),
                "owner_address": self.owner_account.address if self.owner_account else None
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {"connected": False, "error": str(e)}

# Global blockchain service instance
blockchain_service = BlockchainService() 