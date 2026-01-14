from __future__ import annotations

from pydantic import BaseModel, Field

from . import (
    ApikeyDescription,
    ApiKeyId,
    ApikeyName,
    ApikeyPermission,
    ApikeySecretRedacted,
    ApikeyStatus,
    CreatedAt,
    Event,
    NotificationId,
    Timestamp,
    UpdatedAt,
)


class Data(BaseModel):
    id: ApiKeyId | None = None
    name: ApikeyName | None = None
    description: ApikeyDescription | None = None
    key: ApikeySecretRedacted | None = None
    status: ApikeyStatus | None = "active"
    permissions: list[ApikeyPermission] | None = Field(
        None,
        description="Permissions assigned to this API key. Determines what actions the API key can perform.",
    )
    expires_at: Timestamp | None = Field(
        None, description="RFC 3339 datetime string of when this API key expires."
    )
    last_used_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this API key was last used (accurate to within 1 hour). `null` if never used.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="API Key Notification"
    )


class Expired(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="API Key Notification"
    )


class Expiring(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="API Key Notification"
    )


class Exposed(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="API Key Notification"
    )


class Revoked(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="API Key Notification"
    )


class Updated(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="API Key Notification"
    )
