import structlog
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .functions import get_registered_tools_metadata

log = structlog.get_logger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def tools_list(request):
    # Support GET as well as POST for tool discovery
    if request.method == 'GET':
        rpc_id = request.query_params.get("id", None)
    else:  # POST
        rpc_id = request.data.get("id", None)
    log.info("tools_list_requested", rpc_id=rpc_id)

    try:
        tools_metadata = get_registered_tools_metadata()
        log.info("tools_metadata_generated", num_tools=len(tools_metadata))
        return Response({
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "tools": tools_metadata
            }
        })
    except Exception as e:
        log.error("tools_list_generation_failed", error=str(e), exc_info=True, rpc_id=rpc_id)
        return Response({
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {
                "code": -32603,
                "message": f"Failed to retrieve tools list: {e}"
            }
        }, status=500)


urlpatterns = [
    path('', tools_list, name='tools_list_rpc'),
]
