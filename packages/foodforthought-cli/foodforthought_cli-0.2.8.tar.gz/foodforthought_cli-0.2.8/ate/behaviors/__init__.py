"""
Behavior Tree framework for composing robot skills.

Behavior trees allow complex behaviors to be built from simple skills
using a tree structure of:
- Sequences (do A, then B, then C)
- Selectors (try A, if fails try B)
- Conditions (if X is true...)
- Actions (do X)

This is how we turn small demos into valuable composite behaviors.
"""

from .tree import (
    BehaviorNode,
    BehaviorStatus,
    Sequence,
    Selector,
    Parallel,
    Action,
    Condition,
    Inverter,
    Succeeder,
    Repeater,
    RepeatUntilFail,
    BehaviorTree,
)

from .common import (
    # Navigation
    NavigateToPoint,
    NavigateToPose,
    Patrol,
    ReturnHome,
    # Detection
    DetectObject,
    IsObjectVisible,
    FindNearest,
    ApproachObject,
    # Manipulation
    PickUp,
    PlaceAt,
    DropInBin,
    # Conditions
    IsBatteryLow,
    IsPathClear,
    HasObject,
    # Composite behaviors
    PatrolAndCleanup,
    SearchAndRetrieve,
)

__all__ = [
    # Core tree nodes
    "BehaviorNode",
    "BehaviorStatus",
    "Sequence",
    "Selector",
    "Parallel",
    "Action",
    "Condition",
    "Inverter",
    "Succeeder",
    "Repeater",
    "RepeatUntilFail",
    "BehaviorTree",
    # Navigation actions
    "NavigateToPoint",
    "NavigateToPose",
    "Patrol",
    "ReturnHome",
    # Detection actions
    "DetectObject",
    "IsObjectVisible",
    "FindNearest",
    "ApproachObject",
    # Manipulation actions
    "PickUp",
    "PlaceAt",
    "DropInBin",
    # Conditions
    "IsBatteryLow",
    "IsPathClear",
    "HasObject",
    # Composite behaviors
    "PatrolAndCleanup",
    "SearchAndRetrieve",
]
