// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract SimpleHTLC {

    mapping(address => mapping(uint256 => address)) public approves;
    mapping(address => mapping(uint256 => uint256)) public balances;
    mapping(address => mapping(uint256 => uint256)) public timestamps;

    event HTLCTransactionPay(
        address author,
        uint256 secretHash,
        uint256 lockedValue
    );

    constructor() {}

    function start(uint256 secretHash) external payable {
        emit HTLCTransactionPay(msg.sender, secretHash, msg.value);
    }

    function get(uint256 secret) external {
    }

    function reclaim() external {
    }
}
