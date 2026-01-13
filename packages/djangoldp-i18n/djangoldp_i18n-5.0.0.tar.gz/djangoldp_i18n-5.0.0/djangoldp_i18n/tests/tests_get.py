from django.test import override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from djangoldp_i18n.tests.models import MultiLingualModel, MultiLingualChild


class TestGET(APITestCase):

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

    # tests that a resource is serialized with @language property (default language)
    def test_get_resource(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")
        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, settings.MODELTRANSLATION_DEFAULT_LANGUAGE)

        self.assertEqual(response.data.get('title'), post.title)
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

    # tests resource serialization when a single language is set
    def test_get_resource_language_set(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")
        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'fr')

        self.assertEqual(response.data.get('title'), post.title_fr)
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

    def test_get_resource_localised_language(self):
        post = MultiLingualModel.objects.create(title_en_gb="titleGB", title_en_us="titleUS")
        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='en-US')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'en-us')

        self.assertEqual(response.data.get('title'), post.title_en_us)
        self.assertNotIn('title_en_gb', response.data.keys())
        self.assertNotIn('title_en_us', response.data.keys())

    def test_get_resource_localised_language_not_provided(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")
        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='fr-BE')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'fr')

        self.assertEqual(response.data.get('title'), post.title_fr)
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

    # tests resource serialization when multiple languages requested
    def test_get_resource_language_multiple_requested(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")
        # prioritising French
        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'fr')
        self.assertEqual(response.data.get('title'), post.title_fr)

        # prioritising German, then English
        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='fr;q=0.7, en;q=0.8, de;q=0.9, *;q=0.5')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'en')
        self.assertEqual(response.data.get('title'), post.title_en)


    # tests respource serialization when no default language is set - should default to English
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE=None)
    def test_get_resource_no_default_setting(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")
        response = self.client.get('/multilingualmodel/{}/'.format(post.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'en')

        self.assertEqual(response.data.get('title'), post.title_en)
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

    # tests resource serialization with modeltranslation fallback
    def test_get_resource_fallback_language(self):
        post = MultiLingualModel.objects.create()
        child = MultiLingualChild.objects.create(parent=post, title_fr="titre")
        response = self.client.get('/multilingualchildren/{}/'.format(post.pk, child.id),
                                   content_type='application/ld+json', HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'en')

        self.assertEqual(response.data.get('title'), child.title_fr)
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE=None)
    def test_get_resource_language_does_not_exist(self):
        post = MultiLingualModel.objects.create(title_en='title', title_fr='titre')
        response = self.client.get('/multilingualmodel/{}/'.format(post.pk),
                                   content_type='application/ld+json', HTTP_ACCEPT_LANGUAGE='it')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'en')

        self.assertEqual(response.data.get('title'), post.title_en)
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

        child = MultiLingualChild.objects.create(parent=post, title_fr="titre", title_en="title")
        response = self.client.get('/multilingualchildren/{}/'.format(child.pk),
                                   content_type='application/ld+json', HTTP_ACCEPT_LANGUAGE='it')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'en')

        self.assertEqual(response.data.get('title'), child.title_en)
        self.assertNotIn('title_en', response.data.keys())
        self.assertNotIn('title_fr', response.data.keys())

    # tests resource serialization on containers
    def test_get_container(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")
        child = MultiLingualChild.objects.create(parent=post, title_en="title", title_fr="titre")
        response = self.client.get('/multilingualmodel/', content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'fr')

        contained = response.data['ldp:contains']
        self.assertEqual(MultiLingualModel.objects.local().count(), len(contained))
        resource = contained[0]
        self.assertEqual(resource.get('title'), post.title_fr)
        self.assertNotIn('title_en', resource.keys())
        self.assertNotIn('title_fr', resource.keys())

        # test nested content
        self.assertEqual(resource['children'][0].get('title'), child.title_fr)

    # tests nested resource serialization
    def test_get_resource_nested(self):
        post = MultiLingualModel.objects.create(title_en="title", title_fr="titre")
        child = MultiLingualChild.objects.create(parent=post)
        response = self.client.get('/multilingualmodel/{}/children/'.format(post.pk), content_type='application/ld+json',
                                   HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 200)
        self._assert_language_set_in_response(response, 'fr')

        contained = response.data['ldp:contains']
        self.assertEqual(post.children.count(), len(contained))
        resource = contained[0]
        self.assertEqual(resource.get('title'), child.title_fr)
        self.assertNotIn('title_en', resource.keys())
        self.assertNotIn('title_fr', resource.keys())
