from django.conf.urls import url
from recommender.views import recommender

print('****************',recommender)
urlpatterns = [
    url('', recommender, name='submission'),
]







# from django.conf.urls import url
# from recommender.views import recommender
#
#
# urlpatterns = [
#     url('', recommender, name='submission'),
# ]
# #grabs the request going into recommender
# # name= doesn't matter