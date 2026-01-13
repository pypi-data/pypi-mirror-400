import itertools
import sys
from typing import Optional
from pydantic import BaseModel
from champions.model.datacard import DataCard, Feature, FeatureType
from champions.model.dataframes import (
    CatCats,
    CombinedCategorizedFeature,
    ContCats,
    TrainDataframes,
    CategorizedFeature,
)
from champions.model.filter import (
    Filter,
    SympyContainer,
    SympyToSqlHelper,
)
from champions.model.settings import TrainSettings
from champions.model.champions import Champion, Spore
import polars as pl


import logging

from champions.service.darkwing import Darkwing

logger = logging.getLogger(__name__)


class Train(BaseModel):
    dc: DataCard
    settings: TrainSettings
    darkwing: Optional[Darkwing] = None

    def model_post_init(self, __context) -> None:
        self.darkwing = Darkwing(dc=self.dc)
        super().model_post_init(__context)

    def run(self):
        logger.info("start training")
        SympyToSqlHelper.columns = self.dc.feature_names
        for n in range(self.settings.n):
            for cat in self.dc.target.values:
                if self.settings.champion_exists(target=cat, n=n):
                    logger.info(f"tree {n} for label {cat} already exists")
                    continue

                logger.info(f"train tree {n} for label {cat}")

                train_res = Champion(
                    spore=self.train_champion(
                        target_filter=self.gen_target_filter(cat=cat),
                        path_filter=[],
                    ),
                    target=cat,
                )
                self.settings.save_champion(champion=train_res, n=n)

    def gen_target_filter(self, cat) -> Filter:
        return Filter(
            combine=SympyContainer(
                feat_name=self.dc.target.feature_name,
                operator="=",
                value=cat,
                assumptions={},
            ).get_sympy()
        )

    def make_spore(
        self, path_filter: list[Filter], depth: str, train_df: TrainDataframes
    ) -> Spore:
        score = train_df.score()
        logging.info(
            f"final spore depth: {depth}, {score} non target {train_df.non_target_df_size} target: {train_df.target_df_size}"
        )
        return [
            Spore(
                cut=[fil.sql() for fil in path_filter],
                score=score,
                depth=depth,
            )
        ]

    def train_champion(
        self, target_filter: Filter, path_filter: list[Filter], depth: str = ""
    ) -> list[Spore]:
        train_df = self.darkwing.read_akt_train(
            targer_filter=target_filter,
            train_settings=self.settings,
            akt_filters=path_filter,
        )

        if train_df.is_final_size() or len(depth) >= self.settings.max_depth:
            return self.make_spore(
                path_filter=path_filter, depth=depth, train_df=train_df
            )

        self.cater(train_df=train_df)
        left_filter, neutral_filter, right_filter = self.counter(train_df=train_df)
        if left_filter is None and right_filter is None:
            # neutral must then be true.
            logger.info("Best cut lands all in neutral")
            return self.make_spore(
                path_filter=path_filter, depth=depth, train_df=train_df
            )

        left_spores = (
            self.train_champion(
                target_filter=target_filter,
                path_filter=path_filter + [left_filter],
                depth=depth + "l",
            )
            if left_filter is not None
            else []
        )
        neutral_spores = (
            self.train_champion(
                target_filter=target_filter,
                path_filter=path_filter + [neutral_filter],
                depth=depth + "n",
            )
            if neutral_filter is not None
            else []
        )

        right_spores = (
            self.train_champion(
                target_filter=target_filter,
                path_filter=path_filter + [right_filter],
                depth=depth + "r",
            )
            if right_filter is not None
            else []
        )
        return left_spores + neutral_spores + right_spores

    def counter(
        self, train_df: TrainDataframes
    ) -> tuple[Filter, Filter | None, Filter]:
        sorted_train_feats = sorted(
            train_df.train_features,
            key=lambda x: x.calc_diff(),
            reverse=True,
        )
        best_feat = sorted_train_feats[0]
        best_feat_diff = best_feat.calc_diff()

        for dim in range(2, self.settings.n_dims + 1):
            counter = 0
            for comb in itertools.combinations(sorted_train_feats, r=dim):
                counter += 1
                akt_feature = CombinedCategorizedFeature(
                    comb,
                    non_target_size=train_df.n_count_non_target,
                    target_size=train_df.n_count_target,
                    neutral_faktor=self.settings.neutral_faktor,
                )
                if akt_feature.calc_diff() > best_feat_diff:
                    best_feat = akt_feature
                    best_feat_diff = akt_feature.calc_diff()

                if (
                    self.settings.calcs_per_dim
                    and counter > self.settings.calcs_per_dim
                ):
                    break

        return best_feat.get_left_right_filter()

    def cater(self, train_df: TrainDataframes):
        for feat in self.dc.train_features:
            categorized_feature = self.feat_cater(feat=feat, train_df=train_df, n=2)
            for n in range(3, self.settings.n_cat + 1):
                cat_feature = self.feat_cater(feat=feat, train_df=train_df, n=n)
                if cat_feature.calc_diff() > categorized_feature.calc_diff():
                    categorized_feature = cat_feature

            if not categorized_feature.is_diff_to_low():
                train_df.train_features.append(categorized_feature)

    def feat_cater(
        self, feat: Feature, train_df: TrainDataframes, n: int
    ) -> CategorizedFeature:
        match feat.statistical:
            case FeatureType.CATEGORIAL:
                return self.cat_cater_impl(feat=feat, train_df=train_df, n=n)
            case FeatureType.NUMERICAL:
                return self.cont_cater_impl(feat=feat, train_df=train_df, n=n)

        raise NotImplementedError(f"FeatureType {feat.statistical} not implemented")

    def cat_cater_impl(
        self, feat: Feature, train_df: TrainDataframes, n: int
    ) -> CategorizedFeature:
        df = (
            train_df.df_group.group_by(feat.name)
            .agg(pl.col("weight").sum(), pl.col("target_weight").sum())
            .sort(pl.col("weight"), descending=True)
        )
        default_cat = df.item(-1, feat.name)
        offstet = 0
        map = {}

        # First filter out large categories
        for i in range(n):
            if df.height == 0:
                break
            val = df.item(0, "weight")
            if val < 1.0 / (n - i):
                break
            map[df.item(0, feat.name)] = str(i)
            df = df.tail(-1).with_columns(pl.col("weight").truediv((1.0 - val)))
            offstet = i + 1

        if df.height == 0:
            return train_df.create_categorized_features(
                feat=feat,
                cuts=CatCats(
                    mapping=map, default=map.get(default_cat), feat_name=feat.name
                ),
            )
        # Sort by amount of target
        df = df.with_columns(
            pl.col("target_weight").truediv(pl.col("weight")).alias("target_rate")
        ).sort("target_rate", descending=False)

        # Build the column for the quatile
        df = df.with_columns(pl.col("weight").cum_sum().alias("cum_weight"))

        labels = [str(i) for i in range(offstet, n)]
        m = len(labels)
        breaks = [i / m for i in range(1, m)]

        # TODO the hole function is numerical instable. Write some test to find this error
        df = df.with_columns(
            pl.col("cum_weight")
            .cut(
                breaks=breaks,
                labels=labels,
                left_closed=True,
            )
            .alias("bin")
        )

        df_res = df.group_by("bin").agg(pl.col(feat.name))
        for row in df_res.to_dicts():
            map.update({feat: row.get("bin") for feat in row.get(feat.name)})
        return train_df.create_categorized_features(
            feat=feat,
            cuts=CatCats(
                mapping=map, default=map.get(default_cat), feat_name=feat.name
            ),
        )

    def cont_cater_impl(
        self, feat: Feature, train_df: TrainDataframes, n: int
    ) -> CategorizedFeature:
        df_sorted = train_df.df_group[[feat.name, "weight"]].sort(feat.name)
        cumulative_weights = df_sorted["weight"].cum_sum()

        res = []
        label = ["0"]
        idx = 0
        for i in range(1, n):
            quantile = i / n
            index = (cumulative_weights >= quantile).arg_true()[0]

            if index > 0:
                weight_below = cumulative_weights[index - 1]
                value_below = df_sorted[feat.name][index - 1]
                value_at_index = df_sorted[feat.name][index]
                fraction = (quantile - weight_below) / (
                    cumulative_weights[index] - weight_below
                )
                value = value_below + fraction * (value_at_index - value_below)
            else:
                value = df_sorted[feat.name][0]
            if value in res:
                continue
            idx += 1
            label.append(f"{idx}")
            res.append(value)

        return train_df.create_categorized_features(
            feat=feat,
            cuts=ContCats(cuts=res, labels=label, feat_name=feat.name),
        )
