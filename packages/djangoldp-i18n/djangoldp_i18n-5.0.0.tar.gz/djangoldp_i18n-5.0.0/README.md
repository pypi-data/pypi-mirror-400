
# I18nLDPViewSet

I18nLDPViewSet overrides DjangoLDP's LDPViewSet to provide serialization using the I18nLDPSerializer, instead of the default LDPSerializer

You can activate the custom functionality on your DjangoLDP Model by setting `view_set` in the Model.Meta: https://git.startinblox.com/djangoldp-packages/djangoldp#view_set

## Client-Side

If you are using Startin'Blox in your client application, please see the [Startin'Blox docs](https://docs.startinblox.com)

If you are writing your own client, a full how-to for requesting from the DjangoLDP viewset is out of the scope of this package README, but the adjustments needed to include a requested language are simple:
* for GET requests, simply set the `Accept-Language` header, following the [HTTP spec](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language)
* for POST requests it is easiest to do the same. For information, it is also possible to submit the langauge in [JSON-LD value-object syntax](https://www.w3.org/TR/json-ld/#value-objects), but the _response_ will be serialized into the HTTP-requested language

Both GET and POST requests currently only accommodate serialization in one language per-request. In POST requests this means that you cannot POST multiple language at the same time

# I18nLDPSerializer

The main functionality of I18n is provided in the serializer, which overrides DjangoLDP's LDPSerializer to select the activated language content and display this in the context of the response

The language is selected and the data manipulated automatically, based on the request object in the serializer context. A feature to provide the serialization into a language using a setting (without a request object) is TODO

# DjangoLDPI18nAdmin

This admin class simply inherits from `DjangoLDPAdmin` from DjangoLDP and `TranslationAdmin` from [Django-Modeltranslation](https://django-modeltranslation.readthedocs.io/en/latest/admin.html) to provide the features from both. It does so without additions
