# Copyright 2025 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from . import wrap_locations
from cwl_utils.parser import Process
from cwl_loader import dump_cwl
from datetime import datetime
from loguru import logger
from pathlib import Path
from typing import Optional
import click
import time

@click.command()
@click.option("--directory-stage-in", required=False, help="The CWL stage-in URL or file for Directory derived types")
@click.option("--file-stage-in", required=False, help="The CWL stage-in URL or file for File derived types")
@click.option("--workflow", required=True, help="The CWL workflow URL or file")
@click.option("--workflow-id", required=True, help="ID of the workflow")
@click.option("--stage-out", required=True, help="The CWL stage-out URL or file")
@click.option("--output", type=click.Path(path_type=Path), required=True, help="The output file path")
def main(
    directory_stage_in: str,
    file_stage_in: str,
    workflow: str,
    workflow_id: str,
    stage_out: str,
    output: Path
):
    '''
    Composes a CWL `Workflow` from a series of `Workflow`/`CommandLineTool` steps, defined according to [Application package patterns based on data stage-in and stage-out behaviors commonly used in EO workflows](https://github.com/eoap/application-package-patterns), and **packs** it into a single self-contained CWL document.

    Args:
        `directory_stage_in` (`str`): The CWL stage-in URL or file for `Directory` derived types
        `file_stage_in` (`str`): The CWL stage-in URL or file for `File` derived types
        `workflow` (`str`): The CWL document URL or file
        `workflow_id` (`str`): ID of the workflow
        `stage_out` (`Workflow`): The CWL stage-out URL or file
        `output` (`Path`): The Output file path

    Returns:
        `None`: none.
    '''
    start_time = time.time()

    main_workflow = wrap_locations(
        directory_stage_in=directory_stage_in,
        file_stage_in=file_stage_in,
        workflows=workflow,
        workflow_id=workflow_id,
        stage_out=stage_out
    )

    logger.info('------------------------------------------------------------------------')
    logger.info('BUILD SUCCESS')
    logger.info('------------------------------------------------------------------------')

    logger.info(f"Saving the new Workflow to {output}...")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w") as f:
        dump_cwl(main_workflow, f)

    logger.info(f"New Workflow successfully saved to {output}!")

    end_time = time.time()

    logger.info(f"Total time: {end_time - start_time:.4f} seconds")
    logger.info(f"Finished at: {datetime.fromtimestamp(end_time).isoformat(timespec='milliseconds')}")

if __name__ == "__main__":
    main()
