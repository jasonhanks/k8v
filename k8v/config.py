import dataclasses


@dataclasses.dataclass
class Config:
    """Configuration variables used for the Viewer."""

    # color scheme
    colors: str = "none"

    # delimeter to use for related resources
    delimeter: str = "    "

    # excludes list
    excludes: list = dataclasses.field(default_factory=list)

    # includes list
    includes: list = dataclasses.field(default_factory=list)

    # namespaces to search
    namespaces: list = dataclasses.field(default_factory=list)

    # output mode
    output: str = "default"

    # resource types
    resources: list = dataclasses.field(default_factory=list)

    # label selectors
    selectors: dict = dataclasses.field(default_factory=dict)

    # verbose logging
    verbose: bool = False
