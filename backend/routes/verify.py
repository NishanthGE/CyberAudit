"""
Blockchain Verifier Route — Compare off-chain log hash vs on-chain hash
"""

from fastapi import APIRouter, HTTPException
from db.mongo_client import get_log_by_id
from blockchain.web3_client import get_log_from_chain, compute_log_hash, is_blockchain_available

router = APIRouter(prefix="/api/verify", tags=["verify"])


@router.get("/{log_id}")
async def verify_log(log_id: str):
    """
    Verify a log's integrity:
    1. Fetch log from MongoDB
    2. Re-compute its SHA-256 hash
    3. Fetch the hash stored on-chain
    4. Compare → VERIFIED or TAMPERED
    """
    # 1. Fetch off-chain document
    log_doc = await get_log_by_id(log_id)
    if not log_doc:
        raise HTTPException(status_code=404, detail="Log not found in database")

    if not is_blockchain_available():
        # Compute hash anyway so user can see it
        recomputed = compute_log_hash(log_doc)
        return {
            "status": "UNAVAILABLE",
            "message": "Blockchain node not reachable — install web3+setuptools and restart",
            "log_id": log_id,
            "recomputed_hash": recomputed,
            "stored_hash": None,
        }

    if not log_doc.get("tx_hash"):
        return {
            "status": "NOT_ON_CHAIN",
            "message": "This log was not stored on-chain (blockchain unavailable at ingestion time)",
            "log_id": log_id,
            "recomputed_hash": compute_log_hash(log_doc),
            "stored_hash": None,
        }

    # 2. Recompute hash from current MongoDB document
    recomputed_hash = compute_log_hash(log_doc)  # returns "0x<hex>" string

    # 3. Fetch stored hash from chain using blockchain log index
    chain_index = log_doc.get("chain_index", 0)
    chain_data = get_log_from_chain(chain_index)
    if not chain_data:
        return {
            "status": "NOT_FOUND_ON_CHAIN",
            "message": "Log not found in smart contract by index",
            "log_id": log_id,
            "recomputed_hash": recomputed_hash,
            "stored_hash": None,
        }

    stored_hash = chain_data["log_hash"]  # "0x<hex>" string from web3_client

    # 4. Compare
    is_verified = recomputed_hash.lower() == stored_hash.lower()

    return {
        "status": "VERIFIED" if is_verified else "TAMPERED",
        "log_id": log_id,
        "recomputed_hash": recomputed_hash,
        "stored_hash": stored_hash,
        "hashes_match": is_verified,
        "tx_hash": log_doc.get("tx_hash"),
        "block_number": chain_data.get("block_number"),
        "risk_score": chain_data.get("risk_score"),
        "threat_label": chain_data.get("threat_label"),
        "event_type": chain_data.get("event_type"),
        "user_id": chain_data.get("user_id"),
    }
