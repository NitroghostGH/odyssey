from django.test import TestCase
from django.contrib.auth import get_user_model
from tickets.models import Board, Ticket

class BoardModelTest(TestCase):
    def test_str(self):
        board = Board.objects.create(name='Test Board')
        self.assertEqual(str(board), 'Test Board')

class TicketModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Dev Board')
        self.user = get_user_model().objects.create(username='testuser')

    def test_importance_above_10_invalid(self):
        ticket = Ticket(title='Bug', board=self.board, importance=11)
        with self.assertRaises(Exception):
            ticket.full_clean()

    def test_importance_below_1_invalid(self):
        ticket = Ticket(title='Bug', board=self.board, importance=0)
        with self.assertRaises(Exception):
            ticket.full_clean()

    def test_urgency_above_10_invalid(self):
        ticket = Ticket(title='Bug', board=self.board, urgency=11)
        with self.assertRaises(Exception):
            ticket.full_clean()

    def test_urgency_below_1_invalid(self):
        ticket = Ticket(title='Bug', board=self.board, urgency=0)
        with self.assertRaises(Exception):
            ticket.full_clean()

    def test_str(self):
        ticket = Ticket.objects.create(title='Bug', board=self.board)
        self.assertEqual(str(ticket), 'Bug')

    def test_default_status_and_priority(self):
        ticket = Ticket.objects.create(title='Bug', board=self.board)
        self.assertEqual(ticket.status, 'todo')
        self.assertEqual(ticket.priority, 'medium')

    def test_assignee(self):
        ticket = Ticket.objects.create(title='Bug', board=self.board, assignee=self.user)
        self.assertEqual(ticket.assignee, self.user)
