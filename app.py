import os
#from dotenv import load_dotenv
import google.genai as google_genai
from google.genai import Client  # <-- Updated to modern Google SDK
from PIL import Image
import streamlit as st

# =====================================================================
# 1. ENVIRONMENT & API CONFIGURATION
# =====================================================================
#load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("⚠️ API Key missing! Please check your `.env` file configuration.")
    st.stop() 

# Initialize the modern client (automatically uses the stable production routing)
client = Client()


# =====================================================================
# 2. SESSION STATE INITIALIZATION
# =====================================================================
if "wellnest_profile" not in st.session_state:
    st.session_state.wellnest_profile = {
        "intentions": "Increase daily energy, improve sleep quality, and eat mindfully.",
        "vibe": "Desk job, moderately active, practice yoga occasionally.",
        "stress_level": "Moderate to high during work weeks.",
        "dietary_style": "Plant-forward, focus on whole foods.",
        "sensitivities": "Sensitive to heavy dairy and highly processed sugar.",
        "weight": 70.0,
        "height": 170.0,
        "age": 25,
        "activity_level": "Moderately Active",
        "bmi": 24.2
    }

# Feature 2 Session State Setup
if "app_goal" not in st.session_state:
    st.session_state.app_goal = "General Health Alignment"


# =====================================================================
# 3. CORE HELPER FUNCTIONS
# =====================================================================
def get_wellnest_response(input_prompt, image_payload=None):
    """Sends the constructed holistic prompt and optional image data using the new SDK client."""
    try:
        # Combine text prompt and image data if it exists
        contents = [input_prompt]
        if image_payload:
            contents.append(image_payload)
            
        # Using the standard flagship model name
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

st.title("🪹 Wellnest")
st.markdown("*Welcome to your personal sanctuary for mindful nutrition, body awareness, and holistic health.*")
st.write("---")

# Sidebar: Enhanced "Nest Profile" with Interactive BMI Calculator (FEATURE 1)
with st.sidebar:
    st.subheader("🌿 Your Nest Profile")
    st.caption("Define your current physical and mental baseline.")

    user_intentions = st.text_area("Core Intentions & Goals", value=st.session_state.wellnest_profile["intentions"])
    user_vibe = st.text_area("Daily Rhythm & Activity", value=st.session_state.wellnest_profile["vibe"])
    user_stress = st.text_area("Current Stress Levels", value=st.session_state.wellnest_profile["stress_level"])
    user_diet = st.text_area("Dietary Philosophy", value=st.session_state.wellnest_profile["dietary_style"])
    user_sensitivities = st.text_area("Sensitivities & Restrictions", value=st.session_state.wellnest_profile["sensitivities"])
    
    st.write("---")
    st.markdown("### 📊 Live Body Metrics")
    # Interactive numeric profile elements
    user_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=float(st.session_state.wellnest_profile.get("weight", 70.0)))
    user_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(st.session_state.wellnest_profile.get("height", 170.0)))
    user_age = st.number_input("Age (years)", min_value=10, max_value=100, value=int(st.session_state.wellnest_profile.get("age", 25)))
    user_activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"], index=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"].index(st.session_state.wellnest_profile.get("activity_level", "Moderately Active")))

    # Real-time BMI processing
    height_m = user_height / 100
    computed_bmi = round(user_weight / (height_m ** 2), 1)
    
    st.metric(label="Calculated BMI", value=computed_bmi)
    if computed_bmi < 18.5: st.warning("Classification: Underweight")
    elif computed_bmi < 25: st.success("Classification: Healthy Baseline")
    elif computed_bmi < 30: st.info("Classification: Overweight Zone")
    else: st.warning("Classification: Class Definition")

    if st.button("Sync Profile"):
        st.session_state.wellnest_profile = {
            "intentions": user_intentions,
            "vibe": user_vibe,
            "stress_level": user_stress,
            "dietary_style": user_diet,
            "sensitivities": user_sensitivities,
            "weight": user_weight,
            "height": user_height,
            "age": user_age,
            "activity_level": user_activity,
            "bmi": computed_bmi
        }
        st.success("Your Nest profile has synced beautifully!")

# Quick-Focus Mode Injection Dashboard (FEATURE 2)
st.subheader("🎯 What is your primary focus today?")
goal_col1, goal_col2, goal_col3 = st.columns(3)

with goal_col1:
    if st.button("🥗 Plan My Meals", use_container_width=True):
        st.session_state.app_goal = "Strict Nutrition & Tailored Meal Prep"
with goal_col2:
    if st.button("💪 Design a Workout", use_container_width=True):
        st.session_state.app_goal = "Custom Movement & Physical Routines"
with goal_col3:
    if st.button("🧘 Mindfulness & Stress Focus", use_container_width=True):
        st.session_state.app_goal = "Mental Wellness, Sleep Optimization, and Nervous System Care"

st.info(f"✨ Currently Tuning Advice For: **{st.session_state.app_goal}**")
st.write("---")

# Main App Navigation Features
tab1, tab2, tab3 = st.tabs(["🥗 Mindful Nourishment", "📸 Conscious Scan", "🔮 Wellness Oracle"])

