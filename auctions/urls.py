from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listingDetail/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path("categories", views.categories, name="categories"),
    path('categories/<str:category_name>/', views.category_listings_view, name='category_listings'),
    path("create/", views.create_listing, name="create_listing"),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('viewsbid/', views.user_bids, name="bid_view")
]
