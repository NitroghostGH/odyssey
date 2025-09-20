from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tickets.models_theme import UserTheme, ThemePreference
from tickets.models import Board
import json

class ThemesPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pw12345')
        self.other = User.objects.create_user(username='bob', password='pw12345')
        self.client = Client()
        self.client.login(username='alice', password='pw12345')
        self.board = Board.objects.create(name='Board', description='B')
        self.user_theme = UserTheme.objects.create(user=self.user, name='Alice Theme', colors={'primary':'#000','text':'#fff'}, is_public=False)
        self.public_theme = UserTheme.objects.create(user=self.other, name='Bob Public', colors={'primary':'#111','text':'#eee'}, is_public=True)

    def test_themes_page_loads(self):
        url = reverse('tickets:themes-page')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Themes', resp.content.decode())

    def test_select_theme_from_themes_page(self):
        set_pref = reverse('tickets:set_theme_preference')
        resp = self.client.post(set_pref, data=json.dumps({'theme_id': self.user_theme.id}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(ThemePreference.objects.filter(user=self.user, theme=self.user_theme).exists())

    def test_delete_theme_via_api(self):
        delete_url = reverse('tickets:delete_theme', args=[self.user_theme.id])
        resp = self.client.delete(delete_url)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(UserTheme.objects.filter(id=self.user_theme.id).exists())

    def test_cannot_delete_others_theme(self):
        delete_url = reverse('tickets:delete_theme', args=[self.public_theme.id])
        resp = self.client.delete(delete_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('error', resp.json())

    def test_set_public_theme_preference(self):
        set_pref = reverse('tickets:set_theme_preference')
        resp = self.client.post(set_pref, data=json.dumps({'theme_id': self.public_theme.id}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(ThemePreference.objects.filter(user=self.user, theme=self.public_theme).exists())

    def test_edit_theme_updates_values(self):
        # Navigate to edit page
        edit_url = reverse('tickets:theme-creator') + f'?edit={self.user_theme.id}'
        resp = self.client.get(edit_url)
        self.assertEqual(resp.status_code, 200)
        # Post updated values
        post_data = {
            'name': 'My Theme Updated',
            'primary-color': '#123456',
            'secondary-color': '#654321',
            'background-color': '#111111',
            'surface-color': '#222222',
            'text-color': '#eeeeee',
            'accent-color': '#abcdef',
            'border-color': '#333333',
            'danger-color': '#ff0000',
            'success-color': '#00ff00',
            'info-color': '#0000ff',
            'is_public': 'on'
        }
        resp2 = self.client.post(edit_url, post_data)
        self.assertEqual(resp2.status_code, 302)  # redirect back to themes page
        updated = UserTheme.objects.get(id=self.user_theme.id)
        self.assertEqual(updated.name, 'My Theme Updated')
        self.assertTrue(updated.is_public)
        self.assertEqual(updated.colors['primary'], '#123456')

    def test_edit_theme_prefills_existing_colors(self):
        # Ensure the color value from the original theme is present in the form inputs (not overridden by active theme preload)
        original_primary = self.user_theme.colors.get('primary')
        edit_url = reverse('tickets:theme-creator') + f'?edit={self.user_theme.id}'
        resp = self.client.get(edit_url)
        self.assertContains(resp, f'value="{original_primary}"')
        # Check all key colors present
        for key, val in self.user_theme.colors.items():
            # form inputs use hyphenated ids like primary-color
            # presence of value attribute with this hex ensures it wasn't replaced
            self.assertIn(val, resp.content.decode())
