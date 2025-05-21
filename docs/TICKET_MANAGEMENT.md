# Ticket Management Documentation

This document provides an overview of the ticket management functionality in the Repport system, focusing on the ticket creation, response, and resolution workflow.

## Ticket Workflow

The standard ticket lifecycle follows these steps:

1. **Creation**: User creates a ticket with a title, description, and initial status
2. **Initial Response**: Admin responds to the ticket
3. **Resolution**: Admin either:
   - Adds multiple responses until the issue is resolved
   - Formally solves the ticket, marking it as closed

## Admin Capabilities

Administrators have the following capabilities:

1. **View All Tickets**: Access to all tickets in the system
2. **Multiple Responses**: Can add several responses to a ticket as needed
3. **Status Management**: Can change ticket status (open, in_progress, closed)
4. **Ticket Resolution**: Can formally solve and close tickets with a final response

## User Interface

### Ticket Response UI

The ticket response interface enables multiple responses from administrators until a ticket is marked as closed:

```
+-------------------------------------------+
| Ticket Details                            |
+-------------------------------------------+
| Title: Cannot access my account     [Open]|
|                              [SOLVE BUTTON]
+-------------------------------------------+
| Created by: user@example.com              |
| Date: 2025-05-21 10:00:00                 |
+-------------------------------------------+
| Description:                              |
| I can't log into my account since...      |
+-------------------------------------------+
| Response:  [Admin]                        |
|                                           |
| Please try resetting your password...     |
| This response is highlighted with a       |
| light gray background and left border     |
+-------------------------------------------+
| Add Additional Response:                  |
|                                           |
| [Text Area]                               |
|                                           |
| [Submit Response]                         |
+-------------------------------------------+
```

### Response Styling

Admin responses are styled with the following visual cues:
- An "Admin" chip label next to the response heading
- A light gray background color to make the response stand out
- A colored left border to visually separate the response
- Medium font weight for better readability

### Ticket Table View

In the admin dashboard, tickets with responses are visually distinguished:
- Light blue background for rows with responses
- "Has Response" chip label next to the ticket title

### Solve Ticket Dialog

When an admin clicks the "Solve" button, a dialog appears to add a final response and close the ticket:

```
+-------------------------------------------+
| Solve Ticket                              |
+-------------------------------------------+
| Add a final response and close this       |
| ticket. Once closed, no further responses |
| can be added.                             |
|                                           |
| [Final Response Text Area]                |
|                                           |
| [Cancel]      [Solve & Close Ticket]      |
+-------------------------------------------+
```

## API Endpoints

### Create Ticket

```
POST /api/v1/tickets/
```

**Request Body**:
```json
{
  "title": "Cannot access my account",
  "description": "I'm having trouble logging in...",
  "status": "open"
}
```

### Respond to Ticket

```
POST /api/v1/tickets/{id}/respond
```

**Request Body**:
```json
{
  "response": "Please try the following steps..."
}
```

**Response**: Complete updated ticket object

This endpoint now returns the complete ticket object after responding, which includes:
- All ticket details
- The updated response text
- Timestamps for creation and updates

### Solve Ticket (Admin Only)

```
PUT /api/v1/tickets/{id}/solve
```

**Request Body**:
```json
{
  "response": "This issue has been resolved by..."
}
```

This endpoint:
1. Updates the ticket response with the final message
2. Sets the ticket status to "closed"
3. Records the resolution timestamp
4. Sends a notification to the user

## Best Practices

1. **Response Clarity**: Provide clear, concise responses to user tickets
2. **Ticket Lifecycle**: Keep tickets in "open" or "in_progress" status until fully resolved
3. **Response History**: Add multiple responses as needed to document the troubleshooting process
4. **Formal Resolution**: Always use the "Solve" feature to formally close tickets with a clear resolution message
5. **User Communication**: Ensure users understand the solution provided before closing tickets

## Implementation Details

The "Solve Ticket" functionality is implemented with these key components:

1. **Frontend**:
   - `TicketPage.tsx` - Includes solve button and dialog UI
   - `api.ts` - Contains the `solveTicket` API call

2. **Backend**:
   - `tickets.py` - Implements the `/tickets/{id}/solve` endpoint

The backend ensures:
- Only administrators can solve tickets
- Tickets are properly marked as closed
- Resolution timestamps are recorded
- Users receive notification of the resolution

## User Experience Improvements

1. **Response Visibility**: Admin responses are now highlighted with:
   - Distinctive styling with light gray background
   - Left border in the primary color
   - Admin badge for clear identification
   - Medium font weight for better readability

2. **Ticket Metadata**: Ticket creator and date information is now:
   - Displayed in a separate info box
   - Formatted more clearly with labels
   - More robust against missing date values

3. **Admin Dashboard**: Tickets with responses are now:
   - Visually identified with light blue background
   - Labeled with "Has Response" chip
   - Easier to distinguish from tickets without responses

4. **Persistent Conversations**: The updated response flow ensures:
   - Responses are properly preserved after submission
   - The ticket is automatically refreshed if needed
   - No more disappearing conversations
   - Better error handling for edge cases 