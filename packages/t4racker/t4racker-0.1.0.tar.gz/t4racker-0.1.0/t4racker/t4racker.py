from dataclasses import dataclass, is_dataclass, fields
from enum import Enum
from typing import Any, Dict, List, Tuple


# --- JSON Serialization ---
def is_primitive_type(value):
    """Check if value is a JSON primitive."""
    return value is None or isinstance(value, (str, int, float, bool))


def _invalid_key_error(key):
    return TypeError(f"No key converter registered for type {type(key).__name__}")


class OpType(Enum):
    SET_ITEM = "set_item"
    DEL_ITEM = "del_item"
    SET_ADD = "set_add"
    SET_REMOVE = "set_remove"
    LIST_APPEND = "list_append"
    LIST_POP = "list_pop"
    LIST_CLEAR = "list_clear"
    LIST_EXTEND = "list_extend"


@dataclass
class Operation:
    """Atomic state change."""
    op_type: OpType
    value: Any = None


@dataclass
class Step:
    """Mutation with forward/backward operations."""
    path: Tuple[Any, ...]
    forward: Operation
    backward: Operation = None


@dataclass
class Snapshot:
    """State checkpoint."""
    name: str
    step_idx: int
    state: Dict[str, Any]


class TTTTracker:
    """Records mutations on Python objects for time-travel replay."""

    def __init__(self):
        self.steps: List[Step] = []  # Flat list of steps
        self.snapshots: List[Snapshot] = []  # Captured states
        self._root_obj = None  # Root object being tracked
        self._key_converters = {
            # identity
            str: str,
            int: str,
        }

    def register_key_converters(self, key_converters: dict):
        self._key_converters.update(key_converters)

    def _get_key(self, value):
        """Convert value to dict key string via registered converters."""
        # Prefer exact-type converters to avoid bool -> int ambiguity.
        value_type = type(value)
        converter = self._key_converters.get(value_type)
        if converter is not None:
            result = converter(value)
            if not isinstance(result, str):
                raise TypeError(
                    f"Key converter for type {value_type.__name__} returned {type(result).__name__}, expected str"
                )
            return result

        # bool is a subclass of int, so without an explicit bool converter we reject it.
        if isinstance(value, bool):
            raise _invalid_key_error(value)

        for key_type, converter in self._key_converters.items():
            if isinstance(value, key_type):
                result = converter(value)
                if not isinstance(result, str):
                    raise TypeError(
                        f"Key converter for type {key_type.__name__} returned {type(result).__name__}, expected str"
                    )
                return result

        raise _invalid_key_error(value)

    def to_json(self, value):
        """Convert Python value to JSON-serializable form."""
        if is_primitive_type(value):
            return value
        elif isinstance(value, set):
            # Represent set as dict with type marker and boolean values
            result = {"__type__": "set"}
            for item in value:
                # Set items become dict keys - use _get_key for conversion
                key = self._get_key(item)
                result[key] = True
            return result
        elif isinstance(value, (list, tuple)):
            return [self.to_json(v) for v in value]
        elif isinstance(value, dict):
            result = {}
            for k, v in value.items():
                # Dict keys - use _get_key for conversion
                key = self._get_key(k)
                result[key] = self.to_json(v)
            return result
        elif is_dataclass(value):
            # Handle dataclasses (including frozen ones)
            # Don't use asdict() as it tries to reconstruct tracked containers incorrectly
            result = {}
            for field in fields(value):
                field_value = getattr(value, field.name)
                result[field.name] = self.to_json(field_value)
            return result
        elif hasattr(value, '__dict__'):
            # Plain Python object - use __dict__
            # Filter out private/internal attributes
            return {k: self.to_json(v) for k, v in value.__dict__.items()
                    if not k.startswith('_')}
        else:
            # Unsupported type - fail explicitly
            raise TypeError(f"Serialization of type '{type(value).__name__}' is not supported")

    def track(self, obj, tracked_fields):
        """Start tracking an object."""
        self.track_instance(obj, tracked_fields=tracked_fields)
        self._root_obj = obj
        return obj

    def capture_snapshot(self, name: str):
        """Capture current state."""
        if self._root_obj is None:
            raise ValueError("No object is being tracked")

        tracked_fields = self._root_obj._tracked_fields_filter

        state = {}
        for field in tracked_fields:
            if hasattr(self._root_obj, field):
                value = getattr(self._root_obj, field)
                state[field] = self.to_json(value)

        snapshot = Snapshot(
            name=name,
            step_idx=len(self.steps),
            state=state
        )
        self.snapshots.append(snapshot)
        return snapshot

    def _record_step(self, step: Step):
        self.steps.append(step)

    def _wrap_value(self, value, path: Tuple):
        if callable(value):
            raise ValueError("Cannot track a callable object")
        if isinstance(value, dict) and not isinstance(value, TrackedDict):
            return TrackedDict(value, self, path)
        elif isinstance(value, set) and not isinstance(value, TrackedSet):
            return TrackedSet(value, self, path)
        elif isinstance(value, list) and not isinstance(value, TrackedList):
            return TrackedList(value, self, path)
        elif hasattr(value, '__dict__'):
            # User-defined struct - track with path prefix
            self.track_instance(value, path)
            return value
        return value

    def track_instance(self, obj, path_prefix: Tuple[str, ...] = (), tracked_fields=None):
        """Apply tracking to an instance via dynamic subclassing."""
        tracker = self
        original_class = type(obj)

        # Check if already tracked
        if hasattr(original_class, '_is_tracked'):
            return obj

        # Convert to set if provided, or compute all fields
        if tracked_fields is not None:
            tracked_fields = set(tracked_fields)
        else:
            tracked_fields = {a for a in dir(obj) if not a.startswith('_') and not callable(getattr(obj, a, None))}

        # Create a new tracking class that inherits from the original
        class TrackedInstanceClass(original_class):
            _is_tracked = True
            _tracker = tracker
            _path_prefix = path_prefix
            _tracked_fields_filter = tracked_fields

            def __setattr__(self, name, value):
                # Only track specified fields
                if name not in self._tracked_fields_filter:
                    super().__setattr__(name, value)
                    return

                # Get old value
                try:
                    old_value = object.__getattribute__(self, name)
                except AttributeError:
                    old_value = None

                # Wrap containers/structs
                wrapped_value = self._tracker._wrap_value(value, self._path_prefix + (name,))

                # Record step
                self._tracker._record_step(Step(
                    path=self._path_prefix + (name,),
                    forward=Operation(OpType.SET_ITEM, self._tracker.to_json(value)),
                    backward=Operation(OpType.SET_ITEM, self._tracker.to_json(old_value))
                ))

                # Set the value using parent's setattr
                super().__setattr__(name, wrapped_value)

        # TrackedInstanceClass.__name__ = original_class.__name__
        # TrackedInstanceClass.__qualname__ = original_class.__qualname__
        TrackedInstanceClass.__name__ = f"Tracked[{original_class.__name__}]"
        TrackedInstanceClass.__qualname__ = f"Tracked[{original_class.__qualname__}]"

        # Try to change the instance's class
        # If this fails, the object is immutable (frozen dataclass, namedtuple, etc.)
        # and we treat it as a primitive value
        try:
            obj.__class__ = TrackedInstanceClass
        except AttributeError:
            # Object is immutable (frozen dataclass, etc.), treat as primitive
            return obj
        except TypeError as e:
            # Unexpected: built-in immutable type with __dict__ (shouldn't normally happen)
            import warnings
            warnings.warn(
                f"Cannot track {type(obj).__name__}: {e}. Treating as primitive.",
                UserWarning,
                stacklevel=2
            )
            return obj

        for attr_name in tracked_fields:
            try:
                attr_value = getattr(obj, attr_name)
            except AttributeError:
                # Field doesn't exist, skip it
                continue
            wrapped = tracker._wrap_value(attr_value, path_prefix + (attr_name,))
            if wrapped is not attr_value:  # Only set if wrapping occurred
                object.__setattr__(obj, attr_name, wrapped)

        return obj

    def to_dict(self) -> dict:
        """Export to JSON-serializable dict."""

        def serialize_op(op: Operation) -> dict:
            if op is None:
                return None
            return {
                "op_type": op.op_type.value,
                "value": op.value
            }

        def serialize_step(step: Step) -> dict:
            # Convert path elements to JSON-serializable format
            path_serialized = []
            for elem in step.path:
                if is_primitive_type(elem):
                    path_serialized.append(elem)
                else:
                    # TODO: Consider checking for provided custom serializers.
                    # TODO: Consider fail-fast checks upstream to make this case be impossible.
                    raise TypeError(f"Non-primitive path element type {type(elem).__name__} is not supported")

            return {
                "path": path_serialized,
                "forward": serialize_op(step.forward),
                "backward": serialize_op(step.backward)
            }

        def serialize_snapshot(snapshot: Snapshot) -> dict:
            return {
                "name": snapshot.name,
                "step_idx": snapshot.step_idx,
                "state": snapshot.state
            }

        return {
            "snapshots": [serialize_snapshot(s) for s in self.snapshots],
            "steps": [serialize_step(d) for d in self.steps]
        }


