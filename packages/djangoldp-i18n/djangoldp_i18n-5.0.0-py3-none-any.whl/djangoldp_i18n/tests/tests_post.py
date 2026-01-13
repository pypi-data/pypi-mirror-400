from django.test import override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework.utils import json
from djangoldp_i18n.tests.models import MultiLingualModel


class TestPOST(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                         password='glass onion')
        self.client.force_authenticate(self.user)

    def tearDown(self):
        pass

    # auxiliary function for retrieving context for request
    def _get_context_with_language(self, language='en'):
        return {
            '@context': {
                '@language': language
            }
        }

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

    # test that I can post a resource with a language set
    def test_post_resource_with_language(self):
        post = {
            'https://cdn.startinblox.com/owl#title': 'title'
        }
        post.update(self._get_context_with_language('en'))

        response = self.client.post('/multilingualmodel/', data=json.dumps(post), content_type='application/ld+json',
                                    HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, 'fr')

        self.assertEqual(response.data.get('title'), None)
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

        # test object is updated correctly too
        post = MultiLingualModel.objects.get(urlid=response.data['@id'])
        self.assertEqual(post.title_en, 'title')
        self.assertEqual(post.title_fr, None)

    # language provided, but not by context
    def test_post_resource_with_language_by_header(self):
        post = {
            'https://cdn.startinblox.com/owl#title': 'titre'
        }

        response = self.client.post('/multilingualmodel/', data=json.dumps(post), content_type='application/ld+json',
                                    HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, 'fr')

        self.assertEqual(response.data.get('title'), 'titre')
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

        # test object is updated correctly too
        post = MultiLingualModel.objects.get(urlid=response.data['@id'])
        self.assertEqual(post.title_fr, 'titre')
        self.assertEqual(post.title_en, None)

    # test the default behaviour when a language is not set
    def test_post_resource_without_language(self):
        post = {
            'https://cdn.startinblox.com/owl#title': 'title'
        }
        response = self.client.post('/multilingualmodel/', data=json.dumps(post), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, settings.MODELTRANSLATION_DEFAULT_LANGUAGE)

        self.assertEqual(response.data.get('title'), 'title')
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

    def test_post_resource_localised_language(self):
        # post once with en-GB content
        post = {
            'https://cdn.startinblox.com/owl#title': 'titleGB'
        }
        post.update(self._get_context_with_language('en-GB'))
        response = self.client.post('/multilingualmodel/', data=json.dumps(post), content_type='application/ld+json',
                                    HTTP_ACCEPT_LANGUAGE='en-GB')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, 'en-gb')

        self.assertEqual(response.data.get('title'), 'titleGB')
        self.assertNotIn('title_en_gb', response.data.keys())
        self.assertNotIn('title_en_us', response.data.keys())

        # patch with en-US content
        post = {
            '@id': response.data['@id'],
            'https://cdn.startinblox.com/owl#title': 'titleUS'
        }
        post.update(self._get_context_with_language('en-US'))
        response = self.client.patch('/multilingualmodel/1/', data=json.dumps(post), content_type='application/ld+json',
                                     HTTP_ACCEPT_LANGUAGE='en-US')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'en-us')

        self.assertEqual(response.data.get('title'), 'titleUS')
        self.assertNotIn('title_en_gb', response.data.keys())
        self.assertNotIn('title_en_us', response.data.keys())

        # test object is updated correctly too
        post = MultiLingualModel.objects.get(urlid=response.data['@id'])
        self.assertEqual(post.title_en_gb, 'titleGB')
        self.assertEqual(post.title_en_us, 'titleUS')
        self.assertEqual(post.title_fr, None)

    def test_post_resource_localised_language_not_provided(self):
        post = {
            'https://cdn.startinblox.com/owl#title': 'titre'
        }
        post.update(self._get_context_with_language('fr-BE'))
        response = self.client.post('/multilingualmodel/', data=json.dumps(post), content_type='application/ld+json',
                                    HTTP_ACCEPT_LANGUAGE='fr-BE')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, 'fr')

        self.assertEqual(response.data.get('title'), 'titre')
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

        # test object is updated correctly too
        post = MultiLingualModel.objects.get(urlid=response.data['@id'])
        self.assertEqual(post.title_fr, 'titre')
        self.assertEqual(post.title_en, None)

    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE=None)
    def test_post_resource_language_not_provided(self):
        post = {
            'https://cdn.startinblox.com/owl#title': 'titolo'
        }
        post.update(self._get_context_with_language('it'))
        response = self.client.post('/multilingualmodel/', data=json.dumps(post), content_type='application/ld+json',
                                    HTTP_ACCEPT_LANGUAGE='it')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, 'en')

        self.assertEqual(response.data.get('title'), 'titolo')
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

        # test object is updated correctly too
        post = MultiLingualModel.objects.get(urlid=response.data['@id'])
        self.assertEqual(post.title_en, 'titolo')
        self.assertEqual(post.title_fr, None)

    def test_post_resource_language_multiple_requested(self):
        post = {
            'https://cdn.startinblox.com/owl#title': 'titre'
        }
        # prioritising French
        response = self.client.post('/multilingualmodel/', data=json.dumps(post), content_type='application/ld+json',
                                    HTTP_ACCEPT_LANGUAGE='fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, 'fr')
        self.assertEqual(response.data.get('title'), 'titre')

        # prioritising German, then English
        response = self.client.post('/multilingualmodel/', data=json.dumps(post), content_type='application/ld+json',
                                    HTTP_ACCEPT_LANGUAGE='fr;q=0.7, en;q=0.8, de;q=0.9, *;q=0.5')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, 'en')
        self.assertEqual(response.data.get('title'), 'titre')

    def test_post_resource_nested(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")
        child = {
            'https://cdn.startinblox.com/owl#title': 'titre'
        }
        child.update(self._get_context_with_language('fr'))

        response = self.client.post('/multilingualmodel/{}/children/'.format(post.pk),
                                    data=json.dumps(child),
                                    content_type='application/ld+json',
                                    HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 201)
        self._assert_language_set_in_response(response, 'fr')
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

        self.assertEqual(len(post.children.all()), 1)
        child = post.children.all()[0]
        self.assertEqual(child.title_fr, 'titre')
        self.assertEqual(child.title_en, None)
