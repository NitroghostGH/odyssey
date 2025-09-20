from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tickets.models import Board, Ticket
from tickets.forms import TicketForm

class ViewsTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test board
        self.board = Board.objects.create(
            name='Test Board',
            description='Test Board Description'
        )
        
        # Create test epic ticket
        self.epic_ticket = Ticket.objects.create(
            title='Epic Alpha',
            board=self.board,
            ticket_type='epic'
        )
        
        # Create test story ticket linked to the epic
        self.story_ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test Description',
            board=self.board,
            parent=self.epic_ticket,
            ticket_type='ticket',
            updated_by=self.user,
            status='todo',
            priority='medium',
            importance=3,
            urgency=3
        )
        
        # Set up test client
        self.client = Client()
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')

    def test_board_view(self):
        """Test the board view template and context"""
        response = self.client.get(reverse('tickets:board-view', args=[self.board.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/board.html')
        self.assertIn('board', response.context)
        self.assertIn('grouped', response.context)

    def test_ticket_edit_view_get(self):
        """Test the ticket edit view GET request"""
        response = self.client.get(reverse('tickets:ticket-edit', args=[self.story_ticket.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_form.html')
        self.assertIsInstance(response.context['form'], TicketForm)
        self.assertEqual(response.context['title'], 'Edit Ticket')

    def test_ticket_edit_view_post(self):
        """Test the ticket edit view POST request"""
        data = {
            'title': 'Updated Test Ticket',
            'description': 'Updated Description',
            'status': 'in_progress',
            'priority': 'high',
            'importance': 4,
            'urgency': 4,
            'board': self.board.id,
            'ticket_type': 'ticket',
            'parent': self.epic_ticket.id
        }
        response = self.client.post(
            reverse('tickets:ticket-edit', args=[self.story_ticket.id]),
            data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect after successful edit
        # Verify the ticket was updated
        updated_ticket = Ticket.objects.get(id=self.story_ticket.id)
        self.assertEqual(updated_ticket.title, 'Updated Test Ticket')
        # Ensure an activity entry created with 'updated'
        self.assertTrue(updated_ticket.activities.filter(activity_type='updated').exists())

    def test_ticket_new_view_get(self):
        """Test the new ticket view GET request"""
        response = self.client.get(reverse('tickets:ticket_new', args=[self.board.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_form.html')
        self.assertIsInstance(response.context['form'], TicketForm)
        self.assertEqual(response.context['title'], 'Create New Ticket')

    def test_ticket_new_view_post(self):
        """Test creating a new ticket with POST request"""
        data = {
            'title': 'Brand New Ticket',
            'description': 'New Ticket Description',
            'status': 'todo',
            'priority': 'medium',
            'importance': 3,
            'urgency': 3,
            'board': self.board.id,
            'ticket_type': 'ticket',
            'parent': self.epic_ticket.id
        }
        response = self.client.post(
            reverse('tickets:ticket_new', args=[self.board.id]),
            data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        # Verify the ticket was created
        new_ticket = Ticket.objects.filter(title='Brand New Ticket').first()
        self.assertIsNotNone(new_ticket)
        self.assertEqual(new_ticket.parent, self.epic_ticket)

    def test_create_epic(self):
        """Test creating a new epic ticket"""
        data = {
            'title': 'New Epic Ticket',
            'description': 'Epic level work',
            'status': 'todo',
            'priority': 'medium',
            'importance': 6,
            'urgency': 5,
            'board': self.board.id,
            'ticket_type': 'epic'
        }
        response = self.client.post(
            reverse('tickets:ticket_new', args=[self.board.id]),
            data
        )
        self.assertEqual(response.status_code, 302)
        epic_created = Ticket.objects.filter(title='New Epic Ticket', ticket_type='epic').exists()
        self.assertTrue(epic_created)

    def test_unauthorized_access(self):
        """Test that unauthorized users can't access protected views"""
        # Log out the test user
        self.client.logout()
        
        urls = [
            reverse('tickets:board-view', args=[self.board.id]),
            reverse('tickets:ticket-edit', args=[self.story_ticket.id]),
            reverse('tickets:ticket_new', args=[self.board.id])
        ]
        
        for url in urls:
            response = self.client.get(url)
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url.split('?')[0], '/accounts/login/')

    def test_board_view_ticket_grouping(self):
        """Test that tickets are properly grouped by status in board view"""
        # Create additional tickets with different statuses
        Ticket.objects.create(
            title='Todo Ticket',
            board=self.board,
            status='todo',
            updated_by=self.user,
            ticket_type='ticket',
            parent=self.epic_ticket
        )
        Ticket.objects.create(
            title='In Progress Ticket',
            board=self.board,
            status='in_progress',
            updated_by=self.user,
            ticket_type='ticket',
            parent=self.epic_ticket
        )
        Ticket.objects.create(
            title='Done Ticket',
            board=self.board,
            status='done',
            updated_by=self.user,
            ticket_type='ticket',
            parent=self.epic_ticket
        )
        
        response = self.client.get(reverse('tickets:board-view', args=[self.board.id]))
        grouped = response.context['grouped']['by_status']
        
        self.assertTrue(any(t.title == 'Todo Ticket' for t in grouped['todo']))
        self.assertTrue(any(t.title == 'In Progress Ticket' for t in grouped['in_progress']))
        self.assertTrue(any(t.title == 'Done Ticket' for t in grouped['done']))

    def test_non_existent_resources(self):
        """Test handling of non-existent boards and tickets"""
        # Test non-existent board
        response = self.client.get(reverse('tickets:board-view', args=[99999]))
        self.assertEqual(response.status_code, 404)
        
        # Test non-existent ticket
        response = self.client.get(reverse('tickets:ticket-edit', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_priority_selection_values(self):
        """Test that importance and urgency values (simple selects) are stored and product is as expected."""
        data = {
            'title': 'Priority Test Ticket',
            'description': 'Testing priority matrix',
            'status': 'todo',
            'priority': 'high',
            'importance': 10,  # Highest importance after reversion
            'urgency': 10,     # Highest urgency after reversion
            'board': self.board.id,
            'ticket_type': 'ticket',
            'parent': self.epic_ticket.id
        }
        response = self.client.post(
            reverse('tickets:ticket_new', args=[self.board.id]),
            data
        )
        self.assertEqual(response.status_code, 302)
        new_ticket = Ticket.objects.get(title='Priority Test Ticket')
        self.assertEqual(new_ticket.importance, 10)
        self.assertEqual(new_ticket.urgency, 10)
        self.assertEqual(new_ticket.importance * new_ticket.urgency, 100)

    def test_add_comment_creates_activity(self):
        url = reverse('tickets:ticket-edit', args=[self.story_ticket.id])
        response = self.client.post(url, {
            'comment_mode': '1',
            'comment_body': 'This is a comment.'
        })
        self.assertEqual(response.status_code, 302)
        self.story_ticket.refresh_from_db()
        self.assertTrue(self.story_ticket.comments.filter(body__icontains='This is a comment.').exists())
        self.assertTrue(self.story_ticket.activities.filter(activity_type='commented').exists())