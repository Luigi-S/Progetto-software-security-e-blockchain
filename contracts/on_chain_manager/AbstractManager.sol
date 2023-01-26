// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "@openzeppelin/contracts/access/Ownable.sol";

abstract contract AbstractManager is Ownable{

    modifier onlyOracle;

    struct Contract {
        string shard;
        address loc;
        string name;
        string deployTime;
    };

    struct InfoShard {
        bool active;
        uint256 numDeploy;
        //other params
    };

    //qui contratti deployati
    mapping ( uint256 => Contract) public deployMap;
    
    //qui shard disponibili
    mapping ( string => InfoShard) public shardMap;

    //algoritmo selezionato
    uint8 currentAlg;

    //algoritmi disponibili
    function () [] algs;

    //oracle
    address oracle;
    

    constructor() Ownable(){
        currentAlg = 0;
        algs.push(defaultAlg);
    }

    //onlyOwner

    //setta nuovo algoritmo
    function setAlg(uint8 newAlg) public onlyOwner{
        require(newAlg >= 0 && newAlg < algs.length);
        currentAlg = newAlg;
    }

    //setta status shard
    function setShardStatus(string url, bool status) public onlyOwner;


    //utente

    //calcola shard per deploy
    function nextShard() public view returns(string){
        return algs[currentAlg]();
    }

    //dichiara il deploy
    function declareDeploy(string shard, address loc, string name, string deployTime) public;

    //dichiare l'eliminazione
    function declareDel(uint256 id) public;

    //algoritmo di default
    function defaultAlg() internal returns(string);

    //va chiamata solo dopo il deploy e la verifica dell'oracolo
    function addDeploy(uint256 id) public onlyOracle;
 
    //va chiamata solo dopo l'eliminazione e la verifica dell'oracolo
    function delDeploy(uint256 id) public onlyOracle;
    
}
