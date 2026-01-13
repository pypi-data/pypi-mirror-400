import itertools
import logging
from typing import Any
import mi_amore
import polars as pl
from pydantic import BaseModel
from dataclasses import dataclass

from sympy import And, Not, Or, SOPform, Symbol, simplify
from sympy.logic import POSform
from mi_amore.minimize import minimize
from sympy.logic.boolalg import BooleanTrue

from champions.model.datacard import Feature
from champions.model.filter import Filter, SympyContainer, SympyToSqlHelper
import sys

logger = logging.getLogger(__name__)


class CatsMixin(BaseModel):
    # labels: list[str]

    def get_bits(self, label: str) -> list[int]:
        bits = [0] * (len(self.labels))
        bits[int(label)] = 1
        return bits

    def get_bits_list(self, labels: list[str]) -> list[str]:
        return [self.get_bits(label=label) for label in labels]

    def get_sympy_from_bits(self, bits: list[int]):
        bits_sum = sum(bits)
        if bits_sum == len(bits):
            return simplify(True)
        if bits_sum == 1:
            for i, bit in enumerate(bits):
                if bit == 1:
                    return self.get_single_filter(i).get_sympy()
        if bits_sum == len(bits) - 1:
            for i, bit in enumerate(bits):
                if bit == 0:
                    return Not(self.get_single_filter(i).get_sympy())
        res = Or(
            *[
                self.get_single_filter(i).get_sympy()
                for i, bit in enumerate(bits)
                if bit == 1
            ]
        )
        # return res
        return simplify(res)


class CatCats(CatsMixin):
    mapping: dict[str | int, str]
    default: str
    feat_name: str

    @property
    def labels(self) -> list[str]:
        return list(set(self.mapping.values()))

    @property
    def inverted_mapping(self) -> dict[str, list[str | int]]:
        ret_map = {}
        for k, v in self.mapping.items():
            ret_map.setdefault(v, []).append(k)
        return ret_map

    @property
    def get_default_cuts(self) -> list[str]:
        defalut_cuts = []
        for i, v in self.inverted_mapping.items():
            if self.default != i:
                defalut_cuts += v
        return defalut_cuts

    def cut(self, df: pl.DataFrame) -> pl.Series:
        return df[self.feat_name].replace_strict(self.mapping, default=self.default)

    def get_single_filter(self, i: int) -> SympyContainer:
        i = f"{i}"
        if self.default == i:
            dev_cats = self.get_default_cuts
            if len(dev_cats) == 1:
                return SympyContainer(
                    feat_name=self.feat_name,
                    operator="!=",
                    value=dev_cats[0],
                    assumptions={},
                )
            return SympyContainer(
                feat_name=self.feat_name,
                operator="not in",
                value=dev_cats,
                assumptions={},
            )
        cats = self.inverted_mapping.get(i)

        if len(cats) == 1:
            return SympyContainer(
                feat_name=self.feat_name, operator="=", value=cats[0], assumptions={}
            )
        return SympyContainer(
            feat_name=self.feat_name, operator="in", value=cats, assumptions={}
        )


class ContCats(CatsMixin):
    cuts: list[float]
    labels: list[str]
    feat_name: str

    def cut(self, df: pl.DataFrame) -> pl.Series:
        # return series.cut(self.cuts)
        return df[self.feat_name].cut(self.cuts, labels=self.labels)

    def get_single_filter(self, i: int) -> SympyContainer:
        if i == 2 and len(self.cuts) == 1:
            logger.error("to low cuts")
            sys.exit()

        if i == 0:
            return SympyContainer(
                feat_name=self.feat_name,
                operator="<=",
                value=self.cuts[i],
                assumptions={"float": True},
            )

        if i == len(self.labels) - 1:
            return SympyContainer(
                feat_name=self.feat_name,
                operator=">",
                value=self.cuts[i - 1],
                assumptions={"float": True},
            )
        return SympyContainer(
            feat_name=self.feat_name,
            operator="between",
            value=[self.cuts[i - 1], self.cuts[i]],
            assumptions={"float": True},
        )


