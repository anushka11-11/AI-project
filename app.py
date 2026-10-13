import random
import time
import html

import streamlit as st
from questions import questions

st.set_page_config(
    page_title="MindSprint | AI Quiz",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TOTAL_QUESTIONS = 50
QUIZ_TIME = 20 * 60
POINTS_PER_QUESTION = 2

if len(questions) != TOTAL_QUESTIONS:
    st.error(
        f"The quiz must contain exactly {TOTAL_QUESTIONS} questions, "
        f"but questions.py contains {len(questions)}."
    )
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(135deg, #0b1020 0%, #14152f 55%, #21153b 100%);
    color: #f4f4ff;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}
header[data-testid="stHeader"] {
    background: transparent;
}
h1, h2, h3, p, label {
    color: #f4f4ff;
}
.hero {
    padding: 28px 30px;
    border: 1px solid #38345f;
    border-radius: 22px;
    background: linear-gradient(120deg, #25234b, #171b36 65%, #31204b);
    margin-bottom: 22px;
}
.hero h1 {
    font-size: 38px;
    font-weight: 800;
    margin: 0;
}
.hero p {
    color: #c2c6e6;
    margin-top: 8px;
    margin-bottom: 0;
}
.metric-card {
    padding: 16px;
    border-radius: 16px;
    background: #191d37;
    border: 1px solid #303657;
    min-height: 91px;
}
.metric-label {
    color: #aeb5d9;
    font-size: 12px;
    letter-spacing: .7px;
}
.metric-value {
    color: #fff;
    font-size: 26px;
    font-weight: 800;
    margin-top: 5px;
}
.question-card {
    background: #171b34;
    border: 1px solid #343858;
    padding: 25px;
    border-radius: 20px;
    margin: 15px 0;
}
.tag {
    color: #c8b8ff;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.question-text {
    color: #fff;
    font-size: 21px;
    font-weight: 650;
    line-height: 1.55;
    margin-top: 12px;
}
.feedback-correct {
    padding: 17px;
    background: #12372f;
    border: 1px solid #24775d;
    border-radius: 13px;
}
.feedback-wrong {
    padding: 17px;
    background: #3a202d;
    border: 1px solid #874052;
    border-radius: 13px;
}
.small-note {
    color: #b7bddb;
    font-size: 13px;
}
div.stButton > button {
    border-radius: 11px;
    font-weight: 650;
    min-height: 43px;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #8b5cf6, #6d5dfc);
    color: white;
    border: none;
}
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #9b72ff, #62d6e7);
}
</style>
""", unsafe_allow_html=True)


def initialise_state():
    defaults = {
        "started": False,
        "finished": False,
        "question_order": [],
        "current": 0,
        "answers": {},
        "feedback": {},
        "hints_used": set(),
        "fifty_used": set(),
        "hidden_options": {},
        "start_time": None,
        "deadline": None,
        "player_name": "Player",
        "finish_confirm": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            if isinstance(value, (dict, list, set)):
                st.session_state[key] = value.copy()
            else:
                st.session_state[key] = value


initialise_state()


def start_quiz():
    st.session_state.started = True
    st.session_state.finished = False
    st.session_state.question_order = random.sample(
        questions, TOTAL_QUESTIONS
    )
    st.session_state.current = 0
    st.session_state.answers = {}
    st.session_state.feedback = {}
    st.session_state.hints_used = set()
    st.session_state.fifty_used = set()
    st.session_state.hidden_options = {}
    st.session_state.start_time = time.time()
    st.session_state.deadline = time.time() + QUIZ_TIME
    st.session_state.finish_confirm = False


def calculate_score():
    correct = sum(
        1
        for q in st.session_state.question_order
        if st.session_state.answers.get(q["id"]) == q["answer"]
    )
    return correct * POINTS_PER_QUESTION, correct


def remaining_time():
    if not st.session_state.deadline:
        return QUIZ_TIME
    return max(0, int(st.session_state.deadline - time.time()))


def format_time(seconds):
    minutes, seconds = divmod(max(0, seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


@st.fragment(run_every="1s")
def countdown_card():
    left = remaining_time()

    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">TIME LEFT</div>'
        f'<div class="metric-value">{format_time(left)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if (
        left <= 0
        and st.session_state.started
        and not st.session_state.finished
    ):
        st.session_state.finished = True
        st.rerun()


def go_to(index):
    st.session_state.current = max(
        0, min(index, TOTAL_QUESTIONS - 1)
    )
    st.session_state.finish_confirm = False


def show_results():
    score, correct = calculate_score()
    attempted = len(st.session_state.answers)
    accuracy = correct / attempted * 100 if attempted else 0
    percentage = correct / TOTAL_QUESTIONS * 100
    unanswered = TOTAL_QUESTIONS - attempted

    st.markdown(
        f"""
        <div class="hero">
            <div class="tag">QUIZ COMPLETED</div>
            <h1>Results, {html.escape(st.session_state.player_name)}!</h1>
            <p>Review your performance and see which AI concepts you can strengthen.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    cards = [
        ("TOTAL SCORE", f"{score}/{TOTAL_QUESTIONS * POINTS_PER_QUESTION}"),
        ("CORRECT", f"{correct}/{TOTAL_QUESTIONS}"),
        ("ACCURACY OF ATTEMPTED", f"{accuracy:.1f}%"),
        ("UNANSWERED", str(unanswered)),
    ]

    for col, (label, value) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.progress(percentage / 100)

    if percentage >= 85:
        st.success("Excellent work! You have a strong grasp of these concepts.")
    elif percentage >= 65:
        st.info("Good effort! Review the missed questions to strengthen your understanding.")
    else:
        st.warning("Keep practising. Use the explanations below to revise important concepts.")

    st.subheader("Topic-wise performance")

    topic_stats = {}

    for q in st.session_state.question_order:
        topic = q["topic"]
        topic_stats.setdefault(topic, {"correct": 0, "total": 0})
        topic_stats[topic]["total"] += 1

        if st.session_state.answers.get(q["id"]) == q["answer"]:
            topic_stats[topic]["correct"] += 1

    for topic, values in sorted(topic_stats.items()):
        st.write(
            f'**{topic}** — {values["correct"]}/{values["total"]} correct'
        )
        st.progress(
            values["correct"] / values["total"]
            if values["total"] else 0
        )

    st.subheader("Review your answers")

    for index, q in enumerate(st.session_state.question_order, start=1):
        selected = st.session_state.answers.get(q["id"])
        is_correct = selected == q["answer"]

        if selected is None:
            label = f"⬜ Q{index}. Not answered — {q['question'][:75]}"
        else:
            symbol = "✅" if is_correct else "❌"
            label = f"{symbol} Q{index}. {q['question'][:75]}"

        with st.expander(label):
            st.write(f"**Topic:** {q['topic']}")
            st.write(f"**Type:** {q['type']}")
            st.write(
                f"**Your answer:** {selected if selected is not None else 'Not answered'}"
            )
            st.write(f"**Correct answer:** {q['answer']}")
            st.write(f"**Explanation:** {q['explanation']}")

    if st.button("🔄 Play Again", type="primary", use_container_width=True):
        start_quiz()
        st.rerun()


if not st.session_state.started:
    st.markdown("""
    <div class="hero">
        <div class="tag">ARTIFICIAL INTELLIGENCE • UNITS I & II</div>
        <h1>MindSprint 🧠</h1>
        <p>Think logically. Search intelligently. Solve the challenge.</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.4, 1])

    with left:
        st.markdown("### Ready to test your AI concepts?")
        st.write(
            "Explore intelligent agents, environments, problem formulation, "
            "state-space search, heuristics, hill climbing, constraint "
            "satisfaction, production systems and means-end analysis."
        )

        st.markdown("#### Included question formats")
        st.write(
            "MCQs · True/False · Assertion–Reason · Fill in the Blank · "
            "Match the Following · Scenarios · Search Problems"
        )

        name = st.text_input("Enter your player name", value="Player")
        st.session_state.player_name = name.strip() or "Player"

        if st.button(
            "🚀 Start Quiz",
            type="primary",
            use_container_width=True,
        ):
            start_quiz()
            st.rerun()

    with right:
        st.markdown("""
        <div class="question-card">
            <div class="tag">YOUR MISSION</div>
            <h2>50 Questions</h2>
            <p>Test understanding, not just memorisation.</p>
            <hr>
            <p>⏱️ 20-minute overall timer</p>
            <p>🎯 100 possible points</p>
            <p>💡 Hints available</p>
            <p>✂️ 50:50 for eligible multiple-choice questions</p>
            <p>↩️ Skip questions and return later</p>
            <p>📊 Topic-wise results</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.finished:
    show_results()

else:
    if remaining_time() <= 0:
        st.session_state.finished = True
        st.rerun()

    index = st.session_state.current
    q = st.session_state.question_order[index]
    qid = q["id"]
    answered = qid in st.session_state.answers

    score, correct = calculate_score()
    attempted = len(st.session_state.answers)
    progress = attempted / TOTAL_QUESTIONS

    st.markdown(
        f"""
        <div class="hero">
            <div class="tag">PLAYER: {html.escape(st.session_state.player_name)}</div>
            <h1>MindSprint: AI Quiz</h1>
            <p>Answer now, or skip and return to this question before finishing.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">QUESTION</div>'
            f'<div class="metric-value">{index + 1}/{TOTAL_QUESTIONS}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">CURRENT SCORE</div>'
            f'<div class="metric-value">{score}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with m3:
        countdown_card()

    st.progress(progress)

    st.markdown(
        f"""
        <div class="question-card">
            <div class="tag">
                {html.escape(q['topic'])} · {html.escape(q['type'])} ·
                {html.escape(q['difficulty'])}
            </div>
            <div class="question-text">{html.escape(q['question'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if qid in st.session_state.hints_used:
        st.info(f"💡 Hint: {q['hint']}")

    hidden = st.session_state.hidden_options.get(qid, [])
    visible_options = [
        option for option in q["options"] if option not in hidden
    ]
    answer_key = f"answer_{qid}"

    if answered:
        selected = st.session_state.answers[qid]
        st.radio(
            "Your answer",
            q["options"],
            index=q["options"].index(selected),
            key=f"locked_{qid}",
            disabled=True,
        )
    else:
        current_selection = st.session_state.get(answer_key)

        if current_selection not in visible_options:
            current_selection = None

        selected = st.radio(
            "Choose your answer",
            visible_options,
            index=(
                visible_options.index(current_selection)
                if current_selection is not None else None
            ),
            key=answer_key,
        )

    action1, action2, action3 = st.columns(3)

    with action1:
        if not answered and st.button(
            "💡 Show Hint", use_container_width=True
        ):
            st.session_state.hints_used.add(qid)
            st.rerun()

    with action2:
        eligible_for_fifty = len(q["options"]) > 2

        if (
            not answered
            and eligible_for_fifty
            and qid not in st.session_state.fifty_used
        ):
            if st.button("✂️ 50:50 Lifeline", use_container_width=True):
                wrong_options = [
                    option for option in q["options"]
                    if option != q["answer"]
                ]
                remove_count = min(2, len(wrong_options))
                removed = random.sample(wrong_options, remove_count)

                st.session_state.hidden_options[qid] = removed
                st.session_state.fifty_used.add(qid)

                if st.session_state.get(answer_key) in removed:
                    st.session_state.pop(answer_key, None)

                st.rerun()

    with action3:
        if not answered and st.button(
            "Submit Answer",
            type="primary",
            use_container_width=True,
        ):
            if selected is None:
                st.warning("Please select an answer first, or use Skip & Next.")
            else:
                st.session_state.answers[qid] = selected
                st.session_state.feedback[qid] = selected == q["answer"]
                st.rerun()

    if answered:
        if st.session_state.feedback.get(qid, False):
            st.markdown(
                f'<div class="feedback-correct"><b>✅ Correct!</b><br>'
                f'+{POINTS_PER_QUESTION} points</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="feedback-wrong"><b>❌ Not quite.</b><br>'
                f'Correct answer: <b>{html.escape(q["answer"])}</b></div>',
                unsafe_allow_html=True,
            )

        st.write(f"**Explanation:** {q['explanation']}")

    st.markdown("### Question navigator")
    st.caption(
        "Select any question number to move around. Unanswered questions "
        "can be revisited at any time before you finish."
    )

    nav_cols = st.columns(10)

    for n in range(TOTAL_QUESTIONS):
        with nav_cols[n % 10]:
            nav_qid = st.session_state.question_order[n]["id"]

            if nav_qid in st.session_state.answers:
                label = f"✓ {n + 1}"
            elif n == index:
                label = f"• {n + 1}"
            else:
                label = str(n + 1)

            if st.button(
                label,
                key=f"jump_{n}",
                use_container_width=True,
            ):
                go_to(n)
                st.rerun()

    st.markdown("---")
    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        if st.button(
            "← Previous",
            disabled=(index == 0),
            use_container_width=True,
        ):
            go_to(index - 1)
            st.rerun()

    with nav2:
        if index < TOTAL_QUESTIONS - 1:
            if st.button(
                "Skip & Next →",
                type="secondary",
                use_container_width=True,
            ):
                go_to(index + 1)
                st.rerun()
        else:
            if st.button(
                "Finish Quiz",
                type="primary",
                use_container_width=True,
            ):
                unanswered = TOTAL_QUESTIONS - len(st.session_state.answers)

                if unanswered:
                    st.session_state.finish_confirm = True
                else:
                    st.session_state.finished = True

                st.rerun()

    with nav3:
        if index < TOTAL_QUESTIONS - 1:
            if st.button(
                "Next →",
                type="primary",
                use_container_width=True,
            ):
                go_to(index + 1)
                st.rerun()
        else:
            if st.button("Review & Finish", use_container_width=True):
                st.session_state.finish_confirm = True
                st.rerun()

    if st.session_state.finish_confirm:
        unanswered = TOTAL_QUESTIONS - len(st.session_state.answers)

        st.warning(
            f"You still have {unanswered} unanswered question(s). "
            "Finish now, or go back and answer them."
        )

        confirm1, confirm2 = st.columns(2)

        with confirm1:
            if st.button(
                "Finish and See Results",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.finished = True
                st.session_state.finish_confirm = False
                st.rerun()

        with confirm2:
            if st.button("Return to Quiz", use_container_width=True):
                st.session_state.finish_confirm = False
                st.rerun()

    unanswered = TOTAL_QUESTIONS - len(st.session_state.answers)

    st.markdown(
        f'<p class="small-note">{attempted}/{TOTAL_QUESTIONS} answered · '
        f'{unanswered} unanswered · {correct} correct</p>',
        unsafe_allow_html=True,
    )