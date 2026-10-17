from datetime import datetime
from pathlib import Path

import streamlit as st
from openai import OpenAIError
from schemas import (
    UserProfilePayload,
    BIG_FIVE_QUESTIONS,
    BigFiveResponses,
    PsychometricResponses, 
    BehavioralPatterns, 
    SkillsAndGoals
)
from llm_service import (
    generate_career_analysis,
    get_openai_client,
    test_api_connection,
)

st.set_page_config(
    page_title="AI Career & Personality Strategist",
    page_icon="🧭",
    layout="wide"
)

# --- State Initialization ---
if "step" not in st.session_state:
    st.session_state.step = 1

if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "psychometrics": {
            "analytical_vs_creative": 3,
            "independent_vs_collaborative": 3,
            "risk_tolerance": 3,
            "structure_preference": 3,
            "leadership_drive": 3,
            "task_approach_check": 3,
            "workday_collaboration_check": 3,
            "career_risk_check": 3,
            "work_structure_check": 3,
            "role_influence_check": 3,
        },
        "behavioral": {
            "decision_making_style": "",
            "conflict_resolution": "",
            "intrinsic_motivation": "",
            "past_job_choice": "",
            "compensation_lifestyle_tradeoff": "",
            "meaningful_tradeoff_example": "",
        },
        "skills_and_goals": {
            "top_skills": "",
            "hobbies_passions": "",
            "target_salary_or_lifestyle": "",
            "five_year_vision": "",
        }
    }

st.session_state.user_data.setdefault(
    "big_five",
    {trait: [3] * len(section["items"]) for trait, section in BIG_FIVE_QUESTIONS.items()},
)
for trait, section in BIG_FIVE_QUESTIONS.items():
    st.session_state.user_data["big_five"].setdefault(
        trait, [3] * len(section["items"])
    )

for key in (
    "task_approach_check",
    "workday_collaboration_check",
    "career_risk_check",
    "work_structure_check",
    "role_influence_check",
):
    st.session_state.user_data["psychometrics"].setdefault(key, 3)

for key in (
    "past_job_choice",
    "compensation_lifestyle_tradeoff",
    "meaningful_tradeoff_example",
):
    st.session_state.user_data["behavioral"].setdefault(key, "")

if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None

if "api_test_message" not in st.session_state:
    st.session_state.api_test_message = None


def save_user_responses(user_data):
    psychometrics = user_data["psychometrics"]
    big_five = BigFiveResponses(**user_data["big_five"])
    big_five_scores = big_five.trait_scores()
    behavioral = user_data["behavioral"]
    skills_and_goals = user_data["skills_and_goals"]
    content = f"""Career Advisor Form Submission
Saved: {datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")}

Psychometrics (scale 1-5)
- Thinking preference (analytical to creative): {psychometrics["analytical_vs_creative"]}
- Social workstyle (independent to collaborative): {psychometrics["independent_vs_collaborative"]}
- Risk tolerance: {psychometrics["risk_tolerance"]}
- Structure preference: {psychometrics["structure_preference"]}
- Leadership drive: {psychometrics["leadership_drive"]}

Repeated questions (rephrased consistency checks)
- Problem-solving approach (analysis to experimentation): {psychometrics["task_approach_check"]}
- Preferred workday (solo focus to collaboration): {psychometrics["workday_collaboration_check"]}
- Career choice (security to uncertain upside): {psychometrics["career_risk_check"]}
- Preferred work structure (flexible to process-driven): {psychometrics["work_structure_check"]}
- Preferred role (specialist contribution to setting direction): {psychometrics["role_influence_check"]}

Big Five Personality Inventory (1 = Strongly disagree, 5 = Strongly agree)
"""
    for trait, section in BIG_FIVE_QUESTIONS.items():
        content += f"\n{section['label']} (scored trait average: {big_five_scores[trait]:.2f}/5)\n"
        for index, statement in enumerate(section["items"]):
            content += f"- {statement}: {user_data['big_five'][trait][index]}\n"

    content += f"""
Behavioral patterns
- Decision-making style: {behavioral["decision_making_style"]}
- Conflict resolution: {behavioral["conflict_resolution"]}
- Intrinsic motivation: {behavioral["intrinsic_motivation"]}
- Past job choice approach: {behavioral["past_job_choice"]}
- Compensation versus lifestyle preference: {behavioral["compensation_lifestyle_tradeoff"]}
- Example of a meaningful trade-off: {behavioral["meaningful_tradeoff_example"]}

Skills and goals
- Top skills: {skills_and_goals["top_skills"]}
- Hobbies and passions: {skills_and_goals["hobbies_passions"]}
- Desired lifestyle and compensation: {skills_and_goals["target_salary_or_lifestyle"]}
- Five-year vision: {skills_and_goals["five_year_vision"]}
"""
    output_path = Path(__file__).with_name("career_advisor_responses.txt")
    output_path.write_text(content, encoding="utf-8")
    return output_path


