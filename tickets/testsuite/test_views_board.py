from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tickets.models import Board, Ticket

class BoardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        self.board = Board.objects.create(name='QA Board')
        self.ticket1 = Ticket.objects.create(title='T1', board=self.board, status='todo')
        self.ticket2 = Ticket.objects.create(title='T2', board=self.board, status='done')
        self.epic = Ticket.objects.create(title='Epic 1', board=self.board, ticket_type='epic')
        self.story = Ticket.objects.create(title='Story 1', board=self.board, ticket_type='ticket', parent=self.epic)
        self.bug = Ticket.objects.create(title='Bug 1', board=self.board, ticket_type='bug', parent=self.story)

    def test_board_view_status_code(self):
        url = reverse('tickets:board-view', args=[self.board.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Filter buttons present
        self.assertContains(response, 'data-filter="all"')
        self.assertContains(response, 'data-filter="epic"')
        self.assertContains(response, 'data-filter="ticket"')
        self.assertContains(response, 'data-filter="bug"')

    def test_board_view_context(self):
        url = reverse('tickets:board-view', args=[self.board.id])
        response = self.client.get(url)
        self.assertIn('grouped', response.context)
        grouped = response.context['grouped']
        self.assertIn(self.ticket1, grouped['by_status']['todo'])
        self.assertIn(self.ticket2, grouped['by_status']['done'])
        self.assertIn(self.epic, grouped['by_type']['epic'])
        self.assertIn(self.story, grouped['by_type']['ticket'])
        self.assertIn(self.bug, grouped['by_type']['bug'])
        html = response.content.decode()
        self.assertIn('data-ticket-type="epic"', html)
        self.assertIn('data-ticket-type="ticket"', html)
        self.assertIn('data-ticket-type="bug"', html)

class HomeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        self.board = Board.objects.create(name='Main Board')

    def test_home_view_status_code(self):
        url = reverse('tickets:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_lists_boards(self):
        url = reverse('tickets:home')
        response = self.client.get(url)
        self.assertContains(response, 'Main Board')
