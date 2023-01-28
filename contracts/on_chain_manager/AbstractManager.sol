// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;
import "@openzeppelin/contracts/access/Ownable.sol";
import "./AbstractOracle.sol";

abstract contract AbstractManager is Ownable {

    struct Contract {
        uint8 shardId; 
        bytes20 addr; //address del contratto
        string name; //nome del contratto
        address user; //address dell'utente
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
    uint8 currentShard;

    //algoritmi disponibili
    function() internal returns(uint8) [] algs;

    //oracle
    AbstractOracle private oracle;

    //numero di deploy dichiarati
    uint256 contractId;

    uint8 maxShard;

    constructor() Ownable(){
        currentAlg = 0;
        contractId = 0;
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
    //utente

    //calcola shard per deploy
    function reserveDeploy() external atLeastOneShard returns(uint256, string memory){
        uint8 shardId = algs[currentAlg]();
        string memory url = "";
        if(shardId < maxShard){
            url = shardList[shardId].url;
            contractId++;
            deployMap[contractId] = Contract(shardId, bytes20(0), "", msg.sender, 0, false);
            shardList[shardId].numDeploy++;
            emit DeployReserved(contractId, shardId, url);
        }
        else{
            revert("No shard available for deploy");
        }
        return (contractId, url);
    }

    //dichiara il deploy
    function declareDeploy(uint256 id, bytes20 addr, string calldata name) external oracleInitialized checkDeployReserver(id) deployExists(id){
        uint8 shardId = deployMap[id].shardId;
        string memory shard = shardList[shardId].url;
        deployMap[id].addr = addr;
        deployMap[id].name = name;
        deployMap[id].deployTime = block.timestamp;
        oracle.checkDeploy(id, shard, addr);
        emit DeployDeclared(id, shardId, shard, addr, name);
    }

    //util
    function getInfoByDeployId(uint256 id) internal view returns(uint8, string memory, bytes20, string memory){
        uint8 shardId = deployMap[id].shardId;
        string memory shard = shardList[shardId].url;
        bytes20 addr = deployMap[id].addr;
        string memory name = deployMap[id].name;
        return (shardId, shard, addr, name);
    }

    //dichiara l'eliminazione
    function declareDel(uint256 id) external deployExists(id) oracleInitialized{
        (uint8 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        shardList[shardId].numDeploy--;
        oracle.checkDelete(id, shard, addr);
        emit DeleteDeclared(id, shardId, shard, addr, name);
    }

    //va chiamata solo dopo il deploy e la verifica dell'oracolo
    function confirmDeploy(uint256 id) external oracleInitialized onlyOracle deployExists(id){
        deployMap[id].confirmed = true;
        (uint8 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        emit DeployConfirmed(id, shardId, shard, addr, name);
    }
 
    //va chiamata solo dopo l'eliminazione e la verifica dell'oracolo
    function delDeploy(uint256 id, bool isDeploy) external oracleInitialized onlyOracle deployExists(id){
        (uint8 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        delete deployMap[id];
        if(isDeploy){
            shardList[shardId].numDeploy--;
            emit DeployNotConfirmed(id, shardId, shard, addr, name);
        }
        else{
            emit DeleteConfirmed(id, shardId, shard, addr, name);
        }
    }

    //chiamata quando una delete non è confermata
    function failDelete(uint256 id) external oracleInitialized onlyOracle deployExists(id){
        (uint8 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        shardList[shardId].numDeploy++;
        emit DeleteNotConfirmed(id, shardId, shard, addr, name);
    }

    //algoritmo di default
    function defaultAlg() internal virtual returns(uint8);

    //modifiers

    modifier onlyOracle() {
        require(msg.sender == address(oracle), "Unauthorized.");
        _;
    }

    modifier atLeastOneShard(){
        require(shardList.length > 0, "There are no shards");
        _;
    }

    modifier maxShards(){
        require(shardList.length <= maxShard, "Shards limit reached");
        _;
    }

    modifier deployExists(uint256 id){
        require(deployMap[id].user != address(0), "Deploy not found");
        _;
    }

    modifier oracleInitialized(){
        require(oracle != AbstractOracle(address(0)), "Oracle not initialized.");
        _;
    }

    modifier shardExists(uint8 shardId){
        require(shardId < shardList.length, "Shard not found");
        _;
    }

    modifier algExists(uint8 newAlg){
        require(newAlg < algs.length, "Algorithm doesn't exist");
        _;
    }

    modifier checkDeployReserver(uint256 id){
        require(deployMap[id].user == msg.sender);
        _;
    }

    //events
    event ShardAdded(uint8 shardId, string shard);
    event ChangedOracle(address newAddress);
    event ChangedAlgorithm(uint8 newAlg);
    event DeployReserved(uint256 id, uint8 shardId, string shard);
    event DeployDeclared(uint256 id, uint8 shardId, string shard, bytes20 addr, string  name);
    event DeleteDeclared(uint256 id, uint8 shardId, string shard, bytes20 addr, string  name);
    event DeployConfirmed(uint256 id, uint8 shardId, string shard, bytes20 addr, string  name);
    event DeployNotConfirmed(uint256 id, uint8 shardId, string  shard, bytes20 addr, string  name);
    event DeleteConfirmed(uint256 id, uint8 shardId, string  shard, bytes20 addr, string  name);
    event DeleteNotConfirmed(uint256 id, uint8 shardId, string  shard, bytes20 addr, string  name);
}
