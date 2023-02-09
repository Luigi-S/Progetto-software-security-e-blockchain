// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;
import "@openzeppelin/contracts/access/Ownable.sol";
import "contracts/AbstractOracle.sol";

abstract contract AbstractManager is Ownable {
    
    enum Status{ NONE, RESERVED, PENDING_DEPLOY, DEPLOYED, PENDING_DELETE }

    struct Contract {
        uint8 shardId; 
        bytes20 addr; //address del contratto
        string name; //nome del contratto
        address user; //address dell'utente
        uint256 deployTime; //timestamp deploy
        Status status;
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
    uint8 private currentAlg;

    //shard round robin
    uint8 currentShard;

    //algoritmi disponibili
    function() internal returns(uint8) [] algs;

    //oracle
    AbstractOracle private oracle;

    //numero di deploy dichiarati
    uint256 public contractId;

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

    //util
    function getInfoByDeployId(uint256 id) internal view returns(uint8, string memory, bytes20, string memory){
        uint8 shardId = deployMap[id].shardId;
        string memory shard = shardList[shardId].url;
        bytes20 addr = deployMap[id].addr;
        string memory name = deployMap[id].name;
        return (shardId, shard, addr, name);
    }

    //utente

    //calcola shard per deploy
    function reserveDeploy() external atLeastOneShard returns(uint256, string memory){
        uint8 shardId = algs[currentAlg]();
        string memory url = "";
        if(shardId < maxShard){
            url = shardList[shardId].url;
            contractId++;
            deployMap[contractId] = Contract(shardId, bytes20(0), "", msg.sender, 0, Status.RESERVED);
            shardList[shardId].numDeploy++;
            emit DeployReserved(contractId, shardId, url);
        }
        else{
            revert("No shard available for deploy");
        }
        return (contractId, url);
    }

    //dichiara il deploy
    function declareDeploy(uint256 id, bytes20 addr, string calldata name) external oracleInitialized checkDeployReserver(id)
             deployCheckState(id,Status.RESERVED){
        uint8 shardId = deployMap[id].shardId;
        string memory shard = shardList[shardId].url;
        deployMap[id].addr = addr;
        deployMap[id].name = name;
        deployMap[id].deployTime = block.timestamp;
        deployMap[id].status = Status.PENDING_DEPLOY;
        oracle.checkDeploy(id, shard, addr, deployMap[id].user);
        emit DeployDeclared(id, shardId, shard, addr, name);
    }

    //dichiara l'eliminazione
    function declareDel(uint256 id) external oracleInitialized checkDeployReserver(id)
             deployCheckState(id,Status.DEPLOYED) {
        (uint8 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        shardList[shardId].numDeploy--;
        deployMap[id].status = Status.PENDING_DELETE;
        oracle.checkDelete(id, shard, addr, deployMap[id].user);
        emit DeleteDeclared(id, shardId, shard, addr, name);
    }

    //va chiamata solo dopo il deploy e la verifica dell'oracolo
    function fullfillDeploy(uint256 id, bool result) external oracleInitialized onlyOracle 
             deployCheckState(id,Status.PENDING_DEPLOY){
        (uint8 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        if(result){
            deployMap[id].status = Status.DEPLOYED;
            emit DeployConfirmed(id, shardId, shard, addr, name);
        }
        else{
            delete deployMap[id]; //ok? oppure non eliminiamo e l'utente può riprovare a fare declareDeploy
            shardList[shardId].numDeploy--;
            emit DeployNotConfirmed(id, shardId, shard, addr, name);
        }
    }
 
    //va chiamata solo dopo l'eliminazione e la verifica dell'oracolo
    function fullfillDelete(uint256 id, bool result) external oracleInitialized onlyOracle 
             deployCheckState(id, Status.PENDING_DELETE){
        (uint8 shardId, string memory shard, bytes20 addr, string memory name) = getInfoByDeployId(id);
        if(result){
            delete deployMap[id];
            emit DeleteConfirmed(id, shardId, shard, addr, name);
        }
        else{
            shardList[shardId].numDeploy++;
            deployMap[id].status = Status.DEPLOYED;
            emit DeleteNotConfirmed(id, shardId, shard, addr, name);    
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

    modifier deployCheckState(uint256 id, Status status){
        require(deployMap[id].status == status, "Deploy state error");
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

    modifier checkDeployReserver(uint256 id){
        require(deployMap[id].user == msg.sender, "Caller is not deploy reserver");
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
