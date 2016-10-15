from django.conf.urls import url
from annonce.views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^register/(?P<position>[-\w.]+)/$', register, name='register'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^post/$', PostListView.as_view(), name='my_post_list'),
    url(r'^post/add/$', PostCreateView.as_view(), name='post_add'),
    url(r'^post/edit/(?P<pk>[\d]+)/$', PostUpdateView.as_view(), name='post_edit'),
    url(r'^post/delete/(?P<pk>[\d]+)/$', PostDeleteView.as_view(), name='post_delete'),
    url(r'^add_cv/$', add_cv, name='add_cv'),
    url(r'^display_offer/$', RecentOffers.as_view(), name='recent_post_list'),
    url(r'^display_cv/$', RecentCV.as_view(), name='recent_cv_list'),
    url(r'^display_offer/archived/$', ArchivedOffers.as_view(), name='archived_post_list'),
    url(r'^display_offer/(?P<pk>[\d]+)/(?P<slug>[-\w.]+)$', OfferDetails.as_view(), name='post_details'),
    url(r'^submit_my_app/(?P<pk>[\d]+)/(?P<slug>[-\w.]+)/$', apply_offer, name='submit_my_app'),
]
