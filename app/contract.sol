// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;

contract Contratto {

    uint256 matricola;
    event XXX(uint256 pippo);

    struct Studente {
        uint256 matricola;
        string nome;
    }

    Studente[] public lista_studenti;
    mapping(string => uint256) public nome_matricola;

    function store(uint256 _numero) public {
        matricola = _numero;
        emit XXX(matricola);
    }

    function retrieve() public view returns (uint256){
        return matricola;
    }

    function addStudente(string memory _nome, uint256 _matricola) public {
        lista_studenti.push(Studente(_matricola, _nome));
        nome_matricola[_nome] = _matricola;
    }
}