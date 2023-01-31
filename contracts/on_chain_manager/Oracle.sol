// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "./AbstractOracle.sol";
import "./AbstractManager.sol";

contract Oracle is AbstractOracle {

    AbstractManager private manager;

    //owner
    function setManager(address newAddress) external onlyOwner{
        manager = AbstractManager(newAddress);
        emit ChangedManager(newAddress);
    }

    function deployChecked(uint256 id, bool result) external onlyOwner managerInitialized{
        manager.fullfillDeploy(id, result);
    }

    function deleteChecked(uint256 id, bool result) external onlyOwner managerInitialized{
        manager.fullfillDelete(id, result);
    }

    //manager
    function checkDeploy(uint256 id, string calldata shard, bytes20 addr) external override onlyManager{
        emit CheckDeployRequest(id, shard, addr);
    }

    function checkDelete(uint256 id, string calldata shard, bytes20 addr) external override onlyManager{
        emit CheckDeleteRequest(id, shard, addr);
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
    event CheckDeployRequest(uint256 id, string shard, bytes20 addr);
    event CheckDeleteRequest(uint256 id, string shard, bytes20 addr);
}