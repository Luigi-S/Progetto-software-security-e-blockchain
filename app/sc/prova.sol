// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;

contract Prova {

    uint256 matricola;

    struct Studente {
        uint256 matricola;
        string nome;
    }

    Studente[] public lista_studenti;
    mapping(string => uint256) public nome_matricola;

    function store(uint256 _numero) public {
        matricola = _numero;
    }
}