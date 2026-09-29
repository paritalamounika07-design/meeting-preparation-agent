# 🤝 Meeting Preparation Agent

A simple AI-powered Meeting Preparation Agent that uses Hindsight memory to help prepare for upcoming meetings using relevant information from previous meetings.

## 🚀 What It Does

The agent follows this workflow:

1. Save notes from a previous meeting.
2. Store those notes in Hindsight memory.
3. Enter the topic of an upcoming meeting.
4. Recall relevant information from previous meetings.
5. Use Groq to generate a preparation brief.

The preparation brief includes:

- Previous Discussion
- Decisions
- Pending Follow-ups
- Suggested Questions
- Meeting Focus

## 🧠 Why Memory Matters

Normal AI assistants may not automatically remember what was discussed in an earlier meeting.

This project uses Hindsight as a memory layer.

For example:

**Meeting 1**

> The team agreed that the first prototype must be finalized by October 2, 2026.

**Meeting 2**

The user asks the agent to prepare for a follow-up about the prototype.

Hindsight retrieves the relevant previous information, and the agent uses that context to create the meeting preparation brief.

This demonstrates how persistent memory can make an AI assistant more useful across multiple interactions.

## 🏗️ Architecture

```text
User
  │
  ▼
Streamlit Interface
  │
  ├── Save Meeting
  │      │
  │      ▼
  │   Hindsight
  │      │
  │      └── Stores meeting memory
  │
  └── Prepare Meeting
         │
         ▼
      Hindsight Recall
         │
         ▼
    Relevant Memories
         │
         ▼
        Groq
         │
         ▼
  Meeting Preparation Brief