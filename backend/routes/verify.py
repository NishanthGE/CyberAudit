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
    1. Fetch log from MongoDB by ObjectId
    2. Re-compute its SHA-256 hash
    3. Fetch the hash stored on-chain by logId string (= MongoDB ObjectId)
    4. Compare → VERIFIED or TAMPERED
    """
    # 1. Fetch off-chain document
    log_doc = await get_log_by_id(log_id)
    if not log_doc:
        raise HTTPException(status_code=404, detail="Log not found in database")

    # 2. Recompute hash from current MongoDB document
    recomputed_hash = compute_log_hash(log_doc)  # type: ignore[arg-type]

    if not is_blockchain_available():
        return {
            "status": "UNAVAILABLE",
            "message": "Blockchain node not reachable — install web3+setuptools and restart",
            "log_id": log_id,
            "recomputed_hash": recomputed_hash,
            "stored_hash": None,
        }

    if not log_doc.get("tx_hash"):  # type: ignore[union-attr]
        return {
            "status": "NOT_ON_CHAIN",
            "message": "This log was not stored on-chain (blockchain unavailable at ingestion time)",
            "log_id": log_id,
            "recomputed_hash": recomputed_hash,
            "stored_hash": None,
        }

    # 3. Fetch stored hash from chain using MongoDB ObjectId as the on-chain logId key
    chain_data = get_log_from_chain(log_id)
    if not chain_data:
        return {
            "status": "NOT_FOUND_ON_CHAIN",
            "message": "Log not found in smart contract — it may not have been indexed yet",
            "log_id": log_id,
            "recomputed_hash": recomputed_hash,
            "stored_hash": None,
        }

    stored_hash = chain_data["log_hash"]

    # 4. Compare
    is_verified = recomputed_hash.lower() == stored_hash.lower()

    return {
        "status": "VERIFIED" if is_verified else "TAMPERED",
        "log_id": log_id,
        "recomputed_hash": recomputed_hash,
        "stored_hash": stored_hash,
        "hashes_match": is_verified,
        "tx_hash": log_doc.get("tx_hash"),  # type: ignore[union-attr]
        "block_number": chain_data.get("block_number"),
        "risk_score": chain_data.get("risk_score"),
        "threat_label": chain_data.get("threat_label"),
        "event_type": chain_data.get("event_type"),
        "user_id": chain_data.get("user_id"),
    }
