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


class DashSplitLayout(Component):
    """A DashSplitLayout component.
DashSplitLayout is a component that provides a simple split panel system.
Panels are arranged either horizontally or vertically with resizable dividers.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- id (string; required)

- height (string; optional)

- layout (dict; optional)

- loading_state (dict; optional)

    `loading_state` is a dict with keys:

    - is_loading (boolean; optional)

    - prop_name (string; optional)

    - component_name (string; optional)

- orientation (a value equal to: 'horizontal', 'vertical'; optional)

- panelCount (number; optional)

- panels (list of dicts; optional)

    `panels` is a list of dicts with keys:

    - id (string; required)

    - size (number; optional)

    - minimumSize (number; optional)

    - maximumSize (number; optional)

- proportionalLayout (boolean; optional)

- savedLayout (dict; optional)

- theme (string; optional)"""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_dock_view'
    _type = 'DashSplitLayout'
    Panels = TypedDict(
        "Panels",
            {
            "id": str,
            "size": NotRequired[NumberType],
            "minimumSize": NotRequired[NumberType],
            "maximumSize": NotRequired[NumberType]
        }
    )

    LoadingState = TypedDict(
        "LoadingState",
            {
            "is_loading": NotRequired[bool],
            "prop_name": NotRequired[str],
            "component_name": NotRequired[str]
        }
    )


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        panels: typing.Optional[typing.Sequence["Panels"]] = None,
        layout: typing.Optional[dict] = None,
        savedLayout: typing.Optional[dict] = None,
        theme: typing.Optional[str] = None,
        height: typing.Optional[str] = None,
        orientation: typing.Optional[Literal["horizontal", "vertical"]] = None,
        proportionalLayout: typing.Optional[bool] = None,
        panelCount: typing.Optional[NumberType] = None,
        loading_state: typing.Optional["LoadingState"] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'height', 'layout', 'loading_state', 'orientation', 'panelCount', 'panels', 'proportionalLayout', 'savedLayout', 'theme']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'height', 'layout', 'loading_state', 'orientation', 'panelCount', 'panels', 'proportionalLayout', 'savedLayout', 'theme']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DashSplitLayout, self).__init__(children=children, **args)

setattr(DashSplitLayout, "__init__", _explicitize_args(DashSplitLayout.__init__))
