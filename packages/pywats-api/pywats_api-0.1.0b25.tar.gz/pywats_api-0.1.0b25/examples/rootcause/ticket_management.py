"""
RootCause Domain: Ticket Management

This example demonstrates the RootCause ticketing system for issue tracking.
"""
import os
from datetime import datetime
from pywats import pyWATS

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Get Tickets
# =============================================================================

# Get all tickets
tickets = api.rootcause.get_tickets()

print(f"Found {len(tickets)} tickets")
for ticket in tickets[:5]:
    print(f"  [{ticket.id}] {ticket.title} - {ticket.status}")


# =============================================================================
# Get Single Ticket
# =============================================================================

ticket = api.rootcause.get_ticket("TICKET-001")

if ticket:
    print(f"\nTicket: {ticket.id}")
    print(f"  Title: {ticket.title}")
    print(f"  Status: {ticket.status}")
    print(f"  Priority: {ticket.priority}")
    print(f"  Assigned: {ticket.assignee}")
    print(f"  Created: {ticket.created}")


# =============================================================================
# Create Ticket
# =============================================================================

from pywats.domains.rootcause import Ticket

new_ticket = Ticket(
    title="Voltage test failing on Line 2",
    description="Multiple units failing voltage check at 5V rail",
    priority="High",
    category="Test Failure",
    partNumber="WIDGET-001"
)

result = api.rootcause.create_ticket(new_ticket)
print(f"\nCreated ticket: {result.id}")


# =============================================================================
# Update Ticket
# =============================================================================

ticket = api.rootcause.get_ticket("TICKET-001")

if ticket:
    ticket.status = "In Progress"
    ticket.assignee = "john.smith@company.com"
    
    api.rootcause.update_ticket(ticket)
    print(f"Updated ticket: {ticket.id}")


# =============================================================================
# Search Tickets
# =============================================================================

# Search by various criteria
from pywats.domains.report import WATSFilter

# Open tickets
open_tickets = api.rootcause.search_tickets(status="Open")
print(f"\nOpen tickets: {len(open_tickets)}")

# High priority
high_priority = api.rootcause.search_tickets(priority="High")
print(f"High priority: {len(high_priority)}")

# By part number
product_tickets = api.rootcause.search_tickets(partNumber="WIDGET-001")
print(f"WIDGET-001 tickets: {len(product_tickets)}")


# =============================================================================
# Ticket Workflow
# =============================================================================

def ticket_workflow_example():
    """Demonstrate ticket workflow."""
    print("=" * 50)
    print("Ticket Workflow")
    print("=" * 50)
    
    # 1. Create ticket
    print("\n1. Creating ticket...")
    ticket = Ticket(
        title="ICT failure spike on Line 1",
        description="Failure rate increased from 2% to 8% today",
        priority="High"
    )
    result = api.rootcause.create_ticket(ticket)
    ticket_id = result.id
    print(f"   Created: {ticket_id}")
    
    # 2. Assign ticket
    print("\n2. Assigning ticket...")
    ticket = api.rootcause.get_ticket(ticket_id)
    ticket.assignee = "engineer@company.com"
    ticket.status = "In Progress"
    api.rootcause.update_ticket(ticket)
    print(f"   Assigned to: {ticket.assignee}")
    
    # 3. Add investigation notes
    print("\n3. Adding comment...")
    api.rootcause.add_comment(ticket_id, "Initial investigation started")
    
    # 4. Resolve
    print("\n4. Resolving ticket...")
    ticket = api.rootcause.get_ticket(ticket_id)
    ticket.status = "Resolved"
    ticket.resolution = "Found damaged probe on test fixture"
    api.rootcause.update_ticket(ticket)
    
    print("\n" + "=" * 50)


# ticket_workflow_example()


# =============================================================================
# Link Ticket to Report
# =============================================================================

# Link a ticket to a specific test report
api.rootcause.link_to_report(
    ticket_id="TICKET-001",
    report_id="report-uuid-here"
)

print("Linked ticket to report")


# =============================================================================
# Get Tickets for Report
# =============================================================================

# Get tickets linked to a specific report
tickets = api.rootcause.get_tickets_for_report("report-uuid-here")

print(f"\nTickets for report: {len(tickets)}")
for ticket in tickets:
    print(f"  {ticket.id}: {ticket.title}")
