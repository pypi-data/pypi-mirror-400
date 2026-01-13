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


class AnimatedSvgEdge(Component):
    """An AnimatedSvgEdge component.
AnimatedSvgEdge - An edge that animates a custom SVG element along the path
Useful for showing data flow direction or active connections

Keyword arguments:

- id (string; required)

- data (dict; optional)

    `data` is a dict with keys:

    - duration (number; optional):
        Animation duration in seconds.

    - shape (a value equal to: 'circle', 'rect', 'arrow', 'pulse'; optional):
        Shape to animate: 'circle', 'rect', 'arrow', 'pulse'.

    - size (number; optional):
        Size of the animated shape.

    - color (string; optional):
        Color of the animated shape.

    - count (number; optional):
        Number of shapes to animate along the path.

    - reverse (boolean; optional):
        Reverse the animation direction.

- markerEnd (boolean | number | string | dict | list; optional)

- markerStart (boolean | number | string | dict | list; optional)

- selected (boolean; optional)

- sourcePosition (string; optional)

- sourceX (number; required)

- sourceY (number; required)

- targetPosition (string; optional)

- targetX (number; required)

- targetY (number; required)"""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_flows'
    _type = 'AnimatedSvgEdge'
    Data = TypedDict(
        "Data",
            {
            "duration": NotRequired[NumberType],
            "shape": NotRequired[Literal["circle", "rect", "arrow", "pulse"]],
            "size": NotRequired[NumberType],
            "color": NotRequired[str],
            "count": NotRequired[NumberType],
            "reverse": NotRequired[bool]
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
        style: typing.Optional[typing.Any] = None,
        markerEnd: typing.Optional[typing.Any] = None,
        markerStart: typing.Optional[typing.Any] = None,
        selected: typing.Optional[bool] = None,
        data: typing.Optional["Data"] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'data', 'markerEnd', 'markerStart', 'selected', 'sourcePosition', 'sourceX', 'sourceY', 'style', 'targetPosition', 'targetX', 'targetY']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'data', 'markerEnd', 'markerStart', 'selected', 'sourcePosition', 'sourceX', 'sourceY', 'style', 'targetPosition', 'targetX', 'targetY']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['id', 'sourceX', 'sourceY', 'targetX', 'targetY']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(AnimatedSvgEdge, self).__init__(**args)

setattr(AnimatedSvgEdge, "__init__", _explicitize_args(AnimatedSvgEdge.__init__))
