import json
from rest_framework.test import APITestCase, APIClient
from djangoldp_circle.models import Circle
from djangoldp_circle.tests.utils import get_random_user


class CacheTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = get_random_user()
        self.client.force_authenticate(user=self.user)

    def _get_random_circle(self, public=True, owner=None):
        if owner is None:
            owner = self.user

        return Circle.objects.create(name='Test', public=public, owner=owner)

    def setUpCircle(self, public=True, owner=None):
        self.circle = self._get_random_circle(public, owner)

    def test_leave_circle_user_cache_updates(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle(owner=another_user)
        self.circle.members.user_set.add(self.user)

        response = self.client.get('/users/{}/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertIn('circles', response.data)
        response = self.client.get(response.data['circles']['@id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

        body = {'https://cdn.startinblox.com/owl#user_set': [{"@id": another_user.urlid}]}
        response = self.client.patch('/groups/{}/'.format(self.circle.members.pk), data=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/users/{}/'.format(self.user.username))
        self.assertIn('circles', response.data)
        response = self.client.get(response.data['circles']['@id'])
        self.assertEqual(len(response.data['ldp:contains']), 0)
