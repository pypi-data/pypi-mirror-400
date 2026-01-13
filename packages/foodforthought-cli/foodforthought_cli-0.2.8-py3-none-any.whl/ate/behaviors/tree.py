"""
Core Behavior Tree implementation.

A behavior tree is a directed acyclic graph that controls the execution flow
of robot behaviors. Each node returns one of three statuses:
- SUCCESS: The behavior completed successfully
- FAILURE: The behavior failed
- RUNNING: The behavior is still executing

Composite nodes:
- Sequence: Executes children in order, fails if any child fails
- Selector: Tries children in order, succeeds if any child succeeds
- Parallel: Runs children concurrently

Decorator nodes:
- Inverter: Inverts child result
- Repeater: Repeats child N times
- Succeeder: Always succeeds regardless of child

Leaf nodes:
- Action: Performs an action
- Condition: Checks a condition
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any, Dict
from enum import Enum, auto
import time


class BehaviorStatus(Enum):
    """Result of executing a behavior node."""
    SUCCESS = auto()   # Behavior completed successfully
    FAILURE = auto()   # Behavior failed
    RUNNING = auto()   # Behavior is still running


@dataclass
class Blackboard:
    """
    Shared data store for behavior tree nodes.

    Nodes can read/write data here to communicate.
    Example: Detection node writes target position, Navigation reads it.
    """
    data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def has(self, key: str) -> bool:
        return key in self.data

    def clear(self) -> None:
        self.data.clear()


class BehaviorNode(ABC):
    """Base class for all behavior tree nodes."""

    def __init__(self, name: str = ""):
        self.name = name or self.__class__.__name__
        self.status = BehaviorStatus.RUNNING
        self.blackboard: Optional[Blackboard] = None

    @abstractmethod
    def tick(self) -> BehaviorStatus:
        """
        Execute one tick of this node.

        Returns:
            BehaviorStatus indicating result
        """
        pass

    def reset(self) -> None:
        """Reset node state for re-execution."""
        self.status = BehaviorStatus.RUNNING

    def set_blackboard(self, blackboard: Blackboard) -> None:
        """Set the shared blackboard."""
        self.blackboard = blackboard


class Composite(BehaviorNode):
    """Base class for composite nodes with children."""

    def __init__(self, name: str = "", children: List[BehaviorNode] = None):
        super().__init__(name)
        self.children = children or []

    def add_child(self, child: BehaviorNode) -> "Composite":
        self.children.append(child)
        return self

    def set_blackboard(self, blackboard: Blackboard) -> None:
        super().set_blackboard(blackboard)
        for child in self.children:
            child.set_blackboard(blackboard)

    def reset(self) -> None:
        super().reset()
        for child in self.children:
            child.reset()


class Sequence(Composite):
    """
    Executes children in order.

    - Returns SUCCESS if all children succeed
    - Returns FAILURE if any child fails
    - Returns RUNNING if a child is running

    Use case: "stand up, THEN walk forward, THEN stop"
    """

    def __init__(self, name: str = "", children: List[BehaviorNode] = None):
        super().__init__(name, children)
        self.current_index = 0

    def tick(self) -> BehaviorStatus:
        while self.current_index < len(self.children):
            child = self.children[self.current_index]
            status = child.tick()

            if status == BehaviorStatus.FAILURE:
                self.current_index = 0
                return BehaviorStatus.FAILURE

            if status == BehaviorStatus.RUNNING:
                return BehaviorStatus.RUNNING

            # SUCCESS - move to next child
            self.current_index += 1

        self.current_index = 0
        return BehaviorStatus.SUCCESS

    def reset(self) -> None:
        super().reset()
        self.current_index = 0


class Selector(Composite):
    """
    Tries children in order until one succeeds.

    - Returns SUCCESS if any child succeeds
    - Returns FAILURE if all children fail
    - Returns RUNNING if a child is running

    Use case: "try picking with right hand, OR try left hand"
    """

    def __init__(self, name: str = "", children: List[BehaviorNode] = None):
        super().__init__(name, children)
        self.current_index = 0

    def tick(self) -> BehaviorStatus:
        while self.current_index < len(self.children):
            child = self.children[self.current_index]
            status = child.tick()

            if status == BehaviorStatus.SUCCESS:
                self.current_index = 0
                return BehaviorStatus.SUCCESS

            if status == BehaviorStatus.RUNNING:
                return BehaviorStatus.RUNNING

            # FAILURE - try next child
            self.current_index += 1

        self.current_index = 0
        return BehaviorStatus.FAILURE

    def reset(self) -> None:
        super().reset()
        self.current_index = 0


class Parallel(Composite):
    """
    Runs all children concurrently.

    Policy options:
    - "require_all": SUCCESS if all succeed, FAILURE if any fails
    - "require_one": SUCCESS if any succeeds, FAILURE if all fail

    Use case: "navigate AND detect obstacles simultaneously"
    """

    def __init__(
        self,
        name: str = "",
        children: List[BehaviorNode] = None,
        policy: str = "require_all"
    ):
        super().__init__(name, children)
        self.policy = policy

    def tick(self) -> BehaviorStatus:
        successes = 0
        failures = 0
        running = 0

        for child in self.children:
            status = child.tick()
            if status == BehaviorStatus.SUCCESS:
                successes += 1
            elif status == BehaviorStatus.FAILURE:
                failures += 1
            else:
                running += 1

        if self.policy == "require_all":
            if failures > 0:
                return BehaviorStatus.FAILURE
            if running > 0:
                return BehaviorStatus.RUNNING
            return BehaviorStatus.SUCCESS
        else:  # require_one
            if successes > 0:
                return BehaviorStatus.SUCCESS
            if running > 0:
                return BehaviorStatus.RUNNING
            return BehaviorStatus.FAILURE


class Decorator(BehaviorNode):
    """Base class for decorator nodes with a single child."""

    def __init__(self, child: BehaviorNode, name: str = ""):
        super().__init__(name)
        self.child = child

    def set_blackboard(self, blackboard: Blackboard) -> None:
        super().set_blackboard(blackboard)
        self.child.set_blackboard(blackboard)

    def reset(self) -> None:
        super().reset()
        self.child.reset()


class Inverter(Decorator):
    """
    Inverts the result of child node.

    - SUCCESS becomes FAILURE
    - FAILURE becomes SUCCESS
    - RUNNING stays RUNNING

    Use case: "is NOT battery low"
    """

    def tick(self) -> BehaviorStatus:
        status = self.child.tick()
        if status == BehaviorStatus.SUCCESS:
            return BehaviorStatus.FAILURE
        if status == BehaviorStatus.FAILURE:
            return BehaviorStatus.SUCCESS
        return BehaviorStatus.RUNNING


class Succeeder(Decorator):
    """
    Always returns SUCCESS.

    Use case: Optional actions that shouldn't fail the tree.
    """

    def tick(self) -> BehaviorStatus:
        self.child.tick()
        return BehaviorStatus.SUCCESS


class Repeater(Decorator):
    """
    Repeats child a specified number of times.

    Use case: "walk forward 5 steps"
    """

    def __init__(self, child: BehaviorNode, times: int = 1, name: str = ""):
        super().__init__(child, name)
        self.times = times
        self.count = 0

    def tick(self) -> BehaviorStatus:
        if self.count >= self.times:
            return BehaviorStatus.SUCCESS

        status = self.child.tick()
        if status == BehaviorStatus.RUNNING:
            return BehaviorStatus.RUNNING

        # Child completed (success or failure)
        self.count += 1
        self.child.reset()

        if self.count >= self.times:
            return BehaviorStatus.SUCCESS

        return BehaviorStatus.RUNNING

    def reset(self) -> None:
        super().reset()
        self.count = 0


class RepeatUntilFail(Decorator):
    """
    Repeats child until it fails.

    Use case: "keep picking up trash until none visible"
    """

    def tick(self) -> BehaviorStatus:
        status = self.child.tick()
        if status == BehaviorStatus.FAILURE:
            return BehaviorStatus.SUCCESS
        if status == BehaviorStatus.SUCCESS:
            self.child.reset()
            return BehaviorStatus.RUNNING
        return BehaviorStatus.RUNNING


class Action(BehaviorNode):
    """
    Leaf node that performs an action.

    Wraps a function that returns BehaviorStatus.
    """

    def __init__(
        self,
        action: Callable[[], BehaviorStatus],
        name: str = ""
    ):
        super().__init__(name)
        self.action = action

    def tick(self) -> BehaviorStatus:
        return self.action()


class Condition(BehaviorNode):
    """
    Leaf node that checks a condition.

    Returns SUCCESS if condition is true, FAILURE otherwise.
    Never returns RUNNING.
    """

    def __init__(
        self,
        condition: Callable[[], bool],
        name: str = ""
    ):
        super().__init__(name)
        self.condition = condition

    def tick(self) -> BehaviorStatus:
        if self.condition():
            return BehaviorStatus.SUCCESS
        return BehaviorStatus.FAILURE


class BehaviorTree:
    """
    A complete behavior tree with execution control.

    Provides:
    - Blackboard for shared data
    - Tick loop control
    - Visualization/debugging
    """

    def __init__(self, root: BehaviorNode, name: str = "BehaviorTree"):
        self.root = root
        self.name = name
        self.blackboard = Blackboard()
        self.root.set_blackboard(self.blackboard)
        self.tick_count = 0
        self.running = False

    def tick(self) -> BehaviorStatus:
        """Execute one tick of the tree."""
        self.tick_count += 1
        return self.root.tick()

    def reset(self) -> None:
        """Reset the tree for re-execution."""
        self.root.reset()
        self.tick_count = 0

    def run(
        self,
        tick_rate: float = 10.0,
        max_ticks: int = 0,
        on_tick: Optional[Callable[[int, BehaviorStatus], None]] = None
    ) -> BehaviorStatus:
        """
        Run the tree until completion.

        Args:
            tick_rate: Ticks per second
            max_ticks: Maximum ticks (0 = unlimited)
            on_tick: Callback after each tick

        Returns:
            Final status
        """
        self.running = True
        interval = 1.0 / tick_rate

        while self.running:
            start = time.time()
            status = self.tick()

            if on_tick:
                on_tick(self.tick_count, status)

            if status != BehaviorStatus.RUNNING:
                self.running = False
                return status

            if max_ticks > 0 and self.tick_count >= max_ticks:
                self.running = False
                return BehaviorStatus.FAILURE

            # Sleep to maintain tick rate
            elapsed = time.time() - start
            if elapsed < interval:
                time.sleep(interval - elapsed)

        return BehaviorStatus.FAILURE

    def stop(self) -> None:
        """Stop the tree execution."""
        self.running = False

    def get_blackboard(self) -> Blackboard:
        """Get the shared blackboard."""
        return self.blackboard

    def __repr__(self) -> str:
        return f"BehaviorTree(name='{self.name}', ticks={self.tick_count})"
