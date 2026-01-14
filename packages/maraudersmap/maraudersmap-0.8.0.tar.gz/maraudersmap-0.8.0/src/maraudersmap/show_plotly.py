import numpy as np
import requests, threading, webbrowser,time
import plotly.graph_objs as go
import plotly.io as pio
from dash import Dash, dcc, html, ctx, callback, Patch, clientside_callback, State
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq

import networkx as nx

from maraudersmap.nx_utils import compute_graph_depth
from maraudersmap.layout_debug import gen_grid_layout_data
from maraudersmap.colors_utils import colorscale
from maraudersmap.layout_ripple import layout_ripple
from maraudersmap.layout_forces import (
    connexion_forces,
    repulsion_forces_macros,
    repulsion_forces_neighbors,
    gravity_level_forces,
    gravity_frontier,
)


def server_is_up(url):
    try:
        requests.get(url)
        return True
    except requests.ConnectionError:
        return False


def dash_app_noload(ntx,debug=False, use_reloader=False):
    style = [
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
        dbc.themes.COSMO,
        dbc.themes.BOOTSTRAP,
    ]
    app = Dash(
        __name__,
        external_stylesheets=style,
    )
    interactive_ripple_dash(ntx,app)
    return app


def dash_app_autoload(ntx):
    
    app = dash_app_noload(ntx)
    
    def start_server():
        app.run_server(debug=False, use_reloader=False)  # use_reloader=False to prevent reloading

    def server_is_up(url):
        try:
            requests.get(url)
            return True
        except requests.ConnectionError:
            return False

    host = '127.0.0.1'
    port = 8050
    url = f'http://{host}:{port}'

    # Run the Dash app in a separate thread
    thread = threading.Thread(target=start_server)
    thread.start()

    # Wait for the server to start
    while not server_is_up(url):
        time.sleep(0.1)  # Wait a bit before trying again

    print(f'The Dash app is running at {url}')
    webbrowser.open(url)

    # Join the thread to keep the script running
    thread.join()




