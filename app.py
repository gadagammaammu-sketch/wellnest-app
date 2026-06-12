import os
import google.genai as google_genai
from google.genai import Client
from PIL import Image
import streamlit as st

# =====================================================================
# 1. ENVIRONMENT & API CONFIGURATION
# =====================================================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("⚠️ API Key missing! Please check your Streamlit Secrets.")
    st.stop() 

client = Client()

# =====================================================================
# 2. SESSION STATE INITIALIZATION
# =====================================================================
if "wellnest_profile" not in st.session_state:
    st.session_state.wellnest_profile = {
        "intentions": "Increase daily energy and eat mindfully.",
        "vibe": "Desk job, moderately active.",
        "stress_level": "Moderate.",
        "dietary_style": "Whole foods focus.",
        "sensitivities": "None.",
        "weight": 70.0,
        "height": 170.0,
        "age": 25,
        "activity_level": "Moderately Active",
        "bmi": 24.2
    }

if "app_goal" not in st.session_state:
    st.session_state.app_goal = "General Health Alignment"

# NEW: Tracks which page button is currently active
if "current_page" not in st.session_state:
    st.session_state.current_page = "📊 My Baseline"

# =====================================================================
# 3. CORE HELPER FUNCTIONS
# =====================================================================
def get_wellnest_response(input_prompt, image_payload=None):
    try:
        contents = [input_prompt]
        if image_payload:
            contents.append(image_payload)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
        )
        return response.text
    except Exception as e:
        return f"The Oracle encountered a ripple: {str(e)}"

# =====================================================================
# 4. STREAMLIT UI & INTERFACE LAYOUT
# =====================================================================
st.set_page_config(page_title="Wellnest Hub", layout="wide", page_icon="🪹")

# --- HEADER SECTION ---
st.title("🪹 Wellnest")
st.markdown("*Your organized sanctuary for mindful living and holistic health.*")

# --- PERSISTENT SIDEBAR (Summary Only) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=100)
    st.subheader("🌿 Nest Status")
    st.info(f"**Current Page:** \n{st.session_state.current_page}\n\n**Current Focus:** \n{st.session_state.app_goal}")
    st.metric("Your BMI", st.session_state.wellnest_profile["bmi"])
    st.write("---")
    st.caption("Click the buttons at the top of the main screen to switch dashboards.")

# =====================================================================
# 5. DYNAMIC TOP-BUTTON NAVIGATION MENU
# =====================================================================
st.write("### 🧭 Navigate Your Nest")
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)

with nav_col1:
    if st.button("📊 My Baseline", use_container_width=True):
        st.session_state.current_page = "📊 My Baseline"
with nav_col2:
    if st.button("🥗 Nourishment", use_container_width=True):
        st.session_state.current_page = "🥗 Nourishment"
with nav_col3:
    if st.button("📸 Plate Scan", use_container_width=True):
        st.session_state.current_page = "📸 Plate Scan"
with nav_col4:
    if st.button("🔮 Health Oracle", use_container_width=True):
        st.session_state.current_page = "🔮 Health Oracle"
with nav_col5:
    if st.button("🎯 Daily Rituals", use_container_width=True):
        st.session_state.current_page = "🎯 Daily Rituals"

st.write("---")

# =====================================================================
# 6. CONDITIONAL PAGE RENDERING (Swaps view based on active button)
# =====================================================================

# --- PAGE 1: My Baseline ---
if st.session_state.current_page == "📊 My Baseline":
    st.subheader("📋 Your Physical Baseline")
    st.markdown("Keep your biological metrics updated so the AI can tailor its wisdom specifically to your body.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        u_weight = st.number_input("Weight (kg)", min_value=30.0, value=float(st.session_state.wellnest_profile["weight"]))
        u_height = st.number_input("Height (cm)", min_value=100.0, value=float(st.session_state.wellnest_profile["height"]))
        u_age = st.number_input("Age", min_value=10, value=int(st.session_state.wellnest_profile["age"]))
    
    with col_b:
        u_activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"], 
                                 index=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"].index(st.session_state.wellnest_profile["activity_level"]))
        
        # BMI Calculation Logic
        h_m = u_height / 100
        bmi_calc = round(u_weight / (h_m ** 2), 1)
        st.metric("Calculated BMI", bmi_calc)
        
    st.write("---")
    st.markdown("#### Deep Profile Details")
    u_intentions = st.text_area("Core Intentions", st.session_state.wellnest_profile["intentions"])
    u_diet = st.text_area("Dietary Philosophy", st.session_state.wellnest_profile["dietary_style"])

    if st.button("Save & Sync My Baseline"):
        st.session_state.wellnest_profile.update({
            "weight": u_weight, "height": u_height, "age": u_age, "activity_level": u_activity, 
            "bmi": bmi_calc, "intentions": u_intentions, "dietary_style": u_diet
        })
        st.success("Physical profile synced to the Nest!")

# --- PAGE 2: Nourishment ---
elif st.session_state.current_page == "🥗 Nourishment":
    st.subheader("🥗 Mindful Meal Blueprint")
    extra_needs = st.text_area("Dynamic needs?", placeholder="e.g., Fast 15-minute meals for a busy week.")
    
    if st.button("Weave My Nourishment Plan"):
        with st.spinner("Weaving..."):
            nourish_prompt = f"Holistic meal plan for: {st.session_state.wellnest_profile}. Focus: {st.session_state.app_goal}. Extra: {extra_needs}"
            response = get_wellnest_response(nourish_prompt)
            st.markdown(response)

# --- PAGE 3: Plate Scan ---
elif st.session_state.current_page == "📸 Plate Scan":
    st.subheader("📸 Conscious Plate Scan")
    uploaded_visual = st.file_uploader("Upload meal photo", type=["jpg", "png"])
    if uploaded_visual:
        img = Image.open(uploaded_visual)
        st.image(img, width=400)
        if st.button("Analyze Nutrient Story"):
            with st.spinner("Scanning..."):
                resp = get_wellnest_response("Analyze nutrients in this image.", image_payload=img)
                st.markdown(resp)

# --- PAGE 4: Health Oracle ---
elif st.session_state.current_page == "🔮 Health Oracle":
    st.subheader("🔮 The Wellness Oracle")
    oracle_query = st.text_input("Pose your question...")
    if st.button("Consult Oracle"):
        with st.spinner("Consulting..."):
            prompt = f"Question: {oracle_query}. User Profile: {st.session_state.wellnest_profile}. Mode: {st.session_state.app_goal}"
            st.markdown(get_wellnest_response(prompt))

# --- PAGE 5: Daily Rituals ---
elif st.session_state.current_page == "🎯 Daily Rituals":
    st.subheader("🎯 Daily Focus & Habit Rituals")
    
    st.markdown("#### Select Your Intention for Today")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        if st.button("🥗 Nutrition Focus", use_container_width=True): st.session_state.app_goal = "Strict Nutrition"
    with f_col2:
        if st.button("💪 Movement Focus", use_container_width=True): st.session_state.app_goal = "Custom Workouts"
    with f_col3:
        if st.button("🧘 Mindfulness Focus", use_container_width=True): st.session_state.app_goal = "Stress Care"
    
    st.info(f"**Current Focus Mode:** {st.session_state.app_goal}")
    
    st.write("---")
    st.markdown("#### Manual Habit Trackers")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        h2o = st.slider("Water (Glasses)", 0, 12, 4)
        st.progress(h2o/8 if h2o <= 8 else 1.0)
    with t_col2:
        sleep = st.slider("Sleep (Hours)", 0, 12, 7)
        st.progress(sleep/8 if sleep <= 8 else 1.0)