import os
from dotenv import load_dotenv
from google import genai  # <-- Updated to modern Google SDK
from PIL import Image
import streamlit as st

# =====================================================================
# 1. ENVIRONMENT & API CONFIGURATION
# =====================================================================
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("⚠️ API Key missing! Please check your `.env` file configuration.")
    st.stop() 

# Initialize the modern client (automatically uses the stable production routing)
client = genai.Client(api_key=GOOGLE_API_KEY)


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
    }


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

# Sidebar: The "Nest Profile"
with st.sidebar:
    st.subheader("🌿 Your Nest Profile")
    st.caption("Define your current physical and mental baseline.")

    user_intentions = st.text_area("Core Intentions & Goals", value=st.session_state.wellnest_profile["intentions"])
    user_vibe = st.text_area("Daily Rhythm & Activity", value=st.session_state.wellnest_profile["vibe"])
    user_stress = st.text_area("Current Stress Levels", value=st.session_state.wellnest_profile["stress_level"])
    user_diet = st.text_area("Dietary Philosophy", value=st.session_state.wellnest_profile["dietary_style"])
    user_sensitivities = st.text_area("Sensitivities & Restrictions", value=st.session_state.wellnest_profile["sensitivities"])

    if st.button("Sync Profile"):
        st.session_state.wellnest_profile = {
            "intentions": user_intentions,
            "vibe": user_vibe,
            "stress_level": user_stress,
            "dietary_style": user_diet,
            "sensitivities": user_sensitivities,
        }
        st.success("Your Nest profile has synced beautifully!")

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
            Dynamic Request: {extra_needs if extra_needs else "Focus on a balanced weekly flow."}
            
            Please provide a 7-day visual flow of meals with brief notes on why these choices heal or support their goals.
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
                # Format image seamlessly for the new SDK
                response = get_wellnest_response(
                    input_prompt="Analyze this food image. Provide estimated calories, macronutrients, and key health benefits.",
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
                Keep this user's baseline in mind: {st.session_state.wellnest_profile}
                """
                response = get_wellnest_response(oracle_prompt)
                st.write("---")
                st.markdown(response)