def interactive_ripple_dash(ntx,app):
    # Generate some example data
    # #     #x_data = np.linspace(0, 10, 100)
    pos = nx.random_layout(ntx, seed=2)

    default_colors = []
    for node in pos.keys():
        ntx.nodes[node]["pos"] = pos[node]

    # Create Edges
    edge_trace = go.Scatter(
        x=[],
        y=[],
        mode="markers+lines",
        hoverinfo="none",
        opacity=0.5,
        marker=dict(
            size=10,
            symbol="arrow-bar-up",
            angleref="previous",
            color="black",
        ),
    )
    for edge in ntx.edges():
        x0, y0 = ntx.nodes[edge[0]]["pos"]
        x1, y1 = ntx.nodes[edge[1]]["pos"]
        edge_trace["x"] += tuple([x0, x1, None])
        edge_trace["y"] += tuple([y0, y1, None])

    # Create Nodes
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        hoverinfo="text",
        marker=dict(
            reversescale=True,
            color=[],
            size=[],
            line=dict(width=2),
        ),
    )

    # Update positions and sizes of nodes
    correct_sizes = []
    custom_colors = []
    for node in ntx.nodes():
        x, y = ntx.nodes[node]["pos"]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])
        correct_sizes.append(np.sqrt(ntx.nodes[node]["ssize"]))
        custom_colors.append(ntx.nodes[node]["color"])
    node_trace["marker"]["size"] = correct_sizes

    # Add color to node points
    for node, adjacencies in enumerate(ntx.adjacency()):
        node_trace["marker"]["color"] += tuple(
            [custom_colors[node]] * len(adjacencies[1])
        )
        node_info = (
            "Name: "
            + str(adjacencies[0])
            + "<br># of connections: "
            + str(len(adjacencies[1]))
        )
        node_trace["text"] += tuple([node_info])

    

    # app = Dash(
    #     __name__,
    #     external_stylesheets=style,
    # )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=1, l=5, r=5, t=60),
            plot_bgcolor="white",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )
    content = []

    content.append(
        html.H1(
            children="FLOCN the Callgraph Manipulator",
            style={"textAlign": "center", "color": "black"},
        ),
    )
    content.append(
        html.Hr(style={"borderTop": "3px solid grey"}),
    )

    content.append(
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col([
                        dcc.Graph(
                            id="Graph",
                            figure=fig,
                            style={
                                "max-width": None,
                                "max-height": None,
                                "border": "2px grey solid",
                                "width": "120vh",
                                "height": "80vh",
                            },
                        ),
                        dcc.Store(id='graph-dimensions')],
                        style={
                            "max-width": None,
                            "width": "80%",
                            "height": "100%",
                        },
                    ),
                    dbc.Col(
                        [
                            html.H2(
                                children="Physical Property",
                                style={"textAlign": "center", "color": "black"},
                            ),
                            html.Hr(style={"borderTop": "3px solid grey"}),
                            html.H4(
                                children="Levels :",
                                style={"color": "black"},
                            ),
                            dcc.Slider(
                                id="level-slider",
                                min=-6,
                                max=2,
                                step=0.1,
                                value=-6.0,
                                marks=None,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),
                            html.Br(),
                            html.H4(
                                children="Connexion :",
                                style={"color": "black"},
                            ),
                            dcc.Slider(
                                id="connexion-slider",
                                min=-6,
                                max=0,
                                step=0.1,
                                value=-6.0,
                                marks=None,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),
                            html.Div(
                                [
                                    html.H5(
                                        children="    Length :",
                                        style={"color": "black"},
                                    ),
                                    dcc.Slider(
                                        id="length-slider",
                                        min=0,
                                        max=0.1,
                                        step=0.01,
                                        value=0.05,
                                        marks=None,
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": False,
                                        },
                                    ),
                                ],
                                style={"margin-left": "40px"},
                            ),
                            html.Br(),
                            html.H4(
                                children="Overlay :",
                                style={"color": "black"},
                            ),
                            dcc.Slider(
                                id="overlay-slider",
                                min=-6,
                                max=2,
                                step=0.1,
                                value=-6.0,
                                marks=None,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),
                            html.Div(
                                [
                                    html.H5(
                                        children="    Neighbors :",
                                        style={"color": "black"},
                                    ),
                                    dcc.Slider(
                                        id="neighbors-slider",
                                        min=0.01,
                                        max=1,
                                        step=0.01,
                                        value=0.01,
                                        marks=None,#{0.01: "0.01", 0.1: "0.1", 1: "1"},
                                    ),
                                ],
                                style={"margin-left": "40px"},
                            ),
                            html.Br(),
                            html.H4(
                                children="Repulsion :",
                                style={"color": "black"},
                            ),
                            dcc.Slider(
                                id="repulsion-slider",
                                min=-6,
                                max=2,
                                step=0.1,
                                value=-6.0,
                                marks=None,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),
                            html.Div(
                                [
                                    html.H5(
                                        children="    Quad-Tree Fraction :",
                                        style={"color": "black"},
                                    ),
                                    dcc.Slider(
                                        id="quadtree-slider",
                                        min=0.05,
                                        max=1,
                                        step=0.05,
                                        value=0.5,
                                        marks=None,
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": False,
                                        },
                                    ),
                                ],
                                style={"margin-left": "40px"},
                            ),
                            html.Br(),
                            html.H4(
                                children="Frontier :",
                                style={"color": "black"},
                            ),
                            dcc.Slider(
                                id="gvt-slider",
                                min=-6,
                                max=2,
                                step=0.1,
                                value=-6.0,
                                marks=None,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),
                            # html.Br(),
                            # html.H4(
                            #     children="Allow 3D :",
                            #     style={"color": "black"},
                            # ),
                            # daq.ToggleSwitch(
                            #     id="3D-Toggle",
                            #     value=False,
                            #     color="green",
                            # ),
                            # html.Div(
                            #     [
                            #         html.H5(
                            #             children="    3D Duration :",
                            #             style={"color": "black"},
                            #         ),
                            #         dcc.Slider(
                            #             id="3dDuration-slider",
                            #             min=0,
                            #             max=1,
                            #             step=0.1,
                            #             value=0,
                            #             marks=None,
                            #             disabled=True,
                            #             tooltip={
                            #                 "placement": "bottom",
                            #                 "always_visible": False,
                            #             },
                            #         ),
                            #         html.H5(
                            #             children="    Flattening Force :",
                            #             style={"color": "black"},
                            #         ),
                            #         dcc.Slider(
                            #             id="flatten-slider",
                            #             min=0,
                            #             max=1,
                            #             step=0.1,
                            #             value=0,
                            #             marks=None,
                            #             disabled=True,
                            #             tooltip={
                            #                 "placement": "bottom",
                            #                 "always_visible": False,
                            #             },
                            #         ),
                            #     ],
                            #     style={"margin-left": "40px"},
                            # ),
                            html.Br(),
                            html.H4(
                                children="Iterations :",
                                style={"color": "black"},
                            ),
                            dcc.Slider(
                                id="iteration-slider",
                                min=1,
                                max=5,
                                step=0.2,
                                value=1,
                                marks=None,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),
                        ],
                        style={
                            "max-width": None,
                            "width": "20%",
                            "height": "100%",
                        },
                    ),
                ],
                className="h-75",
            ),
            fluid=True,
        )
    )

    # Addition of buttons
    content.append(
        html.Div(
            children=[
                html.H3("Colorization choices : "),
                html.Button("Default", id="button-def", n_clicks=0),
                html.Button("Complexity", id="button-ccn", n_clicks=0),
                html.Button("Size", id="button-size", n_clicks=0),
                html.Div(id="out-buttons"),
            ],
            style={
                "vertical-align": "inline-block",
                "margin-left": "50px",
            },
        )
    )

    # Additon of Save as pdf button
    content.append(
        html.Div(
            children=[
                html.Br(),
                html.H3("Save option : "),
                html.Button("Save as Pdf",id="save-button",n_clicks=0),
                dcc.Download(id='download'),
            ],
            style={
                "vertical-align": "inline-block",
                "margin-left": "50px",
            },
        )
    )

    app.layout = html.Div(content)

    @callback(
        [
            Output("Graph", "figure", allow_duplicate=True),
            Output("out-buttons", "children"),
        ],
        [
            Input("button-def", "n_clicks"),
            Input("button-ccn", "n_clicks"),
            Input("button-size", "n_clicks"),
            # Input("button-gpu", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def displayClick(btn1, btn2, btn3):
        msg = "None of the buttons have been clicked yet. Default colors is applied"
        fig = Patch()
        new_colors = []
        if "button-def" == ctx.triggered_id:
            msg = "Colorized by Default."
            new_colors = [
                hex_to_rgb(custom_colors[idx]) for idx, _ in enumerate(ntx.nodes)
            ]
        elif "button-ccn" == ctx.triggered_id:
            msg = "Colorized by CCN."
            new_colors = color_by(ntx, "CCN")
        elif "button-size" == ctx.triggered_id:
            msg = "Colorized by Size."
            new_colors = color_by(ntx, "ssize")
        # elif "button-gpu" == ctx.triggered_id:
        #     msg = "Colorized if GPU Pragma in detected."

        fig["data"][1]["marker"]["color"] = tuple(new_colors)

        return (fig, html.Div(msg))


    @app.callback(
        Output('graph-dimensions', 'data'),
        Input('Graph', 'figure')
    )
    def update_dimensions(figure):
        return figure

    @app.callback(
        Output('download', 'data'),
        Input('save-button', 'n_clicks'),
        State('graph-dimensions', 'data'),
        prevent_initial_call=True
    )
    def save_graph_as_pdf(n_clicks, figure):
        if n_clicks > 0 and figure:
            # Extract the figure dimensions from the stored data
            fig = go.Figure(figure)
            width = 1500 
            height = 1000
            print(width,height)
            
            # Use Plotly's write_image function to save the figure as a PDF with the same size
            pio.write_image(fig, 'figure.pdf', width=width, height=height)
            
            # Provide the file for download
            return dcc.send_file('figure.pdf')

    # @callback(
    #     [Output("3dDuration-slider", "disabled"), Output("flatten-slider", "disabled")],
    #     Input("3D-Toggle", "value"),
    # )
    # def toggle_sliders(switch_value):
    #     if switch_value:
    #         return False, False
    #     return True, True

    # Define the callback to update the graph
    @app.callback(
        Output("Graph", "figure"),
        [
            Input("level-slider", "value"),
            Input("connexion-slider", "value"),
            Input("length-slider", "value"),
            Input("overlay-slider", "value"),
            Input("neighbors-slider", "value"),
            Input("repulsion-slider", "value"),
            Input("quadtree-slider", "value"),
            Input("gvt-slider", "value"),
            Input("iteration-slider", "value"),
        ],
    )
    def update_figure(
        lvl_slider,
        conn_slider,
        length_slider,
        ovl_slider,
        neigh_slider,
        rep_slider,
        quad_slider,
        gvt_slider,
        nit_slider,
    ):

        # Might be usefull for future implementation, better keep this here
        depth = compute_graph_depth(ntx)
        depth_array = np.array([depth[node] for node in pos])

        conn = []
        node_list = list(ntx.nodes.keys())
        for edge in ntx.edges:
            if edge[0] != edge[1]:
                conn.append([node_list.index(edge[0]), node_list.index(edge[1])])
        conn = np.array(conn)

        relax_gravity_level = 10.0 ** (lvl_slider)
        relax_connexions = 10.0 ** (conn_slider)
        relax_overlap = 10.0 ** (ovl_slider)
        relax_repulsions = 10.0 ** (rep_slider)
        relax_gravity_frontier = 10.0 ** (gvt_slider)

        nit = int(10.0 ** (nit_slider))

        current_coords_x = list(node_trace["x"])
        current_coords_y = list(node_trace["y"])
        current_coords = np.array(list(zip(current_coords_x, current_coords_y)))

        new_coords = layout_ripple(
            current_coords,
            conn,
            depth_array,
            relax_gravity_level,
            relax_gravity_frontier,
            relax_repulsions,
            relax_overlap,
            relax_connexions,
            nit=nit,
            connexion_length=length_slider,
            neighbors_fac=neigh_slider,
            quad_fac=quad_slider,
            wtf=False,
        )

        fig = Patch()
        fig["data"][1]["x"] = tuple(new_coords[:, 0])
        fig["data"][1]["y"] = tuple(new_coords[:, 1])

        edge_x = []
        edge_y = []
        for link in conn:
            edge_x += tuple([new_coords[link[0], 0], new_coords[link[1], 0], None])
            edge_y += tuple([new_coords[link[0], 1], new_coords[link[1], 1], None])

        fig["data"][0]["x"] = edge_x
        fig["data"][0]["y"] = edge_y

        return fig
    return app
    


def hex_to_rgb(hex_color: str) -> str:
    """

    Args:
        hex_color (str): _description_

    Returns:
        str: _description_
    """
    rgb_color = hex_color.lstrip("#")
    return f"rgb{tuple(int(rgb_color[i:i+2], 16)/255 for i in (0, 2, 4))}"


def color_by(ntx: nx.DiGraph, color_key: str):
    """_summary_"""

    # Span for the CCN / sizes
    minimum = 9e9
    maximum = 9e-9
    for node in ntx.nodes:
        minimum = min(minimum, ntx.nodes[node][color_key])
        maximum = max(maximum, ntx.nodes[node][color_key])

    colors = []
    for node in ntx.nodes:
        colors.append(f"rgb{colorscale(ntx.nodes[node][color_key], minimum, maximum)}")

    return colors
