# File: src/iotopen_bridge/converters/mapping/state_rules.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..normalize.bool import to_bool
from ..normalize.number import to_float, to_int


@dataclass(frozen=True)
class StateRules:
    """Rules for translating raw values to HA boolean (on/off).

    Strategy:
      1) bool-ish parse
      2) compare vs configured state_on/state_off
      3) compare numerics if possible
      4) optional inversion
    """

    state_on: Any = 1
    state_off: Any = 0
    invert: bool = False


def apply_rules(value: Any, rules: StateRules) -> bool | None:
    b = to_bool(value)
    if b is None:
        # direct comparison
        if value == rules.state_on:
            b = True
        elif value == rules.state_off:
            b = False
        else:
            # numeric comparison
            vi = to_int(value)
            if vi is not None:
                if vi == to_int(rules.state_on):
                    b = True
                elif vi == to_int(rules.state_off):
                    b = False
            else:
                vf = to_float(value)
                if vf is not None:
                    so = to_float(rules.state_on)
                    sf = to_float(rules.state_off)
                    if so is not None and vf == so:
                        b = True
                    elif sf is not None and vf == sf:
                        b = False

    if b is None:
        return None
    return (not b) if rules.invert else b
