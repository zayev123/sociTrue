

from django.urls import path


from . import views
from chatSoci import chat_views
from accounts.views import ProfilesStatusView

urlpatterns = [
    path('activity_list', views.ActivitiesListView.as_view()),
    path('activity_list/<int:pk>/', views.ActivitiesListViewI.as_view()),
    path('activity_schedule', views.ActvtySchdView.as_view()),
    path('create_activity', views.ActivitiesCreateView.as_view()),
    path('activity_details/<int:pk>/', views.ActivitiesDetailView.as_view()),
    path('activity_update/<int:pk>/', views.ActivitiesUpdateView.as_view()),
    path('activity_delete/<int:pk>/', views.DeleteActView.as_view()),
    path('profiles_list', views.ProfilesListView.as_view()),
    path('profiles_update/<int:pk>/', views.ProfileUpdateView.as_view()),
    path('profiles_retrieve/<int:pk>/', views.ProfileRetrieveView.as_view()),
    path('hobbies_list', views.HobbiesListView.as_view()),
    path('category_list', views.CategoryListView.as_view()),
    path('participate/<int:pk>/', views.ParticipateView.as_view()),
    path('un_participate', views.UnParticipateView.as_view()),
    path('remove_participant', views.RmPrtcpntView.as_view()),
    path('swap_participant', views.SwpPrtcpntView.as_view()),
    path('activity_details/<int:pk>/comments', views.CommentPageView.as_view()),
    path('delete_comment', views.DeleteCommView.as_view()),
    path('profiles_status/<int:pageNumber>,<int:pageSize>,<int:profId>/',
         ProfilesStatusView.as_view()),
    path('retrieveChat/<int:pk>/', chat_views.RetreiveChatsOfProfile.as_view()),
    path('createChat', chat_views.CreateChat.as_view()),
]
