import numpy as np
from rich.console import Console
import plotly.graph_objs as go

# ===============================================================
# Plotting Functions
# ===============================================================

console = Console()


def human_readable(num):
    """Format large numbers into human-readable form (e.g., 1.5K, 2.3M, 1.1B)."""
    for unit, divisor in [("B", 1e9), ("M", 1e6), ("K", 1e3)]:
        if num >= divisor:
            return f"{num/divisor:.1f}{unit}"
    return str(int(num))


def fmt_list(values):
    """Round and convert a list of numbers to human-readable strings."""
    return [human_readable(round(v, 0)) for v in values]


def make_base_plot(title, xaxis="Number of reads", yaxis="Number of CpGs"):
    """Create a preformatted Plotly figure."""
    fig = go.Figure()
    fig.update_xaxes(title_text=xaxis, showgrid=True)
    fig.update_yaxes(title_text=yaxis, showgrid=True)
    fig.update_layout(
        title=dict(text=title, x=0.5, y=0.9),
        width=950,
        height=620,
        template="plotly_white",
        showlegend=False,
    )
    return fig


def plot_fallback(plot_obj):
    """Fallback plot when curve fitting fails."""
    x_reads = fmt_list([x * plot_obj.reads for x in plot_obj.x_data])
    y_cpgs = fmt_list(plot_obj.y_data)

    fig = make_base_plot(f"{plot_obj.title}<br><sup>{plot_obj.error_msg}</sup>")
    fig.add_trace(
        go.Scatter(
            x=x_reads,
            y=plot_obj.y_data,
            mode="lines",
            name="Observed data",
            customdata=np.column_stack((y_cpgs, plot_obj.x_data)),
            hovertemplate=(
                "<b>Observed</b><br>"
                "Number of reads: %{x}<br>"
                "Number CpGs: %{customdata[0]}<br>"
                "Downsampling: %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

    fig.write_html(plot_obj.output_path)
    print(f"⚠️ Curve fitting failed but plot saved anyway to: {plot_obj.output_path}.")


def plot_fitted_data(plot_obj):
    """Plot observed and predicted CpG values based on fitted asymptotic growth.
    Arguments:
        plot_obj: PlotObject containing all necessary data for plotting.
        x_all: List of downsampling percentages (going from 0.0 to 2.0).
        x_all_obs: List of observed downsampling percentages (going from 0.0 to 1.0).
        y_all: List of CpG counts corresponding to x_all.
        y_all_obs: List of observed CpG counts (corresponding to x_all_obs). While y_all
        contains only predicted values even for the observed points, y_all_obs contains
        the actual observed CpG counts.
        reads_all_fmt: list of number of reads that correspond to x_all, formatted to
        human-readable strings.
        n_obs: Number of observed data points.
    """
    # Extract data from plot object
    x_all = plot_obj.x_data
    x_all_obs = [x for x in x_all if x <= 1.0]
    y_all = plot_obj.y_data
    y_all_obs = plot_obj.observed_y

    # Format the data to human-readable strings
    y_all_fmt = fmt_list(y_all)
    y_all_obs_fmt = fmt_list(y_all_obs)
    reads_all_fmt = fmt_list([x * plot_obj.reads for x in x_all])
    n_obs = plot_obj.is_predicted.count(False)

    # Observed
    fig = make_base_plot(plot_obj.title)
    fig.add_trace(
        go.Scatter(
            x=reads_all_fmt[0:n_obs],
            y=y_all_obs,
            mode="markers",
            name="Observed data",
            marker=dict(
                size=9,
                color="#d62728",
                line=dict(width=1, color="white"),
            ),
            customdata=np.column_stack((y_all_obs_fmt, x_all_obs)),
            hovertemplate=(
                "<b>Observed</b><br>"
                "Number of reads: %{x}<br>"
                "Number CpGs: %{customdata[0]}<br>"
                "Downsampling: %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

    # Predicted
    fig.add_trace(
        go.Scatter(
            x=reads_all_fmt,
            y=y_all,
            mode="lines",
            name="Predicted data",
            customdata=np.column_stack((y_all_fmt, plot_obj.saturations)),
            hovertemplate=(
                "<b>Predicted</b><br>"
                "Number of reads: %{x}<br>"
                "Number CpGs: %{customdata[0]}<br>"
                "Saturation: %{customdata[1]}%<br>"
                "<extra></extra>"
            ),
            line=dict(color="#1f77b4"),
        )
    )

    # Asymptote line: corresponds to theoretical maximum CpG count
    cpgs_found_index = n_obs - 1
    asympt_sat = plot_obj.saturations[cpgs_found_index]
    fig.add_hline(
        y=plot_obj.asymptote,
        line_dash="dash",
        annotation_text=(
            f"Asymptote = {human_readable(plot_obj.asymptote)} CpGs "
            f"(Saturation = {asympt_sat}%)"
        ),
        annotation_position="top right",
        annotation_yshift=10,  # push slightly above
    )

    fig.write_html(plot_obj.output_path)
    print(f"✅ Plot saved to: {plot_obj.output_path}")