def persist_submitted_form():
    try:
        return save_user_responses(st.session_state.user_data)
    except OSError as error:
        st.error(f"Could not save your responses to a text file: {error}")
        st.stop()


def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def reset_all():
    st.session_state.step = 1
    st.session_state.analysis_report = None

# --- Header & Status ---
col_logo, col_stat = st.columns([3, 1])
with col_logo:
    st.title("🧭 AI Career & Personality Strategist")
    st.caption("Discover high-alignment career paths powered by psychometrics and behavioral AI analysis.")

with col_stat:
    if get_openai_client() is None:
        st.info("🟡 Demo Mode Active (No API credentials set in .env)", icon="ℹ️")
    else:
        if st.session_state.api_test_message is None:
            st.warning("LLM API connection not tested", icon="⚠️")
        elif st.session_state.api_test_message.startswith("ERROR:"):
            st.error(st.session_state.api_test_message.removeprefix("ERROR:"))
        else:
            st.success(f"✅ LLM API confirmed: {st.session_state.api_test_message}")
        if st.button("Test API (send hello)", use_container_width=True):
            try:
                st.session_state.api_test_message = test_api_connection()
            except (OpenAIError, ValueError) as error:
                st.session_state.api_test_message = f"ERROR:{error}"
            st.rerun()

# Progress bar
steps_total = 4
st.progress(st.session_state.step / steps_total)
st.write(f"**Step {st.session_state.step} of {steps_total}**")

