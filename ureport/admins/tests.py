from django.core.urlresolvers import reverse
from mock import patch
from ureport.admins import OrgCache, refresh_caches
from ureport.tests import DashTest
from django.template import TemplateSyntaxError


class PollTest(DashTest):
    def setUp(self):
        super(PollTest, self).setUp()
        self.uganda = self.create_org('uganda', self.admin)
        self.nigeria = self.create_org('nigeria', self.admin)

    def test_refresh_cache_view(self):
        refresh_cache_url = reverse('admins.org_refresh_cache', args=[self.uganda.pk])

        post_data = dict(cache=1)

        with patch('ureport.admins.views.refresh_caches') as mock_refresh_caches:
            mock_refresh_caches.return_value = None

            response = self.client.get(refresh_cache_url, SERVER_NAME='uganda.ureport.io')
            self.assertLoginRedirect(response)

            response = self.client.post(refresh_cache_url, post_data, SERVER_NAME='uganda.ureport.io')
            self.assertLoginRedirect(response)

            self.login(self.admin)

            response = self.client.get(refresh_cache_url, SERVER_NAME='uganda.ureport.io')
            self.assertLoginRedirect(response)

            response = self.client.post(refresh_cache_url, post_data, SERVER_NAME='uganda.ureport.io')
            self.assertLoginRedirect(response)

            self.login(self.superuser)

            with self.assertRaises(TemplateSyntaxError):
                self.client.get(refresh_cache_url, SERVER_NAME='uganda.ureport.io')

            with self.assertRaises(KeyError):
                self.client.post(refresh_cache_url, dict(), SERVER_NAME='uganda.ureport.io')

            response = self.client.post(refresh_cache_url, post_data, SERVER_NAME='uganda.ureport.io')
            self.assertEqual(response.status_code, 302)
            mock_refresh_caches.assert_called_once_with(self.uganda, [OrgCache.boundaries])
            mock_refresh_caches.reset_mock()

            response = self.client.post(refresh_cache_url, post_data, SERVER_NAME='uganda.ureport.io', follow=True)
            self.assertEqual(response.context['org'], self.uganda)
            self.assertEqual(response.request['PATH_INFO'], reverse('orgs.org_home'))
            self.assertTrue("Refreshed boundaries cache for this organization" in response.content)

            mock_refresh_caches.assert_called_once_with(self.uganda, [OrgCache.boundaries])
