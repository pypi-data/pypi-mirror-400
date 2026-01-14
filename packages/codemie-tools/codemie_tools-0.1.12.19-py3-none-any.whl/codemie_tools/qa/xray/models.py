from typing import Optional
from pydantic import BaseModel, Field
from codemie_tools.base.models import CodeMieToolConfig, CredentialTypes, RequiredField


class XrayConfig(CodeMieToolConfig):
    """Configuration for Xray Cloud integration.

    Xray is a comprehensive test management tool for Jira that supports
    manual and automated testing workflows with GraphQL API access.
    """

    credential_type: CredentialTypes = Field(
        default=CredentialTypes.XRAY,
        exclude=True,
        frozen=True
    )

    base_url: str = RequiredField(
        description="Xray Cloud base URL",
        json_schema_extra={
            "placeholder": "https://xray.cloud.getxray.app"
        }
    )

    client_id: str = RequiredField(
        description="Xray API client ID for authentication",
        json_schema_extra={
            "placeholder": "your_client_id",
            "help": "https://docs.getxray.app/display/XRAYCLOUD/Authentication+-+REST+v2"
        }
    )

    client_secret: str = RequiredField(
        description="Xray API client secret for authentication",
        json_schema_extra={
            "placeholder": "your_client_secret",
            "sensitive": True,
            "help": "https://docs.getxray.app/display/XRAYCLOUD/Authentication+-+REST+v2"
        }
    )

    limit: Optional[int] = Field(
        default=100,
        description="Maximum number of results to return per query"
    )

    verify_ssl: Optional[bool] = Field(
        default=True,
        description="Verify SSL certificates for API requests"
    )


class XrayGetTestsInput(BaseModel):
    """Input schema for getting tests from Xray."""

    jql: str = Field(
        ...,
        description="""
        JQL query to filter tests. Examples:
        - project = "CALC" AND type = Test
        - key in (CALC-1, CALC-2)
        - status = "To Do" AND assignee = currentUser()
        """.strip()
    )


class XrayCreateTestInput(BaseModel):
    """Input schema for creating a test in Xray."""

    graphql_mutation: str = Field(
        ...,
        description="""
        GraphQL mutation to create a new test in Xray.

        Example for Manual test:
        mutation {
            createTest(
                testType: { name: "Manual" },
                steps: [
                    { action: "Create first example step", result: "First step was created" },
                    { action: "Create second example step with data", data: "Data for the step", result: "Second step was created with data" }
                ],
                jira: {
                    fields: {
                        summary: "Exploratory Test",
                        project: { key: "CALC" }
                    }
                }
            ) {
                test {
                    issueId
                    testType { name }
                    steps { action data result }
                    jira(fields: ["key"])
                }
                warnings
            }
        }

        Example for Generic test:
        mutation {
            createTest(
                testType: { name: "Generic" },
                unstructured: "Perform exploratory tests on calculator.",
                jira: {
                    fields: {
                        summary: "Exploratory Test",
                        project: { key: "CALC" }
                    }
                }
            ) {
                test {
                    issueId
                    testType { name }
                    unstructured
                    jira(fields: ["key"])
                }
                warnings
            }
        }

        Mutation arguments:
        - testType: Test type (Manual, Generic, Cucumber, etc.)
        - steps: Step definitions for Manual tests
        - unstructured: Text definition for Generic tests
        - gherkin: Gherkin definition for Cucumber tests
        - preconditionIssueIds: Related precondition issue IDs
        - folderPath: Test repository folder path
        - jira: Jira issue fields (summary, project, description, etc.)
        """.strip()
    )


class XrayExecuteGraphQLInput(BaseModel):
    """Input schema for executing custom GraphQL queries/mutations."""

    graphql: str = Field(
        ...,
        description="""
        Custom GraphQL query or mutation to execute against Xray API.

        Query example:
        query {
            getTests(jql: "project = CALC", limit: 10) {
                results {
                    issueId
                    jira(fields: ["key", "summary"])
                    testType { name }
                }
            }
        }

        Mutation example:
        mutation {
            updateTest(
                issueId: "12345",
                testType: { name: "Manual" }
            ) {
                test {
                    issueId
                    testType { name }
                }
            }
        }

        Refer to Xray GraphQL API documentation for available queries and mutations:
        https://docs.getxray.app/display/XRAYCLOUD/GraphQL+API
        """.strip()
    )
