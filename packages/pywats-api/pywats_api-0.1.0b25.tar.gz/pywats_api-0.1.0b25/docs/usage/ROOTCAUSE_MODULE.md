# RootCause Module Usage Guide

## Overview

The RootCause module provides a ticketing system for tracking quality issues, root cause investigations, and corrective actions in WATS. It supports the 8D (Eight Disciplines) problem-solving methodology commonly used in electronics manufacturing.

## Quick Start

```python
from pywats import pyWATS
from pywats.domains.rootcause import TicketStatus, TicketPriority, TicketView

api = pyWATS(base_url="https://wats.example.com", token="credentials")

# Get open tickets assigned to you
tickets = api.rootcause.get_tickets(
    status=TicketStatus.OPEN,
    view=TicketView.ASSIGNED
)

# Create a new ticket
ticket = api.rootcause.create_ticket(
    subject="Solder Bridge Defect - ICT Line 1",
    priority=TicketPriority.HIGH,
    initial_comment="Detected 5% defect rate on PCBA-001"
)
```

## Ticket Status

```python
from pywats.domains.rootcause import TicketStatus

# Individual statuses (IntFlag - can be combined)
TicketStatus.OPEN          # 1 - New ticket
TicketStatus.IN_PROGRESS   # 2 - Being worked on
TicketStatus.ON_HOLD       # 4 - Temporarily paused
TicketStatus.SOLVED        # 8 - Solution found
TicketStatus.CLOSED        # 16 - Closed
TicketStatus.ARCHIVED      # 32 - Archived

# Combining statuses for filtering
active = TicketStatus.OPEN | TicketStatus.IN_PROGRESS  # Open or In Progress
all_active = TicketStatus.OPEN | TicketStatus.IN_PROGRESS | TicketStatus.ON_HOLD
```

## Ticket Priority

```python
from pywats.domains.rootcause import TicketPriority

TicketPriority.LOW     # 0 - Low priority
TicketPriority.MEDIUM  # 1 - Normal priority
TicketPriority.HIGH    # 2 - High priority (production impact)
```

## Ticket Views

```python
from pywats.domains.rootcause import TicketView

TicketView.ASSIGNED   # 0 - Tickets assigned to you
TicketView.FOLLOWING  # 1 - Tickets you're following
TicketView.ALL        # 2 - All tickets (requires permission)
```

## Basic Operations

### 1. Get Tickets

```python
# Get tickets assigned to you (default view)
my_tickets = api.rootcause.get_tickets(
    status=TicketStatus.OPEN | TicketStatus.IN_PROGRESS,
    view=TicketView.ASSIGNED
)

for ticket in my_tickets:
    print(f"#{ticket.ticket_number}: {ticket.subject}")
    print(f"  Status: {TicketStatus(ticket.status).name}")
    print(f"  Priority: {TicketPriority(ticket.priority).name}")
    print(f"  Assignee: {ticket.assignee}")

# Get all open tickets
all_open = api.rootcause.get_tickets(
    status=TicketStatus.OPEN,
    view=TicketView.ALL
)

# Get active tickets (convenience method)
active = api.rootcause.get_active_tickets()  # OPEN | IN_PROGRESS
```

### 2. Get Single Ticket

```python
# Get ticket by ID
ticket = api.rootcause.get_ticket(ticket_id)

if ticket:
    print(f"Ticket #{ticket.ticket_number}")
    print(f"Subject: {ticket.subject}")
    print(f"Owner: {ticket.owner}")
    print(f"Assignee: {ticket.assignee}")
    print(f"Team: {ticket.team}")
    print(f"Created: {ticket.created_utc}")
    
    # History (comments and updates)
    if ticket.history:
        print(f"History entries: {len(ticket.history)}")
        for update in ticket.history:
            print(f"  - {update.update_utc}: {update.content[:50]}...")
```

### 3. Create Ticket

```python
# Basic ticket
ticket = api.rootcause.create_ticket(
    subject="ICT Failure Rate Spike",
    priority=TicketPriority.HIGH,
    initial_comment="Failure rate increased from 1% to 5% this morning."
)

# Ticket linked to a test report
ticket = api.rootcause.create_ticket(
    subject=f"Failure Investigation - {serial_number}",
    priority=TicketPriority.HIGH,
    report_uuid=report_id,  # Link to failing report
    initial_comment="Investigating test failure on unit..."
)

# Ticket with assignee and team
ticket = api.rootcause.create_ticket(
    subject="Process Issue - Reflow Profile",
    priority=TicketPriority.MEDIUM,
    assignee="quality_engineer",
    team="Quality Team",
    initial_comment="Temperature profile may need adjustment."
)
```

