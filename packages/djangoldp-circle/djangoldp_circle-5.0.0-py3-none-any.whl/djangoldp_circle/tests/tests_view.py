from rest_framework.test import APITestCase, APIClient
from djangoldp_circle.models import Circle
from djangoldp_circle.tests.utils import get_random_user


class ViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = get_random_user()
        self.client.force_authenticate(user=self.user)

    def _get_random_circle(self, public=True, owner=None):
        if owner is None:
            owner = self.user

        return Circle.objects.create(name='Test', public=public, owner=owner)

    def test_circles_list(self):
        self.setUpLoggedInUser()
        my_public_circle = self._get_random_circle(public=True, owner=self.user)
        my_private_circle = self._get_random_circle(public=False, owner=self.user)
        another_user = get_random_user()
        their_public_circle = self._get_random_circle(public=True, owner=another_user)
        their_private_circle = self._get_random_circle(public=False, owner=another_user)

        response = self.client.get('/circles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 3)
        ids = [c["@id"] for c in response.data['ldp:contains']]
        self.assertNotIn(their_private_circle.urlid, ids)
        sample = response.data['ldp:contains'][0]
        self.assertIn('name', sample)
        self.assertIn('owner', sample)
        self.assertIn('members', sample)
        self.assertIn('@type', sample)

    # circles joinable should return a list of circles which are public, and I'm not a member of
    def test_circles_joinable(self):
        self.setUpLoggedInUser()
        my_public_circle = self._get_random_circle(public=True, owner=self.user)
        my_private_circle = self._get_random_circle(public=False, owner=self.user)
        another_user = get_random_user()
        their_public_circle = self._get_random_circle(public=True, owner=another_user)
        their_private_circle = self._get_random_circle(public=False, owner=another_user)

        response = self.client.get('/circles/joinable/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)
        sample = response.data['ldp:contains'][0]
        self.assertEqual(their_public_circle.urlid, sample['@id'])
        self.assertEqual(their_public_circle.name, sample['name'])
        self.assertIn('owner', sample)
        self.assertIn('members', sample)
        self.assertIn('@type', sample)

    def test_circles_joinable_anonymous(self):
        user_a = get_random_user()
        public_circle = self._get_random_circle(public=True, owner=user_a)
        private_circle = self._get_random_circle(public=False, owner=user_a)

        response = self.client.get('/circles/joinable/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)
        sample = response.data['ldp:contains'][0]
        self.assertEqual(public_circle.urlid, sample['@id'])
        self.assertEqual(public_circle.name, sample['name'])
        self.assertIn('members', sample)
        self.assertIn('@type', sample)
