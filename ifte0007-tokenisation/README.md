# IFTE0007 Rental Income Tokenisation Implementation

This folder contains a minimal smart-contract implementation for the IFTE0007 individual coursework on asset tokenisation.

## What this implementation demonstrates

- **Token standard:** ERC-20 fungible token
- **Economic logic:** each token represents a proportional claim on distributable net rental income
- **Supply rule:** fixed supply of **1,000,000** tokens
- **Transferability:** standard ERC-20 transfers
- **Ownership clarification:** the token does **not** represent legal ownership of the underlying residential property

## Project structure

```text
ifte0007-tokenisation/
├── contracts/
│   └── RentalIncomeToken.sol
├── scripts/
│   └── deploy.js
├── hardhat.config.js
├── package.json
└── README.md
```

## Contract summary

`RentalIncomeToken.sol` implements a minimal ERC-20 token named **Rental Income Token (RIT)**.

Key design choices:

1. Total supply is minted once on deployment.
2. The deployer / issuer becomes the owner.
3. A demonstration-only event function records income distribution events.
4. The contract intentionally avoids claiming legal property ownership.

## Local setup

```bash
cd ifte0007-tokenisation
npm install
npx hardhat compile
```

## Sepolia deployment

1. Configure a Sepolia RPC endpoint in your local environment.
2. Configure the deployer wallet credentials in your local environment.
3. Run:

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

After deployment, copy the contract address into your report.

## What to include in the report

Add a short implementation-evidence paragraph such as:

> A minimal ERC-20 smart contract was implemented to demonstrate the feasibility of the proposed fungible-token structure. The contract fixes supply at 1,000,000 tokens, supports standard transferability, and explicitly represents a claim on distributable rental income rather than legal ownership of the property. The implementation was deployed on a test network and documented via GitHub.

Then include:

- GitHub repository link
- Testnet contract address
- Deployment screenshot
- Optional transfer screenshot

## Notes

This implementation is intentionally minimal. It is designed to support the coursework argument about **asset -> token -> market -> risk**, rather than to build a full production real-estate tokenisation platform.
