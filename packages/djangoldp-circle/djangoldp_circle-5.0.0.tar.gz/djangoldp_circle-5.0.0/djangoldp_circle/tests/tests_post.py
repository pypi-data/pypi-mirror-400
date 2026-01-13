import json
from rest_framework.test import APITestCase, APIClient
from djangoldp_circle.models import Circle
from djangoldp_circle.tests.utils import get_random_user


class PostTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = get_random_user()
        self.client.force_authenticate(user=self.user)

    def test_post_circle(self):
        self.setUpLoggedInUser()

        body = {
          "public":"true",
          "linebreak":"",
          "name":"test1",
          "subtitle":"test1",
          "description":"\n",
          "help":"",
          "@context": {
            "@vocab":"https://cdn.startinblox.com/owl#",
            "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
            "ldp":"http://www.w3.org/ns/ldp#",
            "foaf":"http://xmlns.com/foaf/0.1/",
            "name":"rdfs:label",
            "description":"rdfs:comment",
            "acl":"http://www.w3.org/ns/auth/acl#",
            "permissions":"acl:accessControl",
            "mode":"acl:mode",
            "geo":"http://www.w3.org/2003/01/geo/wgs84_pos#",
            "lat":"geo:lat",
            "lng":"geo:long",
            "inbox":"https://cdn.startinblox.com/owl#inbox",
            "object":"https://cdn.startinblox.com/owl#object",
            "author":"https://cdn.startinblox.com/owl#author",
            "account":"https://cdn.startinblox.com/owl#account",
            "jabberID":"foaf:jabberID",
            "picture":"foaf:depiction"
          }
        }

        response = self.client.post('/circles/', data=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Circle.objects.count(), 1)

    def test_post_circle_missing_data(self):
        self.setUpLoggedInUser()

        body = {
            "description": "\n",
            "@context": {
                "@vocab": "https://cdn.startinblox.com/owl#",
                # notice the missing context
                # "description":"rdfs:comment",
            }
        }

        response = self.client.post('/circles/', data=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Circle.objects.count(), 1)
