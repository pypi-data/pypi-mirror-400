# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
import pytest
import requests

from dyff.audit.local.platform import DyffLocalPlatform
from dyff.client import Client, HttpResponseError, Timeout
from dyff.client.errors import HTTPError
from dyff.schema import commands, ids
from dyff.schema.platform import (
    CurveSpec,
    ScoreSpec,
    is_status_failure,
    is_status_success,
    is_status_terminal,
)
from dyff.schema.v0.r1.requests import DocumentationEditRequest

DATA_DIR = Path(__file__).parent.resolve() / "data"
COMPARISON_REPLICATIONS = 5


def validate_api_environment(pytestconfig):
    """Validate API endpoint and token for remote testing."""
    api_endpoint = pytestconfig.getoption("api_endpoint") or os.getenv(
        "DYFF_API_ENDPOINT"
    )
    api_token = pytestconfig.getoption("api_token") or os.getenv("DYFF_API_TOKEN")

    if not api_endpoint:
        raise RuntimeError(
            "DYFF_API_ENDPOINT required for remote testing "
            "(e.g., https://api.dyff.local/v0)"
        )

    if not api_token:
        raise RuntimeError(
            "DYFF_API_TOKEN required. Generate with: "
            "kubectl exec -n dyff <dyff-api-pod> -- python3 -m dyff.api.mgmt "
            "tokens create -t account -i <account-id> --role Admin"
        )

    # Test connectivity
    insecure = (
        pytestconfig.getoption("api_insecure") or os.getenv("DYFF_API_INSECURE") == "1"
    )
    health_url = api_endpoint.replace("/v0", "") + "/health"

    try:
        response = requests.get(
            health_url,
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=10,
            verify=not insecure,
        )
        response.raise_for_status()
        print(f"✓ API connection successful to {api_endpoint}")
    except requests.RequestException as e:
        raise RuntimeError(f"API connection failed: {e}")


def pytest_addoption(parser):
    parser.addoption("--storage_root", action="store", default=None)
    parser.addoption("--test_remote", action="store_true", default=False)
    parser.addoption("--new_account", action="store_true", default=False)
    parser.addoption("--api_endpoint", action="store", default=None)
    parser.addoption("--api_token", action="store", default=None)
    parser.addoption("--api_insecure", action="store_true", default=False)
    parser.addoption("--skip_workflows", action="store_true", default=False)
    parser.addoption("--skip_inference_mocks", action="store_true", default=False)
    parser.addoption("--skip_analyses", action="store_true", default=False)
    parser.addoption("--skip_analyses_detailed", action="store_true", default=False)
    parser.addoption("--skip_artifacts", action="store_true", default=False)
    parser.addoption("--skip_artifacts_run", action="store_true", default=False)
    parser.addoption("--skip_challenges", action="store_true", default=False)
    parser.addoption("--skip_documentation", action="store_true", default=False)
    parser.addoption("--skip_evaluations", action="store_true", default=False)
    parser.addoption("--skip_families", action="store_true", default=False)
    parser.addoption("--skip_huggingface", action="store_true", default=False)
    parser.addoption("--skip_methods", action="store_true", default=False)
    parser.addoption("--skip_modules", action="store_true", default=False)
    parser.addoption("--skip_pipelines", action="store_true", default=False)
    parser.addoption("--skip_sessions", action="store_true", default=False)
    parser.addoption("--skip_usecases", action="store_true", default=False)
    parser.addoption("--skip_errors", action="store_true", default=False)
    parser.addoption("--enable_extra", action="store_true", default=False)
    parser.addoption("--enable_flaky", action="store_true", default=False)
    parser.addoption("--enable_fuse", action="store_true", default=False)
    parser.addoption("--enable_vllm", action="store_true", default=False)
    parser.addoption("--enable_vllm_multinode", action="store_true", default=False)
    parser.addoption("--enable_comparisons", action="store_true", default=False)


