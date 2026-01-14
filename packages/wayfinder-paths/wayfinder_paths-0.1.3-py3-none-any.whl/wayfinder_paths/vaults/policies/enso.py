from wayfinder_paths.vaults.policies.util import allow_functions

ENSO_ROUTER = "0xf75584ef6673ad213a685a1b58cc0330b8ea22cf"


async def enso_swap():
    return await allow_functions(
        policy_name="Allow Enso Swap",
        abi_chain_id=8453,
        address=ENSO_ROUTER,
        function_names=[
            "routeMulti",
            "routeSingle",
            "safeRouteMulti",
            "safeRouteSingle",
        ],
    )
