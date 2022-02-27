// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    address payable public mostRecentWinner;
    uint256 public usdEntranceFee;
    uint256 public precision = 18;
    uint256 public mostRecentRandomnessValue;
    AggregatorV3Interface internal ethUsdPriceFeed;
    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyHash;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _linkToken,
        uint256 _fee,
        bytes32 _keyHash
    ) public VRFConsumerBase(_vrfCoordinator, _linkToken) {
        usdEntranceFee = 50 * 10**precision;
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;

        // VRF coordinator params
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        // players must submit at least $50
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        // will need an oracale price feed for ETH to USD price
        (, int256 usdPerEth, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 priceFeedDecimals = uint256(ethUsdPriceFeed.decimals());

        /*
            50_000000000000000000 / 2000_00000000 = 1/40_0000000000
            so need to multiply the result to get back up to 18 precision
            Ex Ans: 18226423210256372 => 0.018226423210256372
        */
        uint256 requiredEth = (usdEntranceFee * 10**priceFeedDecimals) /
            uint256(usdPerEth);
        return requiredEth; // * 10**abs(priceFeedDecimals - precision);
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery yet!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "Lottery is not over yet!"
        );
        require(_randomness > 0, "Random value not yet calculated");
        mostRecentRandomnessValue = _randomness;
        calculateWinner();
        payWinner();
        resetLottery();
    }

    function calculateWinner() private {
        uint256 winnerIndex = mostRecentRandomnessValue % players.length;
        mostRecentWinner = players[winnerIndex];
    }

    function payWinner() private {
        mostRecentWinner.transfer(address(this).balance);
    }

    function resetLottery() private {
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
    }
}