def _create_client(pytestconfig, *, timeout: Optional[Timeout] = None) -> Client:
    endpoint = pytestconfig.getoption("api_endpoint") or os.environ["DYFF_API_ENDPOINT"]
    token = pytestconfig.getoption("api_token") or os.environ["DYFF_API_TOKEN"]
    insecure = (
        pytestconfig.getoption("api_insecure")
        or os.environ.get("DYFF_API_INSECURE") == "1"
    )
    return Client(api_key=token, endpoint=endpoint, insecure=insecure, timeout=timeout)


@pytest.fixture(scope="session", autouse=True)
def validate_test_environment(pytestconfig):
    """Validate test environment before running any tests."""
    if pytestconfig.getoption("test_remote"):
        validate_api_environment(pytestconfig)


@pytest.fixture(scope="session")
def dyffapi(
    pytestconfig, tmp_path_factory, validate_test_environment
) -> Client | DyffLocalPlatform:
    """Provides either a remote Client or a local DyffLocalPlatform."""
    if pytestconfig.getoption("test_remote"):
        return _create_client(pytestconfig)
    storage_root = pytestconfig.getoption("storage_root") or os.getenv(
        "DYFF_AUDIT_LOCAL_STORAGE_ROOT"
    )
    if storage_root:
        return DyffLocalPlatform(Path(storage_root).resolve())
    return DyffLocalPlatform(tmp_path_factory.mktemp("dyff"))


@pytest.fixture(scope="session")
def ctx(pytestconfig) -> dict[str, Any]:
    """Shared context for passing IDs between tests."""
    context: dict[str, Any] = {}
    if pytestconfig.getoption("test_remote"):
        if pytestconfig.getoption("new_account"):
            context["account"] = f"test-{ids.generate_entity_id()}"
        else:
            context["account"] = "test"
    else:
        account = ids.generate_entity_id()
        context["account"] = account
        # pre-create a dummy inference service so later tests depending on it can skip or use it
        from dyff.schema.platform import DyffModelWithID

        context["inferenceservice"] = DyffModelWithID(
            id=ids.generate_entity_id(), account=account
        )
    return context


@pytest.fixture(scope="session", autouse=True)
def cleanup(pytestconfig, dyffapi, ctx, request):
    """Ensure any sessions opened are cleaned up at the end."""

    def terminate():
        # This will delete any recorded inference sessions by ID
        for key in list(ctx):
            if key.startswith("inferencesession"):
                try:
                    dyffapi.inferencesessions.delete(ctx[key].id)
                except Exception:
                    pass

    request.addfinalizer(terminate)


def wait_for_ready(
    dyffapi: Client | DyffLocalPlatform, session_id: str, *, timeout: timedelta
):
    then = datetime.now(timezone.utc)
    while (datetime.now(timezone.utc) - then) < timeout:
        if dyffapi.inferencesessions.ready(session_id):
            return
        time.sleep(10)
    raise AssertionError("timeout")


def wait_for_status(
    get_entity_fn, target_status: str | list[str], *, timeout: timedelta
) -> str:
    if isinstance(target_status, str):
        target_status = [target_status]
    then = datetime.now(timezone.utc)
    while (datetime.now(timezone.utc) - then) < timeout:
        try:
            status = get_entity_fn().status
            if status in target_status:
                return status
        except HTTPError as ex:
            if ex.status != 404:
                raise
        except HttpResponseError as ex:
            if ex.status_code != 404:
                raise
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code != 404:
                raise
        time.sleep(10)
    raise AssertionError("timeout")


def wait_for_terminal_status(get_entity_fn, *, timeout: timedelta) -> str:
    then = datetime.now(timezone.utc)
    while (datetime.now(timezone.utc) - then) < timeout:
        try:
            status = get_entity_fn().status
            if is_status_terminal(status):
                return status
        except HTTPError as ex:
            if ex.status != 404:
                raise
        except HttpResponseError as ex:
            if ex.status_code != 404:
                raise
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code != 404:
                raise
        time.sleep(10)
    raise AssertionError("timeout")


