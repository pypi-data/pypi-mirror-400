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


class DashGridLayout(Component):
    """A DashGridLayout component.
DashGridLayout is a component that provides a grid-based resizable panel system.
Panels can be arranged in rows and columns with adjustable proportions.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- id (string; required)

- activePanel (string; optional)

- height (string; optional)

- hideBorders (boolean; optional)

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

    - minimumWidth (number; optional)

    - maximumWidth (number; optional)

    - minimumHeight (number; optional)

    - maximumHeight (number; optional)

- proportionalLayout (boolean; optional)

- savedLayout (dict; optional)

- theme (string; optional)"""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_dock_view'
    _type = 'DashGridLayout'
    Panels = TypedDict(
        "Panels",
            {
            "id": str,
            "size": NotRequired[NumberType],
            "minimumWidth": NotRequired[NumberType],
            "maximumWidth": NotRequired[NumberType],
            "minimumHeight": NotRequired[NumberType],
            "maximumHeight": NotRequired[NumberType]
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
        activePanel: typing.Optional[str] = None,
        layout: typing.Optional[dict] = None,
        savedLayout: typing.Optional[dict] = None,
        theme: typing.Optional[str] = None,
        height: typing.Optional[str] = None,
        orientation: typing.Optional[Literal["horizontal", "vertical"]] = None,
        proportionalLayout: typing.Optional[bool] = None,
        hideBorders: typing.Optional[bool] = None,
        panelCount: typing.Optional[NumberType] = None,
        loading_state: typing.Optional["LoadingState"] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'activePanel', 'height', 'hideBorders', 'layout', 'loading_state', 'orientation', 'panelCount', 'panels', 'proportionalLayout', 'savedLayout', 'theme']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'activePanel', 'height', 'hideBorders', 'layout', 'loading_state', 'orientation', 'panelCount', 'panels', 'proportionalLayout', 'savedLayout', 'theme']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DashGridLayout, self).__init__(children=children, **args)

setattr(DashGridLayout, "__init__", _explicitize_args(DashGridLayout.__init__))
