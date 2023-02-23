"""vokalpedia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import vokalheart.views

urlpatterns = [
   path('admin/', admin.site.urls),
   path('get_csrf_token/', vokalheart.views.get_csrf_token, name='get_csrf_token'),
   path('', vokalheart.views.login_page, name='login'),
   path('logout/', vokalheart.views.logout_user, name='logout'),
   path('signup/', vokalheart.views.signup_page, name="signup"),
   path('home/', vokalheart.views.home, name='home'),
   path('wikispeech/', vokalheart.views.wikispeech, name='wikispeech'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)