from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name="landing_page"),
    path('signin/', views.signin_view, name="signin"),
    path('signup/', views.signup_view, name="signup"),
    path('logout/', views.logout_view, name="logout"),
    path('send_sms/', views.send_sms, name="send_sms"),

    # Email-related endpoint
    path('send_emails/', views.send_emails, name='send_emails'),
]