### 4. Update Ticket

```python
# Get ticket, modify, update
ticket = api.rootcause.get_ticket(ticket_id)
ticket.priority = TicketPriority.HIGH
ticket.team = "Engineering Team"

updated = api.rootcause.update_ticket(ticket)
```

### 5. Add Comment

```python
# Add comment to ticket
api.rootcause.add_comment(
    ticket_id=ticket.ticket_id,
    comment="Completed 5-Why analysis. Root cause identified as incorrect stencil."
)
```

### 6. Change Status

```python
# Change ticket status
api.rootcause.change_status(
    ticket_id=ticket.ticket_id,
    status=TicketStatus.IN_PROGRESS
)

# Mark as solved
api.rootcause.change_status(
    ticket_id=ticket.ticket_id,
    status=TicketStatus.SOLVED
)
```

### 7. Assign Ticket

```python
# Assign to user
api.rootcause.assign_ticket(
    ticket_id=ticket.ticket_id,
    assignee="john.smith"
)
```

### 8. Archive Tickets

```python
# Archive solved tickets
api.rootcause.archive_tickets([ticket_id1, ticket_id2])

# Note: Only SOLVED tickets can be archived
```

## Team Assignment with Tags

Tags can be used to store team member roles:

```python
from pywats.shared import Setting

# Get ticket and add team member tags
ticket = api.rootcause.get_ticket(ticket_id)

team_tags = [
    Setting(key="Team_Champion", value="J. Smith"),
    Setting(key="Team_Leader", value="M. Johnson"),
    Setting(key="Team_ProcessEng", value="K. Williams"),
    Setting(key="Team_TestEng", value="L. Chen"),
    Setting(key="Team_QualityEng", value="R. Patel"),
]

# Add tags to ticket
if ticket.tags:
    ticket.tags.extend(team_tags)
else:
    ticket.tags = team_tags

api.rootcause.update_ticket(ticket)
```

## 8D Problem-Solving Workflow

The 8D methodology is a structured approach to problem solving. Here's how to implement it with RootCause tickets:

### D0: Preparation

```python
# Create ticket for the problem
ticket = api.rootcause.create_ticket(
    subject=f"[8D] Solder Bridge Defect - {serial_number}",
    priority=TicketPriority.HIGH,
    report_uuid=failing_report_id,
    initial_comment="""
## D0: Preparation

### Emergency Response Actions
1. Quarantine affected batch
2. Stop production on affected line
3. Notify Quality Manager

### Symptom Description
- Defect: Solder bridge on U3 (MCU)
- Impact: ICT test failure
- Urgency: HIGH - Production stopped
"""
)
```

### D1: Establish Team

```python
# Document team formation
d1_comment = """
## D1: Team Assembly

### Cross-Functional Team

| Role | Name | Responsibility |
|------|------|----------------|
| Champion | J. Smith | Executive sponsor |
| Leader | M. Johnson | Investigation lead |
| Process Engineer | K. Williams | Manufacturing process |
| Test Engineer | L. Chen | Test system expert |
| Quality Engineer | R. Patel | Quality documentation |

### Team Charter
- Objective: Identify root cause and implement corrective action
- Timeline: 2 weeks
- Meetings: Daily standup at 09:00
"""

api.rootcause.add_comment(ticket.ticket_id, d1_comment)
api.rootcause.change_status(ticket.ticket_id, TicketStatus.IN_PROGRESS)
```

### D2: Problem Definition

```python
# Document problem using 5W2H
d2_comment = """
## D2: Problem Definition (5W2H)

### WHAT is the problem?
Solder bridges on U3 MCU pins 12-13

### WHERE was it found?
ICT Station 01, Production Line 2

### WHEN did it occur?
Started 2024-12-13 morning shift

### WHO found it?
Automated ICT test system

### WHY is it a problem?
- Causes test failures
- 5% defect rate (threshold: 1%)
- Production line stopped

### HOW MANY affected?
5 units out of 100 tested

### HOW was it detected?
Boundary scan test during ICT
"""

api.rootcause.add_comment(ticket.ticket_id, d2_comment)
```

