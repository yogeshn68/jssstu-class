import streamlit as st


def style_background_home():

    st.markdown("""
        <style>

        .stApp {
            background: white !important;
        }

        .stApp div[data-testid="stColumn"]{
            background-color:white !important;
            padding:2.5rem !important;
            border-radius:3rem !important;
            border:1px solid #E5E7EB !important;
        }

        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():

    st.markdown("""
        <style>

        .stApp {
            background:white !important;
        }

        </style>
    """, unsafe_allow_html=True)


def style_base_layout():

    st.markdown("""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        #MainMenu,
        footer,
        header{
            visibility:hidden;
        }

        html,
        body,
        [class*="css"]{
            font-family:'Poppins',sans-serif !important;
        }

        .block-container{
            padding-top:1.5rem !important;
        }

        h1{
            font-family:'Poppins',sans-serif !important;
            font-size:3rem !important;
            font-weight:700 !important;
            color:black !important;
        }

        h2{
            font-family:'Poppins',sans-serif !important;
            font-size:2rem !important;
            font-weight:600 !important;
            color:black !important;
        }

        h3,h4,h5,h6,p,label{
            font-family:'Poppins',sans-serif !important;
            color:black !important;
        }

        /* ALL BUTTONS */

        .stButton > button{
            width:100%;
            background:white !important;
            color:black !important;
            border:1px solid #D1D5DB !important;
            border-radius:25px !important;
            font-weight:500 !important;
            padding:10px 20px !important;
        }

        .stButton > button:hover{
            background:#F3F4F6 !important;
            color:black !important;
            border:1px solid #9CA3AF !important;
        }

        /* SELECT BOX */

        .stSelectbox div[data-baseweb="select"]{
            border-radius:15px !important;
        }

        /* INPUTS */

        .stTextInput input{
            border-radius:15px !important;
        }

        </style>
    """, unsafe_allow_html=True)