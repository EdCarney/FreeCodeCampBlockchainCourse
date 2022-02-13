// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

contract SimpleStorage {
    uint256 favoriteNumber;

    struct Person {
        string name;
        uint256 favoriteNumber;
    }

    Person[] public people;
    mapping(string => uint256) public peopleNameToFavNum;

    function addPerson(string memory _name, uint256 _favoriteNumber) public {
        Person memory person = Person(_name, _favoriteNumber);
        people.push(person);
        peopleNameToFavNum[_name] = _favoriteNumber;
    }

    function store(uint256 _favoriteNumber) public {
        favoriteNumber = _favoriteNumber;
    }

    function retrieve() public view returns (uint256) {
        return favoriteNumber;
    }
}
