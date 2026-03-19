// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/**
 * @title AuditLog
 * @dev Immutable cybersecurity audit log storage on Ethereum
 * Every cybersecurity event gets its SHA-256 hash stored on-chain
 * for tamper-proof verification.
 */
contract AuditLog {
    address public owner;

    struct LogEntry {
        bytes32 logHash;       // SHA-256 hash of the full log JSON
        uint256 timestamp;     // Block timestamp of storage
        uint8 riskScore;       // 0-100 risk score from ML engine
        string threatLabel;    // Normal / Probe / DoS / R2L / U2R
        string eventType;      // brute_force / port_scan / etc.
        string userId;         // User identifier
        bool exists;           // Existence flag
    }

    // logId (off-chain MongoDB ObjectId string) => LogEntry
    mapping(string => LogEntry) private logs;
    string[] private logIds;

    uint256 public totalLogs;

    event LogStored(
        string indexed logId,
        bytes32 logHash,
        uint256 timestamp,
        uint8 riskScore,
        string threatLabel,
        string eventType,
        string userId
    );

    event LogTamperDetected(
        string indexed logId,
        bytes32 storedHash,
        bytes32 computedHash,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "AuditLog: caller is not the owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Store a cybersecurity event log entry on-chain
     * @param logId Unique identifier (matches MongoDB document ID)
     * @param logHash SHA-256 hash of the full log JSON (off-chain)
     * @param riskScore ML-computed risk score 0-100
     * @param threatLabel Threat classification label
     * @param eventType Type of cybersecurity event
     * @param userId User who triggered the event
     */
    function storeLog(
        string calldata logId,
        bytes32 logHash,
        uint8 riskScore,
        string calldata threatLabel,
        string calldata eventType,
        string calldata userId
    ) external onlyOwner {
        require(!logs[logId].exists, "AuditLog: log already stored");
        require(riskScore <= 100, "AuditLog: risk score must be 0-100");
        require(bytes(logId).length > 0, "AuditLog: logId cannot be empty");

        logs[logId] = LogEntry({
            logHash: logHash,
            timestamp: block.timestamp,
            riskScore: riskScore,
            threatLabel: threatLabel,
            eventType: eventType,
            userId: userId,
            exists: true
        });

        logIds.push(logId);
        totalLogs++;

        emit LogStored(
            logId,
            logHash,
            block.timestamp,
            riskScore,
            threatLabel,
            eventType,
            userId
        );
    }

    /**
     * @dev Retrieve a stored log entry by its ID
     * @param logId The log identifier
     * @return logHash The stored SHA-256 hash
     * @return timestamp When the log was stored on-chain
     * @return riskScore The risk score
     * @return threatLabel The threat classification
     * @return eventType The event type
     * @return userId The user identifier
     */
    function getLog(string calldata logId)
        external
        view
        returns (
            bytes32 logHash,
            uint256 timestamp,
            uint8 riskScore,
            string memory threatLabel,
            string memory eventType,
            string memory userId
        )
    {
        require(logs[logId].exists, "AuditLog: log not found");
        LogEntry storage entry = logs[logId];
        return (
            entry.logHash,
            entry.timestamp,
            entry.riskScore,
            entry.threatLabel,
            entry.eventType,
            entry.userId
        );
    }

    /**
     * @dev Check if a log exists on-chain
     */
    function logExists(string calldata logId) external view returns (bool) {
        return logs[logId].exists;
    }

    /**
     * @dev Get all stored log IDs (paginated)
     * @param offset Start index
     * @param limit Max entries to return
     */
    function getLogIds(uint256 offset, uint256 limit)
        external
        view
        returns (string[] memory)
    {
        require(offset < logIds.length || logIds.length == 0, "AuditLog: offset out of bounds");
        
        uint256 end = offset + limit;
        if (end > logIds.length) {
            end = logIds.length;
        }
        
        string[] memory result = new string[](end - offset);
        for (uint256 i = offset; i < end; i++) {
            result[i - offset] = logIds[i];
        }
        return result;
    }

    /**
     * @dev Transfer ownership to a new address
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "AuditLog: new owner is zero address");
        owner = newOwner;
    }
}
