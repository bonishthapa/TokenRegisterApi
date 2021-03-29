from django.urls import path

from newuser import views

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('login',views.LoginView.as_view()),
    path('email-verify',views.Verify_Email.as_view(),name='email-verify'),
]
