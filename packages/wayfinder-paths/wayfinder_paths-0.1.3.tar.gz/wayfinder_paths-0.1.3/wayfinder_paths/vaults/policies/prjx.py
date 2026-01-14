from wayfinder_paths.vaults.policies.util import allow_functions

PRJX_ROUTER = "0x1ebdfc75ffe3ba3de61e7138a3e8706ac841af9b"
PRJX_NPM = "0xeAd19AE861c29bBb2101E834922B2FEee69B9091"


async def prjx_swap():
    return await allow_functions(
        policy_name="Allow PRJX Swap",
        abi_chain_id=999,
        address=PRJX_ROUTER,
        function_names=[
            "exactInput",
            "exactInputSingle",
            "exactOutput",
            "exactOutputSingle",
        ],
    )


async def prjx_npm():
    return await allow_functions(
        policy_name="Allow PRJX NPM",
        abi_chain_id=999,
        address=PRJX_NPM,
        function_names=[
            "increaseLiquidity",
            "decreaseLiquidity",
        ],
    )
