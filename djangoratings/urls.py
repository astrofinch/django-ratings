from django.conf.urls.defaults import *

from djangoratings.views import AddRatingFromModel

urlpatterns = patterns('',
    url(r'^(?P<app_label>\w+)/(?P<model>\w+)/(?P<object_id>\d+)/$', AddRatingFromModel(), {
        'field_name': 'rating',
    }),
)
