from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tickets.models import Board, Ticket


class PriorityScoreTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='prio', password='pass123')
        self.client = Client()
        self.client.login(username='prio', password='pass123')
        self.board = Board.objects.create(name='Prio Board')
        self.epic = Ticket.objects.create(title='Epic Root', board=self.board, ticket_type='epic')

    def test_priority_product_calculation(self):
        data = {
            'title': 'Score Ticket',
            'description': 'Check product',
            'status': 'todo',
            'priority': 'medium',
            'importance': 4,
            'urgency': 7,
            'board': self.board.id,
            'ticket_type': 'ticket',
            'parent': self.epic.id
        }
        response = self.client.post(reverse('tickets:ticket_new', args=[self.board.id]), data)
        self.assertEqual(response.status_code, 302)
        t = Ticket.objects.get(title='Score Ticket')
        self.assertEqual(t.importance, 4)
        self.assertEqual(t.urgency, 7)
        self.assertEqual(t.importance * t.urgency, 28)