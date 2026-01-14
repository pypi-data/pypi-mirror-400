from typing import Annotated, Any, Optional, Tuple, Union, get_args, get_origin

from bpkio_api.models.common import BaseResource
from pydantic import BaseModel


def _fuzzy_search_through_properties(
    o: BaseModel, key: str, original_property_key: Optional[str] = None
) -> Tuple[str, Any]:
    """Helper function to perform fuzzy search through properties of a Pydantic model.

    Args:
        o: The Pydantic model to search in
        key: The property key to search for
        original_property_key: The original full property path (for error messages)

    Returns:
        Tuple of (matching_key, property_type)
    """
    model_properties = o.__class__.model_fields
    # fuzzy search through the keys
    search_term = key.lower()
    matching_keys = [k for k in model_properties.keys() if search_term in k.lower()]

    if not len(matching_keys):
        error_key = original_property_key or key
        raise KeyError(f"Property '{error_key}' not found")
    if len(matching_keys) > 1:
        error_key = original_property_key or key
        raise KeyError(
            f"Ambiguous property '{error_key}': matches {', '.join(matching_keys)}"
        )
    fld = model_properties[matching_keys[0]]
    runtime_type = _resolve_runtime_type(fld.annotation)
    return matching_keys[0], runtime_type


def get_property(resource: BaseModel, property_key: str):
    """A function that allows retrieving the value of a single property in a pydantic object, possibly nested.
    Dot notation can be used to define the path to the property.

    Special features:
    - Fuzzy matching applies to the property names.
    - If the property is a BaseResource, we return the resource object.

    Args:
        resource: The Pydantic model to search in
        property_key: The property key to search for, can use dot notation for nested properties

    Returns:
        Tuple of (value, json_path) where:
        - value: The value of the property
        - json_path: The JSON path to the property (dot-separated string)

    Raises:
        KeyError: If the property is not found or is ambiguous
    """
    # traverse the model to the property to retrieve
    keys = property_key.split(".")
    o = resource
    property_path = []

    # Navigate through nested objects
    for key in keys[:-1]:
        matching_key, model_type = _fuzzy_search_through_properties(
            o, key, property_key
        )
        property_path.append(matching_key)

        if not issubclass(model_type, BaseModel):
            raise KeyError(
                f"Cannot navigate through property '{'.'.join(property_path)}' (not a Pydantic object)"
            )

        o = getattr(o, matching_key)

        if o is None:
            json_path = ".".join(property_path)
            return (
                None,
                json_path,
            )  # Return None if we encounter a null object in the path

    # retrieve the leaf property
    matching_key, _ = _fuzzy_search_through_properties(o, keys[-1], property_key)
    property_path.append(matching_key)

    # Get the value
    value = getattr(o, matching_key, None)
    json_path = ".".join(property_path)
    return value, json_path


def edit_property(resource: BaseModel, property_key: str, value: object):
    """A function that allows changing the value of a single property in a pydantic object, possibly nested.
    Dot notation can be used to define the path to the property.

    Special features:
    - Fuzzy matching applies to the property names.
    - If the property is inside a nested object that does not exist, we attempt to create it.
    - If the property is a BaseResource, we assume the value is the ID of the resource to link to.
    """
    previous_value = None
    anchor_property_for_new_model = None
    new_model_flag = False
    output_message = ""

    # traverse the model to the property to modify
    keys = property_key.split(".")
    o = resource
    traversed_models = [resource]
    property_path = []
    for i, key in enumerate(keys[:-1]):
        traversed_models.append(o)
        matching_key, model_type = _fuzzy_search_through_properties(
            o, key, property_key
        )
        property_path.append(matching_key)
        o = getattr(o, matching_key)

        if not issubclass(model_type, BaseModel):
            raise KeyError(
                f"Property '{property_key}' cannot be updated (not a Pydantic object)"
            )

        # Create model for null properties that should contain models
        if o is None:
            new_model_flag = True
            anchor_property_for_new_model = traversed_models[-1]

            new_model_data_root = {}
            new_model_data_next_level = new_model_data_root
            new_model_construct = model_type.model_construct()
            # we loop through the remaining keys to build the skeleton of the subobjects
            for k in keys[i + 1 :]:
                sub_k, sub_type = _fuzzy_search_through_properties(
                    new_model_construct, k, property_key
                )
                if issubclass(sub_type, BaseModel):
                    new_model_data_next_level[sub_k] = {}
                    # and in case it's the last key, but it's a BaseResource, we assume the value is the ID
                    if (
                        k == keys[-1]
                        and issubclass(sub_type, BaseResource)
                        and value != "__NULL__"
                    ):
                        new_model_data_next_level[sub_k] = {"id": int(value)}

                    new_model_construct = sub_type.model_construct()
                    new_model_data_next_level = new_model_data_next_level[sub_k]
                else:
                    new_model_data_next_level[sub_k] = sub_type(value)

            # Then we attempt to build it and add it
            o = model_type.model_validate(new_model_data_root)
            setattr(anchor_property_for_new_model, property_path[-1], o)

    # retrieve the leaf property
    matching_key, property_type = _fuzzy_search_through_properties(
        o, keys[-1], property_key
    )
    property_path.append(matching_key)

    # special situation: if property is a nested object with id, attempt to use the value as id
    if issubclass(property_type, BaseResource):
        parent = o
        o = getattr(o, matching_key, None)
        # if it doesn't exist, we create it
        if o is None:
            o = property_type(id=int(value))
            setattr(parent, property_path[-1], o)

        matching_key = "id"
        property_path.append("id")
        property_type = int

    previous_value = getattr(o, matching_key, None) if not new_model_flag else "(empty)"

    if value == "__NULL__" or value == "null" or value == "None":
        setattr(o, matching_key, None)
        output_message = f"Removed {'.'.join(property_path)} (set to null)"
    else:
        # Cast the value to the appropriate type
        try:
            if issubclass(property_type, BaseModel):
                value = property_type.model_validate(value)
            elif property_type is list and isinstance(value, str):
                # Split comma-separated strings before casting to list
                value = [item.strip() for item in value.split(",") if item.strip()]
            else:
                value = property_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot cast value '{value}' to type {property_type}: {e}"
            )

        # modify the property
        # if not o and isinstance(o, BaseModel):
        setattr(o, matching_key, value)
        output_message = f"Updated property '{'.'.join(property_path)}' to {value}"

    return resource, output_message, previous_value


# --- Pydantic helpers ---


def _unwrap_annotated(tp):
    if get_origin(tp) is Annotated:
        return get_args(tp)[0]
    return tp


def _unwrap_optional_union(tp):
    if get_origin(tp) is Union:
        args = [a for a in get_args(tp) if a is not type(None)]
        if len(args) == 1:
            return args[0]
    return tp


def _resolve_runtime_type(annotation):
    """Return a concrete runtime type suitable for issubclass checks.

    - Unwrap Annotated and Optional/Union[None]
    - For collections like List[T], Set[T], Tuple[T,...], Dict[K, V], return the
      collection origin (list/set/tuple/dict) rather than inner type so that
      navigation is not attempted through collections.
    - For non-generic annotations, return the annotation itself (e.g., BaseModel subclass, int, str, etc.).
    """
    tp = _unwrap_optional_union(_unwrap_annotated(annotation))
    origin = get_origin(tp)
    if origin in (list, set, tuple, dict):
        return origin
    return tp
