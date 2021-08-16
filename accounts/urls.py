from django.urls import path
from knox import views as knox_views
from . import views

urlpatterns = [
    path('register', views.RegisterAPI.as_view()),
    path('login', views.LoginAPI.as_view()),
    path('logout', views.Logout.as_view()),
    path('social', views.SocialSignUp.as_view()),
    path('block', views.BlockView.as_view()),
    path('unblock', views.UnBlockView.as_view()),
    path('send_friend_request', views.SendFrnRqstView.as_view()),
    path('accept_friend_request', views.AccptFrnRqstView.as_view()),
    path('remove_friend_requests', views.RmvFrndRqstView.as_view()),
    path('remove_friend', views.RmvFriendView.as_view()),
    path('friends_list/<int:pk>/', views.FrndLstView.as_view()),
    path('received_friend_requests', views.FrndRcvdRqLstView.as_view()),
    path('sent_friend_requests', views.FrndSntRqLstView.as_view()),
    path('become_organizer', views.BcmOrgnzrView.as_view()),
]
