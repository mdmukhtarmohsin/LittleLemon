from django.urls import path
from . import views

urlpatterns = [
    path('api/menu-items/', views.MenuItemView.as_view()),
    path('api/menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('api/c/', views.CategoryView.as_view()),
    path('api/groups/manager/users/', views.Managers_view.as_view()),
    path('api/groups/manager/users/<int:pk>',
         views.SingleManagers_view.as_view()),
    path('api/groups/delivery-crew/users/',
         views.Delivery_crew_view.as_view()),
    path('api/groups/delivery-crew/users/<int:pk>',
         views.SingleDelivery_crew_view.as_view()),
    path('api/cart/menu-items/',
         views.Cart_view.as_view()),
    path('api/orders/', views.Order_view.as_view()),
    path('api/orders/<int:pk>', views.SingleOrder_view.as_view()),
]
