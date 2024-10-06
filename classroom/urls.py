from django.urls import path

from classroom.views import RoutineListCreateAPIView, RoutineRetrieveUpdateDestroyAPIView, \
    NoticeListCreateAPIView, NoticeRetrieveUpdateDestroyAPIView, \
    ClassListCreateAPIView, ClassRetrieveUpdateDestroyAPIView, \
    AssignmentListCreateAPIView, AssignmentRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('routines/', RoutineListCreateAPIView.as_view(), name='routines'),
    path('routines/<int:pk>/', RoutineRetrieveUpdateDestroyAPIView.as_view(), name='routine'),
    path('notices/', NoticeListCreateAPIView.as_view(), name='notices'),
    path('notices/<int:pk>/', NoticeRetrieveUpdateDestroyAPIView.as_view(), name='notice'),
    path('classes/', ClassListCreateAPIView.as_view(), name='classes'),
    path('classes/<int:pk>/', ClassRetrieveUpdateDestroyAPIView.as_view(), name='class'),
    path('assignments/', AssignmentListCreateAPIView.as_view(), name='assignments'),
    path('assignments/<int:pk>/', AssignmentRetrieveUpdateDestroyAPIView.as_view(), name='assignment'),
]
