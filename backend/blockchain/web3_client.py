"""
Web3.py client for AuditLog smart contract interaction.
Gracefully handles missing web3 installation — backend starts normally,
blockchain calls return a 'not available' result instead of crashing.
"""

import os
import json
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Try importing web3 ────────────────────────────────────────────────────────
try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    WEB3_AVAILABLE = True
    logger.info("web3 imported successfully")
except ImportError:
    WEB3_AVAILABLE = False
    Web3 = None
    logger.warning("web3 not installed — blockchain features disabled. Run: pip install setuptools web3")

# ── Config ────────────────────────────────────────────────────────────────────
HARDHAT_RPC     = os.getenv("HARDHAT_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDR   = os.getenv("CONTRACT_ADDRESS", "")
PRIVATE_KEY     = os.getenv("DEPLOYER_PRIVATE_KEY", "")

# Load ABI from deployment.json or artifacts
_w3   = None
_contract = None


def _load_abi() -> list:
    """Try to load ABI from deployment.json or hardhat artifacts."""
    candidates = [
        Path(__file__).parent.parent / "deployment.json",
        Path(__file__).parent.parent.parent / "artifacts" / "contracts" / "AuditLog.sol" / "AuditLog.json",
    ]
    for p in candidates:
        if p.exists():
            data = json.loads(p.read_text())
            return data.get("abi", data.get("abi", []))
    return []


def _get_web3():
    global _w3, _contract
    if not WEB3_AVAILABLE:
        return None, None
    if _w3 is not None:
        return _w3, _contract
    try:
        w3 = Web3(Web3.HTTPProvider(HARDHAT_RPC, request_kwargs={"timeout": 10}))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if not w3.is_connected():
            logger.warning("Hardhat RPC not reachable at %s", HARDHAT_RPC)
            return None, None
        abi = _load_abi()
        if not abi or not CONTRACT_ADDR:
            logger.warning("ABI or CONTRACT_ADDRESS missing — blockchain features disabled")
            return w3, None
        contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDR), abi=abi)
        _w3, _contract = w3, contract
        logger.info("Connected to blockchain at %s, contract %s", HARDHAT_RPC, CONTRACT_ADDR)
        return w3, contract
    except Exception as e:
        logger.warning("Blockchain connection failed: %s", e)
        return None, None


def is_blockchain_available() -> bool:
    w3, contract = _get_web3()
    return w3 is not None and contract is not None


def compute_log_hash(log_data: dict) -> str:
    """Compute a deterministic SHA-256 hash of the log fields."""
    fields = "|".join(str(log_data.get(k, "")) for k in sorted(log_data.keys()))
    return "0x" + hashlib.sha256(fields.encode()).hexdigest()


def store_log_on_chain(log_data: dict) -> dict:
    """Store a log hash on the blockchain. Returns tx info or a fallback dict."""
    w3, contract = _get_web3()
    if not contract:
        return {
            "success": False,
            "tx_hash": None,
            "block_number": None,
            "log_hash": compute_log_hash(log_data),
            "message": "Blockchain not available — install web3 and setuptools",
        }
    try:
        log_hash_hex  = compute_log_hash(log_data)
        log_hash_bytes = bytes.fromhex(log_hash_hex[2:])

        # Pick sender
        if PRIVATE_KEY:
            account = w3.eth.account.from_key(PRIVATE_KEY)
            sender  = account.address
        else:
            sender = w3.eth.accounts[0]

        tx = contract.functions.storeLog(
            log_hash_bytes,
            int(log_data.get("risk_score", 0)),
            log_data.get("threat_label", "Normal"),
            log_data.get("event_type", "unknown"),
            log_data.get("user_id", "unknown"),
        )

        if PRIVATE_KEY:
            built   = tx.build_transaction({
                "from": sender,
                "nonce": w3.eth.get_transaction_count(sender),
                "gas": 200_000,
                "gasPrice": w3.eth.gas_price,
            })
            signed  = w3.eth.account.sign_transaction(built, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        else:
            tx_hash = tx.transact({"from": sender})

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        return {
            "success": True,
            "tx_hash": receipt.transactionHash.hex(),
            "block_number": receipt.blockNumber,
            "log_hash": log_hash_hex,
        }
    except Exception as e:
        logger.error("store_log_on_chain failed: %s", e)
        return {
            "success": False,
            "tx_hash": None,
            "block_number": None,
            "log_hash": compute_log_hash(log_data),
            "message": str(e),
        }


def get_log_from_chain(log_index: int) -> dict | None:
    """Retrieve a stored log entry from the blockchain by index."""
    _, contract = _get_web3()
    if not contract:
        return None
    try:
        result = contract.functions.getLog(log_index).call()
        return {
            "log_hash": "0x" + result[0].hex(),
            "timestamp": result[1],
            "risk_score": result[2],
            "threat_label": result[3],
            "event_type": result[4],
            "user_id": result[5],
        }
    except Exception as e:
        logger.error("get_log_from_chain(%d) failed: %s", log_index, e)
        return None
