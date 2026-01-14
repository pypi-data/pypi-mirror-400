# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# mypy: disable-error-code="import-untyped"
import time
from datetime import datetime, timedelta, timezone

import pytest
from conftest import (  # type: ignore[import-not-found]
    DATA_DIR,
    assert_documentation_exist,
    edit_documentation_and_assert,
    wait_for_pipeline_run_success,
    wait_for_success,
)

from dyff.audit.local.platform import DyffLocalPlatform
from dyff.client import Client
from dyff.schema import commands
from dyff.schema.platform import (
    Challenge,
    ChallengeContent,
    ChallengeContentPage,
    ChallengeRules,
    ChallengeTask,
    ChallengeTaskContent,
    ChallengeTaskExecutionEnvironment,
    ChallengeTaskExecutionEnvironmentChoices,
    ChallengeTaskRules,
    ChallengeTaskSchedule,
    ChallengeTaskVisibility,
    ChallengeVisibility,
    Entities,
    EntityIdentifier,
    InferenceService,
    Method,
    Pipeline,
    SubmissionStructure,
    Team,
    TeamAffiliation,
    TeamMember,
)
from dyff.schema.requests import (
    ChallengeContentEditRequest,
    ChallengeCreateRequest,
    ChallengeRulesEditRequest,
    ChallengeTaskCreateRequest,
    ChallengeTaskRulesEditRequest,
    ChallengeTeamCreateRequest,
    SubmissionCreateRequest,
    TeamEditRequest,
)


