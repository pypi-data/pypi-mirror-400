import json
import os
from pathlib import Path
import sys
from typing import Optional
import duckdb
from pydantic import BaseModel
import yaml
import altair as alt

from champions.model.champions import Champion, Champions
from champions.model.datacard import DataCard
from champions.model.settings import EvalSettings
from champions.service.darkwing import Darkwing
import polars as pl
import logging

logger = logging.getLogger(__name__)


class Eval(BaseModel):
    dc: DataCard
    settings: EvalSettings
    darkwing: Optional[Darkwing] = None

    def model_post_init(self, __context) -> None:
        self.darkwing = Darkwing(dc=self.dc)
        os.makedirs(self.settings.out_folder, exist_ok=True)
        super().model_post_init(__context)

    def run(self):
        logger.info("Start Eval")

        df_res = self.darkwing._get_pl_eval_df(col_sql=self.dc.target.feature_name)

        # df_res = pl.read_parquet("test.parquet")
        roc_plots = None

        for target in self.dc.target.values:
            logger.info(f"Evaluate target {target}")
            target_champions = self.load_champions(target=f"{target}")

            sr = self.darkwing.get_eval_sr(
                champions=target_champions,
                max_parallel_where=self.settings.max_parallel_where,
            )
            df_res = df_res.with_columns(sr)
            hist_plot = self.plot_hist(df=df_res, target_label=target, stack=None)
            hist_plot.save(self.settings.out_folder / f"{target}_hist.html")

            rel_pdf_plot = self.plot_hist(
                df=df_res, target_label=target, stack="normalize"
            )
            rel_pdf_plot.save(self.settings.out_folder / f"{target}_pdf_rel.html")

            new_roc_plot = self.plot_roc(df=df_res, target_label=target)
            new_roc_plot.save(self.settings.out_folder / f"{target}_roc.html")
            if roc_plots is None:
                roc_plots = new_roc_plot
            else:
                roc_plots = roc_plots + new_roc_plot

        roc_plots.save(self.settings.out_folder / "all_roc.html")

        if len(self.dc.target.values) > 1:
            df_multi_res = self.add_multi_class_result(
                df=df_res, target_values=self.dc.target.values
            )
            df_res = pl.concat(
                [df_res, df_multi_res],
                how="horizontal",
            )

            multi_res_plot = (
                df_res.group_by(self.dc.target.feature_name)
                .agg(pl.col("correct").sum() / pl.count())
                .sort(self.dc.target.feature_name)
                .plot.bar(x=self.dc.target.feature_name, y="correct")
            )
            prec = df_res["correct"].sum() / df_res["correct"].count()
            all_pred_labels = (
                alt.Chart(pl.DataFrame({"correct": [prec]}))
                .mark_rule()
                .encode(y="correct")
            )
            (multi_res_plot + all_pred_labels).save(
                self.settings.out_folder / "multi_class_result.html"
            )
        logger.info(f"{df_res}")

    def add_multi_class_result(self, df: pl.DataFrame, target_values: list[str | int]):
        greates = ", ".join([f'"{value}"' for value in target_values])
        cases = [
            f'WHEN "{value}" = GREATEST({greates}) THEN {value}'
            for value in target_values
        ]
        p_name = f"predicted_{self.dc.target.feature_name}"
        return (
            duckdb.sql(f"""
            SELECT
                {self.dc.target.feature_name},
                CASE
                    {" \n ".join(cases)}
                END AS {p_name}
            FROM df
        """)
            .pl()
            .with_columns(
                (pl.col(f"{self.dc.target.feature_name}") == pl.col(p_name))
                .cast(pl.Int64)
                .alias("correct")
            )
            .select(p_name, "correct")
        )

    def load_champions(self, target: str) -> Champions:
        data = {}
        for folder in self.settings.in_folders:
            target_folder = folder / target
            if not target_folder.exists():
                logger.error(f"folder {target_folder} does not exist. ")
                break
            for file in target_folder.glob("*.json"):
                f_name = str(file).rstrip(".json").replace("/", "_")
                with file.open("rb") as f:
                    logger.info(f"Load Champion from {file}")
                    data[f_name] = Champion.model_validate_json(f.read())
        return Champions(champions=data, target=target)

    def plot_hist(
        self, df: pl.DataFrame, target_label: str | int, stack: bool | str | None
    ):
        return (
            df.with_columns(
                pl.col(self.dc.target.feature_name).eq(target_label).alias("Result")
            )
            .plot.bar(
                x=alt.X(f"{target_label}", bin=alt.Bin(maxbins=40)),
                y=alt.Y("count()", stack=stack),
                color="Result",
            )
            .properties(title="Histogramm der Werte")
        ).configure_mark(
            opacity=0.7  # Transparenz einstellen, kann angepasst werden
        )

    def plot_roc(self, df: pl.DataFrame, target_label: str | int):
        score_feat = f"{target_label}"

        df_plot = duckdb.sql(f"""
            SELECT fp,tp
            FROM (
                SELECT
                    ROUND(SUM(CASE WHEN {self.dc.target.feature_name} == '{target_label}' THEN 1 ELSE 0 END) OVER (ORDER BY "{score_feat}" DESC) / SUM(CASE WHEN {self.dc.target.feature_name} == '{target_label}' THEN 1 ELSE 0 END) OVER (), 4)  AS tp,
                    ROUND(SUM(CASE WHEN {self.dc.target.feature_name} == '{target_label}' THEN 0 ELSE 1 END) OVER (ORDER BY "{score_feat}" DESC) / SUM(CASE WHEN {self.dc.target.feature_name} == '{target_label}' THEN 0 ELSE 1 END) OVER (), 4)  AS fp
                FROM df
                )
            GROUP BY fp,tp
            ORDER BY fp,tp
        """).pl(
            # ).vstack(pl.DataFrame({'fp': 0.0, 'tp': 0.0})
        )
        df_shift = df_plot.with_columns(
            [
                pl.col("fp").shift(-1).alias("fp_next"),
                pl.col("tp").shift(-1).alias("tp_next"),
            ]
        )
        auc = (
            df_shift.with_columns(
                (
                    (pl.col("fp_next") - pl.col("fp"))
                    * (pl.col("tp") + pl.col("tp_next"))
                    / 2
                ).alias("trap")
            )
            .select(pl.col("trap").sum())
            .item()
        )

        plot = (
            df_plot.with_columns(
                pl.lit(f"{score_feat} (AUC {auc:.4f})").alias("target")
            )
            .plot.line(x="fp", y="tp", color="target")
            .interactive()
        )

        return plot
