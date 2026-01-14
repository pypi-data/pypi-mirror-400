import argparse
import json
from pathlib import Path

from eth_account import Account

from wayfinder_paths.core.utils.wallets import (
    load_wallets,
    make_random_wallet,
    write_wallet_to_json,
)


def to_keystore_json(private_key_hex: str, password: str):
    return Account.encrypt(private_key_hex, password)


def write_env(rows: list[dict[str, str]], out_dir: Path) -> None:
    with open(out_dir / ".env.example", "w") as f:
        if rows:
            label_to_wallet = {r.get("label"): r for r in rows if r.get("label")}
            main_w = (
                label_to_wallet.get("main") or label_to_wallet.get("default") or rows[0]
            )
            vault_w = label_to_wallet.get("vault")

            f.write("RPC_URL=https://rpc.ankr.com/eth\n")
            # Back-compat defaults
            f.write(f"PRIVATE_KEY={main_w['private_key_hex']}\n")
            f.write(f"FROM_ADDRESS={main_w['address']}\n")
            # Explicit main/vault variables
            f.write(f"MAIN_WALLET_ADDRESS={main_w['address']}\n")
            if vault_w:
                f.write(f"VAULT_WALLET_ADDRESS={vault_w['address']}\n")
                # Optional: expose vault private key for local dev only
                f.write(f"PRIVATE_KEY_VAULT={vault_w['private_key_hex']}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate local dev wallets")
    parser.add_argument(
        "-n",
        type=int,
        default=0,
        help="Number of wallets to create (ignored if --label is used)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("."),
        help="Output directory for wallets.json (and .env/keystore)",
    )
    parser.add_argument(
        "--keystore-password",
        type=str,
        default=None,
        help="Optional password to write geth-compatible keystores",
    )
    parser.add_argument(
        "--label",
        type=str,
        default=None,
        help="Create a wallet with a custom label (e.g., strategy name). If not provided, auto-generates labels.",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Load existing wallets
    existing = load_wallets(args.out_dir, "wallets.json")
    has_main = any(w.get("label") in ("main", "default") for w in existing)

    rows: list[dict[str, str]] = []
    index = 0

    # Custom labeled wallet (e.g., for strategy name)
    if args.label:
        # Check if label already exists - if so, skip (don't create duplicate)
        if any(w.get("label") == args.label for w in existing):
            print(f"Wallet with label '{args.label}' already exists, skipping...")
        else:
            # Create wallet with specified label
            w = make_random_wallet()
            w["label"] = args.label
            rows.append(w)
            print(f"[{index}] {w['address']}  (label: {args.label})")
            write_wallet_to_json(w, out_dir=args.out_dir, filename="wallets.json")
            if args.keystore_password:
                ks = to_keystore_json(w["private_key_hex"], args.keystore_password)
                ks_path = args.out_dir / f"keystore_{w['address']}.json"
                ks_path.write_text(json.dumps(ks))
            index += 1

            # If no wallets existed before, also create a "main" wallet
            if not existing:
                main_w = make_random_wallet()
                main_w["label"] = "main"
                rows.append(main_w)
                print(f"[{index}] {main_w['address']}  (main)")
                write_wallet_to_json(
                    main_w, out_dir=args.out_dir, filename="wallets.json"
                )
                if args.keystore_password:
                    ks = to_keystore_json(
                        main_w["private_key_hex"], args.keystore_password
                    )
                    ks_path = args.out_dir / f"keystore_{main_w['address']}.json"
                    ks_path.write_text(json.dumps(ks))
                index += 1
    else:
        # Create wallets with auto-generated labels: first one is "main" if main doesn't exist, others are "temporary_N"
        if args.n == 0:
            args.n = 1  # Default to 1 wallet if neither -n nor --label specified

        # Find next temporary number
        existing_labels = {
            w.get("label", "")
            for w in existing
            if w.get("label", "").startswith("temporary_")
        }
        temp_numbers = set()
        for label in existing_labels:
            try:
                num = int(label.replace("temporary_", ""))
                temp_numbers.add(num)
            except ValueError:
                pass
        next_temp_num = 1
        if temp_numbers:
            next_temp_num = max(temp_numbers) + 1

        for i in range(args.n):
            w = make_random_wallet()
            # Label first wallet as "main" if main doesn't exist, otherwise use temporary_N
            if i == 0 and not has_main:
                w["label"] = "main"
                rows.append(w)
                print(f"[{index}] {w['address']}  (main)")
            else:
                # Find next available temporary number
                while next_temp_num in temp_numbers:
                    next_temp_num += 1
                w["label"] = f"temporary_{next_temp_num}"
                temp_numbers.add(next_temp_num)
                rows.append(w)
                print(f"[{index}] {w['address']}  (label: temporary_{next_temp_num})")

            write_wallet_to_json(w, out_dir=args.out_dir, filename="wallets.json")
            if args.keystore_password:
                ks = to_keystore_json(w["private_key_hex"], args.keystore_password)
                ks_path = args.out_dir / f"keystore_{w['address']}.json"
                ks_path.write_text(json.dumps(ks))
            index += 1

    # Convenience outputs
    write_env(rows, args.out_dir)


if __name__ == "__main__":
    main()
