// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "./AbstractManager.sol";

contract Manager is AbstractManager{
    
    constructor() AbstractManager(){
        algs.push(minDeployAlg);
    }

    function defaultAlg() internal override returns(string memory) {

         uint256 loopShard = (currentShard + shardList.length - 1) % shardList.length;

         while(currentShard != loopShard && !shardList[currentShard].active){
            currentShard = (currentShard + 1) % shardList.length;
         }
         
         string memory url;

         if(shardList[currentShard].active){
            url = shardList[currentShard].url;
         }
         else{
             url = "no_shard_active";
         }

         currentShard = (currentShard + 1) % shardList.length;

         return url;
    }

    function minDeployAlg() internal view returns(string memory) {
        uint256 minDeploy;
        string memory url;

        uint256 i;
        for(i = 0; i < shardList.length && !shardList[i].active; i++){
            //
        }

        if(i < shardList.length){
            minDeploy = shardList[i].numDeploy;
            url = shardList[i].url;
            for(uint256 j = i+1; j < shardList.length; j++){
                if(shardList[j].active && shardList[j].numDeploy < minDeploy){
                    minDeploy = shardList[j].numDeploy;
                    url = shardList[j].url;
                }
            }
        }
        else{
            url = "no_shard_active";
        }

        return url;
    }
    
    //altri algoritmi

}