# --- Tab 1: Mindful Nourishment ---
with tab1:
    st.subheader("Mindful Meal Blueprint")
    st.markdown("Generate a structured, nurturing meal schedule aligned perfectly with your routine.")

    col1, col2 = st.columns([3, 2])
    with col1:
        extra_needs = st.text_area("Any dynamic needs for the upcoming days?", placeholder="e.g., I have an incredibly busy work week and need 15-minute prep times.")
    with col2:
        st.info("💡 **Profile Context Applied:**")
        st.json(st.session_state.wellnest_profile)

    if st.button("Weave My Nourishment Plan"):
        with st.spinner("Weaving your custom plan..."):
            nourish_prompt = f"""
            You are an intuitive, holistic wellness and nutrition guide. Create a personalized meal blueprint based on this profile:
            Core Intentions: {st.session_state.wellnest_profile['intentions']}
            Daily Rhythm: {st.session_state.wellnest_profile['vibe']}
            Current Stress: {st.session_state.wellnest_profile['stress_level']}
            Dietary Style: {st.session_state.wellnest_profile['dietary_style']}
            Sensitivities: {st.session_state.wellnest_profile['sensitivities']}
            Physical Background: Age {st.session_state.wellnest_profile.get('age')}, Weight {st.session_state.wellnest_profile.get('weight')}kg, Height {st.session_state.wellnest_profile.get('height')}cm, Calculated BMI {st.session_state.wellnest_profile.get('bmi')} with an activity profile of {st.session_state.wellnest_profile.get('activity_level')}.
            
            Current Focus Objective: {st.session_state.app_goal}
            Dynamic Request: {extra_needs if extra_needs else "Focus on a balanced weekly flow."}
            
            Please provide a 7-day visual flow of meals with brief notes on why these choices heal or support their goals. Ensure the advice respects their active Focus Objective and calculated physical profile metrics.
            """
            response = get_wellnest_response(nourish_prompt)
            st.write("---")
            st.markdown(response)

# --- Tab 2: Conscious Scan ---
with tab2:
    st.subheader("Conscious Scan")
    st.markdown("Upload a picture of your plate to understand its unique nutrient story.")

    uploaded_visual = st.file_uploader("Share an image of your meal", type=["jpg", "jpeg", "png"])
    if uploaded_visual is not None:
        img_display = Image.open(uploaded_visual)
        st.image(img_display, caption="Your Prepared Meal", use_container_width=True)

        if st.button("Read the Plate"):
            with st.spinner("Decoding nutrients..."):
                scan_prompt = f"""
                Analyze this food image. Provide estimated calories, macronutrients, and key health benefits.
                Tailor any commentary to complement this user baseline: {st.session_state.wellnest_profile}
                And map your nutritional suggestions to coordinate with their current target focus: {st.session_state.app_goal}
                """
                # Format image seamlessly for the new SDK
                response = get_wellnest_response(
                    input_prompt=scan_prompt,
                    image_payload=img_display
                )
                st.write("---")
                st.markdown(response)

# --- Tab 3: Wellness Oracle ---
with tab3:
    st.subheader("The Wellness Oracle")
    st.markdown("Pose a holistic, scientific, or practical question regarding your physical well-being.")

    oracle_query = st.text_input("What aspect of your health would you like to explore today?", placeholder="e.g., How does high stress impact my digestion?")
    if st.button("Consult the Oracle"):
        if not oracle_query:
            st.warning("Please type a question into the spring of knowledge.")
        else:
            with st.spinner("Gathering insights..."):
                oracle_prompt = f"""
                You are a highly qualified holistic wellness consultant. Answer this query with absolute scientific depth: "{oracle_query}"
                Keep this user's biological baseline, physical metrics, and activity settings directly in mind: {st.session_state.wellnest_profile}
                Ensure your response aligns closely with their active lifestyle focus area: {st.session_state.app_goal}
                """
                response = get_wellnest_response(oracle_prompt)
                st.write("---")
                st.markdown(response)


# =====================================================================
# 5. INTEGRATED DAILY PROGRESS TRACKER (FEATURE 3)
# =====================================================================
st.write("---")
st.subheader("🚰 Daily Ritual & Habit Logs")
st.markdown("*Use these sliders to manually log your baseline habits for the day. This visual grid keeps you accountable independent of the AI conversations.*")

track_col1, track_col2 = st.columns(2)

with track_col1:
    glasses = st.slider("Water Consumption (Glasses - 250ml each)", 0, 16, 4)
    st.write(f"💧 Logged **{glasses}** out of an 8-glass daily target profile.")
    if glasses >= 8: 
        st.success("🎉 Hydration Target Met!")
    else:
        st.progress(glasses / 8)

with track_col2:
    sleep = st.slider("Sleep Quality Duration (Hours)", 0.0, 12.0, 7.0, step=0.5)
    st.write(f"🌙 Logged **{sleep} hours** of rest against an optimal 8-hour metric loop.")
    if sleep >= 7.0:
        st.success("🧠 Rest patterns are in recovery balance!")
    else:
        st.progress(sleep / 8.0)