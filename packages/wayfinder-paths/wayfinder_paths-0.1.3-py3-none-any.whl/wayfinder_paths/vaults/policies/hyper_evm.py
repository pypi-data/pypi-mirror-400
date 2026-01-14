from wayfinder_paths.vaults.policies.evm import native_transfer
from wayfinder_paths.vaults.policies.util import allow_functions

WHYPE_TOKEN = "0x5555555555555555555555555555555555555555"
HYPERCORE_SENTINEL_ADDRESS = "0x2222222222222222222222222222222222222222"
HYPERCORE_SENTINEL_VALUE = 100_000_000_000


def hypecore_sentinel_deposit():
    return native_transfer(HYPERCORE_SENTINEL_ADDRESS, HYPERCORE_SENTINEL_VALUE)


async def whype_deposit_and_withdraw():
    return await allow_functions(
        policy_name="Allow WHYPE Deposit and Withdraw",
        abi_chain_id=999,
        address=WHYPE_TOKEN,
        function_names=["deposit", "withdraw"],
    )
