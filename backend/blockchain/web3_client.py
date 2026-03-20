"""
Web3.py client for AuditLog smart contract interaction.
Gracefully handles missing web3 installation — backend starts normally,
blockchain calls return a 'not available' result instead of crashing.

Compatible with web3.py v5.x (installed) which uses camelCase API.
"""

import os
import json
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Try importing web3 ────────────────────────────────────────────────────────
try:
    from web3 import Web3  # type: ignore[import-untyped]
    try:
        # web3 >= 6.x renamed the middleware
        from web3.middleware import ExtraDataToPOAMiddleware as _poa_middleware  # type: ignore[import-untyped]
    except ImportError:
        try:
            # web3 v5.x middleware
            from web3.middleware import geth_poa_middleware as _poa_middleware  # type: ignore[import-untyped]
        except ImportError:
            _poa_middleware = None
    WEB3_AVAILABLE = True
    logger.info("web3 imported successfully")
except ImportError:
    WEB3_AVAILABLE = False
    Web3 = None  # type: ignore[assignment,misc]
    _poa_middleware = None
    logger.warning("web3 not installed — blockchain features disabled. Run: pip install setuptools web3")

# ── Config ────────────────────────────────────────────────────────────────────
HARDHAT_RPC     = os.getenv("HARDHAT_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDR   = os.getenv("CONTRACT_ADDRESS", "")
PRIVATE_KEY     = os.getenv("DEPLOYER_PRIVATE_KEY", "")

# Cached instances
_w3       = None
_contract = None


def _load_abi() -> list:
    """Try to load ABI from hardhat artifacts or deployment.json (if it includes abi)."""
    candidates = [
        # Hardhat artifact always has the full ABI
        Path(__file__).parent.parent.parent / "artifacts" / "contracts" / "AuditLog.sol" / "AuditLog.json",
        # deployment.json only if it happens to embed the abi
        Path(__file__).parent.parent / "deployment.json",
    ]
    for p in candidates:
        if p.exists():
            data = json.loads(p.read_text())
            abi = data.get("abi", [])
            if abi:   # skip files that have no abi field
                return abi
    return []


def _is_connected(w3) -> bool:  # type: ignore[no-untyped-def]
    """Works for both web3 v5 (isConnected) and v6 (is_connected)."""
    try:
        return bool(w3.is_connected())
    except AttributeError:
        return bool(w3.isConnected())  # type: ignore[union-attr]


def _to_checksum(addr: str) -> str:
    """Works for both web3 v5 (toChecksumAddress) and v6 (to_checksum_address)."""
    try:
        return str(Web3.to_checksum_address(addr))  # type: ignore[union-attr]
    except AttributeError:
        return str(Web3.toChecksumAddress(addr))  # type: ignore[union-attr]


def _get_nonce(w3, sender: str) -> int:  # type: ignore[no-untyped-def]
    """Works for both web3 v5 and v6."""
    try:
        return int(w3.eth.get_transaction_count(sender))
    except AttributeError:
        return int(w3.eth.getTransactionCount(sender))  # type: ignore[union-attr]


def _get_gas_price(w3):  # type: ignore[no-untyped-def]
    """Works for both web3 v5 and v6."""
    try:
        return w3.eth.gas_price
    except AttributeError:
        return w3.eth.gasPrice  # type: ignore[union-attr]


def _send_raw_tx(w3, raw_tx):  # type: ignore[no-untyped-def]
    """Works for both web3 v5 and v6."""
    try:
        return w3.eth.send_raw_transaction(raw_tx)
    except AttributeError:
        return w3.eth.sendRawTransaction(raw_tx)  # type: ignore[union-attr]


def _wait_receipt(w3, tx_hash, timeout: int = 30):  # type: ignore[no-untyped-def]
    """Works for both web3 v5 and v6."""
    try:
        return w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
    except AttributeError:
        return w3.eth.waitForTransactionReceipt(tx_hash, timeout=timeout)  # type: ignore[union-attr]


def _get_web3():
    global _w3, _contract
    if not WEB3_AVAILABLE:
        return None, None
    if _w3 is not None:
        return _w3, _contract
    try:
        w3 = Web3(Web3.HTTPProvider(HARDHAT_RPC, request_kwargs={"timeout": 10}))  # type: ignore[misc]
        if _poa_middleware is not None:
            w3.middleware_onion.inject(_poa_middleware, layer=0)
        if not _is_connected(w3):
            logger.warning("Hardhat RPC not reachable at %s", HARDHAT_RPC)
            return None, None
        abi = _load_abi()
        if not abi or not CONTRACT_ADDR:
            logger.warning("ABI or CONTRACT_ADDRESS missing — blockchain features disabled")
            return w3, None
        contract = w3.eth.contract(address=_to_checksum(CONTRACT_ADDR), abi=abi)  # type: ignore[union-attr]
        _w3, _contract = w3, contract
        logger.info("Connected to blockchain at %s, contract %s", HARDHAT_RPC, CONTRACT_ADDR)
        return w3, contract
    except Exception as e:
        logger.warning("Blockchain connection failed: %s", e)
        return None, None


def is_blockchain_available() -> bool:
    w3, contract = _get_web3()
    return w3 is not None and contract is not None


_HASH_FIELDS = [
    "user_id", "source_ip", "event_type", "description", "hour",
    "threat_label", "threat_confidence", "is_anomaly", "anomaly_score",
    "risk_score", "severity",
]


def compute_log_hash(log_data: dict) -> str:
    """Compute a deterministic SHA-256 hash of the core event fields.
    
    Uses a fixed canonical field list so the hash is identical:
    - at ingestion time (doc sent to store_log_on_chain)
    - at verify time (doc fetched from MongoDB, which has extra fields like _id, tx_hash)
    """
    fields = "|".join(str(log_data.get(k, "")) for k in _HASH_FIELDS)
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
            "message": "Blockchain not available — Hardhat node not running",
        }
    try:
        log_hash_hex: str = compute_log_hash(log_data)
        log_hash_bytes = bytes.fromhex(log_hash_hex[2:])

        # Pick sender
        if PRIVATE_KEY:
            account = w3.eth.account.from_key(PRIVATE_KEY)  # type: ignore[union-attr]
            sender  = account.address
        else:
            sender = w3.eth.accounts[0]  # type: ignore[union-attr]

        tx = contract.functions.storeLog(
            str(log_data.get("_id", "")),           # logId  (MongoDB ObjectId string)
            log_hash_bytes,                          # logHash (bytes32)
            int(log_data.get("risk_score", 0)),     # riskScore (uint8)
            str(log_data.get("threat_label", "Normal")),  # threatLabel
            str(log_data.get("event_type", "unknown")),   # eventType
            str(log_data.get("user_id", "unknown")),      # userId
        )

        if PRIVATE_KEY:
            built   = tx.buildTransaction({
                "from": sender,
                "nonce": _get_nonce(w3, sender),
                "gas": 200_000,
                "gasPrice": _get_gas_price(w3),
            })
            signed  = w3.eth.account.sign_transaction(built, PRIVATE_KEY)  # type: ignore[union-attr]
            tx_hash = _send_raw_tx(w3, signed.rawTransaction)
        else:
            tx_hash = tx.transact({"from": sender})

        receipt = _wait_receipt(w3, tx_hash, timeout=30)
        return {
            "success": True,
            "tx_hash": bytes(receipt.transactionHash).hex(),
            "block_number": int(receipt.blockNumber),
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


def get_log_from_chain(log_id: str) -> dict | None:
    """Retrieve a stored log entry from the blockchain by its MongoDB ObjectId string."""
    _, contract = _get_web3()
    if not contract:
        return None
    try:
        result = contract.functions.getLog(log_id).call()
        # Returns: (logHash:bytes32, timestamp:uint256, riskScore:uint8,
        #           threatLabel:string, eventType:string, userId:string)
        return {
            "log_hash":    "0x" + result[0].hex(),
            "timestamp":   result[1],
            "risk_score":  result[2],
            "threat_label": result[3],
            "event_type":  result[4],
            "user_id":     result[5],
        }
    except Exception as e:
        logger.error("get_log_from_chain(%s) failed: %s", log_id, e)
        return None
