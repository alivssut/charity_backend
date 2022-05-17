from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from accounts.permissions import IsCharityOwner, IsBenefactor
from charities.models import Task , Benefactor
from accounts.permissions import IsBenefactor , IsCharityOwner
from django.contrib.auth.decorators import permission_required
from charities.serializers import (
    TaskSerializer, CharitySerializer, BenefactorSerializer
)


class BenefactorRegistration(APIView):
    def post(self , request):
        form = BenefactorSerializer(data = request.POST)
        
        if form.is_valid():
            form.save(user=request.user)
            return HttpResponse(form, status=201)
        return HttpResponse(form, status=400)


class CharityRegistration(APIView):
    def post(self , request):
        form = CharitySerializer(data = request.POST)
        
        if form.is_valid():
            form.save(user=request.user)
            return HttpResponse(form, status=201)
        return HttpResponse(form, status=400)


class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {
            **request.data,
            "charity_id": request.user.charity.id
        }
        serializer = self.serializer_class(data = data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsCharityOwner, ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)


class TaskRequest(APIView):
    permission_classes = [IsBenefactor]
    def get(self , request ,task_id):
        tasks = get_object_or_404(Task , id = task_id)
        if tasks.state != "P":
            return Response(data = {'detail': 'This task is not pending.'}, status=404)
        else:
            tasks.state = Task.TaskStatus.WAITING
            
            tasks.assigned_benefactor = Benefactor.objects.get(id=task_id)
            tasks.save()
            #Task.objects.filter(id = task_id).update(state = Task.TaskStatus.WAITING)
            return Response(data= {'detail': 'Request sent.'}, status=200)



class TaskResponse(APIView):
    permission_classes = [IsCharityOwner]
    def post(self , request , task_id):
        task = get_object_or_404(Task , id = task_id)
        res = request.data.get('response')
        
        if res == "A" or res == "R":
            if task.state == "W":
                if res == "A":
                    task.state = Task.TaskStatus.ASSIGNED
                    task.save()
                    return Response(data={'detail': 'Response sent.'}, status=200)
                elif res == "R":
                    task.state = Task.TaskStatus.PENDING
                    task.assigned_benefactor = None
                    task.save()
                    return Response(data={'detail': 'Response sent.'}, status=200)
            else:
                return Response(data={'detail': 'This task is not waiting.'}, status=404)
        else:
            return Response(data={'detail': 'Required field ("A" for accepted / "R" for rejected)'}, status=400)  

class DoneTask(APIView):
    permission_classes = [IsCharityOwner]
    def post(self , request , task_id):
        task = get_object_or_404(Task , id = task_id)
        
        
        if task.state != 'A':
            return Response(data={'detail': 'Task is not assigned yet.'}, status=404)
        else:
            task.state = Task.TaskStatus.DONE
            task.save()
            return Response(data={'detail': 'Task has been done successfully.'}, status=200)



