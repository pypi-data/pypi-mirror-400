import seaborn as sns
import numpy as np
import pandas as pd
import scanpy as sc
from shapely.geometry import MultiPoint,Polygon, MultiPolygon
import alphashape
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display, clear_output
from scipy.interpolate import splprep, splev
from sklearn.neighbors import KDTree
import time
def widget_uid_fix():
    # Initialize widget manager
    dummy_out = widgets.Output(layout=widgets.Layout(display='none'))
    display(dummy_out)

    # Flush to ensure the frontend has the comm ready
    with dummy_out:
        clear_output(wait=True)

def polygon_from_selected_points_simple(X):
    poly = MultiPoint(X).convex_hull
    return poly



def polygon_from_selected_points(X, alpha=1.5):
    poly = alphashape.alphashape(X, alpha)
    return poly


def polygon_to_serializable(poly):
    """
    Always returns a list of polygons,
    each polygon = list of [x, y]
    """
    if isinstance(poly, Polygon):
        return [list(map(list, poly.exterior.coords))]
    elif isinstance(poly, MultiPolygon):
        return [
            list(map(list, p.exterior.coords))
            for p in poly.geoms
        ]
    else:
        raise TypeError("Unsupported geometry type")


def selection_to_polygon_coord(X, selected_idxs,polygon_function):    
    polygons = []
    pts=X[selected_idxs,:]
    poly = polygon_function(pts)
    polygons =  polygon_to_serializable(poly)
    # Flatten into a single Scattergl trace
    combined_x = []
    combined_y = []
    for poly in polygons:
        px, py = zip(*poly)  # unzip coordinates
        combined_x += list(px) + [None]  # None to break the path between polygons
        combined_y += list(py) + [None]
    return combined_x, combined_y




def make_discrete_colorscale(colors):
    """
    colors: list of color strings (length N)
    returns: Plotly discrete colorscale
    """
    n = len(colors)
    scale = []
    for i, c in enumerate(colors):
        scale.append([i / n, c])
        scale.append([(i + 1) / n, c])
    return scale




