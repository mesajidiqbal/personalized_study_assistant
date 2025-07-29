import inspect
from datetime import date

import openai
import structlog
from django.conf import settings
from django.db import transaction

from .models import StudyProgress

log = structlog.get_logger(__name__)

_registered_tools = []


class OpenAIAPIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass


def tool(name: str, description: str):
    """
    Decorator to register functions as tools for the AI assistant.
    Extracts function signature to create JSON Schema for parameters.
    """

    def decorator(func):
        signature = inspect.signature(func)
        parameters_properties = {}
        required_params = []

        for param_name, param in signature.parameters.items():
            if param_name == 'kwargs':
                continue

            param_type = "string"
            if param.annotation is int:
                param_type = "integer"
            elif param.annotation is float:
                param_type = "number"
            elif param.annotation is bool:
                param_type = "boolean"

            parameters_properties[param_name] = {
                "type": param_type,
                "description": ""  # Can be enhanced by parsing docstrings
            }

            if param.default is inspect.Parameter.empty:
                required_params.append(param_name)

        tool_metadata = {
            "name": name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": parameters_properties,
                "required": required_params,
            }
        }
        _registered_tools.append(tool_metadata)

        def wrapper(*args, **kwargs):
            log.info(f"Tool call: {name}", function_name=func.__name__, args=args, kwargs=kwargs)
            try:
                result = func(*args, **kwargs)
                log.info(f"Tool success: {name}", function_name=func.__name__, result_preview=str(result)[:100])
                return result
            except OpenAIAPIError as e:
                log.error(f"OpenAI API error in tool: {name}", function_name=func.__name__, error=str(e), exc_info=True)
                raise
            except Exception as e:
                log.error(f"Generic error in tool: {name}", function_name=func.__name__, error=str(e), exc_info=True)
                raise

        return wrapper

    return decorator


def get_registered_tools_metadata():
    """Returns metadata for all registered tools."""
    return _registered_tools


openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
openai_model = settings.OPENAI_MODEL or "gpt-3.5-turbo"


