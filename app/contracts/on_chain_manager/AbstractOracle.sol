// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "@openzeppelin/contracts/access/Ownable.sol";

abstract contract AbstractOracle is Ownable{

    function checkDeploy(uint256 id, string calldata shard, bytes20 addr) external virtual;
    function checkDelete(uint256 id, string calldata shard, bytes20 addr) external virtual;
}
