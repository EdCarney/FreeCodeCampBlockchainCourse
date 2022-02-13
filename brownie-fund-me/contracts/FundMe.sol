// SPDX-License-Identifier: MIT

// Smart contract that lets anyone deposit ETH into the contract
// Only the owner of the contract can withdraw the ETH
pragma solidity >=0.6.0 <0.9.0;
//pragma solidity ^0.6.0;

// Get the latest ETH/USD price from chainlink price feed
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

contract FundMe {
    // safe math library check uint256 for integer overflows
    using SafeMathChainlink for uint256;

    // min price in USD
    uint256 private minUsdPrice = 50;
    // desired precision for our output
    uint256 public desiredPrecision = 18;
    // number of wei in each ETH
    uint256 public weiPerETH = 10**18;
    // mapping to store which address depositeded how much ETH
    mapping(address => uint256) public addressToAmountFunded;
    // array of addresses who deposited
    address[] public funders;
    //address of the owner (who deployed the contract)
    address public owner;
    // chainlink oracle price feed
    AggregatorV3Interface public priceFeed;

    // the first person to deploy the contract is
    // the owner
    constructor(address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    function fund() public payable {
        // 18 digit number to be compared with donated amount
        uint256 minimumUSD = minUsdPrice * 10**desiredPrecision;
        //is the donated amount less than 5USD?
        require(
            getConversionRate(msg.value) >= minimumUSD,
            "You need to spend more ETH!"
        );
        //if not, add to mapping and funders array
        addressToAmountFunded[msg.sender] += msg.value;
        funders.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        // minimumUSD
        uint256 minimumUSD = minUsdPrice * 10**desiredPrecision;
        uint256 USDperETH = getPrice();

        // ReqUSD / (USD / ETH) = ReqETH
        return (minimumUSD * 10**desiredPrecision) / USDperETH;
    }

    function getPrecisionMultiplier() public view returns (uint256) {
        uint256 priceFeedPrecision = uint256(priceFeed.decimals());
        uint256 precisionDiff = desiredPrecision - priceFeedPrecision;
        return 10**precisionDiff;
    }

    //function to get the version of the chainlink pricefeed
    function getVersion() public view returns (uint256) {
        return priceFeed.version();
    }

    // get price of ETH in USD with desired number of decimals
    function getPrice() public view returns (uint256) {
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        // ETH/USD rate in our desired number of digits
        return uint256(answer) * getPrecisionMultiplier();
    }

    // gets amount in USD from amount of Wei; answer returns
    // with desired number of decimals
    function getConversionRate(uint256 weiAmount)
        public
        view
        returns (uint256)
    {
        // $2000 per ETH
        // you sent 50 Wei
        // getPrice gets 2000 with 18 zeros (2000_000000000000000000)
        // ethAmount is 50, but really it's 0.000000000000000050
        // ethAmountInUsd is now (100_000), but it's really $0.000000000000100000

        uint256 USDperETH = getPrice();
        uint256 ethAmount = (weiAmount * 10**desiredPrecision) / weiPerETH;
        uint256 ethAmountInUsd = (USDperETH * ethAmount) /
            (10**desiredPrecision);
        return ethAmountInUsd;
    }

    //modifier: https://medium.com/coinmonks/solidity-tutorial-all-about-modifiers-a86cf81c14cb
    modifier onlyOwner() {
        //is the message sender owner of the contract?
        require(msg.sender == owner);

        _;
    }

    // onlyOwner modifer will first check the condition inside it
    // and
    // if true, withdraw function will be executed
    function withdraw() public payable onlyOwner {
        // If you are using version eight (v0.8) of chainlink aggregator interface,
        // you will need to change the code below to
        // payable(msg.sender).transfer(address(this).balance);
        msg.sender.transfer(address(this).balance);

        //iterate through all the mappings and make them 0
        //since all the deposited amount has been withdrawn
        for (
            uint256 funderIndex = 0;
            funderIndex < funders.length;
            funderIndex++
        ) {
            address funder = funders[funderIndex];
            addressToAmountFunded[funder] = 0;
        }
        //funders array will be initialized to 0
        funders = new address[](0);
    }
}
