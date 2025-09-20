from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tickets.models import Board, Ticket

class MatrixOrientationTest(TestCase):
    """Tests to ensure top-right visual cell represents (importance=10, urgency=10)."""

    def setUp(self):
        self.user = User.objects.create_user(username='matrixuser', password='pass123')
        self.client = Client()
        self.client.login(username='matrixuser', password='pass123')
        self.board = Board.objects.create(name='Matrix Board')
        # Baseline epic for parent selection (not essential for this test but keeps form consistent)
        self.epic = Ticket.objects.create(title='Epic Root', board=self.board, ticket_type='epic')

    def test_top_right_represents_highest_values(self):
        """
        Simulate creating a ticket selecting the highest importance & urgency (10,10) and
        verify those exact numeric values persist.
        This asserts the form->model mapping for the intended top-right cell.
        """
        data = {
            'title': 'Top Right Cell Ticket',
            'description': 'Verifying highest cell mapping',
            'status': 'todo',
            'priority': 'high',
            'importance': 10,
            'urgency': 10,
            'board': self.board.id,
            'ticket_type': 'ticket',
            'parent': self.epic.id
        }
        response = self.client.post(reverse('tickets:ticket_new', args=[self.board.id]), data)
        self.assertEqual(response.status_code, 302, 'Form did not redirect – possible validation issue')
        t = Ticket.objects.get(title='Top Right Cell Ticket')
        self.assertEqual(t.importance, 10, 'Importance not stored as 10')
        self.assertEqual(t.urgency, 10, 'Urgency not stored as 10')

    def test_lowest_bottom_left_values(self):
        """Ensure a (1,1) selection stores the lowest numeric values (sanity check)."""
        data = {
            'title': 'Bottom Left Cell Ticket',
            'description': 'Verifying lowest cell mapping',
            'status': 'todo',
            'priority': 'low',
            'importance': 1,
            'urgency': 1,
            'board': self.board.id,
            'ticket_type': 'ticket',
            'parent': self.epic.id
        }
        response = self.client.post(reverse('tickets:ticket_new', args=[self.board.id]), data)
        self.assertEqual(response.status_code, 302)
        t = Ticket.objects.get(title='Bottom Left Cell Ticket')
        self.assertEqual(t.importance, 1)
        self.assertEqual(t.urgency, 1)
