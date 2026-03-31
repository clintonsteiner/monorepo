import os
import polars as pl
from dash import Dash, html, dcc, Input, Output, callback, dash_table
import plotly.graph_objects as go

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/newsdb")
app = Dash(__name__)
server = app.server

app.layout = html.Div(style={'backgroundColor': '#f4f7f9', 'padding': '20px', 'fontFamily': 'sans-serif'}, children=[
    html.H2("Media Coverage Intelligence", style={'textAlign': 'center', 'color': '#2c3e50'}),

    # Summary Stats
    html.Div(id='stats-container', style={'marginBottom': '20px'}),

    # Control Panel
    html.Div(style={'display': 'flex', 'gap': '20px', 'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
        html.Div(style={'flex': '1'}, children=[
            html.Label("1. Analyze Window:", style={'fontWeight': 'bold'}),
            dcc.DatePickerRange(id='date-range', start_date='2022-02-24', end_date='2022-03-15')
        ]),
        html.Div(style={'flex': '1'}, children=[
            html.Label("2. Smoothing (Rolling Average):", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='smooth-slider',
                min=0, max=48, step=4, value=8,
                marks={0: 'None', 8: '4h', 24: '12h', 48: '24h'}
            )
        ])
    ]),

    dcc.Graph(id='chart-main', style={'marginTop': '20px'})
])

@callback(
    [Output('chart-main', 'figure'), Output('stats-container', 'children')],
    [Input('date-range', 'start_date'), Input('date-range', 'end_date'), Input('smooth-slider', 'value')]
)
def update_dashboard(start, end, smooth_window):
    # SQL Aggregation (30m buckets)
    query = f"""
        SELECT 
            date_bin('30 minutes', timestamp, TIMESTAMP '2022-01-01') AS time_bucket,
            network,
            COUNT(*) as count
        FROM raw_mentions 
        WHERE topic = 'Ukraine' AND timestamp BETWEEN '{start}' AND '{end} 23:59:59'
        GROUP BY 1, 2
        ORDER BY 1 ASC
    """
    try:
        df = pl.read_database_uri(query, DB_URL, engine="adbc")
    except:
        return go.Figure(), "Waiting for database..."

    if df.is_empty():
        return go.Figure(), "No data found."

    # --- SUMMARY STATS ---
    summary = df.group_by("network").agg([
        pl.sum("count").alias("Total"),
        pl.max("count").alias("Peak")
    ]).to_dicts()
    
    stats_table = dash_table.DataTable(
        data=summary, columns=[{"name": i, "id": i} for i in ["network", "Total", "Peak"]],
        style_cell={'textAlign': 'center', 'padding': '5px'}
    )

    # --- CHART LOGIC ---
    fig = go.Figure()
    colors = {'CNN': '#3b5b92', 'FOXNEWS': '#d95f52', 'MSNBC': '#4dbd9c'}

    for net in ['CNN', 'FOXNEWS', 'MSNBC']:
        net_df = df.filter(pl.col("network") == net).sort("time_bucket")
        
        # Original Raw Data
        y_val = net_df['count']
        opacity = 0.3 if smooth_window > 0 else 1.0
        
        # Add the raw spikes (as a faded area if smoothing is on)
        fig.add_trace(go.Scatter(
            x=net_df['time_bucket'], y=y_val, name=f"{net} (Raw)",
            line=dict(width=1, color=colors[net]),
            opacity=opacity, showlegend=(smooth_window == 0)
        ))

        # POLARS MAGIC: Add Moving Average Line
        if smooth_window > 0:
            # rolling_mean needs a window size (integer of rows)
            ma_val = net_df.select(
                pl.col("count").rolling_mean(window_size=smooth_window, center=True)
            ).to_series()

            fig.add_trace(go.Scatter(
                x=net_df['time_bucket'], y=ma_val, name=f"{net} Trend",
                line=dict(width=4, color=colors[net]),
                mode='lines'
            ))

    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor='white',
        xaxis=dict(rangeslider=dict(visible=True)),
        yaxis=dict(title="Mentions per 30m"),
        legend=dict(orientation="h", y=1.1)
    )

    return fig, stats_table

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
