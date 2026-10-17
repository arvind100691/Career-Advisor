import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from schemas import (
    UserProfilePayload, 
    CareerAnalysisReport, 
    CareerPath, 
    SkillRecommendation
)
from prompts import SYSTEM_PROMPT, format_user_prompt

load_dotenv()

def get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
    if not api_key or api_key.strip() == "" or "your_" in api_key.lower():
        return None

    base_url = os.getenv("OPENAI_BASE_URL")
    if not base_url:
        base_url = os.getenv("ANTHROPIC_BASE_URL")
        if base_url:
            base_url = base_url.rstrip("/")
            if not base_url.endswith("/v1"):
                base_url += "/v1"

    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def get_model_name() -> str:
    return os.getenv("OPENAI_MODEL") or os.getenv("ANTHROPIC_MODEL", "gpt-4o-mini")


def _personality_archetype(scores: dict[str, float]) -> str:
    archetypes = {
        "openness": "The Curious Explorer",
        "conscientiousness": "The Intentional Builder",
        "extraversion": "The Social Connector",
        "agreeableness": "The Considerate Collaborator",
        "emotional_stability": "The Steady Navigator",
    }
    leading_trait = max(scores, key=scores.get)
    if scores[leading_trait] < 3.5:
        return "The Balanced Generalist"
    return archetypes[leading_trait]


def test_api_connection() -> str:
    client = get_openai_client()
    if client is None:
        raise ValueError("No LLM API credentials are configured.")

    response = client.chat.completions.create(
        model=get_model_name(),
        messages=[
            {"role": "user", "content": "hello"}
        ],
        max_tokens=16,
    )
    if not response.choices:
        raise ValueError("The LLM API responded without any choices.")
    reply = response.choices[0].message.content
    if not reply or not reply.strip():
        raise ValueError("The LLM API responded but returned an empty reply.")
    return reply.strip()


def generate_mock_report(profile: UserProfilePayload) -> CareerAnalysisReport:
    """Generates a realistic mock report when no API key is provided, enabling instant prototype demonstration."""
    skills_preview = ", ".join(profile.skills_and_goals.top_skills[:3]) if profile.skills_and_goals.top_skills else "problem solving"
    big_five_scores = profile.big_five.trait_scores()
    leading_trait = max(big_five_scores, key=big_five_scores.get)
    personality_signal = (
        f"Your {leading_trait.replace('_', ' ')} is your highest relative Big Five trait "
        f"({big_five_scores[leading_trait]:.1f}/5)."
    )
    personality_summary = ", ".join(
        f"{trait.replace('_', ' ')} {score:.1f}/5"
        for trait, score in big_five_scores.items()
    )
    
    return CareerAnalysisReport(
        personality_archetype=_personality_archetype(big_five_scores),
        personality_summary=(
            f"Your Big Five self-ratings are: {personality_summary}. "
            f"{personality_signal} "
            f"Alongside an analytical-to-creative preference of {profile.psychometrics.analytical_vs_creative}/5, "
            "these broad tendencies can help identify work environments to explore; they are not a diagnosis "
            "or a fixed description of who you are."
        ),
        core_strengths=[
            "High accountability in ambiguous environments",
            "Synthesizing qualitative feedback into technical requirements",
            "Pragmatic risk management and thoughtful stakeholder communication"
        ],
        blind_spots=[
            "May over-index on process refinement before shipping minimum viable prototypes",
            "Tendency to shoulder tasks independently rather than delegating early"
        ],
        career_paths=[
            CareerPath(
                role_title="Technical Product Manager / Systems Strategist",
                fit_score=92,
                why_it_fits_personality=f"Balances structured requirements with cross-functional leadership. {personality_signal}",
                why_it_fits_skills=f"Directly leverages your background in {skills_preview} while giving room to steer high-level product strategy.",
                potential_challenges="Requires managing executive stakeholder conflict without formal authority.",
                recommended_skills_to_learn=[
                    SkillRecommendation(
                        skill_name="System Architecture & API Design Concepts",
                        why_needed="To communicate seamlessly between engineering squads and business leadership.",
                        recommended_action="Complete an end-to-end Microservices & API design course or build an integrated side project."
                    ),
                    SkillRecommendation(
                        skill_name="Data-Driven Metric Instrumentation (SQL & Mixpanel)",
                        why_needed="To substantiate product prioritization decisions with empirical usage metrics.",
                        recommended_action="Execute 3 case studies tracking user funnels and retention dashboards."
                    )
                ]
            ),
            CareerPath(
                role_title="Operations & Solutions Architect",
                fit_score=88,
                why_it_fits_personality=f"Can suit a preference for clear systems and workflow improvement. {personality_signal}",
                why_it_fits_skills=f"Applies your skills in {skills_preview} to eliminate organizational bottlenecks.",
                potential_challenges="Can sometimes feel reactive if leadership priorities shift rapidly.",
                recommended_skills_to_learn=[
                    SkillRecommendation(
                        skill_name="Workflow Automation (Zapier, Python, Low-Code APIs)",
                        why_needed="Automates repetitive enterprise operational tasks rapidly.",
                        recommended_action="Automate a real end-to-end data pipeline between customer touchpoints."
                    )
                ]
            ),
            CareerPath(
                role_title="Specialized Technical Consultant / Advisor",
                fit_score=84,
                why_it_fits_personality=f"Offers autonomy, project variety, and continuous learning. {personality_signal}",
                why_it_fits_skills="Allows monetizing your deepest core skills across multiple industry verticals.",
                potential_challenges="Requires proactive client pipeline management and handling variable scopes.",
                recommended_skills_to_learn=[
                    SkillRecommendation(
                        skill_name="Consultative Selling & Scope Discovery",
                        why_needed="Crucial to diagnosing customer problems before proposing solutions.",
                        recommended_action="Practice conducting structured user discovery interviews and proposals."
                    )
                ]
            )
        ],
        immediate_30_60_90_plan=[
            "Day 1-30: Audit your existing portfolio or resume to highlight systems-level outcomes; begin target upskilling course.",
            "Day 31-60: Build one tangible capstone project showcasing your new skill set and publish a detailed walkthrough.",
            "Day 61-90: Connect with 5-10 practitioners in target roles for informational chats and begin applying to prioritized positions."
        ]
    )

def generate_career_analysis(profile: UserProfilePayload) -> CareerAnalysisReport:
    client = get_openai_client()
    
    # Use mock mode only when no API credentials are configured.
    if not client:
        return generate_mock_report(profile)
    
    user_prompt = format_user_prompt(profile)
    
    response = client.beta.chat.completions.parse(
        model=get_model_name(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format=CareerAnalysisReport,
        temperature=0.7
    )
    report = response.choices[0].message.parsed
    if report is None:
        raise ValueError("The LLM API returned no structured career report.")
    return report
