# RootCause Domain

The RootCause domain provides issue tracking and defect management capabilities. Use this to create tickets for failures, track root cause investigations, assign work, and close issues. It supports status-based workflows (Open → In Progress → Resolved → Closed), priority management, and view filtering (assigned to me, following, all).

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Ticket Management](#ticket-management)
- [Status and Workflow](#status-and-workflow)
- [Priority Management](#priority-management)
- [View Filtering](#view-filtering)
- [Search and Query](#search-and-query)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)

---

## Quick Start

```python
from pywats import pyWATS

# Initialize
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token"
)

# Get all open tickets
open_tickets = api.rootcause.get_open_tickets()

print(f"=== OPEN TICKETS ({len(open_tickets)}) ===")
for ticket in open_tickets:
    print(f"#{ticket.id}: {ticket.subject}")
    print(f"  Priority: {ticket.priority}")
    print(f"  Assigned: {ticket.assigned_to}")

# Get specific ticket
ticket = api.rootcause.get_ticket(12345)

if ticket:
    print(f"\nTicket: {ticket.subject}")
    print(f"Status: {ticket.status}")
    print(f"Description: {ticket.description}")

# Get active tickets (open + in progress)
from pywats.domains.rootcause.models import TicketView

active = api.rootcause.get_active_tickets(view=TicketView.ASSIGNED)
print(f"\n{len(active)} tickets assigned to me")
```

---

## Core Concepts

### Tickets
A **Ticket** is an issue tracking record:
- `subject`: Ticket title
- `description`: Detailed description
- `status`: Current status (OPEN, IN_PROGRESS, etc.)
- `priority`: Priority level (LOW, NORMAL, HIGH, CRITICAL)
- `assigned_to`: User assigned to the ticket

### Status Workflow
Tickets flow through statuses:
- **OPEN**: New ticket, not yet started
- **IN_PROGRESS**: Actively being worked on
- **RESOLVED**: Solution implemented, awaiting verification
- **CLOSED**: Verified and closed

### Priority Levels
Priority indicates urgency:
- **LOW**: Minor issue, no immediate impact
- **NORMAL**: Standard issue
- **HIGH**: Important, needs attention soon
- **CRITICAL**: Urgent, production impact

### Views
View filters control which tickets you see:
- **ASSIGNED**: Tickets assigned to you
- **FOLLOWING**: Tickets you're following
- **ALL**: All tickets (requires permissions)

---

## Ticket Management

### Get Ticket by ID

```python
# Get specific ticket
ticket = api.rootcause.get_ticket(12345)

if ticket:
    print(f"Ticket #{ticket.id}: {ticket.subject}")
    print(f"Status: {ticket.status}")
    print(f"Priority: {ticket.priority}")
    print(f"Assigned: {ticket.assigned_to}")
    print(f"Created: {ticket.created_date_time}")
    print(f"\nDescription:")
    print(ticket.description)
else:
    print("Ticket not found")
```

### Get All Open Tickets

```python
from pywats.domains.rootcause.models import TicketView

# Get all open tickets (view: all)
open_tickets = api.rootcause.get_open_tickets(view=TicketView.ALL)

print(f"=== OPEN TICKETS ({len(open_tickets)}) ===")

for ticket in open_tickets:
    print(f"\n#{ticket.id}: {ticket.subject}")
    print(f"  Priority: {ticket.priority}")
    print(f"  Assigned: {ticket.assigned_to or 'Unassigned'}")
    print(f"  Created: {ticket.created_date_time.strftime('%Y-%m-%d')}")
```

### Get Active Tickets

```python
# Get open + in-progress tickets
active = api.rootcause.get_active_tickets()

print(f"=== ACTIVE TICKETS ({len(active)}) ===")

for ticket in active:
    status_icon = "🟡" if ticket.status == "OPEN" else "🔵"
    print(f"{status_icon} #{ticket.id}: {ticket.subject}")
    print(f"   Status: {ticket.status}")
```

---

## Status and Workflow

### Query by Status

```python
from pywats.domains.rootcause.models import TicketStatus

# Get tickets with specific status
open_tickets = api.rootcause.get_tickets(status=TicketStatus.OPEN)

print(f"Open tickets: {len(open_tickets)}")

# Get in-progress tickets
in_progress = api.rootcause.get_tickets(status=TicketStatus.IN_PROGRESS)

print(f"In progress: {len(in_progress)}")
```

### Combine Multiple Statuses

```python
# Get open OR in-progress tickets using "|" operator
active_status = f"{TicketStatus.OPEN}|{TicketStatus.IN_PROGRESS}"

active_tickets = api.rootcause.get_tickets(status=active_status)

print(f"Active tickets: {len(active_tickets)}")

# Breakdown by status
by_status = {}
for ticket in active_tickets:
    status = ticket.status
    by_status[status] = by_status.get(status, 0) + 1

for status, count in by_status.items():
    print(f"  {status}: {count}")
```

### Track Status Changes

```python
def track_ticket_workflow(ticket_id):
    """Show ticket history and status changes"""
    
    ticket = api.rootcause.get_ticket(ticket_id)
    
    if not ticket:
        print("Ticket not found")
        return
    
    print(f"=== TICKET #{ticket_id}: {ticket.subject} ===")
    print(f"Current Status: {ticket.status}")
    print(f"Created: {ticket.created_date_time}")
    
    # If ticket has updates/history
    if hasattr(ticket, 'updates') and ticket.updates:
        print("\nHistory:")
        for update in ticket.updates:
            print(f"  {update.date_time}: {update.description}")

# Use it
track_ticket_workflow(12345)
```

---

## Priority Management

### Filter by Priority

```python
from pywats.domains.rootcause.models import TicketPriority, TicketView

# Get high priority tickets
high_priority = api.rootcause.get_tickets(
    priority=TicketPriority.HIGH,
    view=TicketView.ALL
)

print(f"=== HIGH PRIORITY TICKETS ({len(high_priority)}) ===")

for ticket in high_priority:
    print(f"#{ticket.id}: {ticket.subject}")
    print(f"  Status: {ticket.status}")
    print(f"  Assigned: {ticket.assigned_to}")
```

### Priority Report

```python
from pywats.domains.rootcause.models import TicketView

def priority_report():
    """Generate report of tickets by priority"""
    
    # Get all active tickets
    active = api.rootcause.get_active_tickets(view=TicketView.ALL)
    
    # Count by priority
    by_priority = {}
    for ticket in active:
        priority = ticket.priority
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    print("=" * 60)
    print("ACTIVE TICKETS BY PRIORITY")
    print("=" * 60)
    
    # Define priority order
    priority_order = ["CRITICAL", "HIGH", "NORMAL", "LOW"]
    
    total = 0
    for priority in priority_order:
        count = by_priority.get(priority, 0)
        total += count
        
        if count > 0:
            icon = "🔴" if priority == "CRITICAL" else "🟠" if priority == "HIGH" else "🟡" if priority == "NORMAL" else "🟢"
            print(f"{icon} {priority:<12} {count:>4}")
    
    print("-" * 60)
    print(f"{'TOTAL':<14} {total:>4}")
    print("=" * 60)

# Use it
priority_report()
```

---

## View Filtering

### Assigned to Me

```python
from pywats.domains.rootcause.models import TicketView

# Get tickets assigned to me
my_tickets = api.rootcause.get_active_tickets(view=TicketView.ASSIGNED)

print(f"=== MY TICKETS ({len(my_tickets)}) ===")

for ticket in my_tickets:
    print(f"#{ticket.id}: {ticket.subject}")
    print(f"  Priority: {ticket.priority}")
    print(f"  Status: {ticket.status}")
```

### Following

```python
# Get tickets I'm following
following = api.rootcause.get_active_tickets(view=TicketView.FOLLOWING)

print(f"=== FOLLOWING ({len(following)}) ===")

for ticket in following:
    print(f"#{ticket.id}: {ticket.subject}")
```

### All Tickets (with permissions)

```python
# Get all tickets (requires permissions)
all_tickets = api.rootcause.get_tickets(view=TicketView.ALL)

print(f"Total tickets: {len(all_tickets)}")

# Group by assigned user
by_user = {}
for ticket in all_tickets:
    user = ticket.assigned_to or "Unassigned"
    if user not in by_user:
        by_user[user] = []
    by_user[user].append(ticket)

print("\n=== TICKETS BY ASSIGNEE ===")
for user, tickets in sorted(by_user.items()):
    print(f"{user}: {len(tickets)} tickets")
```

---

## Search and Query

### Search by Subject/Tags

```python
# Search for tickets containing "calibration"
search_results = api.rootcause.get_tickets(search_string="calibration")

print(f"=== SEARCH: 'calibration' ({len(search_results)}) ===")

for ticket in search_results:
    print(f"#{ticket.id}: {ticket.subject}")
    print(f"  Tags: {', '.join(ticket.tags) if ticket.tags else 'None'}")
```

### Combined Search

```python
from pywats.domains.rootcause.models import TicketStatus, TicketPriority

# Search for high priority open tickets about "ICT"
results = api.rootcause.get_tickets(
    status=TicketStatus.OPEN,
    priority=TicketPriority.HIGH,
    search_string="ICT"
)

print(f"=== HIGH PRIORITY OPEN ICT ISSUES ({len(results)}) ===")

for ticket in results:
    print(f"#{ticket.id}: {ticket.subject}")
```

### Find Tickets for Part Number

```python
def find_tickets_for_part(part_number):
    """Find all tickets related to a part number"""
    
    # Search in subject and tags
    results = api.rootcause.get_tickets(search_string=part_number)
    
    print(f"=== TICKETS FOR {part_number} ({len(results)}) ===")
    
    for ticket in results:
        print(f"\n#{ticket.id}: {ticket.subject}")
        print(f"  Status: {ticket.status}")
        print(f"  Priority: {ticket.priority}")
        print(f"  Created: {ticket.created_date_time.strftime('%Y-%m-%d')}")

# Use it
find_tickets_for_part("WIDGET-001")
```

---

## Advanced Usage

### Ticket Dashboard

```python
from pywats.domains.rootcause.models import TicketView

def ticket_dashboard():
    """Generate comprehensive ticket dashboard"""
    
    # Get all tickets
    all_tickets = api.rootcause.get_tickets(view=TicketView.ALL)
    
    print("=" * 70)
    print("TICKET DASHBOARD")
    print("=" * 70)
    
    # Summary by status
    by_status = {}
    for ticket in all_tickets:
        status = ticket.status
        by_status[status] = by_status.get(status, 0) + 1
    
    print("\nBy Status:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    
    # Get active tickets
    active = [t for t in all_tickets if t.status in ["OPEN", "IN_PROGRESS"]]
    
    # Active by priority
    print(f"\nActive Tickets by Priority ({len(active)} total):")
    by_priority = {}
    for ticket in active:
        priority = ticket.priority
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    for priority in ["CRITICAL", "HIGH", "NORMAL", "LOW"]:
        count = by_priority.get(priority, 0)
        if count > 0:
            print(f"  {priority}: {count}")
    
    # Unassigned
    unassigned = [t for t in active if not t.assigned_to]
    if unassigned:
        print(f"\n⚠ {len(unassigned)} unassigned active tickets")
    
    # Old tickets
    from datetime import datetime, timedelta
    old_cutoff = datetime.now() - timedelta(days=30)
    old_active = [t for t in active if t.created_date_time < old_cutoff]
    
    if old_active:
        print(f"\n⚠ {len(old_active)} active tickets older than 30 days")
    
    print("=" * 70)

# Use it
ticket_dashboard()
```

### Defect Tracking Integration

```python
def track_defect_from_failure(uut_report_id):
    """Create/update ticket when a unit fails"""
    
    # Get the failed UUT report (from Report domain)
    uut_report = api.report.get_uut_report(uut_report_id)
    
    if not uut_report or uut_report.status != "Failed":
        print("UUT did not fail")
        return
    
    # Check if ticket already exists
    search_string = f"UUT:{uut_report.serial_number}"
    existing = api.rootcause.get_tickets(search_string=search_string)
    
    if existing:
        ticket = existing[0]
        print(f"Existing ticket: #{ticket.id}")
    else:
        # Create new ticket (implementation depends on API)
        print(f"Need to create ticket for {uut_report.serial_number}")
        
        subject = f"Failure: {uut_report.part_number} - {uut_report.serial_number}"
        description = f"Unit failed at {uut_report.completed_date_time}\n"
        description += f"Station: {uut_report.station}\n"
        description += f"Operator: {uut_report.operator}\n"
        
        # Add failed steps
        failed_steps = [s for s in uut_report.steps if s.status == "Failed"]
        description += f"\nFailed Steps:\n"
        for step in failed_steps:
            description += f"- {step.step_name}\n"

# Use it
track_defect_from_failure(12345)
```

### Aging Report

```python
from datetime import datetime, timedelta

def aging_report(days_threshold=30):
    """Find old active tickets"""
    
    cutoff = datetime.now() - timedelta(days=days_threshold)
    
    active = api.rootcause.get_active_tickets()
    
    old_tickets = [
        t for t in active 
        if t.created_date_time < cutoff
    ]
    
    # Sort by age (oldest first)
    old_tickets.sort(key=lambda t: t.created_date_time)
    
    print(f"=== TICKETS OLDER THAN {days_threshold} DAYS ({len(old_tickets)}) ===")
    
    for ticket in old_tickets:
        age_days = (datetime.now() - ticket.created_date_time).days
        
        print(f"\n#{ticket.id}: {ticket.subject}")
        print(f"  Age: {age_days} days")
        print(f"  Status: {ticket.status}")
        print(f"  Priority: {ticket.priority}")
        print(f"  Assigned: {ticket.assigned_to or 'Unassigned'}")

# Use it
aging_report(days_threshold=60)
```

---

## API Reference

### RootCauseService Methods

#### Ticket Queries
- `get_ticket(ticket_id)` → `Optional[Ticket]` - Get specific ticket
- `get_tickets(status=None, view=None, search_string=None)` → `List[Ticket]` - Query tickets
- `get_open_tickets(view=None)` → `List[Ticket]` - Get open tickets
- `get_active_tickets(view=None)` → `List[Ticket]` - Get open + in-progress tickets

### Models

#### Ticket
- `id`: int - Ticket ID
- `subject`: str - Ticket title
- `description`: str - Detailed description
- `status`: str - Status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
- `priority`: str - Priority (LOW, NORMAL, HIGH, CRITICAL)
- `assigned_to`: str - Assigned user
- `created_date_time`: datetime - Creation timestamp
- `tags`: List[str] - Tags for organization
- `updates`: List[TicketUpdate] - Update history

#### TicketStatus (Enum)
- `OPEN` - New ticket
- `IN_PROGRESS` - Being worked on
- `RESOLVED` - Solution implemented
- `CLOSED` - Verified and closed

#### TicketPriority (Enum)
- `LOW` - Minor issue
- `NORMAL` - Standard priority
- `HIGH` - Important
- `CRITICAL` - Urgent

#### TicketView (Enum)
- `ASSIGNED` - Tickets assigned to you
- `FOLLOWING` - Tickets you're following
- `ALL` - All tickets (requires permissions)

---

## Best Practices

1. **Use appropriate priority** - Reserve CRITICAL for production impact
2. **Assign tickets promptly** - Avoid unassigned backlog
3. **Search before creating** - Avoid duplicate tickets
4. **Update status regularly** - Keep workflow current
5. **Use tags** - Tag with part numbers, stations, categories
6. **Monitor aging tickets** - Review old active tickets regularly
7. **Link to evidence** - Reference UUT reports, measurements
8. **Close resolved tickets** - Verify and close when complete

---

## See Also

- [Report Domain](REPORT.md) - Link tickets to failed test reports
- [Production Domain](PRODUCTION.md) - Track units with defects
- [Analytics Domain](ANALYTICS.md) - Analyze failure trends
