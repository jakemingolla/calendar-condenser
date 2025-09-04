from datetime import datetime

from src.agents.helpers.models import get_llm
from src.agents.helpers.serialization import serialize_event
from src.types.state import StateWithCalendar
from src.types.user import User

unstructured_llm = get_llm(source="guide.public")


def get_baseline_context(user: User, date: datetime) -> str:
    return "".join(
        (
            "CONTEXT:\n",
            "- You are an assistant that can help with calendar events.\n",
            f"- The current date is {date.strftime('%Y-%m-%d')}.\n"
            f"- You are speaking with {user.given_name}. Their user ID is {user.id!s}.\n"
            f"- The user's timezone is {user.timezone}.\n",
            "- You are a part of an application called 'calendar-condenser'.\n",
            "- The application is designed to help users streamline their calendar events.\n",
        ),
    )


def get_formatting_rules() -> str:
    return "".join(
        (
            "FORMATTING RULES:\n",
            "- You MUST respond with a short sentence.\n",
            "- You are speaking directly to the user. You must be engaging and friendly.\n",
            "- You MUST use Markdown formatting to style your response.\n",
            "- You MUST respond in English.\n",
            "- You MUST NOT use any emojis.\n",
            "- Do NOT include numbered lists in your response.\n",
            "- Do NOT include semicolons in your response.\n",
            "- Do NOT mention you are working for the calendar-condenser application.\n",
        ),
    )


async def introduction_to_user(user: User, date: datetime) -> None:
    baseline_context = get_baseline_context(user, date)
    formatting_rules = get_formatting_rules()
    prompt = "".join(
        (
            baseline_context,
            "\n",
            "CORE OBJECTIVE:\n",
            "- Introduce yourself to the user and explain what you can do for them.\n",
            "- Below you will find a list of steps you will take to streamline the user's calendar.\n",
            "- Describe each step briefly and in a way that is easy to understand.\n",
            "\n",
            "STEPS:\n",
            "- Step 1: You will load the user's calendar events for the current date.\n",
            "- Step 2: You will load the calendars of all invitees for the current date.\n",
            "- Step 3: You will generate a list of rescheduling proposals for the user's calendar events.\n",
            "- Step 4: You will send the rescheduling proposals to each invitee.\n",
            "- Step 5: You will wait for the invitees to accept or reject the rescheduling proposals.\n",
            "- Step 6: You will update the user's calendar with the accepted rescheduling proposals.\n",
            "- Step 7: You will summarize the rescheduling proposals and send the summary to the user.\n",
            "\n",
            formatting_rules,
        ),
    )

    await unstructured_llm.ainvoke(prompt)


async def summarize_state_with_calendar(state: StateWithCalendar) -> None:
    baseline_context = get_baseline_context(state.user, state.date)
    formatting_rules = get_formatting_rules()
    calendar_events = state.calendar.get_events_on(state.date)
    prompt = "".join(
        (
            baseline_context,
            "\n",
            "CORE OBJECTIVE:\n",
            "- Summarize the user's calendar for the given date.\n",
            "- Include the following information:\n",
            "  - How many events are scheduled for the given date.\n",
            "  - The total duration of the events scheduled for the given date.\n",
            "  - The total unique number of invitees for the events scheduled for the given date.\n",
            "- When you have finished summarizing the calendar events, explain the next step:\n",
            "  - You will now load the calendars of all invitees for the current date.\n",
            "\n",
            "RULES:\n",
            "- Do not count the current user towards the total number of invitees.\n",
            formatting_rules,
            "\n",
            "CALENDAR EVENTS:\n",
            "".join(serialize_event(event) for event in calendar_events),
        ),
    )

    await unstructured_llm.ainvoke(prompt)


async def anticipate_rescheduling_proposals(state: StateWithCalendar) -> None:
    baseline_context = get_baseline_context(state.user, state.date)
    formatting_rules = get_formatting_rules()
    prompt = "".join(
        (
            baseline_context,
            "\n",
            "CORE OBJECTIVE:\n",
            "- Explain to the user you will be generating rescheduling proposals for their calendar events.\n",
            "- Explain that you will try and find the best time to reschedule their events.\n",
            "- Indicate you are thinking very hard by using language like 'Hmmm...' or 'Let me think about this...'.\n",
            "\n",
            formatting_rules,
        ),
    )

    await unstructured_llm.ainvoke(prompt)
