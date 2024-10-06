from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from account.permissions import IsAdmin, IsAdminOrTeacher
from classroom.models import Routine, Notice, Class, Assignment
from classroom.serializers import RoutineSerializer, NoticeSerializer, ClassSerializer, AssignmentSerializer


class RoutineListCreateAPIView(ListCreateAPIView):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdmin()]
        return []


class RoutineRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer

    def get_permissions(self):
        if self.request.method != 'GET':
            return [IsAuthenticated(), IsAdmin()]
        return []


class NoticeListCreateAPIView(ListCreateAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdmin()]
        return []


class NoticeRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

    def get_permissions(self):
        if self.request.method != 'GET':
            return [IsAuthenticated(), IsAdmin()]
        return []


class ClassListCreateAPIView(ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]


class ClassRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def get_permissions(self):
        if self.request.method != 'GET':
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]


class AssignmentListCreateAPIView(ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]


class AssignmentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.request.method != 'GET':
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]
