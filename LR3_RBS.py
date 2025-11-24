import streamlit as st
import json
from typing import Any, Dict, List, Tuple

RULES_JSON = """[
{
"name": "Top merit candidate", "priority": 100,
"conditions": [ ["cgpa", ">=", 3.7],
["co_curricular_score", ">=", 80],
["family_income", "<=", 8000],
["disciplinary_actions", "==", 0]
],
"action": {
"decision": "AWARD_FULL",
"reason": "Excellent academic & co-curricular performance, with acceptable need"
}
},
{
"name": "Good candidate - partial scholarship", "priority": 80,
"conditions": [ ["cgpa", ">=", 3.3],
["co_curricular_score", ">=", 60],
["family_income", "<=", 12000],
["disciplinary_actions", "<=", 1]
],
"action": {
"decision": "AWARD_PARTIAL",
"reason": "Good academic & involvement record with moderate need"
}
},
{
"name": "Need-based review", "priority": 70, "conditions": [
["cgpa", ">=", 2.5],
["family_income", "<=", 4000]
],
"action": { "decision": "REVIEW",
"reason": "High need but borderline academic score"
}
},
{
"name": "Low CGPA – not eligible", "priority": 95,
"conditions": [ ["cgpa", "<", 2.5]
],
"action": { "decision": "REJECT",
"reason": "CGPA below minimum scholarship requirement"
 
}
},
{
"name": "Serious disciplinary record", "priority": 90,
"conditions": [ ["disciplinary_actions", ">=", 2]
],
"action": { "decision": "REJECT",
"reason": "Too many disciplinary records"
}
}
]"""

# Parse rules
RULES = json.loads(RULES_JSON)

def eval_condition(value: Any, op: str, target: Any) -> bool:
    """
    Evaluate condition value op target.
    Supported ops: '>=', '<=', '>', '<', '=='
    """
    try:
        if op == ">=":
            return value >= target
        if op == "<=":
            return value <= target
        if op == ">":
            return value > target
        if op == "<":
            return value < target
        if op == "==":
            return value == target
    except Exception:
        return False
    return False

def evaluate_rules(applicant: Dict[str, Any], rules: List[Dict]) -> Tuple[Dict, List[Dict]]:
    """
    Evaluate rules against applicant.
    Returns (selected_action, matched_rules_list)
    - selected_action is the action dict of the highest-priority matched rule, or default decision if none matched.
    - matched_rules_list is the list of matched rule dicts (sorted by priority desc).
    """
    matched = []
    for rule in rules:
        all_true = True
        for cond in rule.get("conditions", []):
            field, op, target = cond
            # get applicant value; if missing, fail the condition
            if field not in applicant:
                all_true = False
                break
            value = applicant[field]
            if not eval_condition(value, op, target):
                all_true = False
                break
        if all_true:
            matched.append(rule)

    # sort matched rules by priority descending
    matched_sorted = sorted(matched, key=lambda r: r.get("priority", 0), reverse=True)
    if matched_sorted:
        selected = matched_sorted[0]["action"]
    else:
        selected = {
            "decision": "NO_MATCH",
            "reason": "No rule matched. Candidate requires manual review or different policy."
        }
    return selected, matched_sorted

st.set_page_config(page_title="Scholarship Advisory (Rule-based)", layout="centered")
st.title("Scholarship Advisory — Rule-based System")

st.markdown("Enter applicant data below and the system will evaluate the rules (exact JSON rules embedded).")

with st.form("applicant_form"):
    st.subheader("Applicant information")
    col1, col2 = st.columns(2)
    with col1:
        cgpa = st.number_input("CGPA", min_value=0.0, max_value=4.0, value=3.0, step=0.01, format="%.2f")
        co_curricular_score = st.number_input("Co-curricular score (0-100)", min_value=0, max_value=100, value=50, step=1)
    with col2:
        family_income = st.number_input("Family monthly income (RM)", min_value=0.0, value=10000.0, step=100.0, format="%.2f")
        disciplinary_actions = st.number_input("Number of disciplinary actions", min_value=0, value=0, step=1)

    submitted = st.form_submit_button("Evaluate")

if submitted:
    applicant = {
        "cgpa": float(cgpa),
        "co_curricular_score": int(co_curricular_score),
        "family_income": float(family_income),
        "disciplinary_actions": int(disciplinary_actions)
    }

    selected_action, matched_rules = evaluate_rules(applicant, RULES)

    st.markdown("### Result")
    st.write("**Decision:**", selected_action["decision"])
    st.write("**Reason:**", selected_action.get("reason", ""))

    st.markdown("### Matched rules (in priority order)")
    if matched_rules:
        for r in matched_rules:
            st.write(f"- **{r['name']}** (priority: {r.get('priority', 0)}): decision → {r['action']['decision']} — {r['action'].get('reason','')}")
    else:
        st.write("No rules matched. Candidate requires manual review.")

    st.markdown("### Evaluation trace (inputs)")
    st.json(applicant)

# Sidebar: show embedded JSON and how to use it
with st.expander("View embedded JSON rules (exactly as used)"):
    st.code(RULES_JSON, language="json")

st.markdown("---")
st.markdown("**Notes:**")
st.markdown("""
- Rules are evaluated as **all conditions must be true** (logical AND for conditions inside a rule).
- If multiple rules match, the rule with the **highest priority** is selected.
- Supported conditional operators: `>=`, `<=`, `>`, `<`, `==`.
- If no rule matches, the system returns `NO_MATCH` for manual review.
""")
