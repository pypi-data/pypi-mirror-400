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


class DashPaneLayout(Component):
    """A DashPaneLayout component.
DashPaneLayout is a component that provides collapsible panes (accordion style).
Each pane has a header that can be clicked to expand/collapse the content.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Dash components to render in panels. Each child should have an id
    matching a panel id.

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- disableDnd (boolean; optional):
    Disable drag-and-drop for reordering panes.

- height (string; optional):
    Height of the component.

- layout (dict; optional):
    Current layout configuration (read-only).

- loading_state (dict; optional):
    Dash loading state.

    `loading_state` is a dict with keys:

    - is_loading (boolean; optional)

    - prop_name (string; optional)

    - component_name (string; optional)

- panelCount (number; optional):
    Total number of panels.

- panels (list of dicts; optional):
    Initial panels to display.

    `panels` is a list of dicts with keys:

    - id (string; required)

    - title (string; optional)

    - isExpanded (boolean; optional)

    - minimumSize (number; optional)

    - maximumSize (number; optional)

- savedLayout (dict; optional):
    Layout JSON to load.

- theme (string; optional):
    Theme class name."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_dock_view'
    _type = 'DashPaneLayout'
    Panels = TypedDict(
        "Panels",
            {
            "id": str,
            "title": NotRequired[str],
            "isExpanded": NotRequired[bool],
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
        disableDnd: typing.Optional[bool] = None,
        panelCount: typing.Optional[NumberType] = None,
        loading_state: typing.Optional["LoadingState"] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'disableDnd', 'height', 'layout', 'loading_state', 'panelCount', 'panels', 'savedLayout', 'theme']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'disableDnd', 'height', 'layout', 'loading_state', 'panelCount', 'panels', 'savedLayout', 'theme']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DashPaneLayout, self).__init__(children=children, **args)

setattr(DashPaneLayout, "__init__", _explicitize_args(DashPaneLayout.__init__))
