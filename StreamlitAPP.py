import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st

from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQ_Generator import generate_evaluate_chain
from src.mcqgenerator.logger import logging


with open('/Users/itamarlevi/Desktop/MCQ_Generator/response.json','r') as file:
    RESPONSE_JSON = json.load(file)


#creating a title for the app
st.title("Multiple Choice Quiz Generator 🦜🔗")

#Create a form using st.form
with st.form("user_inputs"):
    #File Upload
    uploaded_file = st.file_uploader("Upload a PDF or txt file")

    #Input Fields
    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)

    #Subject
    subject = st.text_input("Insert Subject", max_chars=20)

    #Quiz Complexity
    tone = st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Easy")

    #Add Button
    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text = read_file(uploaded_file)
                # Count tokens and the cost of API call
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )
                    #st.write(response)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            else:
                if isinstance(response, dict):
                    # Extract the quiz data from the response
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            # Display the review in a text box as well
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(response)
