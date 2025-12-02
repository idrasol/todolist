from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    path('', views.board_list, name='board_list'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('board/create/', views.board_create, name='board_create'),
    path('board/<int:board_id>/delete/', views.board_delete, name='board_delete'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:post_id>/update/', views.post_update, name='post_update'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:post_id>/feedback/', views.post_feedback, name='post_feedback'),
    path('post/<int:post_id>/comment/create/', views.comment_create, name='comment_create'),
    path('gallery/', views.gallery, name='gallery'),
]

