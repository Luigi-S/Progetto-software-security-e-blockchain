// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;
import "@openzeppelin/contracts/access/Ownable.sol";
import "contracts/AbstractOracle.sol";

abstract contract AbstractManager is Ownable {

    struct Contract {
        uint8 shardId;
        string shardUrl; 
        bytes20 addr; //address del contratto
        string name; //nome del contratto
        address user; //address dell'utente
        uint32 deployTime; //timestamp deploy
        bool reserved;
    }

    struct Shard {
        string url;
        bool active; //disponibilità shard
        uint256 numDeploy; //quanti deploy sono stati fatti
    }

    //qui contratti deployati
    Contract [] public deployMap;
    
    //qui shard disponibili
    Shard [] public shardList;

    //algoritmo selezionato
    uint8 private currentAlg;

    //shard round robin
    uint8 currentShard;

    //algoritmi disponibili
    function() internal returns(uint8) [] algs;

    //oracle
    AbstractOracle private oracle;

    uint8 maxShard;

    constructor() Ownable(){
        currentAlg = 0;
        maxShard = 10;
        algs.push(defaultAlg);
    }

    //onlyOwner
    
    //setta oracle
    function setOracle(address newAddress) external onlyOwner {
        oracle = AbstractOracle(newAddress);
        emit ChangedOracle(newAddress);
    }

    function addShard(string calldata url, bool active) external onlyOwner maxShards{
        //require url valido: magari sull'offchain?
        shardList.push(Shard(url, active, 0));
        uint8 shardId = uint8(shardList.length - 1); 
        emit ShardAdded(shardId,url);
    }

    //setta nuovo algoritmo
    function setAlg(uint8 newAlg) external onlyOwner algExists(newAlg){
        currentAlg = newAlg;
        emit ChangedAlgorithm(newAlg);
    }

    //setta status shard
    function setShardStatus(uint8 shardId, bool status) external onlyOwner shardExists(shardId) {
        shardList[shardId].active = status;
    }

    //util
    function getIdFromUrl(string calldata shardUrl) internal view returns(uint8){
         uint8 shardId;
        for(uint8 i=0; i < shardList.length; i++){
            if(keccak256(abi.encodePacked(shardList[i].url)) == keccak256(abi.encodePacked(shardUrl)) ){
                shardId = i;
                break;
            }
        }
        return shardId;
    }

    //utente

    function getDeployMap() external view returns(Contract [] memory){
        Contract [] memory array = new Contract[](deployMap.length);
        for(uint256 i=0; i < deployMap.length; i++){
            array[i] = deployMap[i];
        }
        return array;
    }

    //calcola shard per deploy
    function reserveDeploy(string calldata name) external atLeastOneShard{ //returns(string memory){
        uint8 shardId = algs[currentAlg]();
        string memory url = "";
        if(shardId < maxShard){
            url = shardList[shardId].url;
            emit DeployUrl(url);
            oracle.notifyDeploy(msg.sender,url,name);
        }
        else{
            revert("No shard available for deploy");
        }
        //return url;
    }

    //va chiamata solo dopo il deploy e la verifica dell'oracolo
    function fullfillDeploy(address user, string calldata shardUrl, string calldata name, bytes20 addr, bool reserved, uint32 timestamp) 
        external oracleInitialized onlyOracle {
        uint8 shardId = getIdFromUrl(shardUrl);
        Contract memory c = Contract(shardId, shardUrl, addr, name, user, timestamp, reserved);
        deployMap.push(c);
        shardList[shardId].numDeploy++;
        emit DeploySaved(deployMap.length-1, c);
    }
 
    //va chiamata solo dopo l'eliminazione e la verifica dell'oracolo
    function fullfillDelete(string calldata shardUrl, bytes20 addr) 
        external oracleInitialized onlyOracle {
        uint8 shardId = getIdFromUrl(shardUrl);
        uint8 i;
        Contract memory c;
        for(i=0; i < deployMap.length; i++){
            if(deployMap[i].shardId == shardId &&
               deployMap[i].addr == addr){
                c = deployMap[i];
                break;
            }
        }
        if(i < deployMap.length){
            shardList[shardId].numDeploy--;
            emit DeployDeleted(i, c);
            delete deployMap[i];
        }
    }

    //algoritmo di default
    function defaultAlg() internal virtual returns(uint8);

    //modifiers

    modifier onlyOracle() {
        require(msg.sender == address(oracle), "Caller is not oracle");
        _;
    }

    modifier atLeastOneShard(){
        require(shardList.length > 0, "No shard registered");
        _;
    }

    modifier maxShards(){
        require(shardList.length <= maxShard, "No more shard can be added");
        _;
    }

    modifier oracleInitialized(){
        require(oracle != AbstractOracle(address(0)), "Oracle not initialized");
        _;
    }

    modifier shardExists(uint8 shardId){
        require(shardId < shardList.length, "Shard does not exist");
        _;
    }

    modifier algExists(uint8 newAlg){
        require(newAlg < algs.length, "Algorithm does not exist");
        _;
    }

    //events
    event DeploySaved(uint256 id, Contract c);
    event DeployDeleted(uint256 id, Contract c);
    event ShardAdded(uint8 shardId, string shard);
    event ChangedOracle(address newAddress);
    event ChangedAlgorithm(uint8 newAlg);
    event DeployUrl(string url);
}