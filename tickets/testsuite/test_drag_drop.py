from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from tickets.models import Board, Ticket

class DragDropTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', is_staff=True)
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        self.board = Board.objects.create(name='Test Board')
        self.ticket = Ticket.objects.create(title='Test Ticket', board=self.board, status='todo', priority='medium')

    def test_update_ticket_position(self):
        url = reverse('tickets:update-ticket-position')
        data = {
            'ticket_id': self.ticket.id,
            'importance': 5,
            'urgency': 8
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.importance, 5)
        self.assertEqual(self.ticket.urgency, 8)
