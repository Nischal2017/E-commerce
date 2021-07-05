from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create",views.create, name="create"),
    path("listing/<int:auction_item_id>",views.listing,name='listing'),
    path("watchlist/<int:user_id>",views.watchlist,name="watchlist"),
    path("inactive",views.inactive,name="inactive"),
    path("categories",views.categories,name="categories"),
    path("categories/<str:category>", views.category_listings, name="category_listings")
]



    