# --- Tracked Containers ---
class TrackedDict(dict):
    def __init__(self, data, tracker, path):
        super().__init__()
        self._tracker = tracker
        self._path = path

        # Wrap existing values
        for key, value in data.items():
            # Convert key using registered converters (validates and converts)
            key_str = self._tracker._get_key(key)
            wrapped_value = self._tracker._wrap_value(value, self._path + (key_str,))
            super().__setitem__(key, wrapped_value)

    def __setitem__(self, key, value):
        # Convert key using registered converters (validates and converts)
        key_str = self._tracker._get_key(key)
        wrapped_value = self._tracker._wrap_value(value, self._path + (key_str,))

        # Check if key exists (not just if value is not None)
        key_existed = key in self
        old_value = self[key] if key_existed else None
        super().__setitem__(key, wrapped_value)

        self._tracker._record_step(Step(
            path=self._path + (key_str,),
            forward=Operation(OpType.SET_ITEM, self._tracker.to_json(value)),
            backward=Operation(OpType.SET_ITEM, self._tracker.to_json(old_value)) if key_existed else Operation(
                OpType.DEL_ITEM)
        ))

    def __delitem__(self, key):
        # Convert key using registered converters (validates and converts)
        key_str = self._tracker._get_key(key)

        old_value = self.get(key)
        super().__delitem__(key)
        self._tracker._record_step(Step(
            path=self._path + (key_str,),
            forward=Operation(OpType.DEL_ITEM),
            backward=Operation(OpType.SET_ITEM, self._tracker.to_json(old_value))
        ))


