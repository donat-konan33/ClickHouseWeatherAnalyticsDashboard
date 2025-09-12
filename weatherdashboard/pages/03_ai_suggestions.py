"""
With this page it will be interesting to request ai suggestions about the weather

"""
import streamlit as st
st.set_page_config(page_title="Weather Dashboard",
                 layout="wide",
                 page_icon="🌦️")

import sys
sys.path.append("/app")

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import requests
import json

from weatherdashboard.functions.queries import WeatherQueries
from weatherdashboard.functions.state import WeatherState
from weatherdashboard.functions.constants import WeatherConstants

# ---------  add login credentials -------- #
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

class AgentSunAI:
    def __init__(self):
        self.state = WeatherState()
        self.queries = WeatherQueries()
        self.constants = WeatherConstants()

    def household_use(self):
        """
        This method helps to define, with your location that you will give and other necessary features,
        which machine could consume the location corresponding to weekly solar energy recorded in the database
        """

        client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=str(OPENROUTER_API_KEY)
        )
        col1, col2 = st.columns([3, 5])
        with col1:
            pick_dep = st.selectbox("Select a department... ", self.constants.department())
            data = self.state.get_query_result("get_solarenergy_agg_pday", pick_dep)
            with st.container(border=True):
                col3, col4 = st.columns([3, 2])
                text1 = f"""
                        <div style="text-align: left;">
                            <p>Department : {data[0]["department"]} </p>
                            <p>Energy Density (kWh/m²) : {round(data[0]['solarenergy_kwhpm2'], 2)}</p>
                            <p>Peak Energy (kWhc) : {round(data[0]['available_solarenergy_kwhc'], 2)}</p>
                        </div>
                    """
                text2 = f"""
                        <div style="text-align: left;">
                            <p style="font-size: 14px; font-weight: bold;" > Available Electrical Energy for household per day over the 7 next days : </p>
                            <p style="font-size: 54px; font-weight: bold; color: green;" > {round(data[0]['real_production_kwhpday'], 2)} </p>
                            <p style="font-size: 20px; font-weight: bold"> kWh </p>
                        </div>
                    """

                with col3:
                    st.container().write(text1, unsafe_allow_html=True)
                with col4:
                    st.container(border=True,).write(text2, unsafe_allow_html=True)

        with col2:
            #prompt = st.text_input("Hit the features of your Solar panel")
            if data is not None:
                    if st.button("Generate AgentSunAI suggestions"):
                        try:
                            with st.spinner("Please let AgentSunAI a few time (40-60s) to provide consumption suggestion... You should retry if no result"):
                                completion = client.chat.completions.create(
                                            model="deepseek/deepseek-r1:free",
                                            messages=[
                                        {"role": "system", "content": "You are an expert assistant in solar energy management. Your suggestion might take into account only much smaller appliances."},
                                        {"role": "user", "content": f"""data : {round(data[0]["real_production_kwhpday"], 2)}
                                                Prompt :
                                                Based on the real_production_kwhpday (in kwh per day) value, distribute this energy among the following appliances:
                                                - Lighting
                                                - Refrigerator
                                                - Television
                                                - Laptop
                                                - Washing Machine
                                                - Microwave
                                                **Output Format:**
                                                Provide only a **table** with the following columns:
                                                    1. **Utilization** (Usage)
                                                    2. **(Daily Consumption) (kWh)**
                                                    3. **Details of Daily Distribution and precise the working time**
                                                Generate the response **only in French**.
                                                **No additional text or explanation.** """}
                                            ],
                                            max_tokens=1500,  # max tokens to generate,
                                            temperature=0

                                )
                                response = completion.choices[0].message.content
                                st.write(response) #.message.content or .reasoning
                                if response is not None:
                                    text = """
                                    ----------------------------------------------------------
                                    The real electrical production from Solar Panel is based on a specific one studied previously in an article.
                                    You can check it out via this [link](https://onokana8.github.io/SolarPanelsNasa/2024/05/30/Analyzing-extracted-Data-handling-with-Power-BI-and-Python.html)
                                    Note: We use a free model so generation could take a little bit time to give you answer.
                                        """
                                    st.markdown(text)
                        except Exception as e:
                            st.write("Authentication Error:  {}".format(e))
    @staticmethod
    def test():
        """
        for test
        """
        API_KEY = os.getenv("OPENROUTER_API_KEY")
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)

        st.write(f"test of status : {response.status_code}")
        st.json(response.json())


if __name__ == '__main__':
    suggestions = AgentSunAI()
    suggestions.household_use()
