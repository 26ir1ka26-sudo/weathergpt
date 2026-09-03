cimport os
import requests
import streamlit as st
from google import genai

# Page configuration
st.set_page_config(
    page_title="WeatherGPT - SIH26068", page_icon="🌤️", layout="centered"
)

st.title("🌤️ WeatherGPT")
st.markdown(
    "Conversational AI for Weather Forecasting, Alerts, and Climate Information"
)

# API Key input in the sidebar
api_key = st.sidebar.text_input("Enter Google GenAI API Key:", type="password")

if api_key:
  client = genai.Client(api_key=api_key)
else:
  st.warning("Please enter your Gemini API Key in the sidebar to proceed.")


def get_weather_data(city_name):
  """Fetches current weather data for a given city from OpenWeatherMap API."""
  url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=895123512b7d41f19f201d43a6d71c82&units=metric"
  try:
    response = requests.get(url)
    if response.status_code == 200:
      return response.json()
    else:
      return None
  except Exception:
    return None


# Chat Interface Initialization
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display prior chat history
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input(
    "Ask about the weather (e.g., 'What is the weather like in Gwalior?')"
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    with st.spinner("Analyzing atmospheric data..."):
      words = prompt.split()
      target_city = "Gwalior"  # Default fallback city
      for word in words:
        if word.istitle() and word.lower() not in [
            "what",
            "is",
            "the",
            "weather",
            "in",
            "forecast",
        ]:
          target_city = word
          break

      weather_json = get_weather_data(target_city)

      if weather_json and api_key:
        context_prompt = f"""
                You are WeatherGPT, an advanced meteorological conversational assistant.
                User Query: {prompt}
                Live Weather Data retrieved for {target_city}:
                - Temperature: {weather_json['main']['temp']}°C
                - Condition: {weather_json['weather'][0]['description']}
                - Humidity: {weather_json['main']['humidity']}%
                - Wind Speed: {weather_json['wind']['speed']} m/s
                
                Provide a conversational, accurate, and helpful response addressing the user's query using this data. Include advice or alerts if conditions require it.
                """

        try:
          response = client.models.generate_content(
              model="gemini-2.5-flash", contents=context_prompt
          )
          bot_reply = response.text
        except Exception as e:
          bot_reply = f"Error generating AI response: {str(e)}."
      else:
        bot_reply = (
            f"I couldn't fetch live data for '{target_city}'. Please check your"
            " API key or try another city name."
        )

      st.markdown(bot_reply)
      st.session_state.messages.append(
          {"role": "assistant", "content": bot_reply}
      )