def wait_for_success(get_entity_fn, *, timeout: timedelta):
    then = datetime.now(timezone.utc)
    while (datetime.now(timezone.utc) - then) < timeout:
        try:
            status = get_entity_fn().status
            if is_status_success(status):
                return
            elif is_status_failure(status):
                raise AssertionError(f"failure status: {status}")
        except HTTPError as ex:
            if ex.status != 404:
                raise
        except HttpResponseError as ex:
            if ex.status_code != 404:
                raise
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code != 404:
                raise
        time.sleep(10)
    raise AssertionError("timeout")


def wait_for_completion(get_entity_fn, *, timeout: timedelta):
    then = datetime.now(timezone.utc)
    while (datetime.now(timezone.utc) - then) < timeout:
        try:
            return get_entity_fn()
        except HTTPError as ex:
            if ex.status != 404:
                raise
        except HttpResponseError as ex:
            if ex.status_code != 404:
                raise
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code != 404:
                raise
        time.sleep(10)
    raise AssertionError("timeout")


def wait_for_pipeline_run_success(get_run_status_fn, *, timeout: timedelta):
    then = datetime.now(timezone.utc)
    while (datetime.now(timezone.utc) - then) < timeout:
        try:
            status = get_run_status_fn()
            for node, node_status in status.nodes.items():
                if is_status_failure(node_status.status):
                    raise AssertionError(f"node {node}: failure status: {node_status}")
                elif not is_status_success(node_status.status):
                    break
            else:
                return
        except HTTPError as ex:
            if ex.status != 404:
                raise
        time.sleep(10)
    raise AssertionError("timeout")


def download_and_assert(download_func, download_id, download_dir):
    with tempfile.TemporaryDirectory() as tmp:
        download_path = Path(tmp) / download_dir
        download_func(download_id, download_path)
        assert download_path.exists(), "Download directory was not created"
        assert any(download_path.iterdir()), "No files were downloaded"


def assert_documentation_exist(get_doc_func, resource_id):
    documentation = wait_for_completion(
        lambda: get_doc_func(resource_id),
        timeout=timedelta(minutes=2),
    )
    assert documentation is not None


def edit_documentation_and_assert(edit_doc_func, resource_id, **kwargs):
    edited_title = kwargs.get("title", "EditedTitle")
    edited_summary = kwargs.get("summary", "EditedSummary")
    edited_fullpage = kwargs.get("fullPage", "EditedFullPage")

    documentation_post_edit = wait_for_completion(
        lambda: edit_doc_func(
            resource_id,
            DocumentationEditRequest(
                documentation=commands.EditEntityDocumentationPatch(
                    title=edited_title,
                    summary=edited_summary,
                    fullPage=edited_fullpage,
                ),
            ),
        ),
        timeout=timedelta(minutes=2),
    )

    assert documentation_post_edit.title == edited_title
    assert documentation_post_edit.summary == edited_summary
    assert documentation_post_edit.fullPage == edited_fullpage


