# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# mypy: disable-error-code="import-untyped"
from datetime import datetime, timedelta, timezone

import pytest
from conftest import (  # type: ignore[import-not-found]
    DATA_DIR,
    score_specs_for_tests,
    wait_for_pipeline_run_success,
    wait_for_status,
    wait_for_success,
)

from dyff.audit.local.platform import DyffLocalPlatform
from dyff.client import Client
from dyff.schema.platform import *
from dyff.schema.requests import *


@pytest.mark.datafiles(DATA_DIR)
def test_pipelines_create_module(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_pipelines"):
        pytest.skip()

    account = ctx["account"]
    module_jupyter_notebook_dir = datafiles / "module_jupyter_notebook"
    pipeline_module = dyffapi.modules.create_package(
        module_jupyter_notebook_dir,
        account=account,
        name="pipeline_module",
    )

    wait_for_status(
        lambda: dyffapi.modules.get(pipeline_module.id),
        "WaitingForUpload",
        timeout=timedelta(minutes=1),
    )

    dyffapi.modules.upload_package(pipeline_module, module_jupyter_notebook_dir)
    print(f"pipeline_module: {pipeline_module.id}")
    ctx["pipeline_module"] = pipeline_module

    wait_for_success(
        lambda: dyffapi.modules.get(pipeline_module.id),
        timeout=timedelta(minutes=2),
    )


@pytest.mark.depends(
    on=[
        "test_pipelines_create_module",
    ]
)
def test_pipelines_create_method(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx
):
    if pytestconfig.getoption("skip_pipelines"):
        pytest.skip()

    account = ctx["account"]
    pipeline_module = ctx["pipeline_module"]
    pipeline_method_request = MethodCreateRequest(
        name="pipeline_method",
        scope=MethodScope.InferenceService,
        description="""# Markdown Description""",
        implementation=MethodImplementation(
            kind=MethodImplementationKind.JupyterNotebook,
            jupyterNotebook=MethodImplementationJupyterNotebook(
                notebookModule=pipeline_module.id,
                notebookPath="test-notebook.ipynb",
            ),
        ),
        parameters=[MethodParameter(keyword="trueName", description="His real name")],
        inputs=[
            MethodInput(kind=MethodInputKind.Evaluation, keyword="cromulence"),
        ],
        output=MethodOutput(
            kind=MethodOutputKind.SafetyCase,
            safetyCase=SafetyCaseSpec(
                name="safetycase_notebook_no_scores",
                description="""# Markdown Description""",
            ),
        ),
        scores=score_specs_for_tests(),
        modules=[pipeline_module.id],
        account=account,
    )
    pipeline_method = dyffapi.methods.create(pipeline_method_request)
    print(f"pipeline_method: {pipeline_method.id}")
    ctx["pipeline_method"] = pipeline_method

    wait_for_success(
        lambda: dyffapi.methods.get(pipeline_method.id),
        timeout=timedelta(minutes=2),
    )


@pytest.mark.depends(
    on=[
        "tests/test_datasets.py::test_datasets_create",
        "test_pipelines_create_method",
    ]
)
def test_pipelines_create(pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx):
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    if pytestconfig.getoption("skip_pipelines"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    account = ctx["account"]
    dataset: Dataset = ctx["dataset"]
    pipeline_method = ctx["pipeline_method"]

    evaluation_request = PipelineEvaluationRequest(
        dataset=dataset.id,
        inferenceSession=EvaluationInferenceSessionRequest(
            inferenceService="$(submission)",
            expires=datetime.now(timezone.utc) + timedelta(days=1),
            replicas=1,
            useSpotPods=False,
        ),
        replications=2,
        workersPerReplica=2,
    )
    print(evaluation_request.model_dump())

    # SafetyCase for JupyterNotebook
    safetycase_request = PipelineSafetyCaseRequest(
        method=pipeline_method.id,
        scope=AnalysisScope(
            evaluation=None,
            dataset=None,
            inferenceService="$(submission)",
        ),
        arguments=[
            AnalysisArgument(keyword="trueName", value="Hans Sprungfeld"),
            AnalysisArgument(keyword="isOutlier", value="true"),
        ],
        inputs=[
            # The request depends on the Evaluation step
            AnalysisInput(keyword="cromulence", entity="$(evaluation.id)"),
        ],
    )

    pipeline_request = PipelineCreateRequest(
        account=account,
        name="test",
        nodes={
            "evaluation": PipelineNode(name="evaluation", request=evaluation_request),
            "safetycase": PipelineNode(name="safetycase", request=safetycase_request),
        },
        parameters={
            "submission": PipelineParameter(
                keyword="submission", description="The input dataset"
            ),
        },
    )
    print(pipeline_request.model_dump())

    pipeline = dyffapi.pipelines.create(pipeline_request)
    print(f"pipeline: {pipeline.id}")
    ctx["pipeline"] = pipeline

    wait_for_success(
        lambda: dyffapi.pipelines.get(pipeline.id),
        timeout=timedelta(minutes=1),
    )


@pytest.mark.depends(
    on=[
        "tests/test_inference.py::test_inferenceservices_create_mock",
        "test_pipelines_create",
    ]
)
def test_pipelines_run(pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx):
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    if pytestconfig.getoption("skip_pipelines"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    account = ctx["account"]
    inferenceService: InferenceService = ctx["inferenceservice_mock"]
    pipeline: Pipeline = ctx["pipeline"]

    request = PipelineRunRequest(
        account=account,
        pipeline=pipeline.id,
        arguments={"submission": inferenceService.id},
    )

    pipeline_run = dyffapi.pipelines.run(pipeline.id, request)
    print(f"pipeline_run: {pipeline_run.id}")
    ctx["pipeline_run"] = pipeline_run

    wait_for_pipeline_run_success(
        lambda: dyffapi.pipelines.get_run_status(pipeline_run.id),
        timeout=timedelta(minutes=10),
    )


@pytest.mark.depends(
    on=[
        "tests/test_inference.py::test_inferenceservices_create_container",
        "test_pipelines_create",
    ]
)
def test_pipelines_run_container(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx
):
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    if pytestconfig.getoption("skip_pipelines"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    account = ctx["account"]
    inferenceService: InferenceService = ctx["inferenceservice_container"]
    pipeline: Pipeline = ctx["pipeline"]

    request = PipelineRunRequest(
        account=account,
        pipeline=pipeline.id,
        arguments={"submission": inferenceService.id},
    )

    pipeline_run = dyffapi.pipelines.run(pipeline.id, request)
    print(f"pipeline_run: {pipeline_run.id}")
    ctx["pipeline_run"] = pipeline_run

    wait_for_pipeline_run_success(
        lambda: dyffapi.pipelines.get_run_status(pipeline_run.id),
        timeout=timedelta(minutes=10),
    )
