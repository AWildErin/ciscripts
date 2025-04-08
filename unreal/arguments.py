"""
Various data classes for Unreal engine commands
"""

from dataclasses import dataclass


def arg_formatter(args: dict) -> list[str]:
    # @todo we should maybe handle dicts and lists

    cmd = []
    for k, v in args.items():
        if v is None:
            continue

        if isinstance(v, bool):
            if v is True:
                cmd.append(f'-{k}')

        elif isinstance(v, (str, int)):
            cmd.append(f'-{k}={v}')

    return cmd


@dataclass
class BuildCookRunArguments:
    """
    BuildCookRun arguments data class.
    @todo Fill in the rest from the UE5 repo. It's a bit confusing to know which are applicable but you can find them here
        https://github.com/EpicGames/UnrealEngine/blob/5.3/Engine/Source/Programs/AutomationTool/Scripts/BuildCookRun.Automation.cs
        https://github.com/EpicGames/UnrealEngine/blob/5.3/Engine/Source/Programs/AutomationTool/AutomationUtils/ProjectParams.cs
    """
    # Required arguments
    platform: str
    configuration: str

    build: bool = False
    clean: bool = False
    cook: bool = False
    pak: bool = False
    stage: bool = False
    stagingdirectory: str = None
