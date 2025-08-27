from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='monitoring_index'),
    path('api/loki/query/', views.query_loki_logs, name='query_loki_logs'),
    path('api/loki/metrics/', views.get_loki_metrics, name='get_loki_metrics'),
    path('api/jenkins/jobs/', views.get_jenkins_jobs, name='get_jenkins_jobs'),
    path('api/jenkins/jobs/<str:job_name>/', views.get_jenkins_build_info, name='get_jenkins_build_info'),
] 