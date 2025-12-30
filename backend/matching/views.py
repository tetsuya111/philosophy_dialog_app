from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .choices import UserMatchingStatus
from .serializers import UserMatchingStatusSerializer


# Create your views here.
class PostProcessingHistoryView(APIView):
    serializer_class = UserMatchingStatusSerializer

    def get(self, request: Request) -> Response:
        data = self.serializer_class(request.user.matching_status)
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request: Request, status: int) -> Response:
        if status not in UserMatchingStatus.values:
            msg = "statusが範囲外です"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        request.user.matching_status = status
        return Response(data, status=status.HTTP_200_OK)


@api_view["POST"]
def join_matching(request: Request) -> Response:
    if request.user.matching_status != UserMatchingStatus.NONE:
        data = UserMatchingStatusSerializer(request.user.matching_status)
        msg: str = f"{request.user.username}は待機中または参加中です"
        return Response({**data, "msg": msg}, status=status.HTTP_400_BAD_REQUEST)
    return PostProcessingHistoryView.post(request, UserMatchingStatus.WATING)
