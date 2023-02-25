// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "contracts/AbstractOracle.sol";
import "contracts/AbstractManager.sol";

contract Oracle is AbstractOracle {

    AbstractManager private manager;

    //owner
    function setManager(address newAddress) external onlyOwner{
        manager = AbstractManager(newAddress);
        emit ChangedManager(newAddress);
    }

    function deployFound(address user, string calldata shard, string calldata name, bytes20 addr, bool reserved, uint32 timestamp) 
        external onlyOwner managerInitialized{
        manager.fullfillDeploy(user, shard, name, addr, reserved, timestamp);
    }

    
    function deleteFound(string calldata shard, bytes20 addr) 
        external onlyOwner managerInitialized{
        manager.fullfillDelete(shard, addr);
    }
    

    //manager
    function notifyDeploy(address user, string calldata shard, string calldata name) 
        external override managerInitialized onlyManager{
        emit DeployReserved(user, shard, name);
    }

    //modifiers
    modifier onlyManager() {
        require(msg.sender == address(manager), "Caller is not manager");
        _;
    }

    modifier managerInitialized(){
        require(manager != AbstractManager(address(0)), "Manager not initialized");
        _;
    }

    //event
    event ChangedManager(address newAddress);
    event DeployReserved(address user, string shard, string name);
}