# TrackedDict.__name__ = 'dict'
# TrackedDict.__qualname__ = 'dict'
TrackedDict.__name__ = 'Tracked[dict]'
TrackedDict.__qualname__ = 'Tracked[dict]'


class TrackedSet(set):
    def __init__(self, data, tracker: TTTTracker, path):
        # Validate all items by converting them (will raise if no converter registered)
        for item in data:
            tracker._get_key(item)
        super().__init__(data)
        self._tracker = tracker
        self._path = path

    def add(self, value):
        # Convert value to key representation (validates and converts)
        value_key = self._tracker._get_key(value)

        was_present = value in self
        super().add(value)

        # Only create backward op if value wasn't already present
        # Use key representation for set items (must be hashable/string)
        backward_op = None if was_present else Operation(OpType.SET_REMOVE, value_key)

        self._tracker._record_step(Step(
            path=self._path,
            forward=Operation(OpType.SET_ADD, value_key),
            backward=backward_op
        ))

    def remove(self, value):
        # Convert value to key representation (validates and converts)
        value_key = self._tracker._get_key(value)

        super().remove(value)
        self._tracker._record_step(Step(
            path=self._path,
            forward=Operation(OpType.SET_REMOVE, value_key),
            backward=Operation(OpType.SET_ADD, value_key)
        ))

    def discard(self, value):
        # Convert value to key representation (validates and converts)
        value_key = self._tracker._get_key(value)

        was_present = value in self
        super().discard(value)

        if was_present:
            self._tracker._record_step(Step(
                path=self._path,
                forward=Operation(OpType.SET_REMOVE, value_key),
                backward=Operation(OpType.SET_ADD, value_key)
            ))


