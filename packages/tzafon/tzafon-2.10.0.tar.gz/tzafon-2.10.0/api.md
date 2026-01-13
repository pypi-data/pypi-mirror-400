# Computers

Types:

```python
from tzafon.types import (
    ComputerCreateResponse,
    ComputerRetrieveResponse,
    ComputerListResponse,
    ComputerCaptureScreenshotResponse,
    ComputerClickResponse,
    ComputerDebugResponse,
    ComputerDoubleClickResponse,
    ComputerDragResponse,
    ComputerExecuteActionResponse,
    ComputerExecuteBatchResponse,
    ComputerGetHTMLResponse,
    ComputerKeepAliveResponse,
    ComputerKeyDownResponse,
    ComputerKeyUpResponse,
    ComputerMouseDownResponse,
    ComputerMouseUpResponse,
    ComputerNavigateResponse,
    ComputerPressHotkeyResponse,
    ComputerRightClickResponse,
    ComputerScrollViewportResponse,
    ComputerSetViewportResponse,
    ComputerTypeTextResponse,
)
```

Methods:

- <code title="post /computers">client.computers.<a href="./src/tzafon/resources/computers/computers.py">create</a>(\*\*<a href="src/tzafon/types/computer_create_params.py">params</a>) -> <a href="./src/tzafon/types/computer_create_response.py">ComputerCreateResponse</a></code>
- <code title="get /computers/{id}">client.computers.<a href="./src/tzafon/resources/computers/computers.py">retrieve</a>(id) -> <a href="./src/tzafon/types/computer_retrieve_response.py">ComputerRetrieveResponse</a></code>
- <code title="get /computers">client.computers.<a href="./src/tzafon/resources/computers/computers.py">list</a>() -> <a href="./src/tzafon/types/computer_list_response.py">ComputerListResponse</a></code>
- <code title="post /computers/{id}/screenshot">client.computers.<a href="./src/tzafon/resources/computers/computers.py">capture_screenshot</a>(id, \*\*<a href="src/tzafon/types/computer_capture_screenshot_params.py">params</a>) -> <a href="./src/tzafon/types/computer_capture_screenshot_response.py">ComputerCaptureScreenshotResponse</a></code>
- <code title="post /computers/{id}/click">client.computers.<a href="./src/tzafon/resources/computers/computers.py">click</a>(id, \*\*<a href="src/tzafon/types/computer_click_params.py">params</a>) -> <a href="./src/tzafon/types/computer_click_response.py">ComputerClickResponse</a></code>
- <code title="get /computers/{id}/ws">client.computers.<a href="./src/tzafon/resources/computers/computers.py">connect_websocket</a>(id) -> None</code>
- <code title="post /computers/{id}/debug">client.computers.<a href="./src/tzafon/resources/computers/computers.py">debug</a>(id, \*\*<a href="src/tzafon/types/computer_debug_params.py">params</a>) -> <a href="./src/tzafon/types/computer_debug_response.py">ComputerDebugResponse</a></code>
- <code title="post /computers/{id}/double-click">client.computers.<a href="./src/tzafon/resources/computers/computers.py">double_click</a>(id, \*\*<a href="src/tzafon/types/computer_double_click_params.py">params</a>) -> <a href="./src/tzafon/types/computer_double_click_response.py">ComputerDoubleClickResponse</a></code>
- <code title="post /computers/{id}/drag">client.computers.<a href="./src/tzafon/resources/computers/computers.py">drag</a>(id, \*\*<a href="src/tzafon/types/computer_drag_params.py">params</a>) -> <a href="./src/tzafon/types/computer_drag_response.py">ComputerDragResponse</a></code>
- <code title="post /computers/{id}/execute">client.computers.<a href="./src/tzafon/resources/computers/computers.py">execute_action</a>(id, \*\*<a href="src/tzafon/types/computer_execute_action_params.py">params</a>) -> <a href="./src/tzafon/types/computer_execute_action_response.py">ComputerExecuteActionResponse</a></code>
- <code title="post /computers/{id}/batch">client.computers.<a href="./src/tzafon/resources/computers/computers.py">execute_batch</a>(id, \*\*<a href="src/tzafon/types/computer_execute_batch_params.py">params</a>) -> <a href="./src/tzafon/types/computer_execute_batch_response.py">ComputerExecuteBatchResponse</a></code>
- <code title="post /computers/{id}/html">client.computers.<a href="./src/tzafon/resources/computers/computers.py">get_html</a>(id, \*\*<a href="src/tzafon/types/computer_get_html_params.py">params</a>) -> <a href="./src/tzafon/types/computer_get_html_response.py">ComputerGetHTMLResponse</a></code>
- <code title="post /computers/{id}/keepalive">client.computers.<a href="./src/tzafon/resources/computers/computers.py">keep_alive</a>(id) -> <a href="./src/tzafon/types/computer_keep_alive_response.py">ComputerKeepAliveResponse</a></code>
- <code title="post /computers/{id}/key-down">client.computers.<a href="./src/tzafon/resources/computers/computers.py">key_down</a>(id, \*\*<a href="src/tzafon/types/computer_key_down_params.py">params</a>) -> <a href="./src/tzafon/types/computer_key_down_response.py">ComputerKeyDownResponse</a></code>
- <code title="post /computers/{id}/key-up">client.computers.<a href="./src/tzafon/resources/computers/computers.py">key_up</a>(id, \*\*<a href="src/tzafon/types/computer_key_up_params.py">params</a>) -> <a href="./src/tzafon/types/computer_key_up_response.py">ComputerKeyUpResponse</a></code>
- <code title="post /computers/{id}/mouse-down">client.computers.<a href="./src/tzafon/resources/computers/computers.py">mouse_down</a>(id, \*\*<a href="src/tzafon/types/computer_mouse_down_params.py">params</a>) -> <a href="./src/tzafon/types/computer_mouse_down_response.py">ComputerMouseDownResponse</a></code>
- <code title="post /computers/{id}/mouse-up">client.computers.<a href="./src/tzafon/resources/computers/computers.py">mouse_up</a>(id, \*\*<a href="src/tzafon/types/computer_mouse_up_params.py">params</a>) -> <a href="./src/tzafon/types/computer_mouse_up_response.py">ComputerMouseUpResponse</a></code>
- <code title="post /computers/{id}/navigate">client.computers.<a href="./src/tzafon/resources/computers/computers.py">navigate</a>(id, \*\*<a href="src/tzafon/types/computer_navigate_params.py">params</a>) -> <a href="./src/tzafon/types/computer_navigate_response.py">ComputerNavigateResponse</a></code>
- <code title="post /computers/{id}/hotkey">client.computers.<a href="./src/tzafon/resources/computers/computers.py">press_hotkey</a>(id, \*\*<a href="src/tzafon/types/computer_press_hotkey_params.py">params</a>) -> <a href="./src/tzafon/types/computer_press_hotkey_response.py">ComputerPressHotkeyResponse</a></code>
- <code title="post /computers/{id}/right-click">client.computers.<a href="./src/tzafon/resources/computers/computers.py">right_click</a>(id, \*\*<a href="src/tzafon/types/computer_right_click_params.py">params</a>) -> <a href="./src/tzafon/types/computer_right_click_response.py">ComputerRightClickResponse</a></code>
- <code title="post /computers/{id}/scroll">client.computers.<a href="./src/tzafon/resources/computers/computers.py">scroll_viewport</a>(id, \*\*<a href="src/tzafon/types/computer_scroll_viewport_params.py">params</a>) -> <a href="./src/tzafon/types/computer_scroll_viewport_response.py">ComputerScrollViewportResponse</a></code>
- <code title="post /computers/{id}/viewport">client.computers.<a href="./src/tzafon/resources/computers/computers.py">set_viewport</a>(id, \*\*<a href="src/tzafon/types/computer_set_viewport_params.py">params</a>) -> <a href="./src/tzafon/types/computer_set_viewport_response.py">ComputerSetViewportResponse</a></code>
- <code title="get /computers/{id}/events">client.computers.<a href="./src/tzafon/resources/computers/computers.py">stream_events</a>(id) -> None</code>
- <code title="get /computers/{id}/screencast">client.computers.<a href="./src/tzafon/resources/computers/computers.py">stream_screencast</a>(id) -> None</code>
- <code title="delete /computers/{id}">client.computers.<a href="./src/tzafon/resources/computers/computers.py">terminate</a>(id) -> None</code>
- <code title="post /computers/{id}/type">client.computers.<a href="./src/tzafon/resources/computers/computers.py">type_text</a>(id, \*\*<a href="src/tzafon/types/computer_type_text_params.py">params</a>) -> <a href="./src/tzafon/types/computer_type_text_response.py">ComputerTypeTextResponse</a></code>

