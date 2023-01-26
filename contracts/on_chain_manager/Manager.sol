// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "AbstractManager.sol";

contract Manager is AbstractManager{

	function setShardStatus (string url, bool status) public onlyOwner {
        shardMap[url].active = status;
        //definire evento nell'abstract manager
    }

    function declareDeploy(string shard, address loc, string name, string deployTime) public {
            deployMap[contractId].shard = shard;
            deployMap[contractId].loc = loc;
            deployMap[contractId].name = name;
            deployMap[contractId].deployTime = deployTime;
            deployMap[contractId].confirmed = false;
            contractId++;
            //chiamata all'Oracle
    }

     function declareDel(uint256 id) public {
            //chiamata Oracle per verifica delete
     }

     function defaultAlg() internal returns(string) {
         string url = shardList[currentShard].url;
         currentShard = (currentShard + 1) % shardList.length
         return url;
      }

    function confirmDeploy(uint256 id) public onlyOracle {
        deployMap[id].confirmed = true;
    }
     
     function delDeploy(uint256 id) public onlyOracle {
        delete deployMap[id];
     }
}
