// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "@openzeppelin/contracts/access/Ownable.sol";

abstract contract AbstractOracle is Ownable{
    function notifyDeploy(address user, string calldata shard, string calldata name) external virtual;
}
