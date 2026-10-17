from typing import Annotated, List, Optional
from pydantic import BaseModel, Field

# --- User Input Models ---

Rating = Annotated[int, Field(ge=1, le=5)]

BIG_FIVE_QUESTIONS = {
    "openness": {
        "label": "Openness and imagination",
        "items": [
            "I have a rich vocabulary.",
            "I have a vivid imagination.",
            "I have excellent ideas.",
            "I am quick to understand things.",
            "I spend time reflecting on things.",
        ],
    },
    "conscientiousness": {
        "label": "Conscientiousness",
        "items": [
            "I am always prepared.",
            "I pay attention to details.",
            "I get chores done right away.",
            "I like order.",
            "I follow a schedule.",
        ],
    },
    "extraversion": {
        "label": "Extraversion",
        "items": [
            "I am the life of the party.",
            "I feel comfortable around people.",
            "I start conversations.",
            "I talk to many different people at parties.",
            "I am quiet around strangers.",
        ],
    },
    "agreeableness": {
        "label": "Agreeableness",
        "items": [
            "I am interested in people.",
            "I sympathise with others' feelings.",
            "I have a soft heart.",
            "I take time out for others.",
            "I feel little concern for others.",
        ],
    },
    "emotional_stability": {
        "label": "Emotional stability",
        "items": [
            "I get stressed out easily.",
            "I worry about things.",
            "I am easily disturbed.",
            "I get irritated easily.",
            "I am relaxed most of the time.",
        ],
    },
}


class BigFiveResponses(BaseModel):
    openness: List[Rating] = Field(min_length=5, max_length=5)
    conscientiousness: List[Rating] = Field(min_length=5, max_length=5)
    extraversion: List[Rating] = Field(min_length=5, max_length=5)
    agreeableness: List[Rating] = Field(min_length=5, max_length=5)
    emotional_stability: List[Rating] = Field(min_length=5, max_length=5)

    def trait_scores(self) -> dict[str, float]:
        reverse_keyed_items = {
            "extraversion": {4},
            "agreeableness": {4},
            "emotional_stability": {0, 1, 2, 3},
        }
        scores = {}
        for trait, responses in self.model_dump().items():
            reverse_items = reverse_keyed_items.get(trait, set())
            adjusted = [
                6 - response if index in reverse_items else response
                for index, response in enumerate(responses)
            ]
            scores[trait] = sum(adjusted) / len(adjusted)
        return scores


class PsychometricResponses(BaseModel):
    analytical_vs_creative: int = Field(description="1 (Analytical) to 5 (Creative)", ge=1, le=5)
    independent_vs_collaborative: int = Field(description="1 (Independent) to 5 (Collaborative)", ge=1, le=5)
    risk_tolerance: int = Field(description="1 (Low Risk/Stable) to 5 (High Risk/Dynamic)", ge=1, le=5)
    structure_preference: int = Field(description="1 (Fluid/Ambiguous) to 5 (Strict Process/Organized)", ge=1, le=5)
    leadership_drive: int = Field(description="1 (Individual Contributor) to 5 (Lead/Drive Teams)", ge=1, le=5)
    task_approach_check: int = Field(description="Rephrased analytical-creative preference: 1 (evidence and analysis) to 5 (ideas and experimentation)", ge=1, le=5)
    workday_collaboration_check: int = Field(description="Rephrased independent-collaborative preference: 1 (mostly solo focus) to 5 (frequent collaboration)", ge=1, le=5)
    career_risk_check: int = Field(description="Rephrased risk preference in a career context: 1 (secure and predictable) to 5 (uncertain with greater upside)", ge=1, le=5)
    work_structure_check: int = Field(description="Rephrased structure preference: 1 (flexible approach) to 5 (clear process and steps)", ge=1, le=5)
    role_influence_check: int = Field(description="Rephrased leadership preference: 1 (focus on own specialist work) to 5 (set direction for others)", ge=1, le=5)

class BehavioralPatterns(BaseModel):
    decision_making_style: str = Field(description="How decisions are made under pressure or uncertainty")
    conflict_resolution: str = Field(description="How user handles disagreement or friction")
    intrinsic_motivation: str = Field(description="What truly energizes or drains them during work")
    past_job_choice: str = Field(description="How the user approached an earlier job choice, including whether they accepted the first offer or compared options")
    compensation_lifestyle_tradeoff: str = Field(description="How the user weighs higher compensation against work-life balance")
    meaningful_tradeoff_example: str = Field(description="A real past choice where the user balanced competing priorities and what drove the decision")

class SkillsAndGoals(BaseModel):
    top_skills: List[str] = Field(description="Hard and soft skills currently mastered")
    hobbies_passions: List[str] = Field(description="Activities enjoyed outside of work")
    target_salary_or_lifestyle: str = Field(description="Work-life balance, remote preference, or financial targets")
    five_year_vision: str = Field(description="Where they want to be in 5 years")

class UserProfilePayload(BaseModel):
    psychometrics: PsychometricResponses
    big_five: BigFiveResponses
    behavioral: BehavioralPatterns
    skills_and_goals: SkillsAndGoals

# --- LLM Output Schemas ---

class SkillRecommendation(BaseModel):
    skill_name: str = Field(description="Name of the skill to acquire or sharpen")
    why_needed: str = Field(description="Why this skill is crucial for this career trajectory")
    recommended_action: str = Field(description="Course, project, certification, or concrete practice suggestion")

class CareerPath(BaseModel):
    role_title: str = Field(description="Specific, industry-recognized title")
    fit_score: int = Field(description="Overall alignment score from 0 to 100", ge=0, le=100)
    why_it_fits_personality: str = Field(description="How it aligns with their psychometrics and behavioral tendencies")
    why_it_fits_skills: str = Field(description="How it leverages their current skills and interests")
    potential_challenges: str = Field(description="Potential friction points or downsides given their traits")
    recommended_skills_to_learn: List[SkillRecommendation] = Field(description="Key skills to bridge the gap")

class CareerAnalysisReport(BaseModel):
    personality_archetype: str = Field(description="A memorable, concise, non-clinical personality type name grounded in the user's Big Five traits and work preferences (e.g., 'The Strategic Innovator')")
    personality_summary: str = Field(description="Comprehensive synthesis of their behavioral and cognitive traits")
    core_strengths: List[str] = Field(description="Top 3 to 5 superpower traits")
    blind_spots: List[str] = Field(description="Potential blind spots to watch out for")
    career_paths: List[CareerPath] = Field(description="Top 3-4 recommended career paths")
    immediate_30_60_90_plan: List[str] = Field(description="Concrete milestones for the next 30, 60, and 90 days")
