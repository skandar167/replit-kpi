import streamlit as st
import pandas as pd
import numpy as np
import authentication
import admin
import dashboard
import simulation
import optimization
import database
import kpi_selector
import advanced_kpis
import plotly.express as px


# Configure the page
st.set_page_config(
    page_title="KPI Monitoring and Optimization Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state variables if they don't exist
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Function to display the welcome page
def show_welcome_page():
    st.title("Welcome to the Process Engineering KPI Platform")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Key Performance Indicators in Process Engineering
        
        Key Performance Indicators (KPIs) are crucial metrics that help organizations in the process engineering industries 
        evaluate their success at reaching targets. They are essential tools for monitoring performance and making strategic decisions.
        
        ### KPIs in Various Industries:
        
        #### Oil and Gas
        - Production efficiency
        - Equipment reliability
        - Energy consumption
        - Process safety metrics
        - Greenhouse gas emissions
        
        #### Food and Beverage
        - Yield rates
        - Production throughput
        - Quality consistency
        - Waste reduction
        - Energy efficiency
        
        #### Pharmaceutical
        - Batch cycle time
        - Right-first-time production
        - Compliance metrics
        - Yield consistency
        - Resource utilization
        
        This platform helps you track, analyze, and optimize your process KPIs to achieve better operational performance.
        """)
    
    with col2:
        st.subheader("Account Access")
        
        col_login, col_signup = st.columns(2)
        
        with col_login:
            if st.button("Sign In", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
        
        with col_signup:
            if st.button("Sign Up", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()

# Main application logic
def main():
    # Initialize the database connection
    database.init_connection()
    
    # Check if the page state is defined
    if 'page' not in st.session_state:
        st.session_state.page = "welcome"
    
    # Sidebar navigation (only shown when authenticated)
    if st.session_state.authenticated:
        with st.sidebar:
            st.title(f"Welcome, {st.session_state.username}")
            
            st.write("KPI Management")
            
            if st.button("KPI Dashboard", key="dash_btn"):
                st.session_state.page = "dashboard"
                st.rerun()
            
            if st.button("Sélection KPIs", key="kpi_sel_btn"):
                st.session_state.page = "kpi_selector"
                st.rerun()
            
            if st.button("KPIs Avancés - Saisie", key="adv_kpi_entry_btn"):
                st.session_state.page = "advanced_kpi_entry"
                st.rerun()
            
            if st.button("KPIs Avancés - Dashboard", key="adv_kpi_dash_btn"):
                st.session_state.page = "advanced_kpi_dashboard"
                st.rerun()
            
            st.write("---")
            st.write("Outils d'Analyse")
            
            if st.button("Optimization", key="opt_btn"):
                st.session_state.page = "optimization"
                st.rerun()
            
            if st.button("Simulation", key="sim_btn"):
                st.session_state.page = "simulation"
                st.rerun()
            
            st.write("---")
            
            if st.session_state.is_admin:
                if st.button("User Management", key="admin_btn"):
                    st.session_state.page = "admin_panel"
                    st.rerun()
                st.write("---")
            
            if st.button("Logout", key="logout_btn"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_role = None
                st.session_state.is_admin = False
                st.session_state.page = "welcome"
                st.rerun()
    
    # Page routing
    if st.session_state.page == "welcome":
        show_welcome_page()
    
    elif st.session_state.page == "login":
        authentication.login_page()
    
    elif st.session_state.page == "signup":
        authentication.signup_page()
    
    elif st.session_state.page == "dashboard":
        if st.session_state.authenticated:
            dashboard.show_dashboard()
        else:
            st.error("You need to login first")
            st.session_state.page = "login"
            st.rerun()
    
    elif st.session_state.page == "optimization":
        if st.session_state.authenticated:
            optimization.show_optimization()
        else:
            st.error("You need to login first")
            st.session_state.page = "login"
            st.rerun()
    
    elif st.session_state.page == "simulation":
        if st.session_state.authenticated:
            simulation.show_simulation()
        else:
            st.error("You need to login first")
            st.session_state.page = "login"
            st.rerun()
    
    elif st.session_state.page == "admin_panel":
        if st.session_state.authenticated and st.session_state.is_admin:
            admin.show_admin_panel()
        elif st.session_state.authenticated:
            st.error("You don't have permission to access this page")
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("You need to login first")
            st.session_state.page = "login"
            st.rerun()
    
    elif st.session_state.page == "kpi_selector":
        if st.session_state.authenticated:
            kpi_selector.show_kpi_selector()
        else:
            st.error("You need to login first")
            st.session_state.page = "login"
            st.rerun()
    
    elif st.session_state.page == "advanced_kpi_entry":
        if st.session_state.authenticated:
            advanced_kpis.show_advanced_kpi_entry()
        else:
            st.error("You need to login first")
            st.session_state.page = "login"
            st.rerun()
    
    elif st.session_state.page == "advanced_kpi_dashboard":
        if st.session_state.authenticated:
            advanced_kpis.show_advanced_kpi_dashboard()
        else:
            st.error("You need to login first")
            st.session_state.page = "login"
            st.rerun()

if __name__ == "__main__":
    main()
