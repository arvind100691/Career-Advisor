from schemas import BIG_FIVE_QUESTIONS, UserProfilePayload

SYSTEM_PROMPT = """You are an elite, psychologist-trained Career Strategist and Executive Coach.
Your mission is to deeply analyze an individual's psychometric traits, behavioral patterns, decision-making style, current skills, hobbies, and long-term ambitions to formulate highly personalized, realistic, and high-leverage career trajectories.

Guidelines:
1. Avoid generic, vague career titles (e.g., do not just say 'Manager' or 'Consultant'). Offer concrete, modern roles (e.g., 'Product Operations Lead', 'Quantitative UX Researcher', 'Solutions Architect').
2. Provide nuanced evaluations: explain specifically *why* their personality fits, but also candidly highlight potential friction points / challenges.
3. For skill gaps, give realistic, actionable upskilling recommendations (e.g., projects, certifications, specific tooling).
4. Strictly conform to the requested JSON response schema.
5. Compare each primary psychometric rating with its differently worded consistency-check rating. Treat disagreements as useful context or situational nuance; do not assume either answer is wrong.
6. Interpret the Big Five trait scores as broad self-reported tendencies, not diagnoses or fixed labels. Higher emotional stability means fewer stress/worry responses after reverse-scoring.
7. Use past job choices and real trade-off examples as evidence of demonstrated priorities. Do not judge the user's choices or assume that one universal pay-versus-balance answer is best.
8. Give the personality_archetype a memorable, concise personality type name grounded in the Big Five scores and work preferences. Base the personality summary and career-fit reasoning on the full profile, not just the archetype name; do not present the name as a clinical or fixed identity.
"""

def format_user_prompt(profile: UserProfilePayload) -> str:
    big_five_scores = profile.big_five.trait_scores()
    big_five_item_responses = "\n".join(
        f"- {statement}: {responses[index]}/5"
        for trait, responses in profile.big_five.model_dump().items()
        for index, statement in enumerate(BIG_FIVE_QUESTIONS[trait]["items"])
    )
    return f"""Please analyze the following individual profile and generate a comprehensive Career Analysis Report:

### 1. Psychometric & Working Preferences (Scale 1 to 5):
- Analytical vs Creative: {profile.psychometrics.analytical_vs_creative}/5
- Independent vs Collaborative: {profile.psychometrics.independent_vs_collaborative}/5
- Risk Tolerance: {profile.psychometrics.risk_tolerance}/5
- Structure Preference: {profile.psychometrics.structure_preference}/5
- Leadership Drive: {profile.psychometrics.leadership_drive}/5

### 2. Rephrased Preference Checks (Scale 1 to 5):
- New-problem approach, analysis to experimentation: {profile.psychometrics.task_approach_check}/5
- Typical workday, solo focus to collaboration: {profile.psychometrics.workday_collaboration_check}/5
- Career risk, security to uncertain upside: {profile.psychometrics.career_risk_check}/5
- Work structure, flexible to process-driven: {profile.psychometrics.work_structure_check}/5
- Role preference, specialist contribution to setting direction: {profile.psychometrics.role_influence_check}/5

### 3. Big Five Personality Inventory:
- Openness and imagination: {big_five_scores['openness']:.2f}/5
- Conscientiousness: {big_five_scores['conscientiousness']:.2f}/5
- Extraversion: {big_five_scores['extraversion']:.2f}/5
- Agreeableness: {big_five_scores['agreeableness']:.2f}/5
- Emotional stability: {big_five_scores['emotional_stability']:.2f}/5
- Item responses (1 = strongly disagree and 5 = strongly agree):
{big_five_item_responses}

Reverse-score "I am quiet around strangers", "I feel little concern for others", and the first four emotional stability statements. The trait scores above already account for these reverse-keyed items.

### 4. Behavioral Patterns & Decision Making:
- Decision-Making Style: {profile.behavioral.decision_making_style}
- Conflict Resolution & Stress Response: {profile.behavioral.conflict_resolution}
- Intrinsic Motivations & Drainers: {profile.behavioral.intrinsic_motivation}
- Past Job Choice: {profile.behavioral.past_job_choice}
- Compensation vs. Work-Life Balance: {profile.behavioral.compensation_lifestyle_tradeoff}
- Meaningful Past Trade-off Example: {profile.behavioral.meaningful_tradeoff_example}

### 5. Skills, Hobbies & Aspirations:
- Current Top Skills: {', '.join(profile.skills_and_goals.top_skills) if profile.skills_and_goals.top_skills else 'None specified'}
- Hobbies & Passions: {', '.join(profile.skills_and_goals.hobbies_passions) if profile.skills_and_goals.hobbies_passions else 'None specified'}
- Desired Lifestyle / Balance / Compensation: {profile.skills_and_goals.target_salary_or_lifestyle}
- 5-Year Vision: {profile.skills_and_goals.five_year_vision}

Provide your synthesis in the structured format.
"""
