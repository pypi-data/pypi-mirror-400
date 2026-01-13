from importlib.metadata import entry_points

from typer import Typer


class SbTyper(Typer):
    def __init__(
        self,
        group: str = "tsb_cli",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.group = group

    def load_plugins(self) -> None:
        group = entry_points().select(group=self.group)
        for ep in group:
            self.add_typer(ep.load(), name=ep.name)
