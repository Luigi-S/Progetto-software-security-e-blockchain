// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "./AbstractOracle.sol";
import "./AbstractManager.sol";

contract Oracle is AbstractOracle {
    
    struct InfoContract {
        string shard;
        bytes20 addr;
    }

    mapping(uint256 => InfoContract) public pendingDeploy;
    mapping(uint256 => InfoContract) public pendingDelete;

    AbstractManager private manager;

    //owner
    function setManager(address newAddress) external onlyOwner{
        manager = AbstractManager(newAddress);
        emit ChangedManager(newAddress);
    }

    function deployChecked(uint256 id, bool result) external onlyOwner managerInitialized deployFound(id){
        delete pendingDeploy[id];

        if(result) {
            manager.confirmDeploy(id);
        }
        else{
            manager.delDeploy(id, true);
        }
    }

    function deleteChecked(uint256 id, bool result) external onlyOwner managerInitialized deleteFound(id){
        require(pendingDelete[id].addr != bytes20(0), "Delete request not found");
        delete pendingDelete[id];
        
        if(result) {
            manager.delDeploy(id, false);
        }
        else{
            manager.failDelete(id);
        }
    }

    //manager
    function checkDeploy(uint256 id, string calldata shard, bytes20 addr) external override onlyManager{
        pendingDeploy[id] = InfoContract(shard, addr);
        emit CheckDeployRequest(id, shard, addr);
    }

    function checkDelete(uint256 id, string calldata shard, bytes20 addr) external override onlyManager{
        pendingDelete[id] = InfoContract(shard, addr);
        emit CheckDeleteRequest(id, shard, addr);
    }

    //modifiers
    modifier onlyManager() {
        require(msg.sender == address(manager), "Unauthorized.");
        _;
    }

    modifier managerInitialized(){
        require(manager != AbstractManager(address(0)), "Manager not initialized.");
        _;
    }

    modifier deployFound(uint256 id){
        require(pendingDeploy[id].addr != bytes20(0), "Deploy request not found");
        _;
    }

    modifier deleteFound(uint256 id){
        require(pendingDelete[id].addr != bytes20(0), "Deploy request not found");
        _;
    }
    //event
    event ChangedManager(address newAddress);
    event CheckDeployRequest(uint256 id, string shard, bytes20 addr);
    event CheckDeleteRequest(uint256 id, string shard, bytes20 addr);

}
