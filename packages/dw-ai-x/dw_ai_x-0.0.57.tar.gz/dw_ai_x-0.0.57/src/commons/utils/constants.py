"""
This module contains the constants used in the application.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Constants(BaseSettings):
    """
    Validates and maps environment variables for application constants.
    """

    PROJECT_ID: str | None = Field(default=None, description="GCP Project ID")
    BUCKET_NAME: str | None = Field(default=None, description="GCS Bucket Name")
    FIRESTORE_DATABASE_INTERNAL: str | None = Field(
        default=None, description="Firestore Internal Database Name"
    )
    TOPIC_ID: str | None = Field(default=None, description="PubSub Topic ID")
    EXECUTION_ENVIRONMENT: str = Field(
        default="cloud", description="Execution Environment"
    )
    LOCAL_USER_UUID: str = Field(
        default="test-user-uuid", description="Local User UUID for testing"
    )

    # TODO: Add these in project level settings not here here
    # You can add these directly to the class as they are not environment variables
    FS_ORGANIZATION_COLLECTION: str = "organizations"
    FS_USER_COLLECTION: str = "user"


# Initialize the constants as a singleton
constants = Constants()
