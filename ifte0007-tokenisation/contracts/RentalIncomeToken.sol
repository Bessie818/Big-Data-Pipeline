// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title RentalIncomeToken
 * @notice Minimal ERC-20 implementation for the IFTE0007 asset tokenisation coursework.
 * @dev This token represents a proportional claim on distributable net rental income,
 *      not legal ownership of the underlying residential property.
 */
contract RentalIncomeToken is ERC20, Ownable {
    uint256 public constant INITIAL_SUPPLY = 1_000_000 * 10 ** 18;

    string public constant ASSET_DESCRIPTION =
        "Tokenised claim on residential net rental income; not legal ownership of the property.";

    event IncomeDistributionRecorded(uint256 amount, string period, string note);

    constructor(address initialOwner)
        ERC20("Rental Income Token", "RIT")
        Ownable(initialOwner)
    {
        _mint(initialOwner, INITIAL_SUPPLY);
    }

    /**
     * @notice Demonstration-only event logger for off-chain rental income distributions.
     * @dev This function does not transfer stablecoins or ETH. It records a distribution event
     *      so the implementation can evidence how future income allocation logic may be tracked.
     */
    function recordIncomeDistribution(
        uint256 amount,
        string calldata period,
        string calldata note
    ) external onlyOwner {
        emit IncomeDistributionRecorded(amount, period, note);
    }
}
