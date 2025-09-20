from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from tickets.models import Board, Ticket

class TicketHierarchyValidationTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Hierarchy Board')
        self.user = get_user_model().objects.create(username='hier_user')
        # Legacy epic (no board FK on Epic model) retained only for transitional backward compatibility.
    # Unified epic ticket
        self.epic_ticket = Ticket.objects.create(title='Unified Epic', board=self.board, ticket_type='epic')
        self.story_ticket = Ticket.objects.create(title='Story', board=self.board, ticket_type='ticket', parent=self.epic_ticket)

    def test_epic_cannot_have_parent(self):
        self.epic_ticket.parent = self.story_ticket
        with self.assertRaises(ValidationError):
            self.epic_ticket.full_clean()

    def test_ticket_parent_must_be_epic(self):
        other_story = Ticket.objects.create(title='Other Story', board=self.board, ticket_type='ticket', parent=self.epic_ticket)
        self.story_ticket.parent = other_story  # invalid because parent is a ticket not epic
        with self.assertRaises(ValidationError):
            self.story_ticket.full_clean()

    def test_bug_must_have_ticket_parent(self):
        bug = Ticket(title='UI Bug', board=self.board, ticket_type='bug', parent=self.epic_ticket)  # parent is epic => invalid
        with self.assertRaises(ValidationError):
            bug.full_clean()
        bug_valid_parent = Ticket(title='Another UI Bug', board=self.board, ticket_type='bug', parent=self.story_ticket)
        bug_valid_parent.full_clean()  # should not raise

    def test_cycle_detection(self):
        sub_story = Ticket.objects.create(title='Sub Story', board=self.board, ticket_type='ticket', parent=self.epic_ticket)
        self.epic_ticket.parent = sub_story
        with self.assertRaises(ValidationError):
            self.epic_ticket.full_clean()

    def test_related_tickets_linking(self):
        bug = Ticket.objects.create(title='Bug A', board=self.board, ticket_type='bug', parent=self.story_ticket)
        enhancement = Ticket.objects.create(title='Enhancement', board=self.board, ticket_type='ticket', parent=self.epic_ticket)
        bug.related_tickets.add(enhancement)
        self.assertIn(enhancement, bug.related_tickets.all())
        self.assertIn(bug, enhancement.related_from.all())