# ==========================================
# STEP 1: Psychometrics & Working Style
# ==========================================
if st.session_state.step == 1:
    st.subheader("Step 1: Psychometrics & Behavioral Baseline")
    st.write("Rate your natural inclinations on a scale from 1 to 5.")
    
    with st.form("form_step1"):
        c1, c2 = st.columns(2)
        with c1:
            analytical_vs_creative = st.slider(
                "Thinking Preference",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["analytical_vs_creative"],
                help="1 = Highly Analytical/Data-driven | 5 = Highly Creative/Intuitive"
            )
            st.caption("1: Data & Logic  ⟵  ⟶  5: Art & Intuition")
            task_approach_check = st.slider(
                "When solving a new problem, which approach sounds more like you?",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["task_approach_check"],
                help="1 = Start with evidence and analysis | 5 = Explore ideas and experiment"
            )

            independent_vs_collaborative = st.slider(
                "Social Workstyle",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["independent_vs_collaborative"],
                help="1 = Deep solo focus | 5 = Highly collaborative team setting"
            )
            st.caption("1: Solo Contributor  ⟵  ⟶  5: Constant Collaboration")
            workday_collaboration_check = st.slider(
                "In a typical week, how much do you prefer working with others?",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["workday_collaboration_check"],
                help="1 = Mostly independent focus | 5 = Frequent teamwork and discussion"
            )

            risk_tolerance = st.slider(
                "Risk vs Stability",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["risk_tolerance"],
                help="1 = High stability & predictability | 5 = High risk, experimentation & volatility"
            )
            st.caption("1: Stable & Predictable  ⟵  ⟶  5: Experimental & High Upside")
            career_risk_check = st.slider(
                "Which job opportunity would you be more comfortable choosing?",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["career_risk_check"],
                help="1 = Secure and predictable | 5 = Uncertain but with greater potential upside"
            )

        with c2:
            structure_preference = st.slider(
                "Process & Organization",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["structure_preference"],
                help="1 = Emergent, fluid, ambiguous | 5 = Clear systems, procedures & structure"
            )
            st.caption("1: Fluid / Ambiguous  ⟵  ⟶  5: Rigorous Process")
            work_structure_check = st.slider(
                "Do you prefer deciding how to do the work yourself or following clear steps?",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["work_structure_check"],
                help="1 = Flexible approach | 5 = Clear process and defined steps"
            )

            leadership_drive = st.slider(
                "Influence & Leadership",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["leadership_drive"],
                help="1 = Craft specialist | 5 = Leading, coordinating and steering teams"
            )
            st.caption("1: Craft Specialist  ⟵  ⟶  5: Team Leadership")
            role_influence_check = st.slider(
                "Which role would feel more satisfying to you?",
                min_value=1, max_value=5,
                value=st.session_state.user_data["psychometrics"]["role_influence_check"],
                help="1 = Focus on your own specialist work | 5 = Set direction and coordinate others"
            )

        st.markdown("### Big Five Personality Test")
        st.write(
            "Rate how well each statement describes you in general, not just at work. "
            "There are no right or wrong answers; a few statements are intentionally phrased in the opposite direction."
        )
        st.caption("1 = Strongly disagree · 2 = Disagree · 3 = Neither · 4 = Agree · 5 = Strongly agree")
        big_five_answers = {}
        for trait, section in BIG_FIVE_QUESTIONS.items():
            with st.expander(section["label"], expanded=(trait == "openness")):
                big_five_answers[trait] = [
                    st.select_slider(
                        statement,
                        options=[1, 2, 3, 4, 5],
                        value=st.session_state.user_data["big_five"][trait][index],
                        key=f"big_five_{trait}_{index}",
                    )
                    for index, statement in enumerate(section["items"])
                ]

        submitted = st.form_submit_button("Save & Continue ➜", use_container_width=True)
        if submitted:
            st.session_state.user_data["psychometrics"] = {
                "analytical_vs_creative": analytical_vs_creative,
                "independent_vs_collaborative": independent_vs_collaborative,
                "risk_tolerance": risk_tolerance,
                "structure_preference": structure_preference,
                "leadership_drive": leadership_drive,
                "task_approach_check": task_approach_check,
                "workday_collaboration_check": workday_collaboration_check,
                "career_risk_check": career_risk_check,
                "work_structure_check": work_structure_check,
                "role_influence_check": role_influence_check,
            }
            st.session_state.user_data["big_five"] = big_five_answers
            persist_submitted_form()
            next_step()
            st.rerun()

