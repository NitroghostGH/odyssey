from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from tickets.models_theme import UserTheme, ThemePreference
from tickets.models import Board


class GlobalThemeContextTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        self.client = Client()
        assert self.client.login(username='alice', password='pass12345')
        # Minimal board for board view tests
        self.board = Board.objects.create(name='Main', description='Test board')

    def _extract_root_style(self, content: str) -> str:
        start = content.find('<style id="theme-vars">')
        self.assertNotEqual(start, -1, 'theme-vars style block missing')
        end = content.find('</style>', start)
        self.assertNotEqual(end, -1, 'end style tag missing')
        return content[start:end]

    def test_home_uses_preference_theme_colors(self):
        theme = UserTheme.objects.create(
            user=self.user,
            name='Preferred',
            colors={'primary': '#111111', 'background': '#222222', 'text': '#333333'},
        )
        ThemePreference.objects.create(user=self.user, theme=theme)
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        style = self._extract_root_style(resp.content.decode())
        self.assertIn('--primary-color: #111111', style)
        self.assertIn('--background-color: #222222', style)
        self.assertIn('--text-color: #333333', style)

    def test_home_falls_back_to_latest_theme_if_no_preference(self):
        UserTheme.objects.create(user=self.user, name='Old', colors={'primary': '#aaaaaa'})
        latest = UserTheme.objects.create(user=self.user, name='Newer', colors={'primary': '#123456', 'accent': '#654321'})
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        style = self._extract_root_style(resp.content.decode())
        self.assertIn('--primary-color: #123456', style)
        # untouched defaults should still appear for unspecified values (danger example)
        self.assertIn('--danger-color: #cf6679', style)
        self.assertIn('--accent-color: #654321', style)
        self.assertNotIn('--primary-color: #aaaaaa', style)

    def test_board_view_includes_theme_colors(self):
        theme = UserTheme.objects.create(user=self.user, name='BoardTheme', colors={'primary': '#0f0f0f'})
        ThemePreference.objects.create(user=self.user, theme=theme)
        resp = self.client.get(reverse('board-view', args=[self.board.id]))
        self.assertEqual(resp.status_code, 200)
        style = self._extract_root_style(resp.content.decode())
        self.assertIn('--primary-color: #0f0f0f', style)

    def test_defaults_used_when_preference_cleared(self):
        # Create and then clear preference
        theme = UserTheme.objects.create(user=self.user, name='Temp', colors={'primary': '#abcdef'})
        pref = ThemePreference.objects.create(user=self.user, theme=theme)
        pref.theme = None
        pref.save()
        # Remove the only theme so fallback doesn't supply its color
        theme.delete()
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        style = self._extract_root_style(resp.content.decode())
        # Expect default primary color since no fallback user theme (preference existed but null and no other themes)
        self.assertIn('--primary-color: #bb86fc', style)
        self.assertIn('--background-color: #1a1625', style)
