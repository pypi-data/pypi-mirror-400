from wayfinder_paths.vaults.policies.util import allow_functions

WETH = "0x4200000000000000000000000000000000000006"

M_USDC = "0xEdc817A28E8B93B03976FBd4a3dDBc9f7D176c22"
M_WETH = "0x628ff693426583D9a7FB391E54366292F509D457"
M_WSTETH = "0x627Fe393Bc6EdDA28e99AE648fD6fF362514304b"

COMPTROLLER = "0xfbb21d0380bee3312b33c4353c8936a0f13ef26c"


async def weth_deposit():
    return await allow_functions(
        policy_name="Allow WETH Deposit",
        abi_chain_id=8453,
        address=WETH,
        function_names=["deposit"],
    )


async def musdc_mint_or_approve_or_redeem():
    return await allow_functions(
        policy_name="Allow MUSDC Mint or Approve or Redeem",
        abi_chain_id=8453,
        address=M_USDC,
        function_names=["mint", "approve", "redeem"],
    )


async def mweth_approve_or_borrow_or_repay():
    return await allow_functions(
        policy_name="Allow MWETH Approve or Borrow or Repay",
        abi_chain_id=8453,
        address=M_WETH,
        function_names=["approve", "borrow", "repayBorrow"],
    )


async def mwsteth_approve_or_mint_or_redeem():
    return await allow_functions(
        policy_name="Allow MWSTETH Approve or Mint or Redeem",
        abi_chain_id=8453,
        address=M_WSTETH,
        function_names=["approve", "mint", "redeem"],
    )


async def moonwell_comptroller_enter_markets_or_claim_rewards():
    return await allow_functions(
        policy_name="Allow Moonwell Comptroller Enter Markets or Claim Rewards",
        abi_chain_id=8453,
        address=COMPTROLLER,
        function_names=["enterMarkets", "claimReward"],
    )