## Tabs

Types:

```python
from tzafon.types.computers import (
    TabCreateResponse,
    TabListResponse,
    TabDeleteResponse,
    TabSwitchResponse,
)
```

Methods:

- <code title="post /computers/{id}/tabs">client.computers.tabs.<a href="./src/tzafon/resources/computers/tabs.py">create</a>(id, \*\*<a href="src/tzafon/types/computers/tab_create_params.py">params</a>) -> <a href="./src/tzafon/types/computers/tab_create_response.py">TabCreateResponse</a></code>
- <code title="get /computers/{id}/tabs">client.computers.tabs.<a href="./src/tzafon/resources/computers/tabs.py">list</a>(id) -> <a href="./src/tzafon/types/computers/tab_list_response.py">TabListResponse</a></code>
- <code title="delete /computers/{id}/tabs/{tab_id}">client.computers.tabs.<a href="./src/tzafon/resources/computers/tabs.py">delete</a>(tab_id, \*, id) -> <a href="./src/tzafon/types/computers/tab_delete_response.py">TabDeleteResponse</a></code>
- <code title="post /computers/{id}/tabs/{tab_id}/switch">client.computers.tabs.<a href="./src/tzafon/resources/computers/tabs.py">switch</a>(tab_id, \*, id) -> <a href="./src/tzafon/types/computers/tab_switch_response.py">TabSwitchResponse</a></code>
