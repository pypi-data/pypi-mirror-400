#!/usr/bin/python3
import logging
from typing import Any

import akeyless
import clearskies

import clearskies_gitlab
from clearskies_gitlab.graphql import models as graphql
from clearskies_gitlab.rest import models as rest

logging.basicConfig(level=logging.WARN)


def get_project(
    gitlab_rest_projects: rest.GitlabRestProject, gitlab_gql_projects: graphql.GitlabProject
) -> dict[str, Any]:
    """Local test for projects."""
    project = gitlab_rest_projects.find("id=Cimpress-Technology/cimsec/cimsec-pypi")
    # print(f"Parent group: {project.group.name}")
    # print(f"Count: {len(search_projects)}")
    for variable in project.variables.paginate_all():
        print(f"Variable: {variable.key} = {variable.value}")

    gql_project = gitlab_gql_projects.find("id=278964")
    print(f"GQL Parent group ID: {gql_project.id}")
    print(f"GGL data: {gql_project.get_columns_data()}")
    return project.group.id
    # for project in search_projects.paginate_all():
    #     print(project.name)


def get_group(gitlab_rest_group: rest.GitlabRestGroup) -> dict[str, Any]:
    """Local test for groups."""
    group = gitlab_rest_group.find("id=Cimpress-Technology/cimsec")
    # print(f"Group name: {group.name}")
    # print(f"Count: {len(search_groups)}")
    for variable in group.variables.paginate_all():
        print(f"Variable: {variable.key} = {variable.value}")
    for project in group.projects.limit(5):
        print(f"Project: {project.name}")
    for member in group.members.limit(5):
        print(f"Member: {member.name}")
    return group.id


cli = clearskies.contexts.Cli(
    clearskies.EndpointGroup(
        [
            clearskies.endpoints.Callable(
                get_project,
                url="/project",
                return_standard_response=False,
            ),
            clearskies.endpoints.Callable(
                get_group,
                url="/group",
                return_standard_response=False,
            ),
        ]
    ),
    modules=[clearskies_gitlab],
    bindings={
        "akeyless_sdk": akeyless,
        "secrets": clearskies.secrets.Akeyless(access_id="p-je7a0rik2ptf", access_type="saml", profile="default"),
    },
)

if __name__ == "__main__":
    cli()
