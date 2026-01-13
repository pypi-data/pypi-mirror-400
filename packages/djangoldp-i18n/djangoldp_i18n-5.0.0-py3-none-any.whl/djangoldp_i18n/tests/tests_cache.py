from django.test import override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from djangoldp_i18n.tests.models import MultiLingualModel, MultiLingualChild


class TestCache(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                         password='glass onion')
        self.client.force_authenticate(self.user)

    def tearDown(self):
        pass

    def _language_set_in_context(self, context, value):
        return '@language' in context.keys() and context['@language'] == value

    def _assert_language_set_in_response(self, response, value):
        '''
        Auxiliary function asserts the the language is set in context, with the value passed
        '''
        self.assertIn('@context', response.data.keys())
        context = response.data.get('@context')
        language_found = False
        if isinstance(context, dict):
            language_found = self._language_set_in_context(context, value)
        elif isinstance(context, list):
            for member in context:
                if isinstance(member, dict):
                    language_found = self._language_set_in_context(member, value)

        self.assertTrue(language_found)

    def test_get_resource(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")

        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'fr')
        self.assertEqual(response.data.get('title'), post.title_fr)

        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'en')
        self.assertEqual(response.data.get('title'), post.title_en)
