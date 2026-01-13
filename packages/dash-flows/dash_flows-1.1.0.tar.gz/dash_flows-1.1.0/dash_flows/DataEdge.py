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


class DataEdge(Component):
    """A DataEdge component.
DataEdge - An edge that displays data from the source node
Useful for showing data flow between nodes

Keyword arguments:

- id (string; required)

- data (dict; optional)

    `data` is a dict with keys:

    - key (string; required):
        Key to read from source node's data.

    - prefix (string; optional):
        Prefix to display before the value.

    - suffix (string; optional):
        Suffix to display after the value.

    - labelStyle (dict; optional):
        Custom label styles.

- markerEnd (boolean | number | string | dict | list; optional)

- markerStart (boolean | number | string | dict | list; optional)

- selected (boolean; optional)

- source (string; required)

- sourcePosition (string; optional)

- sourceX (number; required)

- sourceY (number; required)

- targetPosition (string; optional)

- targetX (number; required)

- targetY (number; required)"""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_flows'
    _type = 'DataEdge'
    Data = TypedDict(
        "Data",
            {
            "key": str,
            "prefix": NotRequired[str],
            "suffix": NotRequired[str],
            "labelStyle": NotRequired[dict]
        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        sourceX: typing.Optional[NumberType] = None,
        sourceY: typing.Optional[NumberType] = None,
        targetX: typing.Optional[NumberType] = None,
        targetY: typing.Optional[NumberType] = None,
        sourcePosition: typing.Optional[str] = None,
        targetPosition: typing.Optional[str] = None,
        source: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        markerEnd: typing.Optional[typing.Any] = None,
        markerStart: typing.Optional[typing.Any] = None,
        selected: typing.Optional[bool] = None,
        data: typing.Optional["Data"] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'data', 'markerEnd', 'markerStart', 'selected', 'source', 'sourcePosition', 'sourceX', 'sourceY', 'style', 'targetPosition', 'targetX', 'targetY']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'data', 'markerEnd', 'markerStart', 'selected', 'source', 'sourcePosition', 'sourceX', 'sourceY', 'style', 'targetPosition', 'targetX', 'targetY']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['id', 'source', 'sourceX', 'sourceY', 'targetX', 'targetY']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DataEdge, self).__init__(**args)

setattr(DataEdge, "__init__", _explicitize_args(DataEdge.__init__))