# ==========================================
# STEP 2: Behavioral & Decision Making
# ==========================================
elif st.session_state.step == 2:
    st.subheader("Step 2: Decision Making & Behavioral Patterns")
    st.write("Share how you respond to real-world friction, decisions, and pressures.")

    with st.form("form_step2"):
        decision_making_style = st.text_area(
            "How do you make important decisions when you don't have all the facts?",
            value=st.session_state.user_data["behavioral"]["decision_making_style"],
            placeholder="e.g., I gather as much data as possible, consult 2-3 trusted peers, but if time runs out, I trust my gut and iterate quickly...",
            height=100
        )

        conflict_resolution = st.text_area(
            "How do you typically handle conflict or pushback at work?",
            value=st.session_state.user_data["behavioral"]["conflict_resolution"],
            placeholder="e.g., I step back to understand their core concern, decouple emotion from logic, and seek a compromise based on shared objectives...",
            height=100
        )

        intrinsic_motivation = st.text_area(
            "What activities give you energy, and what tasks drain you the fastest?",
            value=st.session_state.user_data["behavioral"]["intrinsic_motivation"],
            placeholder="e.g., Energized by: architectural problem solving, designing systems, mentoring. Drained by: repetitive bureaucracy and ambiguous meetings without agendas...",
            height=100
        )

        past_job_choice = st.text_area(
            "Think of a past job or education choice. Did you accept the first suitable offer, or compare several options before choosing? What influenced you?",
            value=st.session_state.user_data["behavioral"]["past_job_choice"],
            placeholder="For example: I accepted my first offer because stability mattered then, or I compared several roles for growth, pay, and team fit...",
            height=100
        )

        compensation_lifestyle_tradeoff = st.text_area(
            "When choosing between more money and better work-life balance, where do you usually lean? What might change your mind?",
            value=st.session_state.user_data["behavioral"]["compensation_lifestyle_tradeoff"],
            placeholder="Consider the pay difference, hours, flexibility, family needs, health, and long-term goals...",
            height=100
        )

        meaningful_tradeoff_example = st.text_area(
            "Describe another important choice where you had to trade one benefit for another. What did you choose, and why?",
            value=st.session_state.user_data["behavioral"]["meaningful_tradeoff_example"],
            placeholder="A real example helps distinguish what you say you value from what guided a decision...",
            height=100
        )

        c1, c2 = st.columns([1, 1])
        with c1:
            back_btn = st.form_submit_button("⬅ Back")
        with c2:
            submit_btn = st.form_submit_button("Save & Continue ➜", use_container_width=True)

        if back_btn:
            prev_step()
            st.rerun()
        if submit_btn:
            st.session_state.user_data["behavioral"] = {
                "decision_making_style": decision_making_style or "Prefers empirical observation and agile experimentation.",
                "conflict_resolution": conflict_resolution or "Calm, objective negotiation focusing on shared goals.",
                "intrinsic_motivation": intrinsic_motivation or "Thrives on building high-impact solutions.",
                "past_job_choice": past_job_choice or "Not provided.",
                "compensation_lifestyle_tradeoff": compensation_lifestyle_tradeoff or "Not provided.",
                "meaningful_tradeoff_example": meaningful_tradeoff_example or "Not provided.",
            }
            persist_submitted_form()
            next_step()
            st.rerun()

# ==========================================
# STEP 3: Skills, Passions & Life Goals
# ==========================================
elif st.session_state.step == 3:
    st.subheader("Step 3: Skills, Passions & Life Goals")
    st.write("Detail your tangible abilities and your personal vision for your lifestyle.")

    with st.form("form_step3"):
        top_skills_input = st.text_input(
            "Current Top Skills (comma-separated):",
            value=st.session_state.user_data["skills_and_goals"]["top_skills"],
            placeholder="Python, Public Speaking, Product Management, Financial Modeling, UI Design"
        )

        hobbies_input = st.text_input(
            "Hobbies & Organic Passions (comma-separated):",
            value=st.session_state.user_data["skills_and_goals"]["hobbies_passions"],
            placeholder="Rock climbing, Chess, Open-source contributions, Creative writing, Electronics tinkering"
        )

        lifestyle_input = st.text_input(
            "Desired Work-Life Balance & Lifestyle Targets:",
            value=st.session_state.user_data["skills_and_goals"]["target_salary_or_lifestyle"],
            placeholder="e.g., Remote-first, high autonomy, 40 hrs/week max, target $120k+ compensation"
        )

        vision_input = st.text_area(
            "Where do you envision yourself in 5 years? (Life & Career)",
            value=st.session_state.user_data["skills_and_goals"]["five_year_vision"],
            placeholder="e.g., Leading a technical product or running my own specialized agency with location freedom...",
            height=100
        )

        c1, c2 = st.columns([1, 1])
        with c1:
            back_btn = st.form_submit_button("⬅ Back")
        with c2:
            submit_btn = st.form_submit_button("🚀 Generate Career Synthesis", use_container_width=True)

        if back_btn:
            prev_step()
            st.rerun()
        if submit_btn:
            st.session_state.user_data["skills_and_goals"] = {
                "top_skills": top_skills_input,
                "hobbies_passions": hobbies_input,
                "target_salary_or_lifestyle": lifestyle_input or "Flexible, competitive compensation with healthy work-life balance.",
                "five_year_vision": vision_input or "Established leader in my domain with creative and financial freedom.",
            }
            persist_submitted_form()
            next_step()
            st.rerun()