### D3: Interim Containment

```python
d3_comment = """
## D3: Interim Containment Actions

### Actions Taken

| Action | Owner | Status |
|--------|-------|--------|
| Quarantine batch L2024-1213 | Technician | Complete |
| 100% visual inspection | QC | Complete |
| Increase SPI sampling to 100% | Process Eng | Complete |
| Add manual inspection post-reflow | Supervisor | Complete |

### Verification
- 50 units quarantined and inspected
- 5 total defective units identified
- 45 good units released
- No escapes to customer
"""

api.rootcause.add_comment(ticket.ticket_id, d3_comment)
```

### D4: Root Cause Analysis

```python
d4_comment = """
## D4: Root Cause Analysis

### 5-Why Analysis

1. **Why?** Too much solder paste on pads
2. **Why?** Stencil aperture oversized
3. **Why?** Wrong stencil revision used (Rev A vs Rev B)
4. **Why?** Stencil not verified before changeover
5. **Why?** No stencil verification in changeover procedure

**ROOT CAUSE:** Missing stencil verification step in changeover procedure

### Verification
- Test: Used correct stencil on 20 units
- Result: 0 defects
- Conclusion: Root cause confirmed
"""

api.rootcause.add_comment(ticket.ticket_id, d4_comment)
```

### D5-D8: Continue Pattern

Continue documenting each phase with comments until closure.

## Common Patterns

### Pattern 1: Create Ticket from Test Failure

```python
def create_failure_ticket(report_id, serial_number, failure_description):
    """Create RootCause ticket from a test failure"""
    
    ticket = api.rootcause.create_ticket(
        subject=f"Test Failure - {serial_number}",
        priority=TicketPriority.HIGH,
        report_uuid=report_id,
        initial_comment=f"""
## Test Failure Report

**Serial Number:** {serial_number}
**Report ID:** {report_id}

### Failure Description
{failure_description}

### Initial Assessment
Pending investigation.

---
*Auto-generated from test system*
"""
    )
    
    return ticket
```

### Pattern 2: Get My Active Tickets

```python
def get_my_active_tickets():
    """Get all active tickets assigned to current user"""
    
    tickets = api.rootcause.get_tickets(
        status=TicketStatus.OPEN | TicketStatus.IN_PROGRESS | TicketStatus.ON_HOLD,
        view=TicketView.ASSIGNED
    )
    
    # Sort by priority (HIGH first)
    tickets.sort(key=lambda t: t.priority if t.priority else 0, reverse=True)
    
    return tickets
```

### Pattern 3: Ticket Summary Report

```python
def generate_ticket_summary():
    """Generate summary of all tickets by status"""
    
    all_tickets = api.rootcause.get_tickets(
        status=TicketStatus.OPEN | TicketStatus.IN_PROGRESS | TicketStatus.ON_HOLD | TicketStatus.SOLVED,
        view=TicketView.ALL
    )
    
    # Group by status
    by_status = {}
    for ticket in all_tickets:
        status = TicketStatus(ticket.status).name if ticket.status else "UNKNOWN"
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(ticket)
    
    # Print summary
    print("=" * 50)
    print("ROOTCAUSE TICKET SUMMARY")
    print("=" * 50)
    
    for status, tickets in by_status.items():
        print(f"\n{status}: {len(tickets)} tickets")
        for t in tickets[:5]:  # Show first 5
            priority = TicketPriority(t.priority).name if t.priority else "?"
            print(f"  #{t.ticket_number} [{priority}] {t.subject[:40]}...")
```

### Pattern 4: Close and Archive Workflow

```python
def close_ticket(ticket_id, resolution_comment):
    """Close a ticket with resolution comment"""
    
    # Add resolution comment
    api.rootcause.add_comment(ticket_id, f"""
## Resolution

{resolution_comment}

---
*Ticket closed by automated workflow*
""")
    
    # Change to SOLVED
    api.rootcause.change_status(ticket_id, TicketStatus.SOLVED)
    
    return api.rootcause.get_ticket(ticket_id)


def archive_old_solved_tickets(days_old=30):
    """Archive tickets solved more than X days ago"""
    from datetime import datetime, timedelta
    
    solved = api.rootcause.get_tickets(
        status=TicketStatus.SOLVED,
        view=TicketView.ALL
    )
    
    cutoff = datetime.now() - timedelta(days=days_old)
    to_archive = []
    
    for ticket in solved:
        if ticket.updated_utc and ticket.updated_utc < cutoff:
            to_archive.append(ticket.ticket_id)
    
    if to_archive:
        api.rootcause.archive_tickets(to_archive)
        print(f"Archived {len(to_archive)} tickets")
```

