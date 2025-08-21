from datetime import datetime

from langchain_openai import ChatOpenAI

from src.callbacks.add_source_to_messages import AddSourceToMessagesCallback
from src.types.user import User

unstructured_llm = ChatOpenAI(model="gpt-4o-mini", callbacks=[AddSourceToMessagesCallback(source="guide.public")])


async def introduction_to_user(user: User, date: datetime) -> None:
    prompt = "".join(
        (
            "CONTEXT:\n",
            "- You are an assistant that can help with calendar events.\n",
            f"- The current date is {date.strftime('%Y-%m-%d')}.\n"
            f"- You are speaking with {user.given_name}. Their user ID is {user.id!s}.\n"
            f"- The user's timezone is {user.timezone}.\n",
            "- You are a part of an application called 'calendar-condenser'.\n",
            "- The application is designed to help users streamline their calendar events.\n",
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
            "RULES:\n",
            "- You MUST respond with a short sentence.\n",
            "- You MUST respond in English.\n",
            "- You MUST NOT use any emojis.\n",
            "- Do NOT format your response as a numbered list - be concise and to the point.\n",
        ),
    )

    await unstructured_llm.ainvoke(prompt)