# TrackedSet.__name__ = 'set'
# TrackedSet.__qualname__ = 'set'
TrackedSet.__name__ = 'Tracked[set]'
TrackedSet.__qualname__ = 'Tracked[set]'


class TrackedList(list):
    def __init__(self, data, tracker, path):
        super().__init__()
        self._tracker = tracker
        self._path = path

        # Wrap existing values
        for i, value in enumerate(data):
            wrapped_value = self._tracker._wrap_value(value, self._path + (i,))
            super().append(wrapped_value)

    def append(self, value):
        wrapped_value = self._tracker._wrap_value(value, self._path + (len(self),))
        super().append(wrapped_value)
        self._tracker._record_step(Step(
            path=self._path,
            forward=Operation(OpType.LIST_APPEND, self._tracker.to_json(value)),
            backward=Operation(OpType.LIST_POP, 1)  # Pop 1 item
        ))

    def pop(self, index=-1):
        popped_value = self[index]
        result = super().pop(index)

        self._tracker._record_step(Step(
            path=self._path,
            forward=Operation(OpType.LIST_POP, 1),  # Always pop 1 item
            backward=Operation(OpType.LIST_APPEND, self._tracker.to_json(popped_value))
        ))
        return result

    def __setitem__(self, index, value):
        old_value = self[index]
        wrapped_value = self._tracker._wrap_value(value, self._path + (index,))
        super().__setitem__(index, wrapped_value)
        self._tracker._record_step(Step(
            path=self._path + (index,),
            forward=Operation(OpType.SET_ITEM, self._tracker.to_json(value)),
            backward=Operation(OpType.SET_ITEM, self._tracker.to_json(old_value))
        ))

    def clear(self):
        # Save old contents for backward operation (restore with extend)
        old_contents = [self._tracker.to_json(item) for item in self]
        old_len = len(self)
        super().clear()

        # Forward: clear, Backward: extend with old contents
        self._tracker._record_step(Step(
            path=self._path,
            forward=Operation(OpType.LIST_CLEAR),
            backward=Operation(OpType.LIST_EXTEND, old_contents) if old_len > 0 else None
        ))

    def extend(self, iterable):
        # Convert iterable to list to get length
        items = list(iterable)
        items_count = len(items)

        # Wrap and extend
        start_index = len(self)
        for i, value in enumerate(items):
            wrapped_value = self._tracker._wrap_value(value, self._path + (start_index + i,))
            super().append(wrapped_value)

        # Forward: extend with items, Backward: pop the added items
        items_json = [self._tracker.to_json(item) for item in items]
        self._tracker._record_step(Step(
            path=self._path,
            forward=Operation(OpType.LIST_EXTEND, items_json),
            backward=Operation(OpType.LIST_POP, items_count) if items_count > 0 else None
        ))


# TrackedList.__name__ = 'list'
# TrackedList.__qualname__ = 'list'
TrackedList.__name__ = 'Tracked[list]'
TrackedList.__qualname__ = 'Tracked[list]'
