pragma solidity ^0.5;

contract ImageHash {
    string public ipfsHash;

    function saveHash(string memory x) public {
        ipfsHash = x;
    }
    function getHash( string memory y) public view returns ( string memory x) {
        return ipfsHash;
    }
}
