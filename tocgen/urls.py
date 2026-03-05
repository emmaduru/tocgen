from django.contrib import admin
from django.urls import path, include, re_path
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Override allauth views that ignore project-level templates in 0.57+
    path('accounts/password/change/', core_views.password_change, name='account_change_password'),
    path('accounts/password/reset/', core_views.password_reset, name='account_reset_password'),
    path('accounts/password/reset/done/', core_views.password_reset_done, name='account_reset_password_done'),
    re_path(r'^accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$', core_views.password_reset_from_key, name='account_reset_password_from_key'),
    path('accounts/password/reset/key/done/', core_views.password_reset_from_key_done, name='account_reset_password_from_key_done'),
    path('accounts/social/connections/', core_views.social_connections, name='socialaccount_connections'),
    path('accounts/social/login/cancelled/', core_views.social_login_cancelled, name='socialaccount_login_cancelled'),
    path('accounts/social/login/error/', core_views.social_authentication_error, name='socialaccount_login_error'),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
]