class CategorizedFeatureMixin:
    diff_df: pl.DataFrame
    cut_list: list[ContCats | CatCats]
    feature_list: list[str]
    neutral_faktor: float

    def calc_diff(
        self,
    ) -> float:
        # self.diff_sr.entropy()

        # return self.diff_df["diff"].abs().sqrt().sum()
        # return self.diff_df["diff"].abs().sum()
        return self.diff_df.with_columns(
            (pl.col("diff").abs() * pl.col("diff").abs().sqrt())
        )["diff"].sum()
        # return self.diff_df.with_columns((pl.col("diff") ** 2 ))['diff'].sum()

    def set_diff_df(
        self,
        df_count_target: pl.DataFrame,
        df_count_non_target: pl.DataFrame,
        join_on: list[str] | str,
    ):
        self.diff_df = (
            df_count_non_target.join(df_count_target, on=join_on, how="outer")
            .fill_null(0)
            .with_columns(
                (pl.col("proportion_right") - pl.col("proportion")).alias("diff"),
                pl.max_horizontal(
                    pl.col("proportion"), pl.col("proportion_right")
                ).alias("max_proportion"),
            )
        )

    def get_left_right_filter(self) -> tuple[Filter, Filter | None, Filter]:
        sorted_cut_list = sorted(self.cut_list, key=lambda el: len(el.labels))
        n_binary = 0
        mvars = []
        for el in sorted_cut_list:
            if len(el.labels) == 2:
                n_binary += 1
            else:
                mvars.append(len(el.labels))

        res_df = self.diff_df.with_columns(
            [
                pl.coalesce(
                    pl.col(cut.feat_name), pl.col(f"{cut.feat_name}_right")
                ).alias(f"{cut.feat_name}")
                for cut in sorted_cut_list
            ]
        )
        neutral_range = max(self.neutral_faktor, 0)
        target_lists = [
            res_df.filter(pl.col("diff") > neutral_range)[cut.feat_name].to_list()
            for cut in sorted_cut_list
        ]
        target_list_tupels = [akt_tuple for akt_tuple in zip(*target_lists)]

        non_target_lists = [
            res_df.filter(pl.col("diff") <= -neutral_range)[cut.feat_name].to_list()
            for cut in sorted_cut_list
        ]
        non_target_list_tupels = [akt_tuple for akt_tuple in zip(*non_target_lists)]

        target_cubes = []
        neutral_cubes = []
        non_target_cubes = []

        possible_labels = [cut.labels for cut in sorted_cut_list]
        for possible_combs in itertools.product(*possible_labels):
            bits = [
                flat_bit
                for label, cut in zip(possible_combs, sorted_cut_list)
                for flat_bit in cut.get_bits(label)
            ]
            if possible_combs in target_list_tupels:
                target_cubes.append(bits)
            elif possible_combs in non_target_list_tupels or self.neutral_faktor < 0:
                non_target_cubes.append(bits)
            else:
                neutral_cubes.append(bits)

        min_target_cubes = minimize(
            n_binary=n_binary,
            mvars=mvars,
            cubes_on=target_cubes,
        )
        min_neutral_cubes = minimize(
            n_binary=n_binary,
            mvars=mvars,
            cubes_on=neutral_cubes,
        )

        min_non_target_cubes = minimize(
            n_binary=n_binary,
            mvars=mvars,
            cubes_on=non_target_cubes,
        )
        # start at 0 next are binarys (two bits) and then the mvars
        low_high_cuts = list(itertools.accumulate([0] + [2] * n_binary + mvars))

        return (
            self.get_sympy_combine_filter(
                cut_list=sorted_cut_list,
                low_high_cuts=low_high_cuts,
                min_cubes=min_non_target_cubes,
            ),
            self.get_sympy_combine_filter(
                cut_list=sorted_cut_list,
                low_high_cuts=low_high_cuts,
                min_cubes=min_neutral_cubes,
            ),
            self.get_sympy_combine_filter(
                cut_list=sorted_cut_list,
                low_high_cuts=low_high_cuts,
                min_cubes=min_target_cubes,
            ),
        )

    @staticmethod
    def get_sympy_combine_filter(
        cut_list: list[ContCats | CatCats],
        low_high_cuts: list[int],
        min_cubes: list[list[int]],
    ) -> Filter | None:
        if len(min_cubes) == 0:
            return None
        return Filter(
            combine=Or(
                *[
                    And(
                        *[
                            cut.get_sympy_from_bits(cube[lh[0] : lh[1]])
                            for cut, lh in zip(
                                cut_list, itertools.pairwise(low_high_cuts)
                            )
                        ]
                    )
                    for cube in min_cubes
                ]
            )
        )


