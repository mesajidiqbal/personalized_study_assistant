import structlog
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import functions
from .serializers import SummarizeSerializer, TrackProgressInputSerializer

log = structlog.get_logger(__name__)


class SummarizeTextView(APIView):
    """
    API endpoint to summarize text.
    Delegates summarization logic to tool.functions.summarize_text.
    Requires token authentication.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SummarizeSerializer(data=request.data)
        user = getattr(request.user, 'username', 'anonymous')

        if serializer.is_valid():
            text = serializer.validated_data['text']
            log.info("SummarizeTextView_request", user=user, text_length=len(text))

            try:
                summary = functions.summarize_text(text=text)
                return Response({'summary': summary}, status=status.HTTP_200_OK)
            except functions.OpenAIAPIError as e:
                log.error("SummarizeTextView_openai_failed", user=user, error=str(e), exc_info=True)
                return Response(
                    {"error": f"OpenAI API Error: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                log.error("SummarizeTextView_generic_failure", user=user, error=str(e), exc_info=True)
                return Response(
                    {"error": f"An unexpected error occurred: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        log.error("SummarizeTextView_validation_failed", user=user, errors=serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrackProgressView(APIView):
    """
    API endpoint to record or report study progress.
    Delegates tracking logic to tool.functions.track_progress.
    Requires token authentication.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = TrackProgressInputSerializer(data=request.data)
        user_id = getattr(request.user, 'username', 'anonymous')

        if serializer.is_valid():
            topic = serializer.validated_data['topic']
            hours = serializer.validated_data['hours']
            report_only = serializer.validated_data['report_only']

            log.info("TrackProgressView_request", user_id=user_id, topic=topic, hours=hours, report_only=report_only)

            try:
                response_message = functions.track_progress(
                    user_id=user_id,
                    topic=topic,
                    hours=hours,
                    report_only=report_only
                )
                return Response({'message': response_message}, status=status.HTTP_200_OK)
            except Exception as e:
                log.error("TrackProgressView_failure", user_id=user_id, topic=topic, error=str(e), exc_info=True)
                return Response(
                    {"error": f"Failed to track progress: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        log.error("TrackProgressView_validation_failed", user_id=user_id, errors=serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
