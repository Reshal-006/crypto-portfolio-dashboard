import os
import socket
from datetime import datetime
import json

# Force debug tooling off (some setups export FLASK_DEBUG / DASH_DEBUG globally)
# This must run before importing Dash/Flask.
os.environ["FLASK_DEBUG"] = "0"
os.environ["DASH_DEBUG"] = "0"

import dash
from dash import dcc, html, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import requests
from dash.exceptions import PreventUpdate

try:
    from waitress import serve
except Exception:
    serve = None

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Crypto Portfolio Dashboard"

# API base URL
# Override via env var if needed (e.g. API_URL=http://127.0.0.1:8001/api)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

# Dash server port (override via DASH_PORT). Some environments may have a global
# DASH_PORT=8050 set; since 8050 is often occupied/stuck on Windows, we probe
# for an available port and fall back automatically.
def _is_port_available(host: str, port: int) -> bool:
    # On Windows, binding with SO_REUSEADDR can succeed even if another process
    # is already listening, so we prefer an active connect check.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex((host, port)) != 0
    except OSError:
        return True


_HOST = "127.0.0.1"
_preferred_port = int(os.getenv("DASH_PORT", "8051"))
if _is_port_available(_HOST, _preferred_port):
    DASH_PORT = _preferred_port
else:
    DASH_PORT = None
    for candidate in range(8051, 8061):
        if _is_port_available(_HOST, candidate):
            DASH_PORT = candidate
            break
    if DASH_PORT is None:
        DASH_PORT = 8051

# ========== HELPER FUNCTIONS ==========

def fetch_portfolio_data():
    """Fetch portfolio data from API"""
    try:
        response = requests.get(f"{API_URL}/portfolio")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching portfolio: {e}")
        return []

def fetch_sentiment_data():
    """Fetch sentiment data from API"""
    try:
        response = requests.get(f"{API_URL}/sentiment")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching sentiment: {e}")
        return []

def calculate_portfolio_metrics(portfolio):
    """Calculate portfolio metrics"""
    if not portfolio:
        return {
            "total_value": 0,
            "total_invested": 0,
            "total_gain_loss": 0,
            "gain_loss_percentage": 0
        }

    total_value = 0.0
    total_invested = 0.0
    for row in portfolio:
        qty = float(row.get("quantity") or 0)
        purchase = float(row.get("purchase_price") or 0)
        current = float(row.get("current_price") or 0)
        total_value += qty * current
        total_invested += qty * purchase

    total_gain_loss = total_value - total_invested
    gain_loss_percentage = (total_gain_loss / total_invested * 100.0) if total_invested > 0 else 0.0

    return {
        "total_value": total_value,
        "total_invested": total_invested,
        "total_gain_loss": total_gain_loss,
        "gain_loss_percentage": gain_loss_percentage,
    }

# ========== APP LAYOUT ==========

