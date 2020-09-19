from django.shortcuts import render
from django.contrib.postgres.search import SearchVector
from rest_framework import generics, status
from rest_framework.response import Response
from users.views import SecureCreateView
from .serializers import *
from users.tasks import *
from .models import *
import copy

class CopsListView(generics.ListAPIView):
    serializer_class = CopSerializer
    def initial(self, request, *args, **kwargs):
        super(CopsListView, self).initial(request, *args, **kwargs)
        process_request_data.delay(request.META['HTTP_LAT'], request.META["HTTP_LNG"], request.user.id)

    def get_queryset(self):
        qs = Cop.objects.all()
        query = self.request.GET.get("q")
        if query:
            return Cop.objects.annotate(
                    search=SearchVector("first_name") + 
                        SearchVector("last_name") + 
                        SearchVector("badge_number")
                ).filter(search=query)
        return Cop.objects.all()

class ReportCreationView(SecureCreateView):
    serializer_class = CopDBComplaintSerializer
    def create(request, *args, **kwargs):
        cops = Cop.objects.all()
        if request.POST["cop"]["first_name"]:
            cops = cops.filter(first_name=request.POST["cop"]["first_name"])
        if request.POST["cop"]["last_name"]:
            cops = cops.filter(first_name=request.POST["cop"]["last_name"])
        if request.POST["cop"]["badge_number"]:
            cops = cops.filter(first_name=request.POST["cop"]["badge_number"])
        if cops.count() == 1:
            cop = cops.get()
        elif cop.count() > 1:
            cop = None
        else:
            cop = None
        d = copy.deepcopy(request.POST)
        if cop is not None:
            d["cop"] = CopSerializer(cop).data
        else:
            del d["cop"]
        complaint = CopDBComplaintSerializer(data=d)
        complaint.is_valid(raise_exception=True)
        complaint.save()
        record = CopDBComplaintRequest.objects.create(
            complaint=complaint,
            cop_badge_number=request.POST["cop"]["badge_number"],
            cop_ethnicity=request.POST["cop"]["ethnicity"],
            cop_sex=request.POST["cop"]["sex"],
            cop_first_name=request.POST["cop"]["first_name"],
            cop_last_name=request.POST["cop"]["last_name"],
        )
        serializer = complaint
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


