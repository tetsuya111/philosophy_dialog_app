from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.choices import UserMatchingStatus
from accounts.models import CustomUser
from accounts.serializers import CustomUserSerializer
from accounts.views import UserView

from .models import WaitingQueue


# Create your views here.
class UserMatchingStatusyView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def post(self, request: Request, status: int) -> Response:
        if status not in UserMatchingStatus.values:
            msg = "statusが範囲外です"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        request.user.matching_status = status
        request.user.save()
        return UserView().get(request)


@api_view(["GET"])
def join_matching(request: Request) -> Response:
    if request.user.matching_status != UserMatchingStatus.NONE:
        msg: str = f"{request.user.username}は待機中または参加中です"
        data = {
            "userid": request.user.pk,
            "status": request.user.matching_status,
        }
        return Response({**data, "msg": msg}, status=status.HTTP_400_BAD_REQUEST)
    if not WaitingQueue.objects.filter(user=request.user).exists():
        waiting_queue = WaitingQueue.objects.create(user=request.user)
        waiting_queue.save()
    return UserMatchingStatusyView().post(request, UserMatchingStatus.WATING)


@api_view(["GET"])
def cancel_matching(request: Request) -> Response:
    if request.user.matching_status != UserMatchingStatus.WATING:
        msg: str = f"{request.user.username}は待機中または参加中です"
        data = {
            "userid": request.user.pk,
            "status": request.user.matching_status,
        }
        return Response({**data, "msg": msg}, status=status.HTTP_400_BAD_REQUEST)
    if WaitingQueue.objects.filter(user=request.user).exists():
        waiting_queue = WaitingQueue.objects.create(user=request.user)
        waiting_queue.delete()
    return UserMatchingStatusyView().post(request, UserMatchingStatus.NONE)
