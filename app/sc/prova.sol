// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;

contract Prova {

    struct Person {
        uint256 mat;
        string name;
        bytes random_bytes;
        bool sex;
        string [] hobbies;
        uint8 [2][2] lucky_matrix;
    }

    Person [] public people;

    function addPerson(uint256 mat, string calldata name, 
                        bytes calldata random_bytes, bool sex,
                        string [] calldata hobbies, uint8[2][2] calldata lucky_matrix) public {
        Person memory p = Person(mat, name, random_bytes, sex, hobbies, lucky_matrix);
        people.push(p); 
    }

    function getPerson(uint256 index) public view returns (Person memory){
        return people[index];
    }
}