import json

from rest_framework.test import APITestCase, APIClient
from guardian.shortcuts import assign_perm

from djangoldp_circle.models import Circle
from djangoldp_circle.tests.utils import get_random_user


class PermissionsTestCase(APITestCase):
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

    def _get_request_json(self, **kwargs):
        res = {
            '@context': {
                '@vocab': "https://cdn.startinblox.com/owl#",
                'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
                'ldp': "http://www.w3.org/ns/ldp#",
                'foaf': "http://xmlns.com/foaf/0.1/",
                'name': "rdfs:label",
                'acl': "http://www.w3.org/ns/auth/acl#",
                'permissions': "acl:accessControl",
                'mode': "acl:mode",
                'inbox': "https://cdn.startinblox.com/owl#inbox",
                'object': "https://cdn.startinblox.com/owl#object",
                'author': "https://cdn.startinblox.com/owl#author",
                'account': "https://cdn.startinblox.com/owl#account",
                'jabberID': "foaf:jabberID",
                'picture': "foaf:depiction",
                'firstName': "https://cdn.startinblox.com/owl#first_name",
                'lastName': "https://cdn.startinblox.com/owl#last_name"
            }
        }

        for key, value in kwargs.items():
            if isinstance(value, str):
                res.update({key: {'@id': value}})
            else:
                res.update({key: value})

        return res

    # list circles - not logged in
    def test_list_circles_anonymous_user(self):
        another_user = get_random_user()
        self.setUpCircle(True, another_user)
        response = self.client.get('/circles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # GET circle - not logged in
    def test_get_circle_public_anonymous_user(self):
        another_user = get_random_user()
        self.setUpCircle(True, another_user)

        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # list circles - not include private circles
    def test_list_circles(self):
        self.setUpLoggedInUser()
        # a public circle, a private circle I own and a private circle I'm not in
        another_user = get_random_user()
        self._get_random_circle(True, another_user)
        self._get_random_circle(False, self.user)
        self._get_random_circle(False, another_user)

        response = self.client.get('/circles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 2)

    # GET circle public
    def test_get_public_circle(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle(True, another_user)

        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # GET circle private - I am a member
    def test_get_circle_private_member(self):
        self.setUpLoggedInUser()
        self.setUpCircle(False)

        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # GET circle private - I am not a member
    def test_get_circle_private_not_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle(False, another_user)

        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 404)

    # POST a new circle - anyone authenticated can do this
    def test_post_circle(self):
        self.setUpLoggedInUser()

        response = self.client.post('/circles/', json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # POST a new circle - anonymous user
    def test_post_circle_anonymous_user(self):
        response = self.client.post('/circles/')
        self.assertEqual(response.status_code, 403)

    # PATCH circle public - denied
    def test_patch_public_circle(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle(True, another_user)

        response = self.client.patch('/circles/1/', json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # PATCH circle - I am a member but not an admin - denied
    def test_patch_circle_not_admin(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle(True, another_user)
        self.circle.members.user_set.add(self.user)

        response = self.client.patch('/circles/1/', json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # PATCH circle - I am an admin
    def test_patch_circle_admin(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle(False, another_user)
        self.circle.members.user_set.add(self.user)
        self.circle.admins.user_set.add(self.user)

        response = self.client.patch('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # adding a CircleMember - I am not a member myself
    def test_post_circle_member_not_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle(False, another_user)

        payload = self._get_request_json(user_set=[{'@id': another_user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # removing a CircleMember - I am not an admin
    def test_delete_circle_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle(False, another_user)
        self.circle.members.user_set.add(self.user)

        payload = self._get_request_json(user_set=[])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # removing a circle member - I am not logged in
    def test_delete_circle_member_anonymous_user(self):
        another_user = get_random_user()
        self.setUpCircle(False, another_user)

        payload = self._get_request_json(user_set=[])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # removing myself from CircleMember - I am not an admin
    def test_delete_myself_circle_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle(False, another_user)
        self.circle.members.user_set.add(self.user)

        payload = self._get_request_json(user_set=[{'@id': another_user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

    # adding a CircleMember - I am an admin
    def test_post_circle_member_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle(False, self.user)
        another_user = get_random_user()

        payload = self._get_request_json(user_set=[{'@id': another_user.urlid}, {'@id': self.user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        circle = Circle.objects.get(pk=self.circle.pk)
        self.assertEqual(len(circle.members.user_set.all()), 2)

    # removing a CircleMember - I am an admin
    def test_delete_circle_member_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle(False, self.user)

        another_user = get_random_user()
        self.circle.members.user_set.add(another_user)

        payload = self._get_request_json(user_set=[{'@id': self.user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

    # removing myself from Circle - I am an admin, and I'm not the last admin
    def test_delete_circle_member_admin_not_last_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle(False)

        another_user = get_random_user()
        self.circle.members.user_set.add(another_user)
        self.circle.admins.user_set.add(another_user)

        self.assertEqual(self.circle.members.user_set.count(), 2)
        self.assertEqual(self.circle.members.user_set.all()[0], self.user)
        self.assertEqual(self.circle.admins.user_set.all()[0], self.user)

        payload = self._get_request_json(user_set=[{'@id': another_user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        response = self.client.patch(f'/groups/{self.circle.admins.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.circle.members.user_set.count(), 1)
        self.assertEqual(self.circle.members.user_set.all()[0], another_user)
        self.assertEqual(self.circle.admins.user_set.all()[0], another_user)

    # make another admin - I am the circle owner
    def test_make_circle_member_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle(False, self.user)

        another_user = get_random_user()
        self.circle.members.user_set.add(another_user)

        payload = self._get_request_json(user_set=[{'@id': self.user.urlid},{'@id': another_user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.admins.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.circle.admins.user_set.count(), 2)
        self.assertIn(another_user, self.circle.admins.user_set.all())

    # Join a circle
    def test_join_circle(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle(True, another_user)
        self.assertEqual(self.circle.members.user_set.count(), 1)

        payload = self._get_request_json(user_set=[{'@id': self.user.urlid},{'@id': another_user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.circle.members.user_set.count(), 2)
        self.assertIn(another_user, self.circle.members.user_set.all())

    # test that django guardian object-level permission is applied
    def test_guardian_view_applied(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle(False, another_user)

        assign_perm('view_circle', self.user, self.circle)
        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # even with object-permission, I can't remove an admin
    def test_delete_circle_admin_guardian(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle(False, another_user)

        assign_perm('delete_circle', self.user, self.circle)
        assign_perm('view_circle', self.user, self.circle)

        payload = self._get_request_json(user_set=[{'@id': self.user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_hack_post_circle_member_to_admin(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle(False, another_user)

        payload = self._get_request_json(user_set=[{'@id': self.user.urlid}])
        response = self.client.patch(f'/groups/{self.circle.admins.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(self.user, self.circle.admins.user_set.all())

    def test_update_circle_owner_distant(self):
        self.setUpLoggedInUser()
        self.setUpCircle(True, self.user)

        owner_id = "https://distant.com/users/1/"

        payload = self._get_request_json(owner=owner_id)
        payload.update({'@id': self.circle.urlid})

        response = self.client.patch('/circles/{}/'.format(self.circle.pk),
                                     data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        circle = Circle.objects.get(pk=self.circle.pk)
        self.assertEqual(circle.owner.urlid, owner_id)