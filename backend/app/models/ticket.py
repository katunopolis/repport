from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    status: str = "open"  # open, in_progress, resolved, closed
    created_by: str  # email
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    response: Optional[str] = None
    resolved_at: Optional[datetime] = None

class TicketCreate(SQLModel):
    title: str
    description: str

class TicketResponse(SQLModel):
    id: int
    title: str
    description: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    response: Optional[str] = None
    resolved_at: Optional[datetime] = None
