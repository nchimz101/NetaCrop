from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers


urlpatterns = [
    # path('app',views.index,name = "Home"),
    path('', views.app, name="Home"),
    path('index.html', views.app, name="Main_page"),
    path('diseases/', views.DiseaseList.as_view()),
    path('images/', views.uploadView.as_view()),
    path('collection', views.mycollection, name="My Collection"),
    path('about', views.aboutus, name="About")



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
