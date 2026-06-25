# plot_results.py

import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np

RESULT_DIR = "results"

CSV_FILE = os.path.join(RESULT_DIR, "benchmark.csv")
SUMMARY_FILE = os.path.join(RESULT_DIR, "summary.csv")

SIGN_VS_KEYSIZE_PLOT   = os.path.join(RESULT_DIR, "sign_delay_vs_keysize.png")
SIGN_VS_MSGSIZE_PLOT   = os.path.join(RESULT_DIR, "sign_delay_vs_msgsize.png")
VERIFY_VS_KEYSIZE_PLOT = os.path.join(RESULT_DIR, "verify_delay_vs_keysize.png")
VERIFY_VS_MSGSIZE_PLOT = os.path.join(RESULT_DIR, "verify_delay_vs_msgsize.png")
TX_VS_MSGSIZE_PLOT     = os.path.join(RESULT_DIR, "transmission_delay_vs_msgsize.png")
TX_VS_KEYSIZE_PLOT     = os.path.join(RESULT_DIR, "transmission_delay_vs_keysize.png")


# ==========================================================
# PAPER STYLE
# ==========================================================

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10
})


COLOR_MAP = {
    "SHA256": "#1f77b4",      # blue
    "SHA384": "#d62728",      # red
    "RIPEMD256": "#000000"    # black
}


def plot_graph(
    summary,
    group_col,
    value_col,
    error_col,
    title,
    xlabel,
    ylabel,
    output_path
):

    fig, ax = plt.subplots(figsize=(8, 5))

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    algorithms = sorted(summary["hash_algorithm"].unique())

    for algo in algorithms:

        data = (
            summary[summary["hash_algorithm"] == algo]
            .groupby(group_col)
            .agg({
                value_col: "mean",
                error_col: "mean"
            })
            .reset_index()
            .sort_values(group_col)
        )

        color = COLOR_MAP.get(algo, "black")

        x = data[group_col].values
        y = data[value_col].values

        # ==================================================
        # Smooth hanya untuk Message Size
        # ==================================================

        if group_col == "message_size" and len(x) >= 4:

            x_smooth = np.linspace(
                x.min(),
                x.max(),
                300
            )

            spline = make_interp_spline(
                x,
                y,
                k=3
            )

            y_smooth = spline(x_smooth)

            ax.plot(
                x_smooth,
                y_smooth,
                color=color,
                linewidth=2.0,
                label=algo,
                zorder=1
            )

        else:

            ax.plot(
                x,
                y,
                color=color,
                linewidth=2.0,
                label=algo,
                zorder=1
            )

        # ==================================================
        # Titik eksperimen asli
        # ==================================================

        ax.scatter(
            x,
            y,
            s=35,
            color=color,
            zorder=3
        )

        # ==================================================
        # 95% Confidence Interval
        # ==================================================

        ax.errorbar(
            x,
            y,
            yerr=data[error_col],
            fmt="none",
            ecolor=color,
            elinewidth=1.2,
            capsize=3,
            alpha=0.8,
            zorder=2
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_linewidth(1.0)
    ax.spines["bottom"].set_linewidth(1.0)

    ax.tick_params(
        axis="both",
        which="major",
        length=4,
        width=0.8
    )

    ax.grid(
        True,
        linestyle="--",
        linewidth=0.5,
        alpha=0.4
    )

    ax.set_title(
        title,
        fontweight="bold",
        pad=10
    )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.legend(
        loc="best",
        frameon=False
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=600,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Saved: {output_path}")


def main():

    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"{CSV_FILE} tidak ditemukan")

    print("Membaca benchmark.csv ...")

    df = pd.read_csv(CSV_FILE)

    # summary = (
    #     df.groupby(
    #         ["hash_algorithm", "key_size", "message_size"]
    #     )
    #     .agg(
    #         sign_delay_ms=("sign_delay_ms", "mean"),
    #         verify_delay_ms=("verify_delay_ms", "mean"),
    #         transmission_delay_ms=("transmission_delay_ms", "mean")
    #     )
    #     .reset_index()
    # )

    summary = (
        df.groupby(
            ["hash_algorithm", "key_size", "message_size"]
        )
        .agg(
            sign_delay_ms=("sign_delay_ms", "mean"),
            sign_std=("sign_delay_ms", "std"),

            verify_delay_ms=("verify_delay_ms", "mean"),
            verify_std=("verify_delay_ms", "std"),

            transmission_delay_ms=("transmission_delay_ms", "mean"),
            transmission_std=("transmission_delay_ms", "std")
        )
        .reset_index()
    )

    # ==================================================
    # 95% Confidence Interval
    # ==================================================

    N_SAMPLES = 100

    summary["sign_ci95"] = (
        1.96 * summary["sign_std"] / np.sqrt(N_SAMPLES)
    )

    summary["verify_ci95"] = (
        1.96 * summary["verify_std"] / np.sqrt(N_SAMPLES)
    )

    summary["transmission_ci95"] = (
        1.96 * summary["transmission_std"] / np.sqrt(N_SAMPLES)
    )

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    print(f"Summary disimpan: {SUMMARY_FILE}")

    # ==================================================
    # SIGN DELAY
    # ==================================================

    plot_graph(
        summary,
        group_col="key_size",
        value_col="sign_delay_ms",
        error_col="sign_ci95",
        title="Average Sign Delay vs Key Size",
        xlabel="Key Size (bit)",
        ylabel="Delay (ms)",
        output_path=SIGN_VS_KEYSIZE_PLOT
    )

    plot_graph(
        summary,
        group_col="message_size",
        value_col="sign_delay_ms",
        error_col="sign_ci95",
        title="Average Sign Delay vs Message Size",
        xlabel="Message Size (Byte)",
        ylabel="Delay (ms)",
        output_path=SIGN_VS_MSGSIZE_PLOT
    )

    # ==================================================
    # VERIFY DELAY
    # ==================================================

    plot_graph(
        summary,
        group_col="key_size",
        value_col="verify_delay_ms",
        error_col="verify_ci95",
        title="Average Verify Delay vs Key Size",
        xlabel="Key Size (bit)",
        ylabel="Delay (ms)",
        output_path=VERIFY_VS_KEYSIZE_PLOT
    )

    plot_graph(
        summary,
        group_col="message_size",
        value_col="verify_delay_ms",
        error_col="verify_ci95",
        title="Average Verify Delay vs Message Size",
        xlabel="Message Size (Byte)",
        ylabel="Delay (ms)",
        output_path=VERIFY_VS_MSGSIZE_PLOT
    )

    # ==================================================
    # TRANSMISSION DELAY
    # ==================================================

    plot_graph(
        summary,
        group_col="message_size",
        value_col="transmission_delay_ms",
        error_col="transmission_ci95",
        title="Average Transmission Delay vs Message Size",
        xlabel="Message Size (Byte)",
        ylabel="Delay (ms)",
        output_path=TX_VS_MSGSIZE_PLOT
    )

    plot_graph(
        summary,
        group_col="key_size",
        value_col="transmission_delay_ms",
        error_col="transmission_ci95",
        title="Average Transmission Delay vs Key Size",
        xlabel="Key Size (bit)",
        ylabel="Delay (ms)",
        output_path=TX_VS_KEYSIZE_PLOT
    )

    print("\nSelesai. Total 6 grafik telah disimpan.")


if __name__ == "__main__":
    main()