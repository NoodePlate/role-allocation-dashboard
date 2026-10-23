import streamlit as st
import json
import os

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Role Allocation Dashboard",
    layout="wide"
)

# =====================================================
# SCENARIO FILE STORAGE
# =====================================================

SCENARIO_FILE = "scenarios.json"


def load_scenarios():
    """Load saved scenarios from the local JSON file."""

    if os.path.exists(SCENARIO_FILE):
        try:
            with open(SCENARIO_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}

    return {}


def save_scenarios():
    """Save all scenarios to the local JSON file."""

    with open(SCENARIO_FILE, "w", encoding="utf-8") as file:
        json.dump(
            st.session_state.scenarios,
            file,
            indent=4
        )

# =====================================================
# DATA
# =====================================================

candidate_interests = {
    "Soham": ["Co-chair", "Director of Publicity"],
    "En Cheng": ["Co-chair", "Director of Publicity"],
    "Angel": ["Co-chair"],
    "Zequan": ["Co-chair", "Director of Programme"],
    "Pragati": ["Co-chair", "Director of Programme"],
    "Cynthia": ["Co-chair", "Director of Programme"],
    "Ridzwana": ["Deputy of Programme"],
    "Haziq": ["Co-chair", "Director of Publicity"],
    "Khant": ["Deputy of Programme", "Director of Publicity"],
    "Shavi": ["Director of Programme"],
    "Yasmin": [
        "Director of Publicity",
        "Deputy of Publicity"
    ],
    "Phyllicia": [
        "Director of Publicity",
        "Deputy of Publicity"
    ]
}

# The dictionary value is used to match candidate interests.
role_mapping = {
    "Co-chair A": "Co-chair",
    "Co-chair B": "Co-chair",
    "Director of Programme Development": "Director of Programme",
    "Deputy of Programme Development A": "Deputy of Programme",
    "Deputy of Programme Development B": "Deputy of Programme",
    "Director of Publicity & Student Engagement":
        "Director of Publicity",
    "Deputy of Publicity & Student Engagement":
        "Deputy of Publicity"
}

role_slots = list(role_mapping.keys())

# =====================================================
# SESSION STATE
# =====================================================

if "selected_role" not in st.session_state:
    st.session_state.selected_role = None

if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None

# Store saved allocation scenarios
if "scenarios" not in st.session_state:
    st.session_state.scenarios = load_scenarios()

# Create or update the assignments dictionary.
if "role_assignments" not in st.session_state:
    st.session_state.role_assignments = {
        role: None for role in role_slots
    }
else:
    previous_assignments = st.session_state.role_assignments

    st.session_state.role_assignments = {
        role: previous_assignments.get(role)
        for role in role_slots
    }

# Remove outdated selected roles from previous versions.
if (
    st.session_state.selected_role is not None
    and st.session_state.selected_role not in role_slots
):
    st.session_state.selected_role = None
    st.session_state.selected_candidate = None

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def candidate_assigned_role(candidate):
    """Return the role occupied by a candidate, if any."""

    for role, assigned_candidate in (
        st.session_state.role_assignments.items()
    ):
        if assigned_candidate == candidate:
            return role

    return None

def candidate_has_no_available_role(candidate):
    """Return True if all roles of interest are already occupied."""

    # An assigned candidate is not considered a dead end
    if candidate_assigned_role(candidate) is not None:
        return False

    interests = candidate_interests[candidate]

    # Check every actual role slot
    for role_slot, interest_type in role_mapping.items():

        # Candidate is interested in this type of role
        if interest_type in interests:

            # At least one matching slot is still empty
            if st.session_state.role_assignments[role_slot] is None:
                return False

    # Every matching slot is occupied
    return True


def render_role_button(role):
    """Render a compact role card."""

    assigned_person = st.session_state.role_assignments[role]
    is_selected = st.session_state.selected_role == role

    if assigned_person:
        label = f"{role}\n✅ {assigned_person}"
    else:
        label = role

    clicked = st.button(
        label,
        key=f"role_{role}",
        type="primary" if is_selected else "secondary",
        use_container_width=True
    )

    if clicked:
        if is_selected:
            st.session_state.selected_role = None
            st.session_state.selected_candidate = None
        else:
            st.session_state.selected_role = role
            st.session_state.selected_candidate = None

        st.rerun()


# =====================================================
# STYLING
# =====================================================

st.markdown(
    """
    <style>

    /* Page width and spacing */
    .block-container {
        max-width: 1280px;
        padding-top: 1.25rem;
        padding-bottom: 2rem;
    }

    /* Dashboard title */
    h1 {
        font-size: 2rem !important;
        margin-bottom: 0.15rem !important;
    }

    /* Section headings */
    h2, h3 {
        margin-top: 0.45rem !important;
        margin-bottom: 0.55rem !important;
    }

    /* Reduce excessive Streamlit vertical spacing */
    div[data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }

    /* Leadership role cards */
    .st-key-role_board button {
        min-height: 68px;
        height: 68px;
        padding: 0.4rem 0.7rem;
        border-radius: 9px;
        font-size: 0.92rem;
        font-weight: 500;
        line-height: 1.35;
        white-space: pre-line;
    }

    /* Candidate cards */
    .st-key-candidate_grid button {
        min-height: 52px;
        height: 52px;
        padding: 0.3rem 0.5rem;
        border-radius: 9px;
        font-size: 0.92rem;
        font-weight: 500;
    }

    /* Candidates who are not eligible for the selected role */
    .st-key-candidate_grid button:disabled {
        opacity: 0.42;
        color: #64748b;
        background-color: #f8fafc;
        border-color: #e2e8f0;
    }

    /* Unassigned candidates with no remaining available roles */
    .st-key-candidate_grid [class*="st-key-no_role_"] button {
        opacity: 1 !important;
        color: #991b1b !important;
        background-color: #fee2e2 !important;
        border: 2px solid #ef4444 !important;
    }

    /* Keep dead-end candidate names clearly readable */
    .st-key-candidate_grid [class*="st-key-no_role_"] button p {
        color: #991b1b !important;
        text-decoration: none !important;
        font-weight: 600 !important;
    }

    /* Candidates who have already been assigned */
    .st-key-candidate_grid [class*="st-key-assigned_"] button {
        opacity: 0.75 !important;
        color: #166534 !important;
        background-color: #dcfce7 !important;
        border-color: #22c55e !important;
    }

    /* Assignment confirmation section */
    .st-key-assignment_panel button {
        min-height: 42px;
        height: 42px;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Divider spacing */
    hr {
        margin-top: 0.9rem !important;
        margin-bottom: 0.9rem !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# HEADER
# =====================================================

st.title("Role Allocation Dashboard")

st.caption(
    "Select a role, choose an eligible candidate, "
    "and confirm the assignment."
)

# =====================================================
# LEADERSHIP ROLE BOARD
# =====================================================

st.subheader("Leadership Roles")

with st.container(key="role_board"):

    # -------------------------------------------------
    # ROW 1: CO-CHAIRS
    # -------------------------------------------------

    cochair_left, cochair_right = st.columns(
        2,
        gap="small"
    )

    with cochair_left:
        render_role_button("Co-chair A")

    with cochair_right:
        render_role_button("Co-chair B")

    # -------------------------------------------------
    # ROW 2: DIRECTORS
    #
    # Programme Development and Publicity each occupy
    # one-half of the available width.
    # -------------------------------------------------

    director_programme_col, director_publicity_col = st.columns(
        [1, 1],
        gap="small"
    )

    with director_programme_col:
        render_role_button(
            "Director of Programme Development"
        )

    with director_publicity_col:
        render_role_button(
            "Director of Publicity & Student Engagement"
        )

    # -------------------------------------------------
    # ROW 3: DEPUTIES
    #
    # The left half is divided into two equal
    # Programme Development deputy positions.
    # -------------------------------------------------

    deputy_programme_area, deputy_publicity_area = st.columns(
        [1, 1],
        gap="small"
    )

    with deputy_programme_area:

        deputy_programme_a, deputy_programme_b = st.columns(
            2,
            gap="small"
        )

        with deputy_programme_a:
            render_role_button(
                "Deputy of Programme Development A"
            )

        with deputy_programme_b:
            render_role_button(
                "Deputy of Programme Development B"
            )

    with deputy_publicity_area:
        render_role_button(
            "Deputy of Publicity & Student Engagement"
        )

st.divider()

# =====================================================
# CANDIDATE GRID
# =====================================================

st.subheader("Candidates")

selected_role = st.session_state.selected_role

if selected_role:
    active_interest = role_mapping[selected_role]
else:
    active_interest = None

candidate_names = list(candidate_interests.keys())

with st.container(key="candidate_grid"):

    for row_start in range(0, len(candidate_names), 4):

        candidate_columns = st.columns(
            4,
            gap="small"
        )

        for column_number in range(4):

            candidate_index = row_start + column_number

            if candidate_index >= len(candidate_names):
                continue

            candidate = candidate_names[candidate_index]
            interests = candidate_interests[candidate]

            is_interested = (
                active_interest is None
                or active_interest in interests
            )

            assigned_role = candidate_assigned_role(candidate)
            is_assigned = assigned_role is not None

            has_no_available_role = candidate_has_no_available_role(
                candidate
            )

            is_selected_candidate = (
                st.session_state.selected_candidate == candidate
            )

            # Display the candidate's stated role preferences
            preference_text = " | ".join(interests)

            if is_assigned:
                candidate_label = (
                    f"✅ {candidate}\n"
                    f"{preference_text}"
                )

            elif is_selected_candidate:
                candidate_label = (
                    f"● {candidate}\n"
                    f"{preference_text}"
                )

            else:
                candidate_label = (
                    f"{candidate}\n"
                    f"{preference_text}"
                )



            candidate_disabled = (
                is_assigned
                or has_no_available_role
                or (
                    active_interest is not None
                    and not is_interested
                )
            )

            with candidate_columns[column_number]:

                candidate_clicked = st.button(
                    candidate_label,
                    key=(
                        f"assigned_{candidate}"
                        if is_assigned
                        else (
                            f"no_role_{candidate}"
                            if has_no_available_role
                            else f"candidate_{candidate}"
                        )
                    ),
                    type=(
                        "primary"
                        if is_selected_candidate
                        else "secondary"
                    ),
                    use_container_width=True,
                    disabled=candidate_disabled
                )

                if candidate_clicked:

                    if is_selected_candidate:
                        st.session_state.selected_candidate = None
                    else:
                        st.session_state.selected_candidate = candidate

                    st.rerun()

# =====================================================
# ASSIGNMENT, REPLACEMENT, AND VACATING
# =====================================================

selected_role = st.session_state.selected_role
selected_candidate = st.session_state.selected_candidate

if selected_role:

    current_assignee = st.session_state.role_assignments[selected_role]

    st.divider()

    with st.container(key="assignment_panel"):

        # ---------------------------------------------
        # CASE 1: A candidate has been selected
        # ---------------------------------------------
        if selected_candidate:

            # Role is already occupied, so replacement is required
            if current_assignee:

                st.warning(
                    f"{selected_role} is currently assigned to "
                    f"{current_assignee}."
                )

                st.markdown(
                    f"Replace **{current_assignee}** with "
                    f"**{selected_candidate}**?"
                )

                replace_col, cancel_col = st.columns(2)

                with replace_col:

                    if st.button(
                        "Confirm replacement",
                        type="primary",
                        use_container_width=True
                    ):
                        st.session_state.role_assignments[
                            selected_role
                        ] = selected_candidate

                        st.session_state.selected_role = None
                        st.session_state.selected_candidate = None

                        st.rerun()

                with cancel_col:

                    if st.button(
                        "Cancel replacement",
                        use_container_width=True
                    ):
                        st.session_state.selected_candidate = None
                        st.rerun()

            # Role is empty, so this is a normal assignment
            else:

                st.markdown(
                    f"Assign **{selected_candidate}** to "
                    f"**{selected_role}**?"
                )

                assign_col, cancel_col = st.columns(2)

                with assign_col:

                    if st.button(
                        "Confirm assignment",
                        type="primary",
                        use_container_width=True
                    ):
                        st.session_state.role_assignments[
                            selected_role
                        ] = selected_candidate

                        st.session_state.selected_role = None
                        st.session_state.selected_candidate = None

                        st.rerun()

                with cancel_col:

                    if st.button(
                        "Cancel",
                        use_container_width=True
                    ):
                        st.session_state.selected_candidate = None
                        st.rerun()

        # ---------------------------------------------
        # CASE 2: Occupied role selected, but no new
        # candidate has been selected
        # ---------------------------------------------
        elif current_assignee:

            st.markdown(
                f"**Current assignment:** {current_assignee}"
            )

            st.warning(
                f"Vacating this role will remove {current_assignee} "
                f"from {selected_role}."
            )

            vacate_col, keep_col = st.columns(2)

            with vacate_col:

                if st.button(
                    "Confirm vacate role",
                    type="primary",
                    use_container_width=True
                ):
                    st.session_state.role_assignments[
                        selected_role
                    ] = None

                    st.session_state.selected_role = None
                    st.session_state.selected_candidate = None

                    st.rerun()

            with keep_col:

                if st.button(
                    "Keep assignment",
                    use_container_width=True
                ):
                    st.session_state.selected_role = None
                    st.session_state.selected_candidate = None
                    st.rerun()

# =====================================================
# RESET CONTROLS
# =====================================================

st.divider()
st.subheader("Reset Assignments")

# =====================================================
# RESET CONTROLS
# =====================================================

st.divider()

if st.button(
    "Reset All Assignments",
    use_container_width=True
):
    st.session_state.show_all_reset = True

# =====================================================
# RESET ALL PANEL
# =====================================================

if st.session_state.get("show_all_reset", False):

    st.error("⚠️ Reset ALL assignments?")

    assigned_people = [
        (role, candidate)
        for role, candidate
        in st.session_state.role_assignments.items()
        if candidate is not None
    ]

    if assigned_people:

        st.write("The following assignments will be removed:")

        for role, candidate in assigned_people:
            st.write(f"• **{role}:** {candidate}")

        st.warning(
            "This will clear every current assignment."
        )

        confirm_all_col, cancel_all_col = st.columns(2)

        with confirm_all_col:

            if st.button(
                "Confirm Reset All",
                type="primary",
                use_container_width=True
            ):

                for role in st.session_state.role_assignments:
                    st.session_state.role_assignments[role] = None

                st.session_state.selected_role = None
                st.session_state.selected_candidate = None
                st.session_state.show_all_reset = False

                st.rerun()

        with cancel_all_col:

            if st.button(
                "Cancel Reset",
                use_container_width=True
            ):

                st.session_state.show_all_reset = False
                st.rerun()

    else:

        st.info("There are currently no assignments to reset.")

        if st.button("Close Reset"):
            st.session_state.show_all_reset = False
            st.rerun()

# =====================================================
# SCENARIO MANAGEMENT
# =====================================================

st.divider()
st.subheader("Saved Scenarios")

save_col, load_col = st.columns(2)

# -----------------------------------------------------
# SAVE SCENARIO
# -----------------------------------------------------

with save_col:

    scenario_name = st.text_input(
        "Scenario name",
        placeholder="e.g. Option A"
    )

    if st.button(
        "Save Current Scenario",
        use_container_width=True
    ):

        clean_name = scenario_name.strip()

        if not clean_name:
            st.warning("Please enter a scenario name.")

        elif clean_name in st.session_state.scenarios:
            st.warning(
                f'"{clean_name}" already exists. '
                "Please use a different name."
            )

        else:
            # .copy() is important so later changes do not
            # modify the saved scenario
            st.session_state.scenarios[clean_name] = (
                st.session_state.role_assignments.copy()
            )
            save_scenarios()
            st.success(f'Saved scenario: "{clean_name}"')


# -----------------------------------------------------
# LOAD / DELETE SCENARIO
# -----------------------------------------------------

with load_col:

    if st.session_state.scenarios:

        scenario_to_load = st.selectbox(
            "Saved scenarios",
            list(st.session_state.scenarios.keys())
        )

        load_button_col, delete_button_col = st.columns(2)

        # LOAD
        with load_button_col:

            if st.button(
                "Load Scenario",
                use_container_width=True
            ):

                st.session_state.role_assignments = (
                    st.session_state.scenarios[
                        scenario_to_load
                    ].copy()
                )

                st.session_state.selected_role = None
                st.session_state.selected_candidate = None

                st.rerun()

        # DELETE
        with delete_button_col:

            if st.button(
                "Delete Scenario",
                use_container_width=True
            ):

                st.session_state.scenario_to_delete = (
                    scenario_to_load
                )

    else:

        st.info("No scenarios saved yet.")


# =====================================================
# DELETE SCENARIO CONFIRMATION
# =====================================================

if st.session_state.get("scenario_to_delete"):

    scenario_to_delete = (
        st.session_state.scenario_to_delete
    )

    st.warning(
        f'Delete saved scenario "{scenario_to_delete}"?'
    )

    st.write(
        "The current allocation on the board will not be changed."
    )

    confirm_delete_col, cancel_delete_col = st.columns(2)

    with confirm_delete_col:

        if st.button(
            "Confirm Delete",
            type="primary",
            use_container_width=True
        ):

            del st.session_state.scenarios[
                scenario_to_delete
            ]
            save_scenarios()
            st.session_state.scenario_to_delete = None

            st.rerun()

    with cancel_delete_col:

        if st.button(
            "Cancel Delete",
            use_container_width=True
        ):

            st.session_state.scenario_to_delete = None

            st.rerun()