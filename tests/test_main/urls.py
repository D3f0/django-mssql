from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^test_models/', include('test_models.foo.urls')),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
)
