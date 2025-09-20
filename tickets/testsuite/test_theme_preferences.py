from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tickets.models import Board
from tickets.models_theme import UserTheme, ThemePreference
import json

class ThemePreferenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pw12345')
        self.other = User.objects.create_user(username='bob', password='pw12345')
        self.board = Board.objects.create(name='Board', description='B')
        self.client = Client()
        self.client.login(username='alice', password='pw12345')
        self.user_theme = UserTheme.objects.create(user=self.user, name='Alice Dark', colors={'primary':'#000','text':'#fff'}, is_public=False)
        self.public_other_theme = UserTheme.objects.create(user=self.other, name='Bob Public', colors={'primary':'#111','text':'#eee'}, is_public=True)

    def test_get_themes_lists_user_and_public(self):
        url = reverse('tickets:get_themes')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(any(t['name']==self.user_theme.name for t in data['user_themes']))
        self.assertTrue(any(t['name']==self.public_other_theme.name for t in data['public_themes']))

    def test_get_single_theme(self):
        url = reverse('tickets:get_single_theme', args=[self.user_theme.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['name'], self.user_theme.name)

    def test_set_preference_and_board_view_uses_it(self):
        set_pref = reverse('tickets:set_theme_preference')
        resp = self.client.post(set_pref, data=json.dumps({'theme_id': self.user_theme.id}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(ThemePreference.objects.filter(user=self.user, theme=self.user_theme).exists())
        board_url = reverse('tickets:board-view', args=[self.board.id])
        page = self.client.get(board_url)
        self.assertEqual(page.status_code, 200)
        # Confirm selector includes selected theme option
        self.assertIn('Alice Dark', page.content.decode())

    def test_select_public_theme_as_preference(self):
        set_pref = reverse('tickets:set_theme_preference')
        resp = self.client.post(set_pref, data=json.dumps({'theme_id': self.public_other_theme.id}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(ThemePreference.objects.filter(user=self.user, theme=self.public_other_theme).exists())

    def test_clear_preference(self):
        # First set
        set_pref = reverse('tickets:set_theme_preference')
        self.client.post(set_pref, data=json.dumps({'theme_id': self.user_theme.id}), content_type='application/json')
        # Clear by sending empty string
        self.client.post(set_pref, data=json.dumps({'theme_id': ''}), content_type='application/json')
        self.assertTrue(ThemePreference.objects.filter(user=self.user, theme__isnull=True).exists())

    def test_delete_theme(self):
        # Delete own theme
        delete_url = reverse('tickets:delete_theme', args=[self.user_theme.id])
        resp = self.client.delete(delete_url)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(UserTheme.objects.filter(id=self.user_theme.id).exists())
        # Attempt delete a theme not owned
        delete_other = reverse('tickets:delete_theme', args=[self.public_other_theme.id])
        resp2 = self.client.delete(delete_other)
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('error', resp2.json())
