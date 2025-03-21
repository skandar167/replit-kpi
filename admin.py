import streamlit as st
import pandas as pd
import database
from datetime import datetime

def show_admin_panel():
    st.title("Admin Panel")
    
    if not st.session_state.is_admin:
        st.error("You don't have permission to access this page")
        return
    
    tab1, tab2, tab3 = st.tabs(["User Management", "System Logs", "KPI Overview"])
    
    with tab1:
        show_user_management()
    
    with tab2:
        show_system_logs()
    
    with tab3:
        show_kpi_overview()

def show_user_management():
    st.header("User Management")
    
    # Get all pending users
    pending_users = database.get_users_by_status("pending")
    
    if pending_users and len(pending_users) > 0:
        st.subheader("Pending Approval Requests")
        for user in pending_users:
            with st.container():
                cols = st.columns([3, 1, 1])
                with cols[0]:
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Field:** {user['field']}")
                    st.write(f"**Requested:** {user['created_at']}")
                
                with cols[1]:
                    if st.button("Approve", key=f"approve_{user['username']}"):
                        if database.update_user_status(user['username'], "approved"):
                            st.success(f"User {user['username']} approved!")
                            st.rerun()
                        else:
                            st.error("Error approving user")
                
                with cols[2]:
                    if st.button("Reject", key=f"reject_{user['username']}"):
                        if database.update_user_status(user['username'], "rejected"):
                            st.success(f"User {user['username']} rejected!")
                            st.rerun()
                        else:
                            st.error("Error rejecting user")
                st.divider()
    else:
        st.info("No pending approval requests")
    
    # Get all approved users
    approved_users = database.get_users_by_status("approved")
    
    st.subheader("Approved Users")
    if approved_users and len(approved_users) > 0:
        user_df = pd.DataFrame(approved_users)
        
        # Remove sensitive information
        if 'password' in user_df.columns:
            user_df = user_df.drop(columns=['password'])
        
        st.dataframe(user_df, use_container_width=True)
    else:
        st.info("No approved users found")

def show_system_logs():
    st.header("System Logs")
    
    # Add date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=None)
    with col2:
        end_date = st.date_input("To", value=None)
    
    # Convert to datetime
    if start_date:
        start_date = datetime.combine(start_date, datetime.min.time())
    if end_date:
        end_date = datetime.combine(end_date, datetime.max.time())
    
    # Get logs with date filter
    logs = database.get_system_logs(start_date, end_date)
    
    if logs and len(logs) > 0:
        log_df = pd.DataFrame(logs)
        st.dataframe(log_df, use_container_width=True)
    else:
        st.info("No logs found for the selected period")

def show_kpi_overview():
    st.header("KPI Overview")
    
    # Get all KPI data across users
    kpi_data = database.get_all_kpi_data()
    
    if kpi_data and len(kpi_data) > 0:
        # Convert to dataframe
        kpi_df = pd.DataFrame(kpi_data)
        
        # Summary statistics
        st.subheader("Summary Statistics")
        st.dataframe(kpi_df.describe(), use_container_width=True)
        
        # KPI by industry field
        st.subheader("KPIs by Industry Field")
        
        # Find numeric columns only for aggregation
        numeric_columns = kpi_df.select_dtypes(include=['int64', 'float64']).columns
        
        # Group by field and calculate averages (numeric columns only)
        if len(numeric_columns) > 0:
            field_averages = kpi_df.groupby('field')[numeric_columns].mean().reset_index()
            
            # Create bar chart if we have numeric data
            if not field_averages.empty and len(field_averages.columns) > 1:
                st.bar_chart(field_averages.set_index('field'))
            else:
                st.info("No numeric KPI data available for visualization")
        else:
            st.info("No numeric KPI data available for analysis")
            field_averages = pd.DataFrame()
        
        # KPI by user (numeric columns only)
        st.subheader("KPIs by User")
        if len(numeric_columns) > 0:
            user_averages = kpi_df.groupby('username')[numeric_columns].mean().reset_index()
        else:
            user_averages = pd.DataFrame()
        st.dataframe(user_averages, use_container_width=True)
    else:
        st.info("No KPI data available yet")
