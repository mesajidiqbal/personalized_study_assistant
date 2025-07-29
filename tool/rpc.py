import structlog
from django.urls import path
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .functions import get_registered_tools_metadata, get_tool_function

log = structlog.get_logger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def rpc_endpoint(request):
    if request.method == 'GET':
        # Return InitializeResult
        tools_metadata = get_registered_tools_metadata()
        return Response({
            "protocolVersion": "1.0",
            "capabilities": {},
            "serverInfo": {
                "name": "Personalized Study Assistant",
                "version": "1.0.0",
                "description": "MCP tool endpoint"
            },
            "tools": tools_metadata
        })

    # POST path: call the named tool
    rpc_id = request.data.get("id")
    method_name = request.data.get("method")
    params = request.data.get("params", {})

    if not method_name:
        return Response({"jsonrpc": "2.0", "id": rpc_id,
                         "error": {"code": -32600, "message": "Method not provided"}},
                        status=status.HTTP_400_BAD_REQUEST)

    func = get_tool_function(method_name)
    if not func:
        return Response({"jsonrpc": "2.0", "id": rpc_id,
                         "error": {"code": -32601, "message": f"Method '{method_name}' not found"}},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        result = func(**params)
        return Response({"jsonrpc": "2.0", "id": rpc_id, "result": result})
    except Exception as e:
        log.error("tool_execution_error", method=method_name, error=str(e), exc_info=True)
        return Response({"jsonrpc": "2.0", "id": rpc_id,
                         "error": {"code": -32603, "message": f"Tool execution error: {e}"}},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


urlpatterns = [
    path('', rpc_endpoint, name='tools_rpc'),
]
