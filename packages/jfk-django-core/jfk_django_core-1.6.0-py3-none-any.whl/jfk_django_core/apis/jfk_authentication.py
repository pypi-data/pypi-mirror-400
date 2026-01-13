from drf_spectacular.utils import extend_schema, extend_schema_view
from knox.views import LoginView, LogoutAllView, LogoutView
from rest_framework.authentication import SessionAuthentication

from ..authentication import BasicLikeAuthentication


@extend_schema_view(
    post=extend_schema(operation_id="login"),
)
class TokenLoginView(LoginView):
    authentication_classes = [BasicLikeAuthentication, SessionAuthentication]
    # permission_classes = [AllowAny]


@extend_schema_view(
    post=extend_schema(operation_id="logout"),
)
class TokenLogoutView(LogoutView):
    pass


@extend_schema_view(
    post=extend_schema(operation_id="logoutAll"),
)
class TokenLogoutAllView(LogoutAllView):
    pass
