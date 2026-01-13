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


class StraightEdge(Component):
    """A StraightEdge component.
StraightEdge - Glass morphism styled straight line edge

Keyword arguments:

- id (string; required)

- data (dict; optional)

- label (boolean | number | string | dict | list; optional)

- labelStyle (dict; optional)

- markerEnd (boolean | number | string | dict | list; optional)

- markerStart (boolean | number | string | dict | list; optional)

- selected (boolean; optional)

- sourceX (number; required)

- sourceY (number; required)

- targetX (number; required)

- targetY (number; required)"""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_flows'
    _type = 'StraightEdge'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        sourceX: typing.Optional[NumberType] = None,
        sourceY: typing.Optional[NumberType] = None,
        targetX: typing.Optional[NumberType] = None,
        targetY: typing.Optional[NumberType] = None,
        label: typing.Optional[typing.Any] = None,
        labelStyle: typing.Optional[dict] = None,
        style: typing.Optional[typing.Any] = None,
        markerEnd: typing.Optional[typing.Any] = None,
        markerStart: typing.Optional[typing.Any] = None,
        data: typing.Optional[dict] = None,
        selected: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'data', 'label', 'labelStyle', 'markerEnd', 'markerStart', 'selected', 'sourceX', 'sourceY', 'style', 'targetX', 'targetY']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'data', 'label', 'labelStyle', 'markerEnd', 'markerStart', 'selected', 'sourceX', 'sourceY', 'style', 'targetX', 'targetY']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['id', 'sourceX', 'sourceY', 'targetX', 'targetY']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(StraightEdge, self).__init__(**args)

setattr(StraightEdge, "__init__", _explicitize_args(StraightEdge.__init__))