def lasso_selection_umap_tool(adata, feat=None, cmap='Magma', selectedpoints_col=None, simple_polygon_drawing=True, umap_embedding='X_umap'):
    """
    Interactive UMAP visualization with manual cell selection tools.

    This function displays a UMAP embedding of cells stored in `adata` and
    enables interactive selection of cells using lasso or box selection.
    Optionally, cells can be colored by a feature and selected cell indices can be stored back into
    `adata.obs`.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix containing a UMAP embedding in
        `adata.obsm[umap_embedding]`.

    feat : str or None, optional (default: None)
        Column name in `adata.obs`, gene name in `adata.var_names` or `adata.obsm['crispr']` used
        to color cells. If None, cells are shown in a uniform color.

    cmap : str, optional (default: "Magma")
        Colormap used when coloring cells by `feat`.

    selectedpoints_col : str or None, optional (default: None)
        If provided, the indices of selected cells are stored as a boolean
        column in `adata.obs[selectedpoints_col]`.

    simple_polygon_drawing : bool, optional (default: True)
        If True, enables a simplified polygon-based selection interface.
        If False, uses Plotly’s standard lasso and box selection tools.

    umap_embedding : str, optional (default: "X_umap")
        Key in `adata.obsm` containing the 2D UMAP coordinates to visualize.

    Returns
    -------
    None
        Displays an interactive Plotly figure for UMAP visualization and
        manual cell selection.
    """
    widget_uid_fix()
    X = adata.obsm[umap_embedding]
    if simple_polygon_drawing:
        polygon_function = polygon_from_selected_points_simple
    else:
        polygon_function = polygon_from_selected_points
    # Precompute feature data and type
    feat_data_dict = {}
    feat_type_dict = {}  # "numeric" or "categorical"
    if feat == None:
        pass
    elif feat in adata.var_names:
        expr = adata[:, feat].X
        if not isinstance(expr, np.ndarray):
            expr = expr.toarray().flatten()
        else:
            expr = np.asarray(expr).flatten()
        feat_data_dict[feat] = expr
        feat_type_dict[feat] = "numeric"

    elif feat in adata.obs.columns:
        col = adata.obs[feat]
        feat_data_dict[feat] = col
        is_cat = pd.api.types.is_categorical_dtype(col) or col.dtype == object
        feat_type_dict[feat] = "categorical" if is_cat else "numeric"

    elif ('crispr' in adata.obsm and
            hasattr(adata.obsm['crispr'], 'columns') and
            feat in adata.obsm['crispr'].columns):
        expr = adata.obsm['crispr'][feat].values.astype(float)
        if not isinstance(expr, np.ndarray):
            expr = expr.toarray().flatten()
        else:
            expr = np.asarray(expr).flatten()
        feat_data_dict[feat] = expr
        feat_type_dict[feat] = "numeric"
    else:
        raise ValueError(f"Feature '{feat}' not found in adata.var_names, adata.obs or adata.obsm['crispr']")

    marker=dict(
            size=4,
            opacity=0.8,
            color=None,

        )
    if feat != None:
        if feat_type_dict[feat] == "categorical":
            labels = adata.obs[feat].astype("category")
            codes = labels.cat.codes.values            # 0, 1, 2, ...
            categories = labels.cat.categories
            feat_data_dict[feat] = codes
            try:
                category_colors = adata.uns[f"{feat}_colors"]
            except KeyError:
                categorical_cmap = 'tab10' if len(categories) <= 10 else 'tab20'
                category_colors = sns.color_palette(categorical_cmap, n_colors=len(categories)).as_hex()
            plotly_colorscale = make_discrete_colorscale(category_colors)
            colorbar=dict(
                        title=feat,
                        tickvals=list(range(len(categories))),
                        ticktext=categories
                    )
            cmin=0 
            cmax=len(categories) - 1
        else:
            plotly_colorscale = cmap
            colorbar=dict(title=feat)
            expr = feat_data_dict[feat]
            cmin = np.percentile(expr, 1)
            cmax = np.percentile(expr, 99)
        marker['color'] = feat_data_dict[feat]
        marker['colorscale']=plotly_colorscale
        marker['cmin']=cmin
        marker['cmax']=cmax
        marker['colorbar']=colorbar
    hovertext = adata.obs_names

    fig = go.FigureWidget(
        data=[
            go.Scattergl(
                x=X[:, 0],
                y=X[:, 1],
                mode="markers",
                marker=marker,
                selected=dict(marker=dict(opacity=1)),
                unselected=dict(marker=dict(opacity=0.2)),
                hovertext=hovertext,
                name='cells'
            ),
            go.Scattergl(
                x=[],
                y=[],
                mode='lines',
                line=dict(color='red', width=2),
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                name='polygon',
                visible=False)
        ],
        layout=go.Layout(
            dragmode="lasso",
            width=800,
            height=600,
            title=feat,
        ),
    )

    save_button = widgets.Button(
        description="Save selection",
        button_style="success"
    )
    column_name_input = widgets.Text(
        value="selected cells",
        description="Save to column:",
        placeholder="column name in adata.obs",
        layout=widgets.Layout(width="300px")
    )
    sel_col = column_name_input.value.strip()
    if sel_col not in adata.obs.columns:
        adata.obs[sel_col] = False

    if selectedpoints_col:
        selected_idxs = np.where(adata.obs[selectedpoints_col].values)[0]
        fig.data[0].selectedpoints = selected_idxs



    output = widgets.Output()
    def save_selection(_):
        with output:
            selected_idxs = fig.data[0].selectedpoints

            if selected_idxs is None or len(selected_idxs) == 0:
                print("No cells selected")
                return

            selected_idxs = list(selected_idxs)

            col = column_name_input.value.strip()

            if col == "":
                print("Column name cannot be empty")
                return
            adata.obs[col] = False
            adata.obs.iloc[
                selected_idxs,
                adata.obs.columns.get_loc(col)
            ] = True
            print(f"Saved {len(selected_idxs)} cells to adata.obs['{col}']")
        
    save_button.on_click(save_selection)


    # Button to show/hide polygon
    toggle_button = widgets.Button(description="Toggle Polygon", button_style="info")
    
    def toggle_polygon(_):
        """
        toggle_polygon both makes the polygon visible and invisible as well as updating the polygon based on current selection. 
        The plotly.graph_objects did not allow for an easy update based on selection so this is the quick workaround.
        """
        with output:
            poly_trace_local = fig.data[1]
            if poly_trace_local is None:
                print("No polygon to toggle")
                return
            poly_trace_local.visible = not poly_trace_local.visible
            print(f'polygon visible: {poly_trace_local.visible}')
            selected_idxs = fig.data[0].selectedpoints
            if selected_idxs is None or len(selected_idxs) == 0:
                return

            combined_x, combined_y = selection_to_polygon_coord(X, selected_idxs,polygon_function)

            poly_trace_local.x = combined_x
            poly_trace_local.y = combined_y
    toggle_button.on_click(toggle_polygon)

    display(fig)
    display(column_name_input)
    display(widgets.HBox([save_button, toggle_button]))
    display(output)


def make_spline(points, n_samples=1000, smooth=1.0):
    """
    points: (N,2) array of control points
    smooth: smoothing factor (higher = smoother)
    """
    x, y = points[:, 0], points[:, 1]
    k = min(3, len(points) - 1)

    tck, _ = splprep([x, y], s=smooth, k=k)
    u_fine = np.linspace(0, 1, n_samples)
    xs, ys = splev(u_fine, tck)

    return np.column_stack([xs, ys])

