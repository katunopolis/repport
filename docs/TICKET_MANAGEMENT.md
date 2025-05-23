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
5. **Ticket Visibility**: Can make tickets public or private by toggling their visibility

## Ticket Visibility

The system supports both private and public tickets:

1. **Private Tickets (Default)**: Only visible to the creator and administrators
2. **Public Tickets**: Visible to all users, useful for:
   - Sharing common solutions or FAQs
   - Making announcements that affect multiple users
   - Providing reference examples for common issues

Administrators can toggle a ticket's visibility status in two ways:
- From the admin dashboard using the switch in the ticket list
- From the ticket detail page using the "Make Public"/"Make Private" button

## User Interface

### Ticket Visibility Indicators

Public tickets are visually distinguished using:
- A green "Public" chip in both ticket list and detail views
- Light green background color in the user's ticket list
- A "Shared" chip for tickets the user didn't create but can view

### Admin Toggle Controls

Administrators can toggle ticket visibility with:
- Switch controls in the ticket list:
  ```
  [Public/Private Toggle Switch] Public/Private
  ```
- Button in the ticket detail page:
  ```
  [Make Public] or [Make Private]
  ```

### Ticket Response UI

The ticket response interface enables multiple responses from administrators until a ticket is marked as closed:

```
+-------------------------------------------+
| Ticket Details                            |
+-------------------------------------------+
| Title: Cannot access my account     [Open]|
|                  [Public] [SOLVE BUTTON]  |
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
- Public/Private toggle switch in a dedicated column

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
  "status": "open",
  "is_public": false
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
- Public/private visibility status

### Toggle Ticket Visibility (Admin Only)

```
PUT /api/v1/tickets/{id}/toggle-public
```

**Request Body**:
```json
{
  "is_public": true
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Ticket visibility updated to public",
  "is_public": true
}
```

This endpoint:
1. Updates the ticket's visibility status
2. Returns a confirmation message and the new visibility state
3. Only works for admin users (403 error for regular users)

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
6. **Public Information**: Only make tickets public when they contain information that is:
   - Useful to multiple users
   - Does not contain sensitive or private information
   - Provides general solutions or announcements

## Implementation Details

The ticket visibility functionality is implemented with these key components:

1. **Database**:
   - `is_public` boolean field in the Ticket model (default: false)

2. **Frontend**:
   - `AdminDashboard.tsx` - Toggle switch in ticket list
   - `TicketPage.tsx` - Public/private toggle button
   - `UserDashboard.tsx` - Visual indicators for public tickets
   - `api.ts` - Contains the `toggleTicketPublic` API call

3. **Backend**:
   - `tickets.py` - Implements the `/tickets/{id}/toggle-public` endpoint
   - Modified ticket list endpoint to include public tickets for all users

The backend ensures:
- Only administrators can change ticket visibility
- Regular users can only see their own tickets plus public tickets
- Admin users can see all tickets regardless of visibility

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

5. **Public Ticket Indicators**:
   - Clear visual indicators for public tickets
   - Toggle controls for administrators
   - "Shared" indicators for tickets visible to users who didn't create them 