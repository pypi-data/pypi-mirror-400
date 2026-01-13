from typing import List, Dict, Any

from .t4racker import Step, Operation, OpType


class TrackReplayer:
    """Reconstructs state by replaying tracked steps."""

    def __init__(self, data: dict):
        self.snapshots = data.get("snapshots", [])
        self.steps = self._deserialize_steps(data["steps"])

    @staticmethod
    def from_json_file(filepath: str) -> 'TrackReplayer':
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        return TrackReplayer(data)

    def _deserialize_steps(self, steps_data: list) -> List[Step]:

        def deserialize_op(op_data: dict) -> Operation:
            if op_data is None:
                return None
            return Operation(
                op_type=OpType(op_data["op_type"]),
                value=op_data["value"]
            )

        def deserialize_step(step_data: dict) -> Step:
            return Step(
                path=tuple(step_data["path"]),
                forward=deserialize_op(step_data["forward"]),
                backward=deserialize_op(step_data["backward"])
            )

        return [deserialize_step(d) for d in steps_data]

    def _from_json(self, value):
        if isinstance(value, dict):
            # Check if this is a set representation
            if "__type__" in value and value["__type__"] == "set":
                # Convert back to set (exclude __type__ key)
                return {k for k in value.keys() if k != "__type__"}
            else:
                # Recursively convert dict values (keys stay as strings)
                return {k: self._from_json(v) for k, v in value.items()}
        elif isinstance(value, list):
            # Recursively convert list items
            return [self._from_json(v) for v in value]
        else:
            # Primitives pass through
            return value

    def _apply_step(self, state: Dict[str, Any], step: Step, reverse: bool = False):
        op = step.backward if reverse else step.forward
        if op is None:
            return  # noop

        # Navigate to parent container (state is just a dict, so uniform treatment)
        parent = state
        for key in step.path[:-1]:
            parent = parent[key]

        last_key = step.path[-1]

        # Apply operation to parent[last_key]
        if op.op_type == OpType.SET_ITEM:
            parent[last_key] = self._from_json(op.value)
        elif op.op_type == OpType.DEL_ITEM:
            if last_key in parent:
                # idempotent
                del parent[last_key]
        elif op.op_type == OpType.SET_ADD:
            parent[last_key].add(op.value)
        elif op.op_type == OpType.SET_REMOVE:
            parent[last_key].discard(op.value)
        elif op.op_type == OpType.LIST_APPEND:
            parent[last_key].append(op.value)
        elif op.op_type == OpType.LIST_POP:
            # Pop op.value items from the end (value is always an integer count)
            for _ in range(op.value):
                parent[last_key].pop()
        elif op.op_type == OpType.LIST_CLEAR:
            parent[last_key].clear()
        elif op.op_type == OpType.LIST_EXTEND:
            parent[last_key].extend(op.value)

    def state_at(self, step_index: int) -> Dict[str, Any]:
        """Reconstruct state at given step index."""
        import json

        # Find the latest snapshot at or before target step_index
        base_snapshot = None
        start_step_idx = 0

        for snapshot in self.snapshots:
            if snapshot["step_idx"] <= step_index:
                base_snapshot = snapshot
                start_step_idx = snapshot["step_idx"]
            else:
                break

        if base_snapshot is None:
            raise ValueError(
                f"No suitable snapshot found for step_index={step_index}. "
                f"At least one snapshot must be captured before replay. "
                f"Available snapshots: {len(self.snapshots)}"
            )
        
        # Deep copy snapshot state
        state = json.loads(json.dumps(base_snapshot["state"]))
        # Convert JSON representations back to proper Python types
        state = self._from_json(state)

        # Apply steps from snapshot to target
        for step in self.steps[start_step_idx:step_index + 1]:
            self._apply_step(state, step, reverse=False)

        return state

    def state_at_backward(self, step_index: int) -> Dict[str, Any]:
        """Reconstruct state by rewinding from final state."""
        import json

        # Find the latest snapshot (ideally at the end)
        if self.snapshots:
            latest_snapshot = self.snapshots[-1]
            state = json.loads(json.dumps(latest_snapshot["state"]))
            state = self._from_json(state)
            start_step_idx = latest_snapshot["step_idx"]

            # Apply remaining steps forward from snapshot to end
            for step in self.steps[start_step_idx:]:
                self._apply_step(state, step, reverse=False)
        else:
            # No snapshots - need to apply all steps forward first
            state = {}
            for step in self.steps:
                self._apply_step(state, step, reverse=False)

        # Now go backward from end to target step
        for step in reversed(self.steps[step_index + 1:]):
            self._apply_step(state, step, reverse=True)

        return state
