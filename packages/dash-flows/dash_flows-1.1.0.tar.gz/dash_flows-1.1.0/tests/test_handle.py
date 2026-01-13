from dash.testing.application_runners import import_app


# Basic test for the component rendering.
# The dash_duo pytest fixture is installed with dash (v1.0+)
def test_render_component(dash_duo):
    # Start a dash app contained as the variable `app` in `usage.py`
    app = import_app('usage')
    dash_duo.start_server(app)

    # Find the react-flow component in the initial page load
    react_flow = dash_duo.find_element('#react-flow-example')
    assert react_flow is not None

    # Assert the presence of one of the node handles as configured in the new api in usage.py
    handle_element = dash_duo.find_element('div[data-handleid="handle4"][data-nodeid="2"][data-handlepos="bottom"][data-id="1-2-handle4-target"]')
    assert handle_element is not None
    assert handle_element.get_attribute('class') == 'react-flow__handle react-flow__handle-bottom nodrag nopan target connectable connectablestart connectableend connectionindicator'
    assert handle_element.get_attribute('style') == 'background: rgb(85, 85, 85);'