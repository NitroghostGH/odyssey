from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from tickets.models import Board, Ticket, TicketActivity

class TicketCreationFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='pass123')
        self.client = Client()
        self.client.login(username='creator', password='pass123')
        self.board = Board.objects.create(name='Dev Board')
        self.epic_ticket = Ticket.objects.create(title='Platform Revamp', board=self.board, ticket_type='epic')

    def test_create_ticket_basic(self):
        url = reverse('tickets:ticket_new', args=[self.board.id])
        data = {
            'title': 'New Ticket',
            'description': 'Some description',
            'status': 'todo',
            'priority': 'medium',
            'importance': 5,
            'urgency': 5,
            'board': self.board.id,
            'ticket_type': 'ticket',
            'parent': self.epic_ticket.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        ticket = Ticket.objects.get(title='New Ticket')
        self.assertEqual(ticket.importance, 5)
        self.assertEqual(ticket.urgency, 5)
        self.assertEqual(ticket.parent, self.epic_ticket)

    def test_form_displays_descriptive_choices(self):
        url = reverse('tickets:ticket_new', args=[self.board.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check a few representative option labels
        self.assertContains(response, '10 – VITAL (Mission critical)')
        self.assertContains(response, '1 – Trivial (Little to no impact)')
        self.assertContains(response, '10 – CRITICAL (Immediate action required)')

    def test_create_bug_under_ticket(self):
        story = Ticket.objects.create(title='Story A', board=self.board, ticket_type='ticket', parent=self.epic_ticket)
        url = reverse('tickets:ticket_new', args=[self.board.id])
        data = {
            'title': 'Bug A',
            'description': 'Bug details',
            'status': 'todo',
            'priority': 'high',
            'importance': 7,
            'urgency': 6,
            'board': self.board.id,
            'ticket_type': 'bug',
            'parent': story.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        bug = Ticket.objects.get(title='Bug A')
        self.assertEqual(bug.parent, story)
        self.assertEqual(bug.ticket_type, 'bug')

    def test_activity_logged_on_creation(self):
        url = reverse('tickets:ticket_new', args=[self.board.id])
        data = {
            'title': 'Tracked Ticket',
            'description': 'Should log activity',
            'status': 'todo',
            'priority': 'medium',
            'importance': 4,
            'urgency': 3,
            'board': self.board.id,
            'ticket_type': 'ticket',
            'parent': self.epic_ticket.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        ticket = Ticket.objects.get(title='Tracked Ticket')
        self.assertTrue(TicketActivity.objects.filter(ticket=ticket, activity_type='created').exists())

class TicketValidationEdgeCasesTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Validation Board')

    def test_importance_and_urgency_bounds(self):
        t = Ticket(title='Bounds', board=self.board, importance=1, urgency=10)
        t.full_clean()
        t.importance = 10
        t.urgency = 1
        t.full_clean()

    def test_invalid_values_raise(self):
        t = Ticket(title='Invalid', board=self.board, importance=0, urgency=5)
        with self.assertRaises(ValidationError):
            t.full_clean()
        t2 = Ticket(title='Invalid2', board=self.board, importance=5, urgency=11)
        with self.assertRaises(ValidationError):
            t2.full_clean()
