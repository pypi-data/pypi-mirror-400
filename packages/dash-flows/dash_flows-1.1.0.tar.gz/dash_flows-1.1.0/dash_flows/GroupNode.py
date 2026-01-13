# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class GroupNode(Component):
    """A GroupNode component.
GroupNode - Glass morphism styled container node that can hold other nodes
Child nodes should have parentId set to this node's ID

IMPORTANT: Group nodes should have zIndex set lower than child nodes
in the node definition to ensure proper layering.

Keyword arguments:

- data (dict; optional):
    Node data object containing label, icon, and styling options.

    `data` is a dict with keys:

    - label (boolean | number | string | dict | list; optional):
        Label content for the group - displayed above the group
        container.

    - icon (boolean | number | string | dict | list; optional):
        Icon element to display next to the label.

    - style (dict; optional):
        Custom CSS styles for the group container.

    - labelStyle (dict; optional):
        Custom CSS styles for the label element.

    - resizable (boolean; optional):
        Whether the group can be resized (default: True).

    - minWidth (number; optional):
        Minimum width constraint for resizing.

    - minHeight (number; optional):
        Minimum height constraint for resizing.

- selected (boolean; optional):
    Whether the group is currently selected."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_flows'
    _type = 'GroupNode'
    Data = TypedDict(
        "Data",
            {
            "label": NotRequired[typing.Any],
            "icon": NotRequired[typing.Any],
            "style": NotRequired[dict],
            "labelStyle": NotRequired[dict],
            "resizable": NotRequired[bool],
            "minWidth": NotRequired[NumberType],
            "minHeight": NotRequired[NumberType]
        }
    )


    def __init__(
        self,
        data: typing.Optional["Data"] = None,
        selected: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['data', 'selected']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['data', 'selected']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(GroupNode, self).__init__(**args)

setattr(GroupNode, "__init__", _explicitize_args(GroupNode.__init__))
