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


class TiledViewer(Component):
    """A TiledViewer component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- apiKey (string; optional):
    The API key for the Tiled viewer.

- backgroundClassName (string; optional):
    The class name for the background.

- bearerToken (string; optional):
    The bearer token for the Tiled viewer.

- buttonModeText (string; optional):
    The text for the button mode.

- closeOnSelect (boolean; optional):
    Whether to close the viewer on select.

- contentClassName (string; optional):
    The class name for the content.

- enableStartupScreen (boolean; optional):
    Whether to enable the startup screen.

- inButtonModeShowApiKeyInput (boolean; optional):
    Whether to show the API key input in button mode.

- inButtonModeShowReverseSortInput (boolean; optional):
    Whether to show the reverse sort input in button mode.

- inButtonModeShowSelectedData (boolean; optional):
    Whether to show the selected data in button mode.

- includeAuthTokensInSelectCallback (boolean; optional):
    Whether to include auth tokens in the select item callback. If
    tokens are not found in local storage, the values will be None.

- initialPath (string; optional):
    The initial path for the Tiled viewer.

- isButtonMode (boolean; optional):
    Whether to use button mode.

- isFullWidth (boolean; optional):
    Whether to use full width of the parent element.

- isPopup (boolean; optional):
    Whether the viewer is a popup.

- pageLimit (number; optional):
    The page limit to be shown in columns.

- reloadLastItemOnStartup (boolean; optional):
    Whether to reload the last available selected item on component
    startup.

- reverseSort (boolean; optional):
    Whether to reverse the sort order.

- selectedLinks (boolean | number | string | dict | list; optional):
    The content sent into the callback function from Tiled.

- showPlanName (boolean; optional):
    Whether to show the plan name in columns for BlueskyRuns.

- showPlanStartTime (boolean; optional):
    Whether to show the plan start time in columns for BlueskyRuns.

- singleColumnMode (boolean; optional):
    Whether to use single column mode.

- size (string; optional):
    The size of the viewer. 'small', 'medium', 'large'.

- tiledBaseUrl (string; optional):
    The base URL for the tiled viewer."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'tiled_viewer'
    _type = 'TiledViewer'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        backgroundClassName: typing.Optional[str] = None,
        closeOnSelect: typing.Optional[bool] = None,
        apiKey: typing.Optional[str] = None,
        bearerToken: typing.Optional[str] = None,
        isButtonMode: typing.Optional[bool] = None,
        buttonModeText: typing.Optional[str] = None,
        contentClassName: typing.Optional[str] = None,
        enableStartupScreen: typing.Optional[bool] = None,
        isPopup: typing.Optional[bool] = None,
        selectedLinks: typing.Optional[typing.Any] = None,
        singleColumnMode: typing.Optional[bool] = None,
        tiledBaseUrl: typing.Optional[str] = None,
        size: typing.Optional[str] = None,
        isFullWidth: typing.Optional[bool] = None,
        inButtonModeShowApiKeyInput: typing.Optional[bool] = None,
        inButtonModeShowReverseSortInput: typing.Optional[bool] = None,
        inButtonModeShowSelectedData: typing.Optional[bool] = None,
        reverseSort: typing.Optional[bool] = None,
        initialPath: typing.Optional[str] = None,
        showPlanName: typing.Optional[bool] = None,
        showPlanStartTime: typing.Optional[bool] = None,
        pageLimit: typing.Optional[NumberType] = None,
        reloadLastItemOnStartup: typing.Optional[bool] = None,
        includeAuthTokensInSelectCallback: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'apiKey', 'backgroundClassName', 'bearerToken', 'buttonModeText', 'closeOnSelect', 'contentClassName', 'enableStartupScreen', 'inButtonModeShowApiKeyInput', 'inButtonModeShowReverseSortInput', 'inButtonModeShowSelectedData', 'includeAuthTokensInSelectCallback', 'initialPath', 'isButtonMode', 'isFullWidth', 'isPopup', 'pageLimit', 'reloadLastItemOnStartup', 'reverseSort', 'selectedLinks', 'showPlanName', 'showPlanStartTime', 'singleColumnMode', 'size', 'tiledBaseUrl']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'apiKey', 'backgroundClassName', 'bearerToken', 'buttonModeText', 'closeOnSelect', 'contentClassName', 'enableStartupScreen', 'inButtonModeShowApiKeyInput', 'inButtonModeShowReverseSortInput', 'inButtonModeShowSelectedData', 'includeAuthTokensInSelectCallback', 'initialPath', 'isButtonMode', 'isFullWidth', 'isPopup', 'pageLimit', 'reloadLastItemOnStartup', 'reverseSort', 'selectedLinks', 'showPlanName', 'showPlanStartTime', 'singleColumnMode', 'size', 'tiledBaseUrl']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(TiledViewer, self).__init__(**args)

setattr(TiledViewer, "__init__", _explicitize_args(TiledViewer.__init__))
