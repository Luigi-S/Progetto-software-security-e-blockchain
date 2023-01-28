// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "./AbstractManager.sol";

contract Manager is AbstractManager{
    
    constructor() AbstractManager(){
        algs.push(minDeployAlg);
    }

    function defaultAlg() internal override returns(uint8) {

         uint8 loopShard = uint8((currentShard + shardList.length - 1) % shardList.length);

         while(currentShard != loopShard && !shardList[currentShard].active){
            currentShard = uint8((currentShard + 1) % shardList.length);
         }

         uint8 shardId = shardList[currentShard].active? currentShard : maxShard;
         currentShard = uint8((currentShard + 1) % shardList.length);
         return shardId;
    }

    function minDeployAlg() internal view returns(uint8) {
        uint256 minDeploy;
        uint8 shardId = maxShard;
        uint8 i;

        for(i = 0; i < shardList.length && !shardList[i].active; i++){
            //
        }

        if(i < shardList.length){
            shardId = i;
            minDeploy = shardList[i].numDeploy;

            for(uint8 j = i+1; j < shardList.length; j++){
                if(shardList[j].active && shardList[j].numDeploy < minDeploy){
                    shardId = j;
                    minDeploy = shardList[j].numDeploy;
                }
            }
        }

        return shardId;
    }
    
    //altri algoritmi

}
