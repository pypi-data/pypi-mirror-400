import uuid
import json

from rest_framework.test import APITestCase, APIClient
from djangoldp_project.models import Project, Customer
from djangoldp_account.models import LDPUser


class PermissionsTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self, is_superuser=False):
        self.user = LDPUser(email='test@mactest.co.uk', first_name='Test', last_name='Mactest', username='test',
                         password='glass onion', is_superuser=is_superuser)
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def _get_random_project(self, public=True, customer=None):
        return Project.objects.create(name='Test', public=public, customer=customer)

    def _get_random_customer(self, owner=None):
        return Customer.objects.create(owner=owner)

    def setUpProject(self, public=True):
        self.project = self._get_random_project(public)

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
                'lastName': "https://cdn.startinblox.com/owl#last_name",
                'isAdmin': "https://cdn.startinblox.com/owl#is_admin"
            }
        }

        for kwarg in kwargs:
            if isinstance(kwargs[kwarg], str):
                res.update({kwarg: {'@id': kwargs[kwarg]}})
            else:
                res.update({kwarg: kwargs[kwarg]})

        return res

    def _get_random_user(self):
        return LDPUser.objects.create(email='{}@test.co.uk'.format(str(uuid.uuid4())), first_name='Test', last_name='Test',
                                   username=str(uuid.uuid4()))

    # test project permissions
    def test_list_project_anonymous(self):
        self.setUpProject()
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 403)

    def test_list_project_authenticated(self):
        self.setUpLoggedInUser()
        # a public project, a private project I'm in and a private project I'm not in
        another_user = self._get_random_user()
        public_project = self._get_random_project()
        my_project = self._get_random_project(public=False)
        my_project.members.user_set.add(self.user)
        private_project = self._get_random_project(public=False)

        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 2)

    # test customer permissions
    def test_list_customer_anonymous(self):
        self._get_random_customer()
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 403)

    def test_list_customer_authenticated(self):
        self.setUpLoggedInUser()
        self._get_random_customer()
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)

    def test_get_customer_anonymous(self):
        customer = self._get_random_customer()
        response = self.client.get('/customers/{}/'.format(customer.pk))
        self.assertEqual(response.status_code, 403)

    def test_get_customer_authenticated(self):
        self.setUpLoggedInUser()
        customer = self._get_random_customer()
        self._get_random_project(public=False, customer=customer)
        response = self.client.get('/customers/{}/'.format(customer.pk))
        self.assertEqual(response.status_code, 403)

    def test_get_customer_owner(self):
        self.setUpLoggedInUser()
        customer = self._get_random_customer(owner=self.user)
        response = self.client.get('/customers/{}/'.format(customer.pk))
        self.assertEqual(response.status_code, 200)

    # members of one of their projects can view the customer
    def test_get_customer_project_member(self):
        self.setUpLoggedInUser()
        customer = self._get_random_customer()
        project = self._get_random_project(public=False, customer=customer)
        project.members.user_set.add(self.user)
        response = self.client.get('/projects/{}/'.format(project.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/customers/{}/'.format(customer.pk))
        self.assertEqual(response.status_code, 200)

    def test_post_customer_anonymous(self):
        response = self.client.post('/customers/', data=json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_post_customer_authenticated(self):
        self.setUpLoggedInUser()
        response = self.client.post('/customers/', data=json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # removing a Member - I am an admin
    def test_delete_project_member_admin(self):
        self.setUpLoggedInUser()
        self.setUpProject(public=False)
        self.project.members.user_set.add(self.user)
        self.project.admins.user_set.add(self.user)
        another_user = self._get_random_user()
        self.project.members.user_set.add(another_user)

        self.assertEqual(self.project.members.user_set.count(), 2)
        payload = self._get_request_json(user_set=[{'@id': self.user.urlid}])
        response = self.client.patch(f'/groups/{self.project.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.project.members.user_set.count(), 1)