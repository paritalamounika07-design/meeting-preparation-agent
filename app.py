import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL")
HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID")


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Meeting Preparation Agent",
    page_icon="🤝",
    layout="wide",
)


# =========================================================
# APP TITLE
# =========================================================

st.title("🤝 Meeting Preparation Agent")

st.write(
    "Prepare for your next meeting using relevant information "
    "from previous meetings."
)


# =========================================================
# CHECK CONFIGURATION
# =========================================================

if not GROQ_API_KEY:
    st.error("Groq API key was not loaded. Check your .env file.")
    st.stop()

if not HINDSIGHT_API_KEY:
    st.error("Hindsight API key was not loaded. Check your .env file.")
    st.stop()

if not HINDSIGHT_BASE_URL:
    st.error("Hindsight base URL was not loaded. Check your .env file.")
    st.stop()

if not HINDSIGHT_BANK_ID:
    st.error("Hindsight bank ID was not loaded. Check your .env file.")
    st.stop()


# =========================================================
# CREATE CLIENTS
# =========================================================

groq_client = Groq(
    api_key=GROQ_API_KEY
)

hindsight_client = Hindsight(
    base_url=HINDSIGHT_BASE_URL,
    api_key=HINDSIGHT_API_KEY,
)


st.success(
    "Groq and Hindsight connections configured successfully!"
)


# =========================================================
# SAVE A MEETING
# =========================================================

st.subheader("📝 Save a Meeting")

meeting_title = st.text_input(
    "Meeting title",
    placeholder="Example: Project Planning Meeting",
    key="save_title",
)

meeting_notes = st.text_area(
    "Meeting notes",
    placeholder="Enter the important points discussed in this meeting...",
    height=200,
    key="save_notes",
)


if st.button("Save Meeting", key="save_meeting_button"):

    if not meeting_title.strip():

        st.warning("Please enter a meeting title.")

    elif not meeting_notes.strip():

        st.warning("Please enter some meeting notes.")

    else:

        memory_text = f"""
Meeting title: {meeting_title}

Meeting notes:
{meeting_notes}
"""

        try:

            hindsight_client.retain(
                bank_id=HINDSIGHT_BANK_ID,
                content=memory_text,
            )

            st.success(
                "Meeting saved to Hindsight memory! 🧠"
            )

        except Exception as e:

            st.error(
                f"Could not save meeting to Hindsight: {e}"
            )


# =========================================================
# PREPARE FOR NEXT MEETING
# =========================================================

st.divider()

st.subheader("🎯 Prepare for Your Next Meeting")

next_meeting_title = st.text_input(
    "Next meeting title",
    placeholder="Example: Project Planning Follow-up",
    key="next_title",
)

next_meeting_topic = st.text_area(
    "What is this meeting about?",
    placeholder=(
        "Example: Follow up on the project timeline "
        "and prototype."
    ),
    height=120,
    key="next_topic",
)


if st.button(
    "Prepare My Meeting",
    key="prepare_meeting_button",
):

    if not next_meeting_title.strip():

        st.warning(
            "Please enter the next meeting title."
        )

    elif not next_meeting_topic.strip():

        st.warning(
            "Please describe what the meeting is about."
        )

    else:

        try:

            # -------------------------------------------------
            # ASK HINDSIGHT FOR RELEVANT PREVIOUS MEMORIES
            # -------------------------------------------------

            recall_query = f"""
What did we previously discuss that is relevant
to this upcoming meeting?

Upcoming meeting:
{next_meeting_title}

Topic:
{next_meeting_topic}

Look for previous decisions, deadlines, follow-ups,
open questions, project progress, and important context.
"""

            recall_result = hindsight_client.recall(
                bank_id=HINDSIGHT_BANK_ID,
                query=recall_query,
            )


            # -------------------------------------------------
            # EXTRACT RECALLED MEMORIES
            # -------------------------------------------------

            memories = recall_result.results


            if not memories:

                st.info(
                    "No relevant previous memories were found."
                )

                previous_context = (
                    "No relevant previous meeting memories "
                    "were found."
                )

            else:

                previous_context = "\n\n".join(
                    [
                        f"- {memory.text}"
                        for memory in memories
                    ]
                )

                with st.expander(
                    "🧠 Hindsight memories used"
                ):

                    for memory in memories:

                        st.write(
                            f"- {memory.text}"
                        )


            # -------------------------------------------------
            # ASK GROQ TO CREATE THE PREPARATION BRIEF
            # -------------------------------------------------

            prompt = f"""
You are a Meeting Preparation Agent.

Your job is to prepare a concise and useful briefing
for an upcoming meeting using relevant information
retrieved from previous meetings.

Upcoming meeting:
{next_meeting_title}

Meeting topic:
{next_meeting_topic}

Relevant previous meeting memories:
{previous_context}

Create a preparation brief with exactly these sections:

1. Previous Discussion
Summarize only the relevant information explicitly present
in the retrieved memories.

2. Decisions
List only decisions that are explicitly stated in the
retrieved memories. Do not infer or create decisions.

3. Pending Follow-ups
List only tasks, commitments, or follow-ups that are
explicitly stated as unfinished or still pending in the
retrieved memories.

If no explicit pending follow-ups are present, write:
"No explicit pending follow-ups were recorded."

4. Suggested Questions
Suggest useful questions for the upcoming meeting based
on the retrieved context. These questions may explore
status, blockers, risks, or next steps, but must be clearly
presented as questions rather than facts.

5. Meeting Focus
Give a short focus for the upcoming meeting based only
on the retrieved context.

Important rules:

- Do not invent facts.
- Do not turn suggestions into facts.
- Do not turn questions into facts.
- Do not assume a task is pending unless the retrieved
  memories explicitly indicate that it is pending.
- Use only information supported by the retrieved memories.
- If the retrieved memories do not contain enough information,
  say so clearly.
- Preserve dates exactly as they appear in the retrieved memories.
- Never create a calendar date from a relative date such as
  "Friday", "tomorrow", or "next week".
"""


            completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise and helpful "
                            "meeting preparation assistant. "
                            "You must not invent facts."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
                max_completion_tokens=1200,
            )


            # -------------------------------------------------
            # GET THE AI RESPONSE
            # -------------------------------------------------

            preparation_brief = (
                completion
                .choices[0]
                .message
                .content
            )


            # -------------------------------------------------
            # DISPLAY THE RESULT
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "📋 Meeting Preparation Brief"
            )

            st.markdown(
                preparation_brief
            )


        except Exception as e:

            st.error(
                f"Could not prepare the meeting: {e}"
            )