import dataclasses


@dataclasses.dataclass
class Config:
    """Configuration variables used for the Viewer."""

    # color scheme
    colors: str = "default"

    # namespaces to search
    namespaces: list = dataclasses.field(default_factory=list)

    # display mode
    display_type: str = "default"

    # excludes list
    excludes: list = dataclasses.field(default_factory=list)

    # includes list
    includes: list = dataclasses.field(default_factory=list)

    # label selectors
    selectors: dict = dataclasses.field(default_factory=dict)

    # resource types
    resources: list = dataclasses.field(default_factory=list)

    verbose: bool = False