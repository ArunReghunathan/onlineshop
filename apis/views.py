from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apis.models import User
from onlineshop.auth import GenerateToken


@api_view(["GET"])
@permission_classes((AllowAny, ))
def test_api(request):
    print("success")
    data = {"success": 1}
    # a = User.objects.create(username="arun33",email="ar@ar.in3", first_name="Arun", remark={"test": "success"})
    users = User.objects.filter()
    users_list = []
    for each in users:
        users_list.append(each.email)
        print(each.remark, type(each.remark))
        if "date" in each.remark:
            for e in each.remark:
                print(e,  each.remark[e])

    data['users'] = users_list
    data['token'] = GenerateToken(str(each.uuid), "user")

    return Response(data, status=status.HTTP_200_OK)