## Ticket Model Reference

### Ticket Fields

| Field | Type | Description |
|-------|------|-------------|
| `ticket_id` | UUID | Unique identifier |
| `ticket_number` | int | Human-readable ticket number |
| `subject` | str | Ticket title |
| `status` | TicketStatus | Current status |
| `priority` | TicketPriority | Priority level |
| `owner` | str | Ticket owner username |
| `assignee` | str | Assigned user |
| `team` | str | Assigned team |
| `report_uuid` | UUID | Linked test report ID |
| `created_utc` | datetime | Creation timestamp |
| `updated_utc` | datetime | Last update timestamp |
| `progress` | str | Progress notes |
| `origin` | str | Origin/source |
| `tags` | List[Setting] | Key-value tags |
| `history` | List[TicketUpdate] | Update history |

### TicketUpdate Fields

| Field | Type | Description |
|-------|------|-------------|
| `update_id` | UUID | Update identifier |
| `update_utc` | datetime | Update timestamp |
| `update_user` | str | User who made update |
| `content` | str | Update content |
| `update_type` | TicketUpdateType | Type of update |
| `attachments` | List[TicketAttachment] | Attached files |

## Best Practices

### 1. Use Clear Subjects

```python
# Good - descriptive subjects
"[8D] Solder Bridge on U3 - Batch L2024-1213"
"ICT Failure Spike - Line 2 Morning Shift"
"Customer Return - RMA-2024-001"

# Avoid - vague subjects
"Problem"
"Issue"
"Check this"
```

### 2. Link to Reports

```python
# Always link tickets to related test reports
ticket = api.rootcause.create_ticket(
    subject="...",
    report_uuid=report_id,  # Link to failing report
    ...
)
```

### 3. Document Progress

```python
# Add comments at each stage
api.rootcause.add_comment(ticket_id, "Started 5-Why analysis...")
api.rootcause.add_comment(ticket_id, "Root cause identified: ...")
api.rootcause.add_comment(ticket_id, "Corrective action implemented: ...")
```

### 4. Use Proper Status Transitions

```python
# Typical flow:
# OPEN -> IN_PROGRESS -> SOLVED -> ARCHIVED

# Or with holds:
# OPEN -> IN_PROGRESS -> ON_HOLD -> IN_PROGRESS -> SOLVED
```

### 5. Assign Appropriately

```python
# Assign to specific user for accountability
api.rootcause.assign_ticket(ticket_id, "quality_engineer")

# Use team for group ownership
ticket.team = "Quality Team"
api.rootcause.update_ticket(ticket)
```

## Troubleshooting

### Ticket Not Found

```python
ticket = api.rootcause.get_ticket(ticket_id)
if not ticket:
    # Try searching
    tickets = api.rootcause.get_tickets(
        status=TicketStatus.OPEN | TicketStatus.IN_PROGRESS | TicketStatus.SOLVED,
        view=TicketView.ALL
    )
    # Search by subject or other criteria
```

### Cannot Archive

```python
# Only SOLVED tickets can be archived
ticket = api.rootcause.get_ticket(ticket_id)
if ticket.status != TicketStatus.SOLVED:
    api.rootcause.change_status(ticket_id, TicketStatus.SOLVED)
    
api.rootcause.archive_tickets([ticket_id])
```

### View Returns Empty

```python
# ASSIGNED view requires tickets assigned to current user
# Use ALL view to see everything (requires permission)
tickets = api.rootcause.get_tickets(
    status=TicketStatus.OPEN,
    view=TicketView.ALL  # Instead of ASSIGNED
)
```

## Related Documentation

- [Product Module](PRODUCT_MODULE.md) - Products involved in issues
- [Production Module](PRODUCTION_MODULE.md) - Production units with failures
- [Report Module](REPORT_MODULE.md) - Test reports linked to tickets
