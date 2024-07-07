from django.urls import path

from app_main import views

urlpatterns = [
    path('user-registration/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('super-admin/', views.super_admin_view, name='super-admin'),
    path('org-admin/', views.org_admin_view, name='org-admin'),
    path('end-user/', views.end_user_view, name='end-user'),

    path('users/', views.UserMasterView.as_view(), name='users'),

    path('user-create/', views.UserView.as_view(), name='user-create'),

]
