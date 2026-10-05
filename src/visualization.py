"""Plotly charts used by the dashboard and the notebook."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEMPLATE = "plotly_white"


def cumulative_returns_chart(wealth: pd.DataFrame) -> go.Figure:
    """Growth of 1 TL for the portfolio and benchmark."""
    fig = go.Figure()
    for col in wealth.columns:
        width = 3 if col == "Portfolio" else 1.8
        fig.add_trace(go.Scatter(x=wealth.index, y=wealth[col], name=col, line=dict(width=width)))
    fig.update_layout(
        title="Growth of 1 TL", template=TEMPLATE,
        yaxis_title="Value (TL)", hovermode="x unified",
    )
    return fig


def drawdown_chart(drawdowns: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col in drawdowns.columns:
        fig.add_trace(go.Scatter(
            x=drawdowns.index, y=drawdowns[col], name=col, fill="tozeroy", opacity=0.6,
        ))
    fig.update_layout(
        title="Drawdown", template=TEMPLATE,
        yaxis_tickformat=".0%", hovermode="x unified",
    )
    return fig


def allocation_pie(weights: pd.Series, names: dict | None = None) -> go.Figure:
    labels = [names.get(t, t) for t in weights.index] if names else list(weights.index)
    fig = px.pie(values=weights.values, names=labels, hole=0.45)
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(title="Asset Allocation", template=TEMPLATE)
    return fig


def correlation_heatmap(corr: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
    )
    fig.update_layout(title="Correlation Matrix", template=TEMPLATE)
    return fig


def monthly_returns_chart(monthly: pd.Series) -> go.Figure:
    colors = ["#2e7d32" if v >= 0 else "#c62828" for v in monthly.values]
    fig = go.Figure(go.Bar(x=monthly.index, y=monthly.values, marker_color=colors))
    fig.update_layout(
        title="Portfolio Monthly Returns", template=TEMPLATE, yaxis_tickformat=".0%",
    )
    return fig


def efficient_frontier_chart(
    random_df: pd.DataFrame,
    frontier_df: pd.DataFrame,
    special_points: dict[str, tuple[float, float]],
    asset_points: pd.DataFrame | None = None,
) -> go.Figure:
    """special_points: {label: (volatility, return)}; asset_points has 'return' & 'volatility'."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=random_df["volatility"], y=random_df["return"], mode="markers",
        marker=dict(
            size=4, color=random_df["sharpe"], colorscale="Viridis",
            showscale=True, colorbar=dict(title="Sharpe"), opacity=0.6,
        ),
        name="Random portfolios",
    ))

    fig.add_trace(go.Scatter(
        x=frontier_df["volatility"], y=frontier_df["return"], mode="lines",
        line=dict(color="black", width=3), name="Efficient Frontier",
    ))

    if asset_points is not None:
        fig.add_trace(go.Scatter(
            x=asset_points["volatility"], y=asset_points["return"],
            mode="markers+text", text=asset_points.index, textposition="top center",
            marker=dict(size=9, color="gray", symbol="diamond"), name="Individual assets",
        ))

    palette = {"Max Sharpe": "red", "Min Volatility": "blue", "Current Portfolio": "orange"}
    for label, (vol, ret) in special_points.items():
        fig.add_trace(go.Scatter(
            x=[vol], y=[ret], mode="markers", name=label,
            marker=dict(size=16, symbol="star", color=palette.get(label, "purple"),
                        line=dict(width=1, color="black")),
        ))

    fig.update_layout(
        title="Efficient Frontier", template=TEMPLATE,
        xaxis_title="Risk (Annualized Volatility)", yaxis_title="Expected Return (Annualized)",
        xaxis_tickformat=".0%", yaxis_tickformat=".0%",
    )
    return fig