from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from app.models.ticket import Ticket, TicketCreate, TicketResponse
from app.core.database import get_session
from app.core.email import send_ticket_created_notification, send_ticket_response_notification
from datetime import datetime

router = APIRouter()

@router.post("/tickets/", response_model=TicketResponse)
async def create_ticket(
    ticket: TicketCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    db_ticket = Ticket(**ticket.dict())
    session.add(db_ticket)
    await session.commit()
    await session.refresh(db_ticket)
    
    # Send notification email
    background_tasks.add_task(
        send_ticket_created_notification,
        email_to=ticket.created_by,
        ticket_title=ticket.title
    )
    
    return db_ticket

@router.get("/tickets/", response_model=List[TicketResponse])
async def list_tickets(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    result = await session.execute(
        "SELECT * FROM ticket ORDER BY created_at DESC LIMIT :limit OFFSET :skip",
        {"limit": limit, "skip": skip}
    )
    tickets = result.all()
    return tickets

@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        "SELECT * FROM ticket WHERE id = :ticket_id",
        {"ticket_id": ticket_id}
    )
    ticket = result.first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/tickets/{ticket_id}/respond")
async def respond_to_ticket(
    ticket_id: int,
    response: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        "SELECT * FROM ticket WHERE id = :ticket_id",
        {"ticket_id": ticket_id}
    )
    ticket = result.first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket
    ticket.response = response
    ticket.updated_at = datetime.utcnow()
    await session.commit()
    
    # Send response notification
    background_tasks.add_task(
        send_ticket_response_notification,
        email_to=ticket.created_by,
        ticket_title=ticket.title,
        response=response
    )
    
    return {"status": "success", "message": "Response sent successfully"}

@router.put("/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    status: str,
    session: AsyncSession = Depends(get_session)
):
    if status not in ["open", "in_progress", "resolved", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await session.execute(
        "SELECT * FROM ticket WHERE id = :ticket_id",
        {"ticket_id": ticket_id}
    )
    ticket = result.first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket status
    ticket.status = status
    ticket.updated_at = datetime.utcnow()
    if status in ["resolved", "closed"]:
        ticket.resolved_at = datetime.utcnow()
    
    await session.commit()
    return {"status": "success", "message": f"Ticket status updated to {status}"}