app.layout = dbc.Container(
    [
        dcc.Interval(id="interval-component", interval=5000, n_intervals=0),
        dcc.Store(id="selected-holding-store"),
        dbc.NavbarSimple(
            brand="Crypto Portfolio Dashboard",
            brand_href="#",
            color="dark",
            dark=True,
            className="mb-4",
        ),
        dbc.Row(id="metrics-cards", className="g-3 mb-4"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(id="portfolio-allocation-pie", config={"displayModeBar": False})),
                        className="h-100",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(id="gain-loss-bar", config={"displayModeBar": False})),
                        className="h-100",
                    ),
                    md=6,
                ),
            ],
            className="g-4 mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(id="price-performance-line", config={"displayModeBar": False})),
                        className="h-100",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(id="sentiment-scatter", config={"displayModeBar": False})),
                        className="h-100",
                    ),
                    md=6,
                ),
            ],
            className="g-4 mb-4",
        ),
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.Div("Manage Holdings", className="h5 mb-0"),
                        html.Div(
                            "Select a row to edit or delete. Update supports quantity, purchase price, current price, and category.",
                            className="text-body-secondary",
                        ),
                    ]
                ),
                dbc.CardBody(
                    [
                        dash_table.DataTable(
                            id="holdings-table",
                            columns=[
                                {"name": "Symbol", "id": "crypto_symbol"},
                                {"name": "Name", "id": "crypto_name"},
                                {"name": "Quantity", "id": "quantity", "type": "numeric"},
                                {"name": "Purchase Price", "id": "purchase_price", "type": "numeric"},
                                {"name": "Current Price", "id": "current_price", "type": "numeric"},
                                {"name": "Category", "id": "category"},
                            ],
                            data=[],
                            row_selectable="single",
                            selected_rows=[],
                            page_size=10,
                            style_as_list_view=True,
                            style_table={"overflowX": "auto"},
                            style_cell={"padding": "0.6rem", "textAlign": "left"},
                            style_header={"fontWeight": "600"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Selected Symbol", html_for="edit-symbol"),
                                        dbc.Input(
                                            id="edit-symbol",
                                            type="text",
                                            placeholder="Select a row",
                                            readonly=True,
                                        ),
                                    ],
                                    md=2,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Quantity", html_for="edit-quantity"),
                                        dbc.Input(id="edit-quantity", type="number"),
                                    ],
                                    md=2,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Purchase Price (USD)", html_for="edit-purchase-price"),
                                        dbc.Input(id="edit-purchase-price", type="number"),
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Current Price (USD)", html_for="edit-current-price"),
                                        dbc.Input(id="edit-current-price", type="number"),
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Category", html_for="edit-category"),
                                        dbc.Input(id="edit-category", type="text", placeholder="user_added"),
                                    ],
                                    md=2,
                                ),
                            ],
                            className="g-3 mt-1",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button("Update", id="update-button", n_clicks=0, color="primary"),
                                    width="auto",
                                ),
                                dbc.Col(
                                    dbc.Button("Delete", id="delete-button", n_clicks=0, color="danger"),
                                    width="auto",
                                ),
                                dbc.Col(html.Div(id="manage-status"), className="d-flex align-items-center"),
                            ],
                            className="g-2 mt-3",
                        ),
                    ]
                ),
            ],
            className="mb-4",
        ),
        dbc.Card(
            [
                dbc.CardHeader(html.Div("Add New Holding", className="h5 mb-0")),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Crypto Symbol", html_for="symbol-input"),
                                        dbc.Input(id="symbol-input", type="text", placeholder="BTC"),
                                    ],
                                    md=2,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Quantity", html_for="quantity-input"),
                                        dbc.Input(id="quantity-input", type="number", placeholder="0.5"),
                                    ],
                                    md=2,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Purchase Price (USD)", html_for="purchase-price-input"),
                                        dbc.Input(id="purchase-price-input", type="number", placeholder="45000"),
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Current Price (USD)", html_for="current-price-input"),
                                        dbc.Input(id="current-price-input", type="number", placeholder="50000"),
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "Add Holding",
                                        id="add-button",
                                        n_clicks=0,
                                        color="success",
                                        className="mt-4",
                                    ),
                                    md=2,
                                ),
                            ],
                            className="g-3",
                        ),
                        html.Div(id="add-status", className="mt-3"),
                    ]
                ),
            ]
        ),
    ],
    fluid=True,
    className="py-3",
)

# ========== CALLBACKS ==========

