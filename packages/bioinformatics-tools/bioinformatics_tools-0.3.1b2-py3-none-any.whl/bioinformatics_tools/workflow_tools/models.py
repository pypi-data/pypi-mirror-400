from pathlib import Path

from dataclasses import dataclass


@dataclass
class ApptainerKey:
    '''apptainer information'''
    executable: Path | str
    sif_path: Path | str
    commands: list[str]


@dataclass
class WorkflowKey:  #TODO: Rename this
    '''Information needed to run a workflow and map from cmd line'''
    cmd_identifier: str
    snakemake_file: str
    other: list[str]