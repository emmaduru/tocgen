from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/editor/', views.editor, name='editor'),
    path('api/upload/', views.upload_pdf, name='upload_pdf'),
    path('stripe/checkout/', views.create_checkout_session, name='create_checkout'),
    path('stripe/portal/', views.create_portal_session, name='stripe_portal'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
