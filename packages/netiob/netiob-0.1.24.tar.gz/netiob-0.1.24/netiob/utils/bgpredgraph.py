from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from plotly.offline import plot
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def bg_prediction_graph(prediction_result: dict, scenario_label: str = "BG Prediction", fig_show: bool=True):

    if prediction_result.get("predBGs"):
        baseline_prediction_deliver_at = datetime.fromisoformat(prediction_result.get("deliverAt").replace("Z", "+00:00"))
        baseline_prediction_time_step = timedelta(minutes=5)  # you had baseline_prediction_time_steps, should be _step

        # Define color mapping for each prediction type
        color_map = {
            'IOB': 'rgba(31, 119, 180, 0.8)',   # Blue - insulin action
            'ZT': 'rgba(255, 127, 14, 0.8)',    # Orange - zero temp
            'COB': 'rgba(44, 160, 44, 0.8)',    # Green - carbs
            'UAM': 'rgba(214, 39, 40, 0.8)'     # Red - unannounced meals
        }

        baseline_prediction_fig = go.Figure()

        # Add traces for each prediction curve
        for label, values in prediction_result["predBGs"].items():
            times = [baseline_prediction_deliver_at + i * baseline_prediction_time_step for i in range(len(values))]
            baseline_prediction_fig.add_trace(go.Scatter(
                x=times,
                y=values,
                mode='lines+markers',
                name=label,
                line=dict(color=color_map.get(label, '#333333')),  # fallback to dark grey
                showlegend=True
            ))

        baseline_prediction_fig.add_hline(
            y=prediction_result["target_bg"],
            line=dict(color="green", dash="dot"),
            annotation_text=f"Target BG: {prediction_result['target_bg']}"
        )
        baseline_prediction_fig.add_trace(go.Scatter(
            x=[baseline_prediction_deliver_at + baseline_prediction_time_step * (
                    len(prediction_result["predBGs"]["ZT"]) - 1)],
            y=[prediction_result["eventualBG"]],
            mode='markers+text',
            text=[f"Eventual BG: {prediction_result['eventualBG']}"],
            textposition="top center",
            marker=dict(size=10, color="red", symbol="x"),
            name="Eventual BG",
            showlegend=True
        ))

        baseline_prediction_fig.update_layout(
            title=f"{scenario_label} (deliverAt {baseline_prediction_deliver_at.strftime('%Y-%m-%d %H:%M:%S')})",
            legend=dict(title="Legend", orientation="h", y=-0.2),
            xaxis=dict(title="Time"),
            yaxis=dict(title="BG (mg/dL)", range=[0, 400])
        )

        if fig_show:
            baseline_prediction_fig.show()
    else:
        print(f"{scenario_label} prediction returned: {prediction_result}\n")
    