from __future__ import annotations
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from enterprise_guard.protected_assets import ProtectedAssetRegistry


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('config', nargs='?', default='configs/protected_assets.json')
    ap.add_argument('--show-record', action='store_true')
    ap.add_argument('--test-text', default='')
    args = ap.parse_args()
    reg = ProtectedAssetRegistry.load(ROOT / args.config if not Path(args.config).is_absolute() else args.config)
    enabled = reg.enabled_assets()
    print(f"[OK] loaded {len(enabled)} enabled protected asset(s) from {args.config}")
    if args.show_record:
        for i, a in enumerate(reg.assets, 1):
            state = 'ON' if a.enabled else 'OFF'
            print(f"{i}. [{state}] {a.asset_id} | {a.name} | {a.asset_type} | risk={a.risk_level} | source={a.source} | masked={a.masked_value()}")
    if args.test_text:
        hits = reg.detect(args.test_text)
        print(f"hit_count: {len(hits)}")
        for h in hits:
            print(f"- {h['asset_id']} | {h['asset_type']} | {h['risk_level']} | {h['match_rule']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
