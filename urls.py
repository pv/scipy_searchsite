from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^search/', 'scipy_search.views.index'),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