def score_specs_for_tests():
    return [
        ScoreSpec(
            name="float_unit_primary",
            title="Float (primary; with unit)",
            summary="A float with a unit that is the 'primary' score",
            minimum=0,
            maximum=1,
            unit="MJ/kg",
        ),
        ScoreSpec(
            name="int",
            title="Integer",
            summary="An Integer score",
            valence="positive",
            priority="secondary",
        ),
        ScoreSpec(
            name="int_big",
            title="Integer (Big)",
            summary="A big Integer score",
            valence="positive",
            priority="secondary",
        ),
        ScoreSpec(
            name="int_percent",
            title="Integer (Percentage)",
            summary="A percentage represented as an integer",
            valence="positive",
            priority="secondary",
            minimum=0,
            maximum=100,
        ),
        ScoreSpec(
            name="no_display",
            title="Not displayed",
            summary="A score that should not be displayed",
            valence="negative",
            priority="secondary",
        ),
        ScoreSpec(
            name="exp_rate_low",
            title="Exponential Distribution (Low Rate)",
            summary="An exponential distribution with a low rate, leading to a gradual decay.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=10.0,
        ),
        ScoreSpec(
            name="exp_rate_high",
            title="Exponential Distribution (High Rate)",
            summary="An exponential distribution with a high rate, causing rapid decay.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=10.0,
        ),
        ScoreSpec(
            name="poisson_rate_low",
            title="Poisson Distribution (Low Rate)",
            summary="A Poisson distribution with a low average event rate, generating fewer events.",
            valence="positive",
            priority="secondary",
            minimum=0,
            maximum=20,
        ),
        ScoreSpec(
            name="poisson_rate_high",
            title="Poisson Distribution (High Rate)",
            summary="A Poisson distribution with a high average event rate, generating more events.",
            valence="positive",
            priority="secondary",
            minimum=0,
            maximum=20,
        ),
        ScoreSpec(
            name="normal_standard",
            title="Normal Distribution (Standard)",
            summary="A normal distribution with a mean of 0 and a standard deviation of 1.",
            valence="positive",
            priority="secondary",
            minimum=-5.0,
            maximum=5.0,
        ),
        ScoreSpec(
            name="normal_shifted",
            title="Normal Distribution (Shifted)",
            summary="A normal distribution with a mean of 5 and a standard deviation of 2.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=10.0,
        ),
        ScoreSpec(
            name="bimodal_close",
            title="Bi-Modal Distribution (Close Peaks)",
            summary="A bi-modal distribution with two peaks close to each other, creating moderate separation.",
            valence="positive",
            priority="secondary",
            minimum=-5.0,
            maximum=15.0,
        ),
        ScoreSpec(
            name="bimodal_separated",
            title="Bi-Modal Distribution (Separated Peaks)",
            summary="A bi-modal distribution with two peaks far apart, creating clear separation between clusters.",
            valence="positive",
            priority="secondary",
            minimum=-5.0,
            maximum=20.0,
        ),
        ScoreSpec(
            name="close_together",
            title="Close Values Around 50",
            summary="Values generated close to 50 within an expanded range of ±10.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=100.0,
        ),
        ScoreSpec(
            name="in_middle",
            title="Values in the Middle",
            summary="Values generated in the middle of the range, centered around 50.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=100.0,
        ),
        ScoreSpec(
            name="near_min",
            title="Values Near Minimum",
            summary="Values generated near the minimum, within the range of 0 to 10.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=100.0,
        ),
        ScoreSpec(
            name="near_max",
            title="Values Near Maximum",
            summary="Values generated near the maximum, within the range of 90 to 100.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=100.0,
        ),
        ScoreSpec(
            name="extreme_outliers",
            title="Extreme Outliers",
            summary="Extreme outlier values that are far outside the typical range.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=100.0,
        ),
        ScoreSpec(
            name="same_values",
            title="All Values Exactly the Same",
            summary="All values are exactly the same, uniform data for testing.",
            valence="positive",
            priority="secondary",
            minimum=0.0,
            maximum=100.0,
        ),
        CurveSpec(
            name="roc_curve",
            title="ROC Curve",
            summary="Receiver operating characteristic.",
            dimensions={
                "x": ScoreSpec(
                    name="x",
                    title="False Positive Rate",
                    summary="X-axis: FPR",
                ),
                "y": ScoreSpec(
                    name="y",
                    title="True Positive Rate",
                    summary="Y-axis: TPR",
                ),
                "threshold": ScoreSpec(
                    name="threshold",
                    title="Threshold",
                    summary="Decision threshold",
                ),
            },
        ),
    ]