def umap_gradient_tool(adata, 
                       smooth=1.0,    
                       default_colname="umap_gradient",
                       default_n_points=3,):
    widget_uid_fix()
    X = adata.obsm["X_umap"]

    fig = go.FigureWidget(
        data=[
            go.Scattergl(
                x=X[:, 0],
                y=X[:, 1],
                mode="markers",
                marker=dict(size=4, opacity=0.6, color= "#1f77b4"),
                hovertext=adata.obs_names,
                name="cells",
            )
        ],
        layout=go.Layout(
            width=800,
            height=600,
            title="Click cells to draw a gradient",
        )
    )


    # -----------------------
    # UI
    # -----------------------
    n_points_input = widgets.IntSlider(
        value=default_n_points,
        min=2,
        max=10,
        step=1,
        description="Gradient points:",
        continuous_update=False,
    )

    col_input = widgets.Text(
        value=default_colname,
        description="Save to:",
        layout=widgets.Layout(width="300px"),
    )

    save_button = widgets.Button(
        description="Save gradient",
        button_style="success",
    )

    
    status = widgets.Output()

    clicked_idxs = []
    spline_trace = None
    ctrl_trace = None

    def redraw_spline():
        fig.data = fig.data[:1]
        nonlocal spline_trace, ctrl_trace
        spline_trace = None
        ctrl_trace = None
        ctrl_pts = X[clicked_idxs]

        if len(ctrl_pts) < 3:
            return

        spline_pts = make_spline(ctrl_pts, smooth=smooth)



        tree = KDTree(spline_pts)
        dist, idx = tree.query(X, k=1)

        closest = idx[:, 0]

        # arc-length pseudotime
        deltas = np.diff(spline_pts, axis=0)
        seglen = np.linalg.norm(deltas, axis=1)
        s = np.concatenate([[0], np.cumsum(seglen)])
        s /= s[-1]
        grad = s[closest]
        spline_dist = dist[:, 0]


        # draw spline
        if spline_trace is None:
            spline_trace = go.Scattergl(
                x=spline_pts[:, 0],
                y=spline_pts[:, 1],
                mode="lines",
                line=dict(color="red", width=3),
                name="spline"
            )
            fig.add_trace(spline_trace)

        # draw control points
        if ctrl_trace is None:
            ctrl_trace = go.Scattergl(
                x=ctrl_pts[:, 0],
                y=ctrl_pts[:, 1],
                mode="markers+lines",
                marker=dict(size=10, color="black"),
                line=dict(color="black", dash="dot"),
                name="control points"
            )
            fig.add_trace(ctrl_trace)
        else:
            ctrl_trace.x = ctrl_pts[:, 0]
            ctrl_trace.y = ctrl_pts[:, 1]

        fig.data[0].marker.color = grad
        fig.data[0].marker.colorscale = "Viridis"
        fig.data[0].marker.colorbar = dict(title="Gradient")
        fig.data[0].marker.colorbar.update(
            len=0.7,
        )  
        fig.data[0].marker.showscale = True  
        fig._current_gradient = grad
        fig._current_spline_dist = spline_dist

    # -----------------------
    # Click handler
    # -----------------------

    def click_fn(trace, points, _):
        if not points.point_inds:
            return

        idx = points.point_inds[0]
        clicked_idxs.append(idx)
        
        if len(clicked_idxs) > n_points_input.value:
            clicked_idxs.pop(0)
        with status:
            print(f"Clicked {len(clicked_idxs)} / {n_points_input.value}")
        if len(clicked_idxs) == n_points_input.value:
            redraw_spline()

    fig.data[0].on_click(click_fn)


    # -----------------------
    # Save gradient
    # -----------------------
    def save_gradient(_):
        with status:
            if not hasattr(fig, "_current_gradient"):
                print("No gradient defined yet")
                return

            col = col_input.value.strip()
            if col == "":
                print("Column name cannot be empty")
                return

            adata.obs[col] = fig._current_gradient
            print(f"Saved gradient to adata.obs['{col}']")

    save_button.on_click(save_gradient)


    clear_button = widgets.Button(description="Clear", button_style="warning")

    def clear(_):
        nonlocal spline_trace, ctrl_trace
        clicked_idxs.clear()
        if spline_trace is not None:
            fig.data = fig.data[:1]
            spline_trace = None
            ctrl_trace = None
        with status:
            print("Cleared spline")
        fig.data[0].marker.color = "#1f77b4"
        fig.data[0].marker.colorscale = None
        fig.data[0].marker.showscale = False
    clear_button.on_click(clear)
    
    # Button to show/hide polygon
    toggle_spline_button = widgets.Button(description="Toggle Spline", button_style="info")
    
    def toggle_spline(_):
        # get the polygon trace from fig by name
        spline_object = next((t for t in fig.data if getattr(t, 'name', None) == 'spline'), None)
        control_points_object = next((t for t in fig.data if getattr(t, 'name', None) == 'control points'), None)
        if spline_object is None or control_points_object is None:
            return

        spline_object.visible = not spline_object.visible
        control_points_object.visible = not control_points_object.visible

    toggle_spline_button.on_click(toggle_spline)

    # -----------------------
    # Display
    # -----------------------
    display(fig)
    display(widgets.HBox([n_points_input, col_input]))
    display(widgets.HBox([save_button, clear_button, toggle_spline_button]))
    display(status)