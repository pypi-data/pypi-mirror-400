import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field
import yaml

from champions.model.champions import Champion, Champions

logger = logging.getLogger(__name__)


class EvalSettings(BaseModel):
    in_folders: list[Path] = Field(description="Name where the champion is stored")
    out_folder: Path = Field(description="Name where the evaluation is stored")
    max_parallel_where: int = Field(
        description="Number of points for roc curve", default=100
    )


class TrainSettings(BaseModel):
    n: int = Field(description="Number of Champions per target value", default=1)
    out_folder: Path = Field(description="Name where the champion is stored")
    n_cat: int = Field(description="Number of categories in one featerue", default=3)
    max_depth: int = Field(description="Max depth of the champion", default=10)

    max_eval_fit: int = Field(
        description="Wieviel sollen max für training gleichzeitig benutzt werden",
        default=1000,
    )
    min_eval_fit: int = Field(
        description="Wieviel müssen fürs training mindestens benutzt werden", default=10
    )
    n_dims: int = Field(
        description="Wieviele dimensionen sollen auf einmal benutzt werden", default=3
    )
    calcs_per_dim: int | None = Field(
        description="Wieviele berechnungen sollen pro dimension gemacht werden",
        default=5000,
    )
    frac_eval_cat: float = Field(
        description="Wie groß ist der anteil der für eval benutzt werden soll",
        default=0.5,
    )

    neutral_faktor: float = Field(
        description="Faktor wie groß der Unterschied für Neutral sein soll. Wert kleiner als 0 beduet kein Neutral state",
        default=-1.0,
    )

    def champion_exists(self, target: str | int, n: int) -> bool:
        if self.out_folder.exists():
            if (self.out_folder / f"{target}" / f"{n}.json").exists():
                return True
        return False

    def save_champion(self, champion: Champion, n: int):
        target = champion.target
        out_folder = self.out_folder / f"{target}"
        logger.info(f"save champion {n} for target {target} to {out_folder}")
        out_folder.mkdir(parents=True, exist_ok=True)
        out_file = out_folder / f"{n}.json"
        with out_file.open("w") as f:
            f.write(json.dumps(champion.model_dump(), ensure_ascii=False, indent=2))
