from rest_framework import serializers

from .models import StudyProgress


class StudyProgressSerializer(serializers.ModelSerializer):
    """Serializer for the StudyProgress model, used for output."""

    class Meta:
        model = StudyProgress
        fields = ['id', 'user_id', 'topic', 'hours', 'timestamp']
        read_only_fields = ['timestamp']


class SummarizeSerializer(serializers.Serializer):
    """Serializer for text summarization input."""
    text = serializers.CharField(
        help_text="The text content to be summarized.",
        min_length=10
    )


class TrackProgressInputSerializer(serializers.Serializer):
    """
    Serializer specifically for the input to the trackProgress API view.
    Handles user_id, topic, hours, and the non-model field report_only.
    """
    user_id = serializers.CharField(
        max_length=255,
        help_text="A unique identifier for the user."
    )
    topic = serializers.CharField(
        max_length=255,
        help_text="The topic studied."
    )
    hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0.0,
        required=False,
        default=0.0,
        help_text="The number of hours studied. Set to 0 if only reporting."
    )
    report_only = serializers.BooleanField(
        required=False,
        default=False,
        help_text="If true, only reports existing progress without adding new hours."
    )

    def validate(self, data):
        if not data.get('report_only') and data.get('hours') <= 0:
            raise serializers.ValidationError(
                {"hours": "Hours must be greater than 0 when not in report-only mode."}
            )
        return data
