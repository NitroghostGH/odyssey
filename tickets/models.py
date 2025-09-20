
from django.db import models

class TicketActivity(models.Model):
	ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name='activities')
	user = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
	activity_type = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user} {self.activity_type} {self.ticket} at {self.timestamp}"

class Board(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name


class Ticket(models.Model):

	STATUS_CHOICES = [
		('todo', 'To Do'),
		('in_progress', 'In Progress'),
		('done', 'Done'),
	]

	PRIORITY_CHOICES = [
		('low', 'Low'),
		('medium', 'Medium'),
		('high', 'High'),
	]

	TICKET_TYPE_CHOICES = [
		('epic', 'Epic'),
		('ticket', 'Ticket'),
		('bug', 'Bug'),
	]

	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
	ticket_type = models.CharField(max_length=10, choices=TICKET_TYPE_CHOICES, default='ticket', db_index=True, help_text='Categorizes this ticket in the hierarchy.')
	sort_order = models.IntegerField(default=0, db_index=True)
	importance = models.IntegerField(default=1, help_text='1 (lowest) … 10 (highest). Multiplies with urgency for derived priority score.')
	urgency = models.IntegerField(default=1, help_text='1 (lowest) … 10 (highest). Multiplies with importance for derived priority score.')
	parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE, help_text='Parent ticket in hierarchy (Epic for tickets, Ticket for bugs).')
	related_tickets = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_from', help_text='Non-hierarchical linked tickets.')
	def clean(self):
		from django.core.exceptions import ValidationError
		if not (1 <= self.importance <= 10):
			raise ValidationError({'importance': 'Importance must be between 1 and 10.'})
		if not (1 <= self.urgency <= 10):
			raise ValidationError({'urgency': 'Urgency must be between 1 and 10.'})
		# Hierarchy validation
		if self.ticket_type == 'epic':
			if self.parent_id is not None:
				raise ValidationError({'parent': 'Epics cannot have a parent.'})
		elif self.ticket_type == 'ticket':
				# Tickets may have no parent, or an epic parent. Only validate if parent is set.
				if self.parent and self.parent.ticket_type != 'epic':
					raise ValidationError({'parent': 'If set, parent must be an epic for a standard ticket.'})
		elif self.ticket_type == 'bug':
			if not self.parent or self.parent.ticket_type != 'ticket':
				raise ValidationError({'parent': 'A bug must have a ticket as parent.'})
		# Prevent cycles in hierarchy
		seen = set()
		cur = self.parent
		while cur is not None:
			if cur.id == self.id:
				raise ValidationError({'parent': 'Cyclic parent relationship detected.'})
			if cur.id in seen:
				break
			seen.add(cur.id)
			cur = cur.parent
	board = models.ForeignKey(Board, related_name='tickets', on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	assignee = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
	updated_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_tickets')

	def __str__(self):
		return self.title

class TicketComment(models.Model):
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
	user = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Comment by {self.user} on {self.ticket} at {self.created_at}"
