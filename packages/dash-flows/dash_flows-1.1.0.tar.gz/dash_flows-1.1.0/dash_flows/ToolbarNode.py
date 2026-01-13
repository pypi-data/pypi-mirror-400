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


class ToolbarNode(Component):
    """A ToolbarNode component.
ToolbarNode - Glass morphism styled node with a configurable toolbar

Keyword arguments:

- data (dict; required)

    `data` is a dict with keys:

    - label (boolean | number | string | dict | list; optional)

    - sublabel (string; optional)

    - toolbar (boolean | number | string | dict | list; optional)

    - toolbarVisible (boolean; optional)

    - toolbarPosition (a value equal to: 'top', 'bottom', 'left', 'right'; optional)

    - toolbarAlign (a value equal to: 'start', 'center', 'end'; optional)

    - toolbarOffset (number; optional)

    - toolbarStyle (dict; optional)

    - style (dict; optional)

    - handleStyle (dict; optional)

    - targetPosition (string; optional)

    - sourcePosition (string; optional)

    - showTargetHandle (boolean; optional)

    - showSourceHandle (boolean; optional)

- isConnectable (boolean; optional)

- selected (boolean; optional)"""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_flows'
    _type = 'ToolbarNode'
    Data = TypedDict(
        "Data",
            {
            "label": NotRequired[typing.Any],
            "sublabel": NotRequired[str],
            "toolbar": NotRequired[typing.Any],
            "toolbarVisible": NotRequired[bool],
            "toolbarPosition": NotRequired[Literal["top", "bottom", "left", "right"]],
            "toolbarAlign": NotRequired[Literal["start", "center", "end"]],
            "toolbarOffset": NotRequired[NumberType],
            "toolbarStyle": NotRequired[dict],
            "style": NotRequired[dict],
            "handleStyle": NotRequired[dict],
            "targetPosition": NotRequired[str],
            "sourcePosition": NotRequired[str],
            "showTargetHandle": NotRequired[bool],
            "showSourceHandle": NotRequired[bool]
        }
    )


    def __init__(
        self,
        data: typing.Optional["Data"] = None,
        selected: typing.Optional[bool] = None,
        isConnectable: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['data', 'isConnectable', 'selected']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['data', 'isConnectable', 'selected']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['data']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(ToolbarNode, self).__init__(**args)

setattr(ToolbarNode, "__init__", _explicitize_args(ToolbarNode.__init__))
