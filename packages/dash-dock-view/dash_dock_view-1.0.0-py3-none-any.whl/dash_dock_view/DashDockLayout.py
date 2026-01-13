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


class DashDockLayout(Component):
    """A DashDockLayout component.
DashDockLayout is a component that provides a flexible docking system for Dash applications,
allowing users to create, resize, and rearrange panels in a window manager style interface.
Supports floating groups, layout persistence, and renders Dash components inside panels.

Panel positioning options:
- position: 'left' | 'right' | 'top' | 'bottom' | 'center' (default: 'center')
- size: number (pixels for positioned panels)
- visible: boolean (default: true)
- active: boolean (set as initially active panel)

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Dash components to render in panels. Each child should have an id
    matching a panel id.

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- activatePanelTrigger (dict; optional):
    Trigger to activate/switch to a specific panel tab. Set to
    {panelId: string, timestamp?: number} to activate that panel. The
    timestamp ensures React sees repeated activations as new values.

    `activatePanelTrigger` is a string | dict with keys:

    - panelId (string; required)

    - timestamp (number; optional)

- activePanel (string; optional):
    Currently active panel ID (read-only, updated by component).

- addPanelTrigger (dict; optional):
    Trigger to add a panel. Set to {id, title} to add a new panel.
    Supports position for placing relative to existing panels: -
    position: {referencePanel: 'panel-id', direction:
    'below'|'above'|'left'|'right'|'within'} - size: Initial size in
    pixels (height for above/below, width for left/right).

    `addPanelTrigger` is a dict with keys:

    - id (string; required)

    - title (string; optional)

    - component (string; optional)

    - position (dict; optional)

        `position` is a dict with keys:

        - referencePanel (string; required)

        - direction (a value equal to: 'left', 'right', 'above', 'below', 'within'; optional)

    - size (number; optional)

- clearTrigger (boolean; optional):
    Set to True to clear all panels.

- disableDnd (boolean; optional):
    Disable drag-and-drop functionality.

- disableFloatingGroups (boolean; optional):
    Disable floating groups.

- gap (number; optional):
    Pixel gap between groups.

- height (string; optional):
    Height of the component (CSS value).

- hideBorders (boolean; optional):
    Hide borders between panels.

- hideCloseButtons (boolean; optional):
    Hide close buttons on all tabs. When True, users cannot close
    panels.

- initialLayout (dict; optional):
    Initial layout configuration. Use this to define complex layouts.
    This is a Dockview JSON layout object with grid, panels, and
    activeGroup. Use the `layout` output prop to capture a layout and
    reuse it here.

- layout (dict; optional):
    Current layout configuration (read-only, updated by component).

- loadLayoutTrigger (dict; optional):
    Trigger to load a layout. Set to {layout, timestamp} to load a
    saved layout. The timestamp ensures React sees each load as a new
    value.

    `loadLayoutTrigger` is a dict with keys:

    - layout (dict; required)

    - timestamp (number; optional)

- loading_state (dict; optional):
    Dash loading state.

    `loading_state` is a dict with keys:

    - is_loading (boolean; optional)

    - prop_name (string; optional)

    - component_name (string; optional)

- locked (boolean; optional):
    Lock the entire layout (prevents all modifications).

- panelAdded (dict; optional):
    Last added panel info (read-only, updated by component).

- panelCount (number; optional):
    Total number of panels (read-only, updated by component).

- panelRemoved (dict; optional):
    Last removed panel info (read-only, updated by component).

- panels (list of dicts; optional):
    Initial panels to display. Each panel can have positioning
    options. - id: (required) Unique panel identifier - title: Display
    title for the tab - position: 'left' | 'right' | 'top' | 'bottom'
    | 'center' (default: 'center') - size: Initial size in pixels for
    positioned panels - visible: Whether panel is visible on load
    (default: True) - active: Whether this panel should be
    active/focused on load - collapsed: Whether panel group starts
    collapsed (shows only tab header).

    `panels` is a list of dicts with keys:

    - id (string; required)

    - title (string; optional)

    - position (a value equal to: 'left', 'right', 'top', 'bottom', 'center'; optional)

    - size (number; optional)

    - visible (boolean; optional)

    - active (boolean; optional)

    - collapsed (boolean; optional)

- removePanelTrigger (string; optional):
    Panel ID to remove. Set this to remove a panel.

- savedLayout (dict; optional):
    Layout JSON to load. Set this to restore a previously saved
    layout.

- showAddButton (boolean; optional):
    Show the Add Panel button.

- singleTabMode (a value equal to: 'default', 'fullwidth'; optional):
    Tab display mode ('default' or 'fullwidth').

- theme (string; optional):
    Theme class name ('dockview-theme-light' or
    'dockview-theme-dark')."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_dock_view'
    _type = 'DashDockLayout'
    Panels = TypedDict(
        "Panels",
            {
            "id": str,
            "title": NotRequired[str],
            "position": NotRequired[Literal["left", "right", "top", "bottom", "center"]],
            "size": NotRequired[NumberType],
            "visible": NotRequired[bool],
            "active": NotRequired[bool],
            "collapsed": NotRequired[bool]
        }
    )

    LoadLayoutTrigger = TypedDict(
        "LoadLayoutTrigger",
            {
            "layout": dict,
            "timestamp": NotRequired[NumberType]
        }
    )

    AddPanelTriggerPosition = TypedDict(
        "AddPanelTriggerPosition",
            {
            "referencePanel": str,
            "direction": NotRequired[Literal["left", "right", "above", "below", "within"]]
        }
    )

    AddPanelTrigger = TypedDict(
        "AddPanelTrigger",
            {
            "id": str,
            "title": NotRequired[str],
            "component": NotRequired[str],
            "position": NotRequired["AddPanelTriggerPosition"],
            "size": NotRequired[NumberType]
        }
    )

    ActivatePanelTrigger = TypedDict(
        "ActivatePanelTrigger",
            {
            "panelId": str,
            "timestamp": NotRequired[NumberType]
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
        initialLayout: typing.Optional[dict] = None,
        theme: typing.Optional[str] = None,
        height: typing.Optional[str] = None,
        locked: typing.Optional[bool] = None,
        disableDnd: typing.Optional[bool] = None,
        disableFloatingGroups: typing.Optional[bool] = None,
        hideBorders: typing.Optional[bool] = None,
        hideCloseButtons: typing.Optional[bool] = None,
        gap: typing.Optional[NumberType] = None,
        singleTabMode: typing.Optional[Literal["default", "fullwidth"]] = None,
        showAddButton: typing.Optional[bool] = None,
        panelAdded: typing.Optional[dict] = None,
        panelRemoved: typing.Optional[dict] = None,
        panelCount: typing.Optional[NumberType] = None,
        loadLayoutTrigger: typing.Optional["LoadLayoutTrigger"] = None,
        addPanelTrigger: typing.Optional["AddPanelTrigger"] = None,
        removePanelTrigger: typing.Optional[str] = None,
        clearTrigger: typing.Optional[bool] = None,
        activatePanelTrigger: typing.Optional[typing.Union[str, "ActivatePanelTrigger"]] = None,
        loading_state: typing.Optional["LoadingState"] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'activatePanelTrigger', 'activePanel', 'addPanelTrigger', 'clearTrigger', 'disableDnd', 'disableFloatingGroups', 'gap', 'height', 'hideBorders', 'hideCloseButtons', 'initialLayout', 'layout', 'loadLayoutTrigger', 'loading_state', 'locked', 'panelAdded', 'panelCount', 'panelRemoved', 'panels', 'removePanelTrigger', 'savedLayout', 'showAddButton', 'singleTabMode', 'theme']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'activatePanelTrigger', 'activePanel', 'addPanelTrigger', 'clearTrigger', 'disableDnd', 'disableFloatingGroups', 'gap', 'height', 'hideBorders', 'hideCloseButtons', 'initialLayout', 'layout', 'loadLayoutTrigger', 'loading_state', 'locked', 'panelAdded', 'panelCount', 'panelRemoved', 'panels', 'removePanelTrigger', 'savedLayout', 'showAddButton', 'singleTabMode', 'theme']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DashDockLayout, self).__init__(children=children, **args)

setattr(DashDockLayout, "__init__", _explicitize_args(DashDockLayout.__init__))
