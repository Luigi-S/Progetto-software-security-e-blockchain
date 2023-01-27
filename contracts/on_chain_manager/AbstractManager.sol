// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;
import "@openzeppelin/contracts/access/Ownable.sol";
import "./AbstractOracle.sol";

abstract contract AbstractManager is Ownable {

    struct Contract {
        uint256 shardId; 
        bytes20 addr; //address del contratto
        string name; //nome del contratto
        uint256 deployTime; //timestamp deploy
        bool confirmed; //conferma del deploy

        //altri parametri utili per algoritmi:
        //uint size; //dimensione contratto
    }

    struct Shard {
        string url;
        bool active; //disponibilità shard
        uint256 numDeploy; //quanti deploy sono stati fatti
        
        //altri parametri utili per algoritmi:
        //uint priority; //algoritmo proporzionale?
    }

    //qui contratti deployati
    mapping(uint256 => Contract) public deployMap;
    
    //qui shard disponibili
    Shard [] public shardList;

    //algoritmo selezionato
    uint8 currentAlg;

    //shard round robin
    uint256 currentShard;

    //algoritmi disponibili
    function() internal returns(string memory) [] algs;

    //oracle
    AbstractOracle private oracle;

    //numero di deploy dichiarati
    uint256 contractId;

    constructor() Ownable(){
        currentAlg = 0;
        contractId = 0;
        algs.push(defaultAlg);
    }

    //onlyOwner
    
    //setta oracle
    function setOracle(address newAddress) external onlyOwner {
        oracle = AbstractOracle(newAddress);
        emit ChangedOracle(newAddress);
    }

    function addShard(string calldata url, bool active) external onlyOwner atMostTenShards{
        //require url valido: magari sull'offchain?
        shardList.push(Shard(url, active, 0));
        uint256 shardId = shardList.length - 1; 
        emit ShardAdded(shardId,url);
    }

    //setta nuovo algoritmo
    function setAlg(uint8 newAlg) external onlyOwner algExists(newAlg){
        currentAlg = newAlg;
        emit ChangedAlgorithm(newAlg);
    }

    //setta status shard
    function setShardStatus(uint256 shardId, bool status) external onlyOwner shardExists(shardId) {
        shardList[shardId].active = status;
    }
    //utente

    //calcola shard per deploy
    function nextShard() external atLeastOneShard returns(string memory){
        return algs[currentAlg]();
    }

    //dichiara il deploy
    function declareDeploy(uint256 shardId, bytes20 addr, string calldata name) external oracleInitialized shardExists(shardId){
        contractId++;
        uint256 id = contractId;
        uint256 deployTime = block.timestamp;
        string memory shard = shardList[shardId].url;
        deployMap[id] = Contract(shardId, addr, name, deployTime, false);
        oracle.checkDeploy(id, shard, addr);
        emit DeployDeclared(shardId, shard, addr, name);
    }

    //util
    function getInfoByDeployId(uint256 id) internal view returns(uint256, string memory, bytes20, string memory){
        uint256 shardId = deployMap[id].shardId;
        string memory shard = shardList[shardId].url;
        bytes20 addr = deployMap[id].addr;
        string memory name = deployMap[id].name;
        return (shardId, shard, addr, name);
    }

    //dichiara l'eliminazione
    function declareDel(uint256 id) external deployExists(id) oracleInitialized{
        (uint256 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        oracle.checkDelete(id, shard, addr);
        emit DeleteDeclared(shardId, shard, addr, name);
    }

    //va chiamata solo dopo il deploy e la verifica dell'oracolo
    function confirmDeploy(uint256 id) external onlyOracle deployExists(id){
        deployMap[id].confirmed = true;
        (uint256 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        shardList[shardId].numDeploy++;
        emit DeployConfirmed(shardId, shard, addr, name);
    }
 
    //va chiamata solo dopo l'eliminazione e la verifica dell'oracolo
    function delDeploy(uint256 id, bool isDeploy) external onlyOracle deployExists(id){
        (uint256 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        delete deployMap[id];
        if(isDeploy){
            emit DeployNotConfirmed(shardId, shard, addr, name);
        }
        else{
            shardList[shardId].numDeploy--;
            emit DeleteConfirmed(shardId, shard, addr, name);
        }
    }

    //chiamata quando una delete non è confermata
    function failDelete(uint256 id) external onlyOracle deployExists(id){
        (uint256 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        emit DeleteNotConfirmed(shardId, shard, addr, name);
    }

    //algoritmo di default
    function defaultAlg() internal virtual returns(string memory);

    //modifiers

    modifier onlyOracle() {
        require(msg.sender == address(oracle), "Unauthorized.");
        _;
    }

    modifier atLeastOneShard(){
        require(shardList.length > 0, "There are no shards");
        _;
    }

    modifier atMostTenShards(){
        require(shardList.length <= 10, "Shards limit reached");
        _;
    }

    modifier deployExists(uint256 id){
        require(deployMap[id].addr != bytes20(0), "Deploy not found");
        _;
    }

    modifier oracleInitialized(){
        require(oracle != AbstractOracle(address(0)), "Oracle not initialized.");
        _;
    }

    modifier shardExists(uint256 shardId){
        require(shardId < shardList.length, "Shard not found");
        _;
    }

    modifier algExists(uint8 newAlg){
        require(newAlg < algs.length, "Algorithm doesn't exist");
        _;
    }

    //events
    event ShardAdded(uint256 shardId, string shard);
    event ChangedOracle(address newAddress);
    event ChangedAlgorithm(uint8 newAlg);
    event DeployDeclared(uint256 shardId, string shard, bytes20 addr, string  name);
    event DeleteDeclared(uint256 shardId, string shard, bytes20 addr, string  name);
    event DeployConfirmed(uint256 shardId, string shard, bytes20 addr, string  name);
    event DeployNotConfirmed(uint256 shardId, string  shard, bytes20 addr, string  name);
    event DeleteConfirmed(uint256 shardId, string  shard, bytes20 addr, string  name);
    event DeleteNotConfirmed(uint256 shardId, string  shard, bytes20 addr, string  name);
}
