// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;

contract Mortal {
    address public owner;

    // Initialize Contract: set owner
    constructor() {
        owner = msg.sender;
    }

    // Contract destructor
    function destroy() public {
        require(msg.sender == owner, "msg.sender is not the owner");
        selfdestruct(payable(owner));
    }
}