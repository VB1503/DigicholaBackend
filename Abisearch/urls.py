from django.urls import path
from .views import SearchView



urlpatterns=[

    path('search/<str:query_type>/', SearchView.as_view(), name='search_view'),
    path('search/<str:query_type>/<str:catcall>/', SearchView.as_view(), name='search_view_with_location'),
    
]