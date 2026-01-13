from itertools import batched
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Spore(BaseModel):
    cut: list[str]
    score: float
    depth: str


class Champion(BaseModel):
    spore: list[Spore]
    target: str | int

    def get_sql(self, res_name: str) -> str:
        return "CASE \n" + "\n".join(self.get_where_sql()) + f"END AS {res_name}"

    def get_split_sql(self, max_parallel_where: int) -> list[str]:
        where_cases = self.get_where_sql()
        return [
            "CASE \n" + "\n".join(batch) + f"\nELSE CAST(0 AS DOUBLE)\n END AS res_{i}"
            for i, batch in enumerate(batched(where_cases, max_parallel_where))
        ]

    def get_where_sql(self) -> list[str]:
        return [
            f"  WHEN {' AND '.join(spore.cut)} THEN CAST({spore.score} AS DOUBLE) "
            for spore in self.spore
        ]


class Champions(BaseModel):
    champions: dict[str, Champion]
    target: str

    def get_sql(self) -> dict[str, str]:
        return {
            f"res_{name}": champion.get_sql(f"res_{name}")
            for name, champion in self.champions.items()
        }
