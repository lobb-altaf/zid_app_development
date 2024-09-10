# oauthapp/urls.py
# from django.urls import path
# from . import views_old

# urlpatterns = [
#     path('', views_old.index, name='home'),
#     path('authorize/', views_old.authorize, name='authorize'),

#     # path('oauth_redirect/', views.oauth_redirect, name='oauth_redirect'),
#     path('callback/', views_old.callback, name='callback'),
#     path('create-webhook/', views_old.create_webhook, name='create_webhook'),
#     path('webhook/', views_old.handle_webhook, name='handle_webhook'),
# ]


# oauth/urls.py
from django.urls import path
from . import views
from .views import OauthRedirectView, OauthCallbackView

urlpatterns = [
    path("", views.index, name="home"),
    path("authorize/", OauthRedirectView.as_view(), name="oauth-redirect"),
    path("callback/", OauthCallbackView.as_view(), name="oauth-callback"),
    path("create_webhook/", views.create_webhook, name="create_webhook"),
    path("webhook/", views.handle_webhook, name="handle_webhook"),
    path("zid_json_to_invoice/", views.zid_json_to_invoice, name="zid_json_to_invoice"),
    path("create_invoice_view/", views.create_invoice_view, name="create_invoice_view"),
]
