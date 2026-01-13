#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created: Sun Mar 14 12:03:11 2021

@author: evan
"""

import subprocess

import numpy as np
import pandas as pd
from matplotlib import gridspec
from matplotlib import pyplot as plt


def plot():
    plt.rc("xtick", labelsize=6)
    plt.rc("ytick", labelsize=6)
    df = pd.read_csv(
        "/home/evan/.mvwt/weight_log.csv",
        dtype={"Value": np.float64},
        parse_dates=["Date"],
    )
    df = df[df.Measurement.isin(["Bodyweight"])]
    df.sort_values(by="Date", inplace=True)

    diet_df = pd.read_csv(
        "/home/evan/.mvwt/diet_log.csv", dtype={"Value": int}, parse_dates=["Date"]
    )
    diet_df.sort_values(by="Date", inplace=True)

    rolling_diet = diet_df[["Date", "Value"]].rolling("7d", on="Date").mean()

    periods = [30, 365, 1825]
    titles = ["month", "year", "5 years"]

    height_ratios = [4 if x % 2 == 0 else 1 for x in range(len(periods) * 2)]
    fig = plt.figure(dpi=300, figsize=(6, 10))
    spec = gridspec.GridSpec(
        ncols=1,
        nrows=len(periods) * 2,
        height_ratios=height_ratios,
        figure=fig,
        hspace=0.8,
    )

    for i, per in enumerate(periods):
        df_plot = df[pd.Timestamp.now() - df.Date < pd.Timedelta(per, "D")]

        diet_df_plot = diet_df[
            pd.Timestamp.now() - diet_df.Date < pd.Timedelta(per, "D")
        ]

        window = int(len(df_plot) / 6)
        sub_rolling = df_plot.rolling(window, on="Date", center=True).mean()

        rolling_diet_df_plot = rolling_diet[
            pd.Timestamp.now() - rolling_diet.Date < pd.Timedelta(per, "D")
        ]

        ax = fig.add_subplot(spec[i * 2])
        ax.plot(df_plot.Date, df_plot.Value, "k.")
        ax.plot(sub_rolling.Date, sub_rolling.Value, c="#15B01A")
        ax.set_title(titles[i])
        ax.xaxis.set_tick_params(rotation=30)

        df_plot["diet"] = df_plot.Date.map(
            dict(zip(diet_df_plot.Date, diet_df_plot.Value))
        )

        df_plot["rolling_diet"] = df_plot.Date.map(
            dict(zip(rolling_diet_df_plot.Date, rolling_diet_df_plot.Value))
        )

        ax = fig.add_subplot(spec[i * 2 + 1])
        ax.pcolormesh([df_plot.diet, df_plot.rolling_diet], cmap="RdYlGn_r")
        ax.axes.yaxis.set_visible(False)
        ax.axes.xaxis.set_visible(False)

    plt.tight_layout()
    plt.savefig("/home/evan/.mvwt/plots/weight_plot.png", dpi=300)
    subprocess.run(["xdg-open", "/home/evan/.mvwt/plots/weight_plot.png"], check=True)
