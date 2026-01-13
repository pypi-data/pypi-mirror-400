import uuid
import json
from rest_framework.test import APITestCase, APIClient

from djangoldp_account.models import LDPUser


class PermissionsTestCase(APITestCase):
    # Django runs setUp automatically before every test
    def setUp(self):
        # we set up a client, that allows us
        self.client = APIClient()

    # we have custom set up functions for things that we don't want to run before *every* test, e.g. often we want to
    # set up an authenticated user, but sometimes we want to run a test with an anonymous user
    def setUpLoggedInUser(self, is_superuser=False):
        self.user = LDPUser(email='test@mactest.co.uk', first_name='Test', last_name='Mactest', username='test',
                            password='glass onion', is_superuser=is_superuser)
        self.user.save()
        # this means that our user is now logged in (as if they had typed username and password)
        self.client.force_authenticate(user=self.user)

    # we write functions like this for convenience - we can reuse between tests
    def _get_random_user(self):
        return LDPUser.objects.create(email='{}@test.co.uk'.format(str(uuid.uuid4())), first_name='Test',
                                      last_name='Test', username=str(uuid.uuid4()))

    def _get_context(self):
        return {
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
                'lastName': "https://cdn.startinblox.com/owl#last_name",
                'isAdmin': "https://cdn.startinblox.com/owl#is_admin"
            }

    def test_post_contact_for_myself(self):
        self.setUpLoggedInUser()
        another_user = self._get_random_user()

        body = {
            'user': {'@id': self.user.urlid},
            'contact': another_user.urlid,
            '@context': self._get_context()
        }

        response = self.client.post('/contacts/', json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    def test_post_contact_for_another(self):
        self.setUpLoggedInUser()
        another_user = self._get_random_user()

        body = {
            'user': {'@id': another_user.urlid},
            'contact': self.user.urlid,
            '@context': self._get_context()
        }

        response = self.client.post('/contacts/', json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # repeated tests using nested field
    def test_post_contact_for_myself_nested(self):
        self.setUpLoggedInUser()
        another_user = self._get_random_user()

        body = {
            'user': {'@id': self.user.urlid},
            'contact': another_user.urlid,
            '@context': self._get_context()
        }

        response = self.client.post('/users/{}/contacts/'.format(self.user.username),
                                    json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    def test_post_contact_for_another_nested(self):
        self.setUpLoggedInUser()
        another_user = self._get_random_user()

        body = {
            'user': {'@id': another_user.urlid},
            'contact': self.user.urlid,
            '@context': self._get_context()
        }

        response = self.client.post('/users/{}/contacts/'.format(another_user.username),
                                    json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)
