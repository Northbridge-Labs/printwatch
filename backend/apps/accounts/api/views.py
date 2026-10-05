"""Accounts views."""
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.api.permissions import IsAdmin
from apps.accounts.api.serializers import (
    DeveloperTokenSerializer,
    EmailTokenObtainPairSerializer,
    MintDeveloperTokenResponseSerializer,
    MintDeveloperTokenSerializer,
    UserSerializer,
)
from apps.common.container import container


@extend_schema(tags=["Auth"], responses={200: UserSerializer})
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

    @extend_schema(tags=["Auth"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmailTokenRefreshView(TokenRefreshView):
    @extend_schema(tags=["Auth"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["Accounts"], responses=DeveloperTokenSerializer)
class DeveloperTokenListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        svc = container.resolve("developer_token_service")
        tokens = svc.list(request.user.id)
        return Response(DeveloperTokenSerializer(
            [
                {
                    "id": t.id, "name": t.name, "jti": t.jti, "scopes": t.scopes,
                    "created_at": None, "revoked_at": t.revoked_at,
                }
                for t in tokens
            ],
            many=True,
        ).data)

    @extend_schema(
        request=MintDeveloperTokenSerializer,
        responses={
            201: OpenApiResponse(MintDeveloperTokenResponseSerializer,
                                 description="Token minted (JWT returned once)"),
        },
    )
    def post(self, request):
        serializer = MintDeveloperTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        svc = container.resolve("developer_token_service")
        secret = svc.mint(request.user.id, serializer.validated_data["name"],
                          serializer.validated_data["scopes"])
        return Response(
            {"id": secret.token_id, "jti": secret.jti, "token": secret.jwt},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Accounts"])
class DeveloperTokenRevokeView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, token_id: int):
        svc = container.resolve("developer_token_service")
        svc.revoke(token_id)
        return Response(status=status.HTTP_204_NO_CONTENT)