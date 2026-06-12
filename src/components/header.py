import streamlit as st


def header_home():

    logo_url = "https://image-static.collegedunia.com/public/college_data/images/logos/1583130084jssstu2.jpg"

    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:30px">
            <img src='{logo_url}' style='height:100px;' />
            <h1 style='text-align:center; color:#E0E3FF'>JSSSTU CLASS<br/></h1>
        </div>
                
                """, unsafe_allow_html=True)


def header_dashboard():

    logo_url = "https://image-static.collegedunia.com/public/college_data/images/logos/1583130084jssstu2.jpg"
    
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:10px">
            <img src='{logo_url}' style='height:85px;' />
            <h2 style='text-align:left; color:#5865F2'>JSSSTU CLASS<br/></h1>
        </div>   
                
                """, unsafe_allow_html=True)
