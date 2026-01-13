#!/usr/bin/env python3
"""Run world-model strategies and report scores."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from world_model.entities import (
    DemandPlan,
    Inventory,
    Part,
    PurchaseDecision,
    Strategy,
    Vendor,
)
from world_model.rules import ObjectiveWeights, PurchasePolicy
from world_model.score import score_world
from world_model.simulate import simulate_world
from world_model.state import WorldState
from world_model.uncertainty import LeadTimeUncertainty, PriceUncertainty, SupplyRiskUncertainty


DEFAULT_BASE = Path("world_model/examples")
DEFAULT_WORLD = DEFAULT_BASE / "scm_world_example.json"
DEFAULT_RULES = DEFAULT_BASE / "scm_rules_example.json"
DEFAULT_STRATEGIES = DEFAULT_BASE / "scm_strategies_example.json"
DEFAULT_OUTPUT_DIR = Path("artifacts/world_model")


def load_world(world_path: Path) -> Dict[str, Dict[str, object]]:
    data = json.loads(world_path.read_text(encoding="utf-8"))
    parts = {p["id"]: Part(**p) for p in data["parts"]}
    vendors = {v["name"]: Vendor(**v) for v in data["vendors"]}
    inventory = {inv["part_id"]: Inventory(**inv) for inv in data["inventory"]}

    demand_plans: Dict[str, DemandPlan] = {}
    for dp in data["demand_plans"]:
        demand_plans[dp["part_id"]] = DemandPlan(
            part_id=dp["part_id"],
            demand_by_day={int(day): qty for day, qty in dp["demand_by_day"].items()},
        )
    return {
        "parts": parts,
        "vendors": vendors,
        "inventory": inventory,
        "demand_plans": demand_plans,
    }


def load_rules(rules_path: Path) -> Dict[str, object]:
    data = json.loads(rules_path.read_text(encoding="utf-8"))
    policy = PurchasePolicy(**data["policy"])
    objectives = ObjectiveWeights(**data["objectives"])
    uncertainty = data.get("uncertainty", {})
    lead_unc = LeadTimeUncertainty(**uncertainty.get("lead_time", {"mean": 0, "std": 0}))
    price_unc = PriceUncertainty(**uncertainty.get("price", {"min_factor": 1.0, "max_factor": 1.0}))
    risk_unc = SupplyRiskUncertainty(**uncertainty.get("supply_risk", {"base_prob": 0.0}))
    horizon = data.get("timeline", {}).get("horizon_days", 60)
    return {
        "policy": policy,
        "objectives": objectives,
        "lead_unc": lead_unc,
        "price_unc": price_unc,
        "risk_unc": risk_unc,
        "horizon": horizon,
    }


def load_strategies(path: Path) -> List[Dict[str, object]]:
    entries = json.loads(path.read_text(encoding="utf-8"))
    strategies = []
    for entry in entries:
        decisions = [PurchaseDecision(**dec) for dec in entry["decisions"]]
        strategies.append(
            {
                "name": entry.get("name", "strategy"),
                "description": entry.get("description", ""),
                "decisions": decisions,
            }
        )
    return strategies


def run_strategy(
    name: str,
    description: str,
    decisions: Strategy,
    world_cfg: Dict[str, Dict[str, object]],
    rules: Dict[str, object],
) -> Dict[str, object]:
    state: WorldState = simulate_world(
        parts=world_cfg["parts"],
        vendors=world_cfg["vendors"],
        inventory=world_cfg["inventory"],
        demand_plans=world_cfg["demand_plans"],
        policy=rules["policy"],
        lead_time_unc=rules["lead_unc"],
        price_unc=rules["price_unc"],
        risk_unc=rules["risk_unc"],
        strategy=decisions,
        horizon_days=rules["horizon"],
    )
    score = score_world(state, rules["objectives"])
    return {
        "name": name,
        "description": description,
        "score": score,
        "state": {
            "spent_budget": state.spent_budget,
            "stockout_events": state.stockout_events,
            "accumulated_risk": state.accumulated_risk,
        },
        "deliveries_pending": [
            {
                "arrival_day": d.arrival_day,
                "part_id": d.part_id,
                "quantity": d.quantity,
                "vendor_name": d.vendor_name,
            }
            for d in state.deliveries
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate SCM strategies via world_model.")
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD, help="Path to world JSON.")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES, help="Path to rules JSON.")
    parser.add_argument("--strategies", type=Path, default=DEFAULT_STRATEGIES, help="Path to strategies JSON.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for report JSON.")
    args = parser.parse_args()

    world_cfg = load_world(args.world)
    rules = load_rules(args.rules)
    strategies = load_strategies(args.strategies)

    results = []
    for strategy in strategies:
        result = run_strategy(strategy["name"], strategy["description"], strategy["decisions"], world_cfg, rules)
        results.append(result)
        print(f"Strategy: {result['name']}")
        print(f"  Description: {result['description']}")
        print(f"  Overall score: {result['score']['overall_score']:.3f}")
        print(f"  Spent budget: {result['state']['spent_budget']:.1f}")
        print(f"  Stockout events: {result['state']['stockout_events']}")
        print(f"  Accumulated risk: {result['state']['accumulated_risk']:.3f}")
        print()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = args.output_dir / f"world_model_run_{timestamp}.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "world": str(args.world),
        "rules": str(args.rules),
        "strategies": str(args.strategies),
        "results": results,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Report saved to {output_path}")


if __name__ == "__main__":
    main()
