# AI Career & Personality Advisor

A Streamlit career exploration app that collects work preferences, Big Five self-ratings, behavioral examples, skills, interests, and goals. It uses an OpenAI-compatible language model API to create a structured career report with potential career paths and practical next steps.

> **Important:** This app is a career-planning aid, not a clinical or validated psychological assessment, mental-health service, or guarantee of job suitability. Personality scores are broad self-reported tendencies and should be considered alongside experience, circumstances, and personal judgment.

## Contents

- [Features](#features)
- [Questionnaire](#questionnaire)
- [Career report](#career-report)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configure the LLM API](#configure-the-llm-api)
- [Run the app](#run-the-app)
- [Test the API connection](#test-the-api-connection)
- [Saved responses and privacy](#saved-responses-and-privacy)
- [Project files](#project-files)
- [Troubleshooting](#troubleshooting)

## Features

- Four-step questionnaire with back/forward navigation and Streamlit session-state form values.
- Work-preference ratings and differently worded consistency checks.
- A 25-item Big Five self-report section with reverse-scored negatively worded items.
- Open-ended questions about decision-making, conflict, past job choices, and personal trade-offs.
- Career recommendations with fit scores, rationale, challenges, skill suggestions, and a 30/60/90-day plan.
- A button that makes a real `hello` request to the configured model and displays its reply.
- Local text-file saving of submitted questionnaire answers.
- Demo report generation when no LLM API credential is configured.

## Questionnaire

### Step 1: Work preferences and personality

The work-preference ratings use a 1–5 scale and cover:

- Analytical versus creative thinking.
- Independent versus collaborative work.
- Risk versus stability.
- Flexible versus structured work.
- Individual contribution versus leadership.

Each of these areas also has a differently phrased check question. Differences between the paired responses are passed to the model as context, not treated as a diagnosis or proof that a response is wrong.

| Preference | Main rating | Rephrased check |
| --- | --- | --- |
| Thinking style | Thinking Preference: highly analytical/data-driven to highly creative/intuitive | When solving a new problem, start with evidence and analysis or explore ideas and experiment |
| Work style | Social Workstyle: deep solo focus to highly collaborative teamwork | In a typical week, mostly independent focus or frequent teamwork and discussion |
| Risk | Risk vs Stability: stable/predictable to experimental/high-upside | Choose between a secure/predictable job and an uncertain opportunity with greater potential upside |
| Structure | Process & Organization: fluid/ambiguous to clear systems and procedures | Prefer deciding how to do work yourself or following clear steps |
| Influence | Influence & Leadership: craft specialist to leading/coordinating teams | Prefer focusing on specialist work or setting direction and coordinating others |

The Big Five section asks how much the following statements describe the respondent:

**Scale:** 1 = Strongly disagree, 2 = Disagree, 3 = Neither, 4 = Agree, 5 = Strongly agree.

#### Openness and imagination

1. I have a rich vocabulary.
2. I have a vivid imagination.
3. I have excellent ideas.
4. I am quick to understand things.
5. I spend time reflecting on things.

#### Conscientiousness

1. I am always prepared.
2. I pay attention to details.
3. I get chores done right away.
4. I like order.
5. I follow a schedule.

#### Extraversion

1. I am the life of the party.
2. I feel comfortable around people.
3. I start conversations.
4. I talk to many different people at parties.
5. I am quiet around strangers.

#### Agreeableness

1. I am interested in people.
2. I sympathise with others' feelings.
3. I have a soft heart.
4. I take time out for others.
5. I feel little concern for others.

#### Emotional stability

1. I get stressed out easily.
2. I worry about things.
3. I am easily disturbed.
4. I get irritated easily.
5. I am relaxed most of the time.

The app calculates each trait's average on a 1–5 scale. It reverse-scores “I am quiet around strangers” for extraversion, “I feel little concern for others” for agreeableness, and the first four emotional-stability statements. Higher emotional-stability scores therefore mean fewer reported stress/worry reactions and greater reported calm.

Every rating and written question includes a help hint. The report's named personality type is a brief, non-clinical description derived from the Big Five self-ratings and work preferences; it is not a separate fixed personality test or diagnosis. Live reports receive the calculated trait scores and individual answers, while the demo report derives its archetype from the highest-scoring trait.

### Step 2: Behavioral patterns and decisions

Respondents are asked:

- How they make important decisions without all the facts.
- How they respond to conflict or pushback at work.
- What activities energize or drain them.
- Whether they accepted the first suitable job/education offer or compared options, and what influenced the choice.
- How they weigh higher compensation against work-life balance.
- For an example of a meaningful past trade-off and why they made that choice.

Some unanswered fields use short defaults when the form is submitted.

### Step 3: Skills, interests, and goals

Respondents provide:

- Current top skills (comma-separated).
- Hobbies and passions (comma-separated).
- Desired lifestyle, work-life balance, and compensation.
- A five-year life and career vision.

If lifestyle or vision is left blank, the app supplies a generic default for report generation.

### Step 4: Career synthesis

The app sends the collected profile to the configured model and displays the resulting career report. If no API credentials are set, it instead displays a built-in demonstration report.

## Career report

The structured report includes:

- A named personality type (archetype) and summary based on the self-reported profile.
- Core strengths and potential blind spots.
- Career paths with 0–100 fit scores.
- Reasons each path fits the respondent's personality and skills.
- Potential challenges for each path.
- Recommended skills to develop, why they matter, and suggested actions.
- An actionable 30/60/90-day plan.

The model is instructed to treat personality ratings as self-reported tendencies, consider differences between repeated preference questions as possible situational nuance, and avoid judging personal choices.

## Requirements

- Python 3.9 or newer.
- pip.
- An OpenRouter API key (or another compatible API key) for live analysis. Internet access is required for live model requests.

Dependencies are listed in [`requirements.txt`](./requirements.txt): Streamlit, Pydantic, the OpenAI Python SDK, and python-dotenv.

## Installation

Open PowerShell or a terminal in the project directory:

```powershell
cd C:\Users\arvin\source\testapp\career_advisor
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, you can invoke its Python directly without activation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configure the LLM API

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set the OpenRouter values in `.env`:

```dotenv
ANTHROPIC_BASE_URL=https://openrouter.ai/api
ANTHROPIC_AUTH_TOKEN=your_openrouter_api_key
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=openrouter/free
```

Despite the `ANTHROPIC_` variable names, the app calls OpenRouter using the OpenAI-compatible Python SDK. It adds `/v1` to the configured OpenRouter base URL, resulting in `https://openrouter.ai/api/v1`.

Alternatively, OpenAI-compatible settings are supported:

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://your-provider.example/v1
OPENAI_MODEL=your-model-name
```

When both naming schemes are present, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` take precedence over their `ANTHROPIC_` equivalents. Do not commit, publish, or share `.env`; the project `.gitignore` excludes it. Never place API keys in source code.

If neither API key variable is configured, report generation runs in demo mode. A configured but invalid key, unsupported model, or API failure is an error; the app does not silently replace a failed live request with a mock report.

## Run the app

From the project directory, with the virtual environment active:

```powershell
python -m streamlit run app.py
```

Using `python -m streamlit` works even if the standalone `streamlit` command is not on `PATH`. Open the local URL printed by Streamlit, usually <http://localhost:8501>.

## Test the API connection

Click **Test API (send hello)** in the app header. The app sends a short `hello` message to the configured model and shows its reply only if it receives a non-empty response. This makes a real API request and may use provider quota.

The API status message is not a test by itself: credentials may be present even when a request cannot succeed. If the test fails, check the key, endpoint, model name, provider account limits, and network connection.

## Saved responses and privacy

Each successful form submission updates `career_advisor_responses.txt` in the same folder as `app.py`. The file includes the current questionnaire answers and the calculated Big Five trait averages. It is plain text and is excluded from Git by `.gitignore`.

The file is overwritten with the latest accumulated answers as each form is submitted; it is not an archive of multiple assessments. The generated career report is not written to this file.

For live analysis, the profile is sent to the configured model provider. Do not enter information you are not comfortable sharing with that provider. Remove the local response file when it is no longer needed.

## Project files

```text
career_advisor/
├── app.py                # Streamlit interface, questionnaire, state, and local response saving
├── schemas.py            # Input/output Pydantic models and Big Five scoring
├── prompts.py            # System instructions and analysis prompt formatting
├── llm_service.py        # OpenAI-compatible client, API test, report request, and demo report
├── requirements.txt      # Python dependencies
├── .env.example          # Example API settings (no real credentials)
├── .gitignore            # Excludes local secrets and saved response file
└── README.md             # Setup, questionnaire, and usage guide
```

## Troubleshooting

### `streamlit` is not recognized

Run Streamlit as a Python module:

```powershell
python -m streamlit run app.py
```

### The app shows Demo Mode

Check that `.env` exists in the project directory and contains a non-empty `ANTHROPIC_AUTH_TOKEN` or `OPENAI_API_KEY`. Restart Streamlit after changing environment settings.

### The API hello test or report request fails

Confirm the API key is valid, the model name is available to your account, the base URL is correct, and your provider allows requests. The OpenRouter URL should be `https://openrouter.ai/api`; the app adds `/v1` automatically. Check the error shown by the app and the terminal running Streamlit for further details.

### Responses are not saved

Confirm that the application can write to its project folder. After submitting a form, look for `career_advisor_responses.txt` beside `app.py`. File-writing errors are displayed in the app.