@dataclass
class CategorizedFeature(CategorizedFeatureMixin):
    feature: Feature
    cuts: ContCats | CatCats
    target_sr: pl.Series
    non_target_sr: pl.Series
    neutral_faktor: float

    def __post_init__(self):
        df_count_target = self.target_sr.value_counts()
        df_count_target = df_count_target.with_columns(
            (pl.col("count") / pl.col("count").sum()).alias("proportion")
        )

        df_count_non_target = self.non_target_sr.value_counts()
        df_count_non_target = df_count_non_target.with_columns(
            (pl.col("count") / pl.col("count").sum()).alias("proportion")
        )

        self.set_diff_df(
            df_count_target=df_count_target,
            df_count_non_target=df_count_non_target,
            join_on=self.feature.name,
        )

    @property
    def cut_list(self) -> list[ContCats]:
        return [self.cuts]

    def is_diff_to_low(self, threshold: float = 0.90) -> bool:
        max_wert = self.diff_df["max_proportion"].max()
        min_prop_of_max = self.diff_df.filter(pl.col("max_proportion") == max_wert)[
            "proportion", "proportion_right"
        ].min_horizontal()[0]
        return min_prop_of_max > threshold


class CombinedCategorizedFeature(CategorizedFeatureMixin):
    def __init__(
        self,
        train_features: tuple[CategorizedFeature],
        non_target_size: int,
        target_size: int,
        neutral_faktor: float,
    ):
        groub_by = [train.feature.name for train in train_features]
        non_target_df = pl.DataFrame([train.non_target_sr for train in train_features])
        self.neutral_faktor = neutral_faktor

        df_count_non_target = (
            non_target_df.group_by(groub_by)
            .len(name="proportion")
            .with_columns((pl.col("proportion") / non_target_size))
        )
        target_df = pl.DataFrame([train.target_sr for train in train_features])
        df_count_target = (
            target_df.group_by(groub_by)
            .len(name="proportion")
            .with_columns((pl.col("proportion") / target_size))
        )
        self.set_diff_df(
            df_count_target=df_count_target,
            df_count_non_target=df_count_non_target,
            join_on=groub_by,
        )
        self.cut_list = [train.cuts for train in train_features]


class TrainDataframes:
    def __init__(
        self,
        target_df: pl.DataFrame,
        non_target_df: pl.DataFrame,
        frac_eval_cat: float,
        min_size: int,
        neutral_faktor: float,
    ):
        self.target_df_size = target_df.height
        self.non_target_df_size = non_target_df.height

        self.min_size = min_size
        self.neutral_faktor = neutral_faktor

        self.n_count_target, n_group_target = self._calc_split(
            target_df.height, frac_eval_cat
        )
        self.target_df_count = target_df.head(self.n_count_target)
        target_df_group = target_df.tail(-self.n_count_target)
        target_df_group = target_df_group.with_columns(
            pl.lit(0.5 / max(1, n_group_target)).alias("weight")
        )
        target_df_group = target_df_group.with_columns(
            (2 * pl.col("weight")).alias("target_weight")
        )

        self.n_count_non_target, n_group_non_target = self._calc_split(
            non_target_df.height, frac_eval_cat
        )
        self.non_target_df_count = non_target_df.head(self.n_count_non_target)
        non_target_df_group = non_target_df.tail(-self.n_count_non_target)
        non_target_df_group = non_target_df_group.with_columns(
            pl.lit(0.5 / max(1, n_group_non_target)).alias("weight")
        )
        non_target_df_group = non_target_df_group.with_columns(
            pl.lit(0.0).alias("target_weight")
        )

        self.df_group = pl.concat([target_df_group, non_target_df_group])
        self.train_features: list[CategorizedFeature] = []

    def create_categorized_features(
        self, feat: Feature, cuts: ContCats | CatCats
    ) -> CategorizedFeature:
        target_sr = cuts.cut(df=self.target_df_count)
        non_target_sr = cuts.cut(df=self.non_target_df_count)
        return CategorizedFeature(
            feature=feat,
            cuts=cuts,
            target_sr=target_sr,
            non_target_sr=non_target_sr,
            neutral_faktor=self.neutral_faktor,
        )

    def _calc_split(self, n: int, frac: float):
        split = round(n * frac)
        if split < 1:
            return 1, 0
        if split >= n:
            return n - 1, 1
        return split, n - split

    def score(self) -> float:
        if self.non_target_df_size + self.target_df_size == 0:
            return 0.0
        return (self.target_df_size - self.non_target_df_size) / (
            self.non_target_df_size + self.target_df_size
        )

    def is_final_size(self) -> bool:
        return (
            self.target_df_size < self.min_size
            or self.non_target_df_size < self.min_size
        )


class EvalDataframe:
    def __init__(self, df: pl.DataFrame, target: str | int) -> None:
        self.df = df
