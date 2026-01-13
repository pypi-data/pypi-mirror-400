# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2019, 2020, 2021, 2022 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-DB utils tests."""

from __future__ import absolute_import, print_function
from uuid import uuid4

import pytest

from reana_commons.config import SHARED_VOLUME_PATH

from reana_db.models import Workflow
from reana_db.utils import _get_workflow_with_uuid_or_name, split_run_number


@pytest.mark.parametrize(
    "run_number, run_number_major, run_number_minor",
    [
        ("1", 1, 0),
        ("156.12", 156, 12),
        ("2.4", 2, 4),
        (3.22, 3, 22),
        pytest.param(
            "1.2.3",
            None,
            None,
            marks=pytest.mark.xfail(raises=ValueError, strict=True),
        ),
    ],
)
def test_split_run_number(run_number, run_number_major, run_number_minor):
    """Tests for split_run_number()."""
    assert split_run_number(run_number) == (run_number_major, run_number_minor)


@pytest.mark.parametrize(
    "user_id,workflow_id,workspace_root_path,workspace_path",
    [
        (0, None, None, SHARED_VOLUME_PATH + "/users/0/workflows"),
        (0, 1, None, SHARED_VOLUME_PATH + "/users/0/workflows/1"),
        (0, 1, "/eos/myanalysis", "/eos/myanalysis/1"),
        (0, 1, SHARED_VOLUME_PATH, SHARED_VOLUME_PATH + "/users/0/workflows/1"),
        (0, 1, SHARED_VOLUME_PATH + "/db", SHARED_VOLUME_PATH + "/users/0/workflows/1"),
    ],
)
def test_build_workspace_path(
    user_id, workflow_id, workspace_root_path, workspace_path
):
    """Tests for build_workspace_path()."""
    from reana_db.utils import build_workspace_path

    assert (
        build_workspace_path(
            user_id=user_id,
            workflow_id=workflow_id,
            workspace_root_path=workspace_root_path,
        )
        == workspace_path
    )


def test_get_workflow_with_uuid_or_name(session, new_user):
    """Tests for _get_workflow_with_uuid_or_name."""
    workflow = Workflow(
        id_=uuid4(),
        name="workflow",
        owner_id=new_user.id_,
        reana_specification=[],
        type_="serial",
        logs="",
    )
    session.add(workflow)
    session.commit()

    user_uuid = str(new_user.id_)
    assert workflow == _get_workflow_with_uuid_or_name(str(workflow.id_), user_uuid)
    assert workflow == _get_workflow_with_uuid_or_name(workflow.name, user_uuid)
    assert workflow == _get_workflow_with_uuid_or_name(f"{workflow.name}.1", user_uuid)

    # Check that an exception is raised when passing the wrong owner
    another_user_uuid = str(uuid4())
    with pytest.raises(ValueError):
        _get_workflow_with_uuid_or_name(str(workflow.id_), another_user_uuid)
    with pytest.raises(ValueError):
        _get_workflow_with_uuid_or_name(workflow.name, another_user_uuid)
    with pytest.raises(ValueError):
        _get_workflow_with_uuid_or_name(f"{workflow.name}.1", another_user_uuid)
