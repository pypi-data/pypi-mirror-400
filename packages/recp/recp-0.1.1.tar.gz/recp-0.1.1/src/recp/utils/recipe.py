import os
import yaml
import subprocess
from copy import deepcopy
from typing import (
    List,
    Tuple
)
from importlib.metadata import version as package_version
from packaging.version import Version
from .collections import temp_env
from .exceptions import (
    MinimumVersionRequirementError,
    RequiredValueNotFoundError
)
from .apply import get_apply_registy


class Recipe:
    """Class that represents a recipe loaded from a file and all the additional
    necessary functionality to run the commands on all steps found in the
    recipe.

    Args:
        file (str): Recipe `.yaml` file.
        allow_expr (bool): If `True`, allows using the the `!expr` directive in
            the recipe. This is not allowed by default because this expression
            if considered unsafe.
    """
    ROOT_KEY = "recipe"
    MINIMUM_REQUIRED_VERSION_KEY = "minimum_required_version"
    MANDATORY_STEP_KEYS = ("run",)
    OPTIONAL_STEP_KEYS = ("tag", "description", "env")
    PACKAGE_VERSION = Version(package_version("recp")) 
    def __init__(
            self,
            file: str,
            allow_expr: bool = False,
    ) -> None:
        super().__init__()

        # Params
        self.file = file
        self.allow_expr = allow_expr

        # Load and validate file structure
        self._data = self.load(self.file)
        self.validate_minimum_version_required(self._data)
        self.validate_keys(self._data)

        # Cache apply registry
        self._apply_registry = get_apply_registy()

    def _yaml_expr_constructor(
            self,
            loader: yaml.loader.SafeLoader,
            node: yaml.nodes.ScalarNode
    ) -> int | float:
        if not self.allow_expr:
            raise ValueError(
            f"Invalid !expr constructor at line {node.start_mark.line + 1} "
            f"in recipe file {self.file!r}. The !expr constructor is only "
            "allowed when the --unsafe option is enabled."
        )

        expr = loader.construct_scalar(node)
        return eval(expr)
    
    def _yaml_input_constructor(
            self,
            loader: yaml.loader.SafeLoader,
            node: yaml.nodes.Node
    ) -> str:
        # Get config
        # NOTE: This constructor is not solved here because steps must be
        # first filtered to solve only necessary constructors 
        if isinstance(node, yaml.nodes.MappingNode):
            map = loader.construct_mapping(node)
            map["__constructor__"] = "!input"
        
        elif isinstance(node, yaml.nodes.ScalarNode):
            map = {
                "name": str(loader.construct_scalar(node)),
                "default": None,
                "required": False,
                "__constructor__": "!input"
            }
        
        else:
            raise ValueError(
                f"!input constructor found on a {node.__class__.__name__!r} at"
                f" line {node.start_mark.line + 1} in recipe file "
                f"{self.file!r}. !input constructors only support str or dict "
                "values."
            )

        return map
    
    def _yaml_split_constructor(
            self,
            loader: yaml.loader.SafeLoader,
            node: yaml.nodes.ScalarNode
    ) -> List[str]:
        value = loader.construct_scalar(node)
        return str(value).split(" ")
    
    def load(self, file: str) -> dict:
        """Loads a `.yaml` recipe file.
        
        Args:
            file (str): `.yaml` recipe file to be loaded.
        
        Returns:
            (dict): Parsed `.yaml` recipe file.
        """
        # Add custom constructors
        yaml.SafeLoader.add_constructor("!expr", self._yaml_expr_constructor)
        yaml.SafeLoader.add_constructor("!input", self._yaml_input_constructor)
        yaml.SafeLoader.add_constructor("!split", self._yaml_split_constructor)

        # Open .yaml file
        with open(file, "r") as f:
            data = yaml.safe_load(f)
        
        return data
    
    def validate_minimum_version_required(self, data: dict) -> None:
        """Corroborates the minimum version required is met if the `.yaml`
        recipe file contains a `minimum_required_version` key.

        Args:
            data (dict): Recipe file data.
        """
        if data.get(self.MINIMUM_REQUIRED_VERSION_KEY) is not None:
            minimum_required_version = Version(
                data["minimum_required_version"]
            )

            if not self.PACKAGE_VERSION >= minimum_required_version:  # noqa: SIM300
                raise MinimumVersionRequirementError(
                    f"This recipe requires recp >= {minimum_required_version} "
                    f" but current recp version is {self.PACKAGE_VERSION}"
                )
    
    def validate_keys(self, data: dict) -> None:
        """Validate keys present in the recipe `.yaml` file.
        
        Args:
            data (dict): Recipe `.yaml` file data.
        """
        # Check 'recipe' key exists
        if self.ROOT_KEY not in data:
            raise KeyError(f"Key {self.ROOT_KEY!r} not found in recipe file")
        
        # Check step keys
        for name, data in data[self.ROOT_KEY].items():
            for mandatory_key in self.MANDATORY_STEP_KEYS:
                if mandatory_key not in data:
                    raise KeyError(
                        f"Key {mandatory_key!r} not found in step {name!r}"
                    )
    
    def filter_by_tag(self, data: dict, tag: str | List[str]) -> dict:
        """Filter steps by a given tag.
        
        Args:
            data (dict): Recipe `.yaml` file data.
            tag (str | List[str]): Tag(s) to select. Values not containing any
                tag in the list are removed from the resulting `dict`.
        
        Returns:
            (dict): Resulting `.yaml` recipe filtered after selecting steps by
                tag.
        """
        selected_steps = []

        for name in data["recipe"]:
            step_tags = data["recipe"][name].get("tag", [])

            if all(t in step_tags for t in tag):
                selected_steps.append(name)
        
        data["recipe"] = {
            k: v for k, v in data["recipe"].items() if k in selected_steps
        }

        return data
    
    def parse_env(self, data: dict) -> dict:
        """Parse `env` environment key.

        Args:
            data (dict): Recipe `.yaml` file data.

        Returns:
            (dict): Resulting recipe `.yaml` data after solving all
                environmental variables in the `env` key.
        """
        for step_name, step in data["recipe"].items():
            if (env := step.get("env")) is not None:
                for k, v in env.items():
                    # !input constructor
                    if (
                        isinstance(v, dict)
                        and v["__constructor__"] == "!input"
                    ):
                        if (var := os.environ.get(v["name"])) is None:
                            if v.get("required"):
                                raise RequiredValueNotFoundError(
                                    f"Environmental variable {v['name']!r} is "
                                    f"marked in {step_name!r} as required but "
                                    "was not provided"
                                )
                            
                            else:
                                env[k] = v["default"]
                        
                        else:
                            env[k] = var
        
        return data
    
    def parse_run(self, data: dict) -> dict:
        """Parse `run` commands key.

        Args:
            data (dict): Recipe `.yaml` file data.

        Returns:
            (dict): Resulting recipe `.yaml` data after commands.
        """
        for step_name, step in data["recipe"].items():
            cmd_seq = []

            with temp_env(step.get("env", {})):          
                # 'run' should be a list of commands
                for cmd_idx, cmd in enumerate(step["run"]):
                    if isinstance(cmd, str):
                        cmd_seq.append(
                            os.path.expanduser(os.path.expandvars(cmd))
                        )
                    
                    elif isinstance(cmd, dict):
                        cmd_list = [
                            os.path.expanduser(os.path.expandvars(cmd["cmd"]))
                        ]
                        modifiers = cmd["apply"]

                        for modifier in modifiers:
                            fn = self._apply_registry.get(modifier["fn"], None)

                            if fn is None:
                                raise ValueError(
                                    f"Function {modifier['fn']!r} applied in "
                                    f"command #{cmd_idx} of step {step_name!r}"
                                    " not found"
                                )
                            
                            cmd_list = fn(cmd_list, **modifier["args"])

                        cmd_seq += cmd_list
    
                    else:
                        raise TypeError(
                            f"Command #{cmd_idx} of step is of type "
                            f"{cmd.__class__.__name__!r}, but only str or dict"
                            " commands are supported"
                        )
                
                step["run"] = cmd_seq
        
        return data
            
    def run(
            self,
            tag: Tuple[str] | None = None,
            ignore_errors: bool = False,
            dry_run: bool = False
    ) -> None:
        """Run all processed commands in a recipe `.yaml` file.
        
        Args:
            tag (Tuple[str]): Tag(s) to select.
            ignore_errors (bool): If `True`, steps producing errors will not
                stop the execution of subsequent steps.
            dry_run (bool): If `True`, commands to be run are only displayed
                and not run.
        """
        # ----------------------------------------------------------------------
        # SECTION: INPUT
        # ----------------------------------------------------------------------
        # Copy original data
        print(f"Using recipe {self.file!r} ...")
        data = deepcopy(self._data)
        print(f"{len(data['recipe'])} step(s) found")

        # ----------------------------------------------------------------------
        # SECTION: TEXT PROCESSING
        # ----------------------------------------------------------------------
        print("Pre-processing recipe data ...")
        # Stringify tags, descriptions and env vars
        for step in data["recipe"].values():
            if "tag" in step:
                step["tag"] = [str(t) for t in step["tag"]]
            
            if "description" in step:
                step["description"] = str(step["description"])
        
        print("Recipe pre-processing successfully completed")

        # ----------------------------------------------------------------------
        # SECTION: FILTERING
        # ----------------------------------------------------------------------
        # Filter by tag
        if tag is not None:
            print("Filtering recipe steps by tags ...")
            data = self.filter_by_tag(data, tag)        
            print("Filtering by tags successfully completed")
        
        # ----------------------------------------------------------------------
        # SECTION: CONSTRUCTOR PROCESSING
        # ----------------------------------------------------------------------
        # NOTE: Processed here to only process the filtered steps
        print("Parsing step environments ...")
        data = self.parse_env(data)
        print("Step environments processing successfully completed")

        # ----------------------------------------------------------------------
        # SECTION: RESOLVE COMMANDS
        # ----------------------------------------------------------------------
        print("Pre-processing recipe commands ...")
        data = self.parse_run(data)
        print("Recipe commands successfully completed")

        # ----------------------------------------------------------------------
        # SECTION: RUN COMMANDS
        # ----------------------------------------------------------------------
        num_steps = len(data["recipe"])

        if dry_run:
            print("Running commands in DRY RUN MODE ...")
        
        else:
            print("Running commands ...")
        
        for step_idx, (step_name, step) in enumerate(data["recipe"].items()):
            progress_repr = f"[{step_idx + 1}/{num_steps}]"
            indent = " " * (len(progress_repr) + 1)
            print(f"{progress_repr} Running step {step_name!r} ...")

            if step.get("tag") is not None:
                tags_repr = ", ".join(f"{t!r}" for t in step["tag"])
                print(f"{indent}{'Tags:':<{13}}{tags_repr}")

            if step.get("description") is not None:
                print(
                    f"{indent}{'Description:':<{13}}"
                    f"{step['description']}".rstrip("\n")
                )

            for cmd in step["run"]:
                print(f"{indent}{'Command:':<{13}}{cmd}")

                if not dry_run: 
                    if ignore_errors:
                        subprocess.run(cmd, shell=True)
                    
                    else:
                        subprocess.run(cmd, shell=True, check=True)
