# personalized_study_assistant/tool/rpc.py
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import structlog

from .functions import get_registered_tools_metadata

log = structlog.get_logger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def tools_list(request):
    """
    Expose an InitializeResult-style GET endpoint for Phronetic AI.
    """
    log.info("tools_list_requested")

    try:
        tools_metadata = get_registered_tools_metadata()
        log.info("tools_metadata_generated", num_tools=len(tools_metadata))

        response_data = {
            "protocolVersion": "1.0",
            "capabilities": {},   # no tool definitions here
            "serverInfo": {
                "name":        "Personalized Study Assistant Backend",
                "version":     "1.0.0",
                "description": "Backend service for the AI-powered personalized study assistant."
            },
            "tools": tools_metadata
        }
        return Response(response_data)
    except Exception as e:
        log.error("tools_list_generation_failed", error=str(e), exc_info=True)
        return Response(
            {"error": f"Failed to retrieve tools list: {e}"},
            status=500
        )

urlpatterns = [
    path('', tools_list, name='tools_list_rpc'),
]