# ==========================================
# STEP 4: Synthesis & Career Insights
# ==========================================
elif st.session_state.step == 4:
    st.subheader("Step 4: Personalized Career & Personality Blueprint")
    
    # Check if analysis has already been computed
    if st.session_state.analysis_report is None:
        with st.spinner("🤖 Synthesizing psychometrics, behavioral patterns, and market demands..."):
            # Construct Payload
            raw_skills = [s.strip() for s in st.session_state.user_data["skills_and_goals"]["top_skills"].split(",") if s.strip()]
            raw_hobbies = [h.strip() for h in st.session_state.user_data["skills_and_goals"]["hobbies_passions"].split(",") if h.strip()]
            
            payload = UserProfilePayload(
                psychometrics=PsychometricResponses(**st.session_state.user_data["psychometrics"]),
                big_five=BigFiveResponses(**st.session_state.user_data["big_five"]),
                behavioral=BehavioralPatterns(**st.session_state.user_data["behavioral"]),
                skills_and_goals=SkillsAndGoals(
                    top_skills=raw_skills,
                    hobbies_passions=raw_hobbies,
                    target_salary_or_lifestyle=st.session_state.user_data["skills_and_goals"]["target_salary_or_lifestyle"],
                    five_year_vision=st.session_state.user_data["skills_and_goals"]["five_year_vision"]
                )
            )
            try:
                st.session_state.analysis_report = generate_career_analysis(payload)
            except OpenAIError:
                st.error("The LLM API request failed. Check your OpenRouter API key, endpoint, model, and account limits, then try again.")
                st.stop()

    report = st.session_state.analysis_report

    # --- Render Synthesis ---
    st.markdown(f"### Archetype: **{report.personality_archetype}**")
    st.info(report.personality_summary)

    col_str, col_blind = st.columns(2)
    with col_str:
        st.markdown("#### ⚡ Core Superpowers")
        for s in report.core_strengths:
            st.markdown(f"- **{s}**")
    
    with col_blind:
        st.markdown("#### ⚠️ Watch-outs & Blind Spots")
        for b in report.blind_spots:
            st.markdown(f"- {b}")

    st.markdown("---")
    st.subheader("🎯 Tailored Career Options")

    for i, career in enumerate(report.career_paths):
        with st.expander(f"**{i+1}. {career.role_title}** — Alignment Score: `{career.fit_score}%`", expanded=(i==0)):
            c_score, c_desc = st.columns([1, 4])
            with c_score:
                st.metric("Match Fit", f"{career.fit_score}%")
            with c_desc:
                st.markdown(f"**Why Personality Fits:** {career.why_it_fits_personality}")
                st.markdown(f"**How Skills Align:** {career.why_it_fits_skills}")
                st.markdown(f"**Potential Friction / Challenges:** *{career.potential_challenges}*")

            st.markdown("##### 📚 Recommended Skill Upgrades")
            for skill in career.recommended_skills_to_learn:
                st.markdown(f"- **{skill.skill_name}**: {skill.why_needed}")
                st.caption(f"↳ Action Plan: {skill.recommended_action}")

    st.markdown("---")
    st.subheader("🗓️ 30 / 60 / 90-Day Execution Roadmap")
    for milestone in report.immediate_30_60_90_plan:
        st.markdown(f"- {milestone}")

    st.markdown("<br>", unsafe_allow_html=True)
    c_restart, _ = st.columns([1, 3])
    with c_restart:
        if st.button("🔄 Start New Assessment", use_container_width=True):
            reset_all()
            st.rerun()
