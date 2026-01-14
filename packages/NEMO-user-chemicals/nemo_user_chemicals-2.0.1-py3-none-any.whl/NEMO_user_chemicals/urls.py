from django.urls import path, re_path

from NEMO_user_chemicals import views

urlpatterns = [
    # Chemical Requests and Inventory
    path("chemical_request/", views.chemical_request, name="chemical_request"),
    re_path(
        r"^chemical_request/view/(?P<sort_by>requester|date|approved|name)/$",
        views.view_requests,
        name="view_requests",
    ),
    path("chemical_request/view/", views.view_requests, name="view_requests"),
    path("chemical_request/details/<int:request_id>/", views.request_details, name="request_details"),
    path("chemical_request/approval/<int:request_id>/", views.update_request, name="update_request"),
    re_path(
        r"^user_chemicals/(?P<sort_by>owner|chemical|in_date|expiration|location|label_id)/$",
        views.user_chemicals,
        name="user_chemicals",
    ),
    path("user_chemicals/", views.user_chemicals, name="user_chemicals"),
    path("user_chemicals/add", views.add_user_chemical, name="add_user_chemical"),
    path("user_chemicals/add/<int:chem_req>/", views.add_user_chemical, name="add_user_chemical"),
    path("user_chemicals/update/<int:chem_id>/", views.update_user_chemical, name="update_user_chemical"),
    path("user_chemicals/delete/<int:chem_id>/", views.delete_user_chemical, name="delete_user_chemical"),
    path("chemical/add/", views.add_chemical, name="add_chemical"),
    path("chemical/add/<int:request_id>/", views.add_chemical, name="add_chemical_from_request"),
]