@callback(
    [Output('metrics-cards', 'children'),
     Output('portfolio-allocation-pie', 'figure'),
     Output('gain-loss-bar', 'figure'),
     Output('price-performance-line', 'figure'),
     Output('sentiment-scatter', 'figure'),
     Output('holdings-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    portfolio = fetch_portfolio_data()
    sentiment = fetch_sentiment_data()
    
    # Calculate metrics
    metrics = calculate_portfolio_metrics(portfolio)
    
    # Metrics cards
    metric_cards = [
        create_metric_card("Total Portfolio Value", f"${metrics['total_value']:,.2f}", "success"),
        create_metric_card("Total Invested", f"${metrics['total_invested']:,.2f}", "primary"),
        create_metric_card(
            "Gain/Loss",
            f"${metrics['total_gain_loss']:,.2f}",
            "danger" if metrics["total_gain_loss"] < 0 else "success",
        ),
        create_metric_card(
            "Return %",
            f"{metrics['gain_loss_percentage']:.2f}%",
            "danger" if metrics["gain_loss_percentage"] < 0 else "success",
        ),
    ]
    
    # Portfolio Allocation Pie Chart
    if portfolio:
        labels = [p.get("crypto_name") or p.get("crypto_symbol") or "" for p in portfolio]
        values = [float(p.get("quantity") or 0) * float(p.get("current_price") or 0) for p in portfolio]
        pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.35)])
        pie_fig.update_layout(title="Portfolio Allocation by Value", template="plotly_white")
    else:
        pie_fig = go.Figure().add_annotation(text="No data available")
    
    # Gain/Loss Bar Chart
    if portfolio:
        names = [p.get("crypto_name") or p.get("crypto_symbol") or "" for p in portfolio]
        gains = [
            (float(p.get("quantity") or 0) * float(p.get("current_price") or 0))
            - (float(p.get("quantity") or 0) * float(p.get("purchase_price") or 0))
            for p in portfolio
        ]
        colors = ["#dc3545" if x < 0 else "#198754" for x in gains]
        bar_fig = go.Figure(data=[
            go.Bar(x=names, y=gains, marker_color=colors)
        ])
        bar_fig.update_layout(
            title="Gain/Loss by Holding",
            xaxis_title="Crypto",
            yaxis_title="Gain/Loss (USD)",
            hovermode="x unified",
            template="plotly_white",
        )
    else:
        bar_fig = go.Figure().add_annotation(text="No data available")
    
    # Price Performance Line Chart
    if portfolio:
        names = [p.get("crypto_name") or p.get("crypto_symbol") or "" for p in portfolio]
        current_prices = [float(p.get("current_price") or 0) for p in portfolio]
        purchase_prices = [float(p.get("purchase_price") or 0) for p in portfolio]
        line_fig = go.Figure(data=[
            go.Scatter(x=names, y=current_prices, mode="lines+markers", name="Current Price")
        ])
        line_fig.add_scatter(x=names, y=purchase_prices, mode="lines+markers", name="Purchase Price")
        line_fig.update_layout(
            title="Price Comparison: Current vs Purchase",
            xaxis_title="Crypto",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            template="plotly_white",
        )
    else:
        line_fig = go.Figure().add_annotation(text="No data available")
    
    # Sentiment Scatter Plot
    if sentiment:
        x = [float(s.get("sentiment_score") or 0) for s in sentiment]
        y = [int(s.get("mention_count") or 0) for s in sentiment]
        c = [float(s.get("positive_percentage") or 0) for s in sentiment]
        text = [
            f"{(s.get('crypto_symbol') or '').upper()} ({s.get('source') or ''})"
            for s in sentiment
        ]

        # Keep marker sizes sane (mentions can be large).
        sizes = [max(6, min(40, int((m or 0) ** 0.5))) for m in y]

        scatter_fig = go.Figure(
            data=[
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    text=text,
                    hovertemplate="%{text}<br>Sentiment=%{x}<br>Mentions=%{y}<extra></extra>",
                    marker={
                        "size": sizes,
                        "color": c,
                        "colorscale": "RdYlGn",
                        "showscale": True,
                        "colorbar": {"title": "Positive %"},
                    },
                )
            ]
        )
        scatter_fig.update_layout(
            title="Market Sentiment Analysis",
            xaxis_title="Sentiment Score (-1 to 1)",
            yaxis_title="Mention Count",
            template="plotly_white",
        )
    else:
        scatter_fig = go.Figure().add_annotation(text="No sentiment data available")
    
    return metric_cards, pie_fig, bar_fig, line_fig, scatter_fig, portfolio

@callback(
    Output('add-status', 'children'),
    Input('add-button', 'n_clicks'),
    [dash.dependencies.State('symbol-input', 'value'),
     dash.dependencies.State('quantity-input', 'value'),
     dash.dependencies.State('purchase-price-input', 'value'),
     dash.dependencies.State('current-price-input', 'value')],
    prevent_initial_call=True
)
def add_holding(n_clicks, symbol, quantity, purchase_price, current_price):
    if not all([symbol, quantity, purchase_price]):
        return "❌ Please fill symbol, quantity, and purchase price"
    
    try:
        payload = {
            "crypto_symbol": symbol.upper(),
            "crypto_name": symbol.upper(),
            "quantity": quantity,
            "purchase_price": purchase_price,
            "current_price": current_price if current_price is not None else purchase_price,
            "category": "user_added"
        }
        response = requests.post(f"{API_URL}/portfolio", json=payload)
        if response.status_code == 201:
            return "✅ Holding added successfully!"
        else:
            return f"❌ Error: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@callback(
    Output("selected-holding-store", "data"),
    Input("holdings-table", "selected_rows"),
    State("holdings-table", "data"),
)
def store_selected_holding(selected_rows, table_data):
    if not selected_rows:
        return None
    idx = selected_rows[0]
    if table_data is None or idx >= len(table_data):
        return None
    return table_data[idx]


@callback(
    [
        Output("edit-symbol", "value"),
        Output("edit-quantity", "value"),
        Output("edit-purchase-price", "value"),
        Output("edit-current-price", "value"),
        Output("edit-category", "value"),
    ],
    Input("selected-holding-store", "data"),
)
def populate_edit_fields(selected):
    if not selected:
        return None, None, None, None, None
    return (
        selected.get("crypto_symbol"),
        selected.get("quantity"),
        selected.get("purchase_price"),
        selected.get("current_price"),
        selected.get("category"),
    )


@callback(
    Output("manage-status", "children"),
    [Input("update-button", "n_clicks"), Input("delete-button", "n_clicks")],
    [
        State("selected-holding-store", "data"),
        State("edit-symbol", "value"),
        State("edit-quantity", "value"),
        State("edit-purchase-price", "value"),
        State("edit-current-price", "value"),
        State("edit-category", "value"),
    ],
    prevent_initial_call=True,
)
def update_or_delete_holding(update_clicks, delete_clicks, selected_row, symbol, quantity, purchase_price, current_price, category):
    triggered = dash.callback_context.triggered
    if not triggered:
        raise PreventUpdate

    selected_symbol = None
    if isinstance(selected_row, dict):
        selected_symbol = selected_row.get("crypto_symbol")

    effective_symbol = selected_symbol or symbol
    if not effective_symbol:
        return html.Span("❌ Select a holding first.", style={"color": "#dc3545"})

    effective_symbol = str(effective_symbol).upper()

    trigger_id = triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "delete-button":
        try:
            resp = requests.delete(f"{API_URL}/portfolio/{effective_symbol}")
            if resp.status_code in (200, 204):
                return html.Span(f"✅ Deleted {effective_symbol}.", style={"color": "#28a745"})
            detail = None
            try:
                detail = resp.json().get("detail")
            except Exception:
                pass
            return html.Span(f"❌ Delete failed: {detail or resp.text}", style={"color": "#dc3545"})
        except Exception as e:
            return html.Span(f"❌ Delete error: {str(e)}", style={"color": "#dc3545"})

    if trigger_id == "update-button":
        payload = {}
        if quantity is not None:
            payload["quantity"] = quantity
        if purchase_price is not None:
            payload["purchase_price"] = purchase_price
        if current_price is not None:
            payload["current_price"] = current_price
        if category is not None and str(category).strip() != "":
            payload["category"] = category

        if not payload:
            return html.Span("❌ Nothing to update.", style={"color": "#dc3545"})

        try:
            resp = requests.put(f"{API_URL}/portfolio/{effective_symbol}", json=payload)
            if resp.status_code == 200:
                return html.Span(f"✅ Updated {effective_symbol}.", style={"color": "#28a745"})
            detail = None
            try:
                detail = resp.json().get("detail")
            except Exception:
                pass
            return html.Span(f"❌ Update failed: {detail or resp.text}", style={"color": "#dc3545"})
        except Exception as e:
            return html.Span(f"❌ Update error: {str(e)}", style={"color": "#dc3545"})

    raise PreventUpdate

def create_metric_card(title: str, value: str, variant: str):
    """Create a metric card (Bootstrap-styled)."""
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(title, className="text-body-secondary small"),
                    html.Div(value, className="h3 mb-0"),
                ]
            ),
            color=variant,
            outline=True,
        ),
        md=3,
        sm=6,
        xs=12,
    )

if __name__ == '__main__':
    if serve is not None:
        serve(app.server, host=_HOST, port=DASH_PORT)
    else:
        # Dash 3.x prefers `app.run(...)`; Dash 2.x uses `app.run_server(...)`.
        run = getattr(app, "run", None)
        if callable(run):
            run(host=_HOST, port=DASH_PORT, debug=False)
        else:
            app.run_server(host=_HOST, port=DASH_PORT, debug=False, use_reloader=False)