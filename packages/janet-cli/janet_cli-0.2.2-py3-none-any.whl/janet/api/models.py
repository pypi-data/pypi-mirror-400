"""Pydantic models for API responses."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class Comment(BaseModel):
    """Ticket comment model."""

    id: str
    content: str
    created_by: str
    created_at: str
    updated_at: str


class Attachment(BaseModel):
    """Ticket attachment model."""

    id: str
    mapping_id: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    gcs_uri: str
    signed_url: Optional[str] = None
    ai_description: Optional[str] = None
    ai_processing_status: str
    uploaded_by: str
    created_at: str
    is_direct: bool


class ChildTask(BaseModel):
    """Child task model."""

    id: str
    childIdentifier: str
    fullIdentifier: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    displayOrder: str
    createdBy: str
    updatedBy: Optional[str] = None
    createdAt: str
    updatedAt: str


class Ticket(BaseModel):
    """Ticket model."""

    id: str
    ticket_identifier: str
    ticket_key: str
    title: str
    description: Optional[str] = None
    description_yjs_binary: Optional[str] = None
    ai_summary: Optional[str] = None
    ticket_evaluation: Optional[str] = None
    status: str
    priority: str
    issue_type: str
    assignees: List[str] = []
    labels: List[str] = []
    story_points: Optional[str] = None
    due_date: Optional[str] = None
    sprint: Optional[str] = None
    creator: str
    project_id: str
    organization_id: str
    created_at: str
    updated_at: str
    comments: List[Comment] = []
    child_tasks: List[ChildTask] = []


class OrganizationMember(BaseModel):
    """Organization member model."""

    id: str
    userId: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    profilePictureUrl: Optional[str] = None
    role: str
    status: str
    joinedAt: str