@tool(
    name="generateStudyPlan",
    description="Generates a personalized study plan for a subject, duration, and daily hours in markdown."
)
def generate_study_plan(subject: str, duration_weeks: int, daily_hours: float) -> str:
    log.info("Generating study plan", subject=subject)
    if not settings.OPENAI_API_KEY:
        raise OpenAIAPIError("OpenAI API key not configured.")

    try:
        prompt = (
            f"Generate a personalized study plan for '{subject}' over {duration_weeks} weeks, "
            f"assuming an average of {daily_hours} hours of study per day. "
            "Include a weekly breakdown of topics, learning objectives, suggested daily activities, "
            "and recommended types of resources. Format clearly using markdown. "
            "Return only the plan, no conversational filler."
        )
        response = openai_client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        raise OpenAIAPIError(f"OpenAI API error: {e.status_code} - {e.response}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


@tool(
    name="summarizeText",
    description="Summarizes provided text into key points or a concise overview."
)
def summarize_text(text: str) -> str:
    log.info("Summarizing text", text_length=len(text))
    if not settings.OPENAI_API_KEY:
        raise OpenAIAPIError("OpenAI API key not configured.")

    try:
        prompt = (
            f"Please provide a concise summary of the following text, highlighting the main ideas and key points. "
            f"Return only the summary, no conversational filler:\n\n{text}"
        )
        response = openai_client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        raise OpenAIAPIError(f"OpenAI API error: {e.status_code} - {e.response}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


@tool(
    name="generateQuiz",
    description="Generates a multiple-choice quiz on a topic with a given number of questions."
)
def generate_quiz(topic: str, num_questions: int) -> str:
    log.info("Generating quiz", topic=topic, num_questions=num_questions)
    if not settings.OPENAI_API_KEY:
        raise OpenAIAPIError("OpenAI API key not configured.")

    try:
        prompt = (
            f"Generate a {num_questions}-question multiple-choice quiz about '{topic}'. "
            "For each question, provide 4 options (A, B, C, D) and clearly indicate the correct answer. "
            "Format the output using markdown, with questions numbered and options lettered. "
            "Return only the quiz content, no conversational filler."
        )
        response = openai_client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        raise OpenAIAPIError(f"OpenAI API error: {e.status_code} - {e.response}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


@tool(
    name="generateFlashcards",
    description="Generates study flashcards for a topic with a specified number of cards."
)
def generate_flashcards(topic: str, num_cards: int) -> str:
    log.info("Generating flashcards", topic=topic, num_cards=num_cards)
    if not settings.OPENAI_API_KEY:
        raise OpenAIAPIError("OpenAI API key not configured.")

    try:
        prompt = (
            f"Generate {num_cards} study flashcards for the topic '{topic}'. "
            "For each flashcard, provide a clear 'Front' and a concise 'Back'. "
            "Format each flashcard clearly using markdown. Return only the content."
        )
        response = openai_client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        raise OpenAIAPIError(f"OpenAI API error: {e.status_code} - {e.response}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


@tool(
    name="recommendResources",
    description="Recommends study resources for a subject and proficiency level."
)
def recommend_resources(subject: str, proficiency_level: str, num_resources: int) -> str:
    log.info("Recommending resources", subject=subject, proficiency_level=proficiency_level)
    if not settings.OPENAI_API_KEY:
        raise OpenAIAPIError("OpenAI API key not configured.")

    try:
        prompt = (
            f"Recommend {num_resources} study resources for a '{proficiency_level}' level student "
            f"learning '{subject}'. "
            "Include a mix of types like books, online courses, websites, tutorials, or articles. "
            "For each resource, provide its name, a brief description, and where it can be accessed. "
            "Format as a numbered list with clear descriptions. Return only the list."
        )
        response = openai_client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        raise OpenAIAPIError(f"OpenAI API error: {e.status_code} - {e.response}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


@tool(
    name="trackProgress",
    description="Records or reports study progress, aggregating hours for the same day."
)
def track_progress(user_id: str, topic: str, hours: float = 0.0, report_only: bool = False) -> str:
    current_date = date.today()
    log.info(
        "track_progress_function_called",
        user_id=user_id, topic=topic, hours=hours, report_only=report_only
    )

    try:
        with transaction.atomic():
            progress_entry = StudyProgress.objects.filter(
                user_id=user_id,
                topic=topic,
                timestamp__date=current_date
            ).first()

            if report_only:
                if progress_entry:
                    return (f"Your recorded progress for '{topic}' on {current_date.strftime('%Y-%m-%d')} "
                            f"is {float(progress_entry.hours):.2f} hours.")
                else:
                    return (f"No study progress recorded for '{topic}' on {current_date.strftime('%Y-%m-%d')}.")
            else:
                if hours <= 0:
                    current_hours = float(progress_entry.hours) if progress_entry else 0.0
                    return f"No new hours added for '{topic}'. Current total for today: {current_hours:.2f} hours."

                if progress_entry:
                    progress_entry.hours += hours
                    progress_entry.save()
                    return (f"Updated progress for '{topic}' on {current_date.strftime('%Y-%m-%d')}: "
                            f"Added {hours:.2f} hours. New total: {float(progress_entry.hours):.2f} hours.")
                else:
                    new_entry = StudyProgress.objects.create(
                        user_id=user_id,
                        topic=topic,
                        hours=hours
                    )
                    return (
                        f"Successfully recorded {hours:.2f} hours for '{topic}' on {current_date.strftime('%Y-%m-%d')}. "
                        f"Total for today: {float(new_entry.hours):.2f} hours.")

    except Exception as e:
        log.error("track_progress_database_error", error=str(e), exc_info=True)
        raise Exception(f"Error recording progress: {e}")
