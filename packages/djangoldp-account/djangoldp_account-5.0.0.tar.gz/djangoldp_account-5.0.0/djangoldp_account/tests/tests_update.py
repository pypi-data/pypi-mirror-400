import json
import urllib
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.test import APITestCase, APIClient

from djangoldp_account.models import LDPUser


class UpdateTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = LDPUser(email='test@mactest.co.uk', first_name='Test', last_name='Mactest', username='test',
                            password='glass onion')
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_put_account_picture(self):
        self.setUpLoggedInUser()

        test_picture = "https://github.com/" + urllib.parse.quote("calummackervoy/calummackervoy.github.io/blob/master/assets/img/profile.jpg")

        payload = {
            "@context": {"@vocab": "https://cdn.startinblox.com/owl#"},
            '@id': settings.SITE_URL + "/accounts/{}/".format(self.user.account.slug),
            'picture': test_picture,
            'slug': self.user.slug
        }

        response = self.client.put('/accounts/{}/'.format(self.user.account.slug), data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('picture'), test_picture)