@pytest.mark.datafiles(DATA_DIR)
def test_challenges_create(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    account: str = ctx["account"]

    challenge = dyffapi.challenges.create(
        ChallengeCreateRequest(
            account=account,
            content=ChallengeContent(page=ChallengeContentPage(summary="summary")),
            rules=ChallengeRules(
                visibility=ChallengeVisibility(
                    teams={"*": "submitter", "nobody": "public"}
                )
            ),
        )
    )

    print(f"challenge: {challenge.id}")
    ctx["challenge"] = challenge

    wait_for_success(
        lambda: dyffapi.challenges.get(challenge.id),
        timeout=timedelta(minutes=2),
    )


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "test_challenges_create",
    ]
)
def test_challenges_edit_content(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    challenge: Challenge = ctx["challenge"]

    dyffapi.challenges.edit_content(
        challenge.id,
        ChallengeContentEditRequest(
            content=commands.ChallengeContentPatch(
                page=commands.ChallengeContentPagePatch(summary="", body="body")
            )
        ),
    )

    time.sleep(10)

    updated = dyffapi.challenges.get(challenge.id)
    assert updated.content.page.title == "Untitled Challenge"
    assert updated.content.page.summary == ""
    assert updated.content.page.body == "body"


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "test_challenges_create",
        "test_challenges_create_team",
    ]
)
def test_challenges_edit_rules(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    challenge: Challenge = ctx["challenge"]
    team: Team = ctx["team"]

    dyffapi.challenges.edit_rules(
        challenge.id,
        ChallengeRulesEditRequest(
            rules=commands.ChallengeRulesPatch(
                visibility=commands.ChallengeRulesVisibilityPatch(
                    teams={"nobody": None, team.id: "public"}
                )
            )
        ),
    )

    time.sleep(10)

    updated = dyffapi.challenges.get(challenge.id)
    assert updated.rules.visibility.teams == {
        "*": "submitter",
        team.id: "public",
    }


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "tests/test_pipelines.py::test_pipelines_create",
        "test_challenges_create",
    ]
)
def test_challenges_create_task(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    account: str = ctx["account"]
    challenge: Challenge = ctx["challenge"]
    pipeline: Pipeline = ctx["pipeline"]
    method: Method = ctx["pipeline_method"]

    request = ChallengeTaskCreateRequest(
        account=account,
        challenge=challenge.id,
        name="test",
        assessment=pipeline.id,
        rules=ChallengeTaskRules(
            executionEnvironment=ChallengeTaskExecutionEnvironmentChoices(
                choices={
                    "default": ChallengeTaskExecutionEnvironment(
                        cpu="1",
                        memory="1Gi",
                    ),
                    "big": ChallengeTaskExecutionEnvironment(
                        cpu="2",
                        memory="1Gi",
                    ),
                },
            ),
            schedule=ChallengeTaskSchedule(
                openingTime=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc),
            ),
            visibility=ChallengeTaskVisibility(
                scores={
                    method.id: {
                        "float_unit_primary": "public",
                        "int": "public",
                        "*": "reviewer",
                    },
                    "*": {"int_percent": "public"},
                },
            ),
        ),
        content=ChallengeTaskContent(page=ChallengeContentPage(summary="summary")),
        submissionStructure=SubmissionStructure(
            submissionKind=Entities.InferenceService.value,
            pipelineKeyword="submission",
        ),
    )
    task = dyffapi.challenges.create_task(challenge.id, request)

    print(f"challengetask: {task.id}")
    ctx["challengetask"] = task

    time.sleep(10)
    stored_task = dyffapi.challenges.get(challenge.id).tasks[task.id]
    assert stored_task == task


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "test_challenges_create_task",
    ]
)
def test_challenges_edit_task_content(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    challenge: Challenge = ctx["challenge"]
    task: ChallengeTask = ctx["challengetask"]

    dyffapi.challenges.edit_task_content(
        challenge.id,
        task.id,
        ChallengeContentEditRequest(
            content=commands.ChallengeContentPatch(
                page=commands.ChallengeContentPagePatch(summary="", body="body")
            )
        ),
    )

    time.sleep(10)

    updated = dyffapi.challenges.get(challenge.id)
    updated_task = updated.tasks[task.id]
    assert updated_task.content.page.title == "Untitled Challenge"
    assert updated_task.content.page.summary == ""
    assert updated_task.content.page.body == "body"


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "test_challenges_create_task",
    ]
)
def test_challenges_edit_task_rules(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    challenge: Challenge = ctx["challenge"]
    task: ChallengeTask = ctx["challengetask"]
    method: Method = ctx["pipeline_method"]

    dyffapi.challenges.edit_task_rules(
        challenge.id,
        task.id,
        ChallengeTaskRulesEditRequest.model_validate(
            {
                "executionEnvironment": {
                    "choices": {
                        "default": {
                            "cpu": "2",
                            "memory": "1Gi",
                        },
                        "big": None,
                        "small": {
                            "cpu": "1",
                            "memory": "512Mi",
                        },
                    }
                },
                "schedule": {
                    "openingTime": None,
                    "closingTime": datetime(
                        year=2032, month=1, day=1, tzinfo=timezone.utc
                    ),
                    "submissionLimitPerCycle": 2,
                },
                "visibility": {
                    "scores": {
                        method.id: {
                            "float_unit_primary": None,
                            "int": "reviewer",
                        },
                        "*": None,
                    },
                },
            }
        ),
    )

    time.sleep(10)

    updated = dyffapi.challenges.get(challenge.id)
    updated_task = updated.tasks[task.id]
    assert updated_task.rules.executionEnvironment.model_dump() == {
        "choices": {
            "default": {
                "accelerators": {},
                "cpu": "2",
                "memory": "1Gi",
            },
            "small": {
                "accelerators": {},
                "cpu": "1",
                "memory": "512Mi",
            },
        }
    }
    # The round-trip encoding results in a different type of tzinfo object
    # even though the two are semantically equivalent
    assert updated_task.rules.schedule.model_dump(mode="json") == ChallengeTaskSchedule(
        closingTime=datetime(year=2032, month=1, day=1, tzinfo=timezone.utc),
        submissionLimitPerCycle=2,
    ).model_dump(mode="json")

    assert updated_task.rules.visibility.model_dump() == {
        "scores": {
            method.id: {
                "int": "reviewer",
                "*": "reviewer",
            }
        }
    }


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "test_challenges_create",
    ]
)
def test_challenges_create_team(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    account: str = ctx["account"]
    challenge: Challenge = ctx["challenge"]
    request = ChallengeTeamCreateRequest(
        account=account,
        members={
            "rusty": TeamMember(
                name="Rusty Shackleford",
                isCorrespondingMember=True,
                affiliations=["dales_dead_bug"],
            ),
            "peggy": TeamMember(
                name="Peggy Hill",
                isCorrespondingMember=False,
                affiliations=["tom_landry_middle_school"],
            ),
        },
        affiliations={
            "dales_dead_bug": TeamAffiliation(
                name="Dale's Dead Bug",
            ),
            "tom_landry_middle_school": TeamAffiliation(
                name="Tom Landry Middle School",
            ),
        },
    )
    team = dyffapi.challenges.create_team(challenge.id, request)

    print(f"team: {team.id}")
    ctx["team"] = team

    time.sleep(10)
    stored_team = dyffapi.teams.get(team.id)
    assert stored_team.members == team.members
    assert stored_team.affiliations == team.affiliations


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "test_challenges_create_team",
    ]
)
def test_challenges_list_teams(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    challenge: Challenge = ctx["challenge"]

    teams = dyffapi.challenges.teams(challenge.id)
    assert len(teams) == 1


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "test_challenges_create_team",
    ]
)
def test_challenges_edit_team(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    team: Team = ctx["team"]

    dyffapi.teams.edit(
        team.id,
        TeamEditRequest(
            members={
                "rusty": None,
                "hank": TeamMember(
                    name="Hank Hill",
                    isCorrespondingMember=True,
                    affiliations=["strickland_propane"],
                ),
            },
            affiliations={
                "dales_dead_bug": None,
                "strickland_propane": TeamAffiliation(
                    name="Strickland Propane",
                    note="Taste the meat, not the heat!",
                ),
            },
        ),
    )

    time.sleep(10)
    stored_team = dyffapi.teams.get(team.id)
    assert stored_team.members == {
        "peggy": TeamMember(
            name="Peggy Hill",
            isCorrespondingMember=False,
            affiliations=["tom_landry_middle_school"],
        ),
        "hank": TeamMember(
            name="Hank Hill",
            isCorrespondingMember=True,
            affiliations=["strickland_propane"],
        ),
    }
    assert stored_team.affiliations == {
        "tom_landry_middle_school": TeamAffiliation(name="Tom Landry Middle School"),
        "strickland_propane": TeamAffiliation(
            name="Strickland Propane",
            note="Taste the meat, not the heat!",
        ),
    }


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.depends(
    on=[
        "test_challenges_create_task",
    ]
)
def test_challenges_submit(
    pytestconfig, dyffapi: Client | DyffLocalPlatform, ctx, datafiles
):
    if pytestconfig.getoption("skip_challenges"):
        pytest.skip()
    if not pytestconfig.getoption("test_remote"):
        pytest.skip()
    assert isinstance(dyffapi, Client)

    account: str = ctx["account"]
    challenge: Challenge = ctx["challenge"]
    task: ChallengeTask = ctx["challengetask"]
    team: Team = ctx["team"]
    inferenceService: InferenceService = ctx["inferenceservice_mock"]

    submission = dyffapi.challenges.submit(
        challenge.id,
        task.id,
        SubmissionCreateRequest(
            account=account,
            team=team.id,
            submission=EntityIdentifier.of(inferenceService),
        ),
    )

    print(f"challengesubmission {submission.id}")
    ctx["challengesubmission"] = submission

    wait_for_pipeline_run_success(
        lambda: dyffapi.pipelines.get_run_status(submission.pipelineRun),
        timeout=timedelta(minutes=10),
    )
