from django.conf.urls import url,include
from Hmt import views

urlpatterns = [
    url(r'^task/',views.Task),
    url(r'^script/',views.Script),
    url(r'^group/',views.Group),
    url(r'^task_result/',views.TaskResult),
    url(r'^task_detail/',views.TaskDetail),
    url(r'^callback_info/',views.FetchInfo),
]