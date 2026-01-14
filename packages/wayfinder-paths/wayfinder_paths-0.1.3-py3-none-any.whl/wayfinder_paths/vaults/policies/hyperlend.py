from wayfinder_paths.vaults.policies.util import allow_functions

HYPERLEND_POOL = "0x00A89d7a5A02160f20150EbEA7a2b5E4879A1A8b"


async def hyperlend_supply_and_withdraw():
    return await allow_functions(
        policy_name="Allow Hyperlend Supply and Withdraw",
        abi_chain_id=999,
        address=HYPERLEND_POOL,
        function_names=["supply", "withdraw"],
    )
