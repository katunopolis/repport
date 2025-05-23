from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from app.models.ticket import Ticket, TicketCreate, TicketResponse
from app.core.database import get_session
from app.core.email import send_ticket_created_notification, send_ticket_response_notification
from datetime import datetime
from sqlalchemy import text
from sqlmodel import select
from app.api.auth import current_active_user
from app.models.user import User
import logging

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets")

@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket: TicketCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    # Set the created_by field to the current user's email
    ticket_data = ticket.dict()
    ticket_data["created_by"] = current_user.email
    
    db_ticket = Ticket(**ticket_data)
    session.add(db_ticket)
    await session.commit()
    await session.refresh(db_ticket)
    
    # Send notification email
    background_tasks.add_task(
        send_ticket_created_notification,
        email_to=current_user.email,
        ticket_title=ticket.title
    )
    
    return db_ticket

@router.get("/", response_model=List[TicketResponse])
async def list_tickets(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user),
    skip: int = 0,
    limit: int = 100
):
    try:
        # Admin users can see all tickets
        if current_user.is_superuser:
            result = await session.execute(
                select(Ticket).order_by(Ticket.created_at.desc()).offset(skip).limit(limit)
            )
        else:
            # Non-admin users can see their own tickets OR public tickets
            result = await session.execute(
                select(Ticket)
                .where((Ticket.created_by == current_user.email) | (Ticket.is_public == True))
                .order_by(Ticket.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
        
        tickets = result.scalars().all()
        
        # Ensure all tickets have is_public set (for older records)
        for ticket in tickets:
            if not hasattr(ticket, 'is_public'):
                ticket.is_public = False
                
        return tickets
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch tickets: {str(e)}")

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    # Use SQLModel select instead of raw SQL
    result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if user has permission to view this ticket
    if not current_user.is_superuser and ticket.created_by != current_user.email and not ticket.is_public:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
    
    return ticket

# Add an explicit duplicate endpoint with trailing slash
@router.get("/{ticket_id}/", response_model=TicketResponse)
async def get_ticket_with_slash(
    ticket_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    return await get_ticket(ticket_id, session, current_user)

@router.post("/{ticket_id}/respond", response_model=TicketResponse)
async def respond_to_ticket(
    ticket_id: int,
    background_tasks: BackgroundTasks,
    response: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    # Use SQLModel select instead of raw SQL to get a proper model instance
    result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only admin or the creator can respond to a ticket
    if not current_user.is_superuser and ticket.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to respond to this ticket")
    
    # Update ticket
    ticket.response = response
    ticket.updated_at = datetime.utcnow()
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    
    # Send response notification
    background_tasks.add_task(
        send_ticket_response_notification,
        email_to=ticket.created_by,
        ticket_title=ticket.title,
        response=response
    )
    
    # Return the complete updated ticket object
    return ticket

# Add an explicit duplicate endpoint with trailing slash
@router.post("/{ticket_id}/respond/", response_model=TicketResponse)
async def respond_to_ticket_with_slash(
    ticket_id: int,
    background_tasks: BackgroundTasks,
    response: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    return await respond_to_ticket(ticket_id, background_tasks, response, session, current_user)

@router.put("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    status: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    if status not in ["open", "in_progress", "resolved", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Use SQLModel select instead of raw SQL to get a proper model instance
    result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only admin or the creator can update the ticket status
    if not current_user.is_superuser and ticket.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket's status")
    
    # Update ticket status
    ticket.status = status
    ticket.updated_at = datetime.utcnow()
    if status in ["resolved", "closed"]:
        ticket.resolved_at = datetime.utcnow()
    
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    
    return {"status": "success", "message": f"Ticket status updated to {status}"}

# Add an explicit duplicate endpoint with trailing slash
@router.put("/{ticket_id}/status/")
async def update_ticket_status_with_slash(
    ticket_id: int,
    status: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    return await update_ticket_status(ticket_id, status, session, current_user)

@router.put("/{ticket_id}/solve")
async def solve_ticket(
    ticket_id: int,
    background_tasks: BackgroundTasks,
    data: dict = Body(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    # Only admin can solve tickets
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only administrators can solve tickets")
    
    # Use SQLModel select to get a proper model instance
    result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket with final response and closed status
    ticket.response = data.get("response", ticket.response)
    ticket.status = "closed"
    ticket.updated_at = datetime.utcnow()
    ticket.resolved_at = datetime.utcnow()
    
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    
    # Send notification to user that their ticket was solved
    background_tasks.add_task(
        send_ticket_response_notification,
        email_to=ticket.created_by,
        ticket_title=ticket.title,
        response=f"Your ticket has been marked as solved with the following response:\n\n{ticket.response}"
    )
    
    return ticket

# Add an explicit duplicate endpoint with trailing slash
@router.put("/{ticket_id}/solve/")
async def solve_ticket_with_slash(
    ticket_id: int,
    background_tasks: BackgroundTasks,
    data: dict = Body(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    return await solve_ticket(ticket_id, background_tasks, data, session, current_user)

@router.put("/{ticket_id}/toggle-public")
async def toggle_ticket_public(
    ticket_id: int,
    is_public: bool = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    # Only admin can toggle public status
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only administrators can change ticket visibility")
    
    # Use SQLModel select to get a proper model instance
    result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket with public status
    ticket.is_public = is_public
    ticket.updated_at = datetime.utcnow()
    
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    
    return {"status": "success", "message": f"Ticket visibility updated to {'public' if is_public else 'private'}", "is_public": is_public}

# Add an explicit duplicate endpoint with trailing slash
@router.put("/{ticket_id}/toggle-public/")
async def toggle_ticket_public_with_slash(
    ticket_id: int,
    is_public: bool = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    return await toggle_ticket_public(ticket_id, is_public, session, current_user)
