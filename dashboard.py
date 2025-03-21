import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import database
from datetime import datetime, timedelta

def show_dashboard():
    st.title("KPI Dashboard")

    # Get user data
    user_data = database.get_user_data(st.session_state.username)
    if not user_data:
        st.error("Error fetching user data")
        return

    # Get user's advanced KPI data
    kpi_data = database.get_user_extended_kpi_data(st.session_state.username)

    if not kpi_data or len(kpi_data) == 0:
        st.info("No KPI data available. Please enter your process data in the Advanced KPIs section to see metrics.")
        return

    # Convert to dataframe for easier filtering
    records = []
    for entry in kpi_data:
        record = {
            'date': entry['date'],
            'process_name': entry['process_name'],
            **entry['kpi_data']  # Unpack the KPI data
        }
        records.append(record)
    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'])

    # Filters section
    st.subheader("Select Data to Display")
    col1, col2 = st.columns(2)

    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=df['date'].max().date(),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date()
        )

    with col2:
        process_names = sorted(df['process_name'].unique())
        selected_process = st.selectbox(
            "Select Process",
            process_names
        )

    # Filter data based on selection
    filtered_data = df[
        (df['date'].dt.date == selected_date) &
        (df['process_name'] == selected_process)
    ]

    if len(filtered_data) == 0:
        st.warning("No data available for the selected date and process.")
        return

    # Display KPI summary for selected data
    st.subheader("KPI Summary")
    latest_data = filtered_data.iloc[0]

    # Get user data for field info
    user_data = database.get_user_data(st.session_state.username)
    field = user_data['field'] if user_data else "Generic"

    # Display all available KPIs in the filtered data
    st.write("Available KPIs:")
    for key in latest_data.index:
        if isinstance(latest_data[key], (int, float)) and key not in ['date']:
            st.metric(key.replace('_', ' ').title(), f"{latest_data[key]:.2f}")

    if field == "Oil and Gas":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Flow Efficiency", f"{latest_data.get('flow_efficiency', 0):.2f}%")
        with col2:
            st.metric("Energy Efficiency", f"{latest_data.get('energy_efficiency', 0):.2f} m³/kWh")
        with col3:
            st.metric("Temperature", f"{latest_data.get('temperature', 0):.2f}°C")

    elif field == "Food and Beverage":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Yield Rate", f"{latest_data.get('yield_rate', 0):.2f}%")
        with col2:
            st.metric("Waste Rate", f"{latest_data.get('waste_rate', 0):.2f}%")
        with col3:
            st.metric("Water Efficiency", f"{latest_data.get('water_efficiency', 0):.2f} kg/m³")
        with col4:
            st.metric("Energy Efficiency", f"{latest_data.get('energy_efficiency', 0):.2f} kg/kWh")

    elif field == "Pharmaceutical":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Yield Efficiency", f"{latest_data.get('yield_efficiency', 0):.2f}%")
        with col2:
            st.metric("Production Rate", f"{latest_data.get('production_rate', 0):.2f} kg/h")
        with col3:
            st.metric("Right First Time", f"{latest_data.get('right_first_time', 0):.2f}%")

    else:  # Generic KPIs
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Efficiency", f"{latest_data.get('efficiency', 0):.2f}%")
        with col2:
            st.metric("Productivity", f"{latest_data.get('productivity', 0):.2f} units/h")
        with col3:
            st.metric("Energy Efficiency", f"{latest_data.get('energy_efficiency', 0):.2f} units/kWh")

    # Display trends
    st.subheader("Historical Trends")
    process_data = df[df['process_name'] == selected_process].copy()
    process_data = process_data.sort_values('date')

    # Create trend chart based on industry
    if field == "Oil and Gas":
        fig = px.line(process_data, x='date', y=['flow_efficiency', 'energy_efficiency'],
                     title=f"KPI Trends for {selected_process}")
    elif field == "Food and Beverage":
        fig = px.line(process_data, x='date', y=['yield_rate', 'waste_rate'],
                     title=f"KPI Trends for {selected_process}")
    elif field == "Pharmaceutical":
        fig = px.line(process_data, x='date', y=['yield_efficiency', 'right_first_time'],
                     title=f"KPI Trends for {selected_process}")
    else:
        fig = px.line(process_data, x='date', y=['efficiency', 'productivity'],
                     title=f"KPI Trends for {selected_process}")

    st.plotly_chart(fig, use_container_width=True)


def show_kpi_entry_form(user_data):
    st.subheader("Enter Process Data")
    
    with st.form("kpi_entry_form"):
        # Common inputs for all industries
        date = st.date_input("Date", value=datetime.now())
        process_name = st.text_input("Process Name")
        
        # Industry-specific inputs
        if user_data['field'] == "Oil and Gas":
            inlet_flow = st.number_input("Inlet Flow (m³/h)", min_value=0.0, format="%.2f")
            outlet_flow = st.number_input("Outlet Flow (m³/h)", min_value=0.0, format="%.2f")
            temperature = st.number_input("Process Temperature (°C)", format="%.2f")
            pressure = st.number_input("Process Pressure (bar)", format="%.2f")
            energy_consumption = st.number_input("Energy Consumption (kWh)", min_value=0.0, format="%.2f")
            
            # Calculate KPIs
            if st.form_submit_button("Calculate KPIs"):
                if not process_name:
                    st.error("Please enter a process name")
                    return
                
                # Calculate KPIs
                flow_efficiency = (outlet_flow / inlet_flow * 100) if inlet_flow > 0 else 0
                energy_efficiency = (outlet_flow / energy_consumption) if energy_consumption > 0 else 0
                
                # Prepare data for database
                kpi_data = {
                    "username": st.session_state.username,
                    "field": user_data['field'],
                    "date": date,
                    "process_name": process_name,
                    "inlet_flow": inlet_flow,
                    "outlet_flow": outlet_flow,
                    "temperature": temperature,
                    "pressure": pressure,
                    "energy_consumption": energy_consumption,
                    "flow_efficiency": flow_efficiency,
                    "energy_efficiency": energy_efficiency
                }
                
                # Save to database
                if database.save_kpi_data(kpi_data):
                    st.success("KPI data saved successfully!")
                    st.rerun()
                else:
                    st.error("Error saving KPI data")
        
        elif user_data['field'] == "Food and Beverage":
            raw_material = st.number_input("Raw Material Input (kg)", min_value=0.0, format="%.2f")
            final_product = st.number_input("Final Product Output (kg)", min_value=0.0, format="%.2f")
            energy_consumption = st.number_input("Energy Consumption (kWh)", min_value=0.0, format="%.2f")
            water_usage = st.number_input("Water Usage (m³)", min_value=0.0, format="%.2f")
            waste_generated = st.number_input("Waste Generated (kg)", min_value=0.0, format="%.2f")
            
            # Calculate KPIs
            if st.form_submit_button("Calculate KPIs"):
                if not process_name:
                    st.error("Please enter a process name")
                    return
                
                # Calculate KPIs
                yield_rate = (final_product / raw_material * 100) if raw_material > 0 else 0
                waste_rate = (waste_generated / raw_material * 100) if raw_material > 0 else 0
                water_efficiency = (final_product / water_usage) if water_usage > 0 else 0
                energy_efficiency = (final_product / energy_consumption) if energy_consumption > 0 else 0
                
                # Prepare data for database
                kpi_data = {
                    "username": st.session_state.username,
                    "field": user_data['field'],
                    "date": date,
                    "process_name": process_name,
                    "raw_material": raw_material,
                    "final_product": final_product,
                    "energy_consumption": energy_consumption,
                    "water_usage": water_usage,
                    "waste_generated": waste_generated,
                    "yield_rate": yield_rate,
                    "waste_rate": waste_rate,
                    "water_efficiency": water_efficiency,
                    "energy_efficiency": energy_efficiency
                }
                
                # Save to database
                if database.save_kpi_data(kpi_data):
                    st.success("KPI data saved successfully!")
                    st.rerun()
                else:
                    st.error("Error saving KPI data")
        
        elif user_data['field'] == "Pharmaceutical":
            batch_size = st.number_input("Batch Size (kg)", min_value=0.0, format="%.2f")
            actual_yield = st.number_input("Actual Yield (kg)", min_value=0.0, format="%.2f")
            theoretical_yield = st.number_input("Theoretical Yield (kg)", min_value=0.0, format="%.2f")
            cycle_time = st.number_input("Cycle Time (hours)", min_value=0.0, format="%.2f")
            defect_rate = st.number_input("Defect Rate (%)", min_value=0.0, max_value=100.0, format="%.2f")
            
            # Calculate KPIs
            if st.form_submit_button("Calculate KPIs"):
                if not process_name:
                    st.error("Please enter a process name")
                    return
                
                # Calculate KPIs
                yield_efficiency = (actual_yield / theoretical_yield * 100) if theoretical_yield > 0 else 0
                production_rate = (actual_yield / cycle_time) if cycle_time > 0 else 0
                right_first_time = 100 - defect_rate
                
                # Prepare data for database
                kpi_data = {
                    "username": st.session_state.username,
                    "field": user_data['field'],
                    "date": date,
                    "process_name": process_name,
                    "batch_size": batch_size,
                    "actual_yield": actual_yield,
                    "theoretical_yield": theoretical_yield,
                    "cycle_time": cycle_time,
                    "defect_rate": defect_rate,
                    "yield_efficiency": yield_efficiency,
                    "production_rate": production_rate,
                    "right_first_time": right_first_time
                }
                
                # Save to database
                if database.save_kpi_data(kpi_data):
                    st.success("KPI data saved successfully!")
                    st.rerun()
                else:
                    st.error("Error saving KPI data")
        
        else:  # Generic form for other industries
            input_quantity = st.number_input("Input Quantity", min_value=0.0, format="%.2f")
            output_quantity = st.number_input("Output Quantity", min_value=0.0, format="%.2f")
            energy_consumption = st.number_input("Energy Consumption", min_value=0.0, format="%.2f")
            process_time = st.number_input("Process Time (hours)", min_value=0.0, format="%.2f")
            
            # Calculate KPIs
            if st.form_submit_button("Calculate KPIs"):
                if not process_name:
                    st.error("Please enter a process name")
                    return
                
                # Calculate KPIs
                efficiency = (output_quantity / input_quantity * 100) if input_quantity > 0 else 0
                productivity = (output_quantity / process_time) if process_time > 0 else 0
                energy_efficiency = (output_quantity / energy_consumption) if energy_consumption > 0 else 0
                
                # Prepare data for database
                kpi_data = {
                    "username": st.session_state.username,
                    "field": user_data['field'],
                    "date": date,
                    "process_name": process_name,
                    "input_quantity": input_quantity,
                    "output_quantity": output_quantity,
                    "energy_consumption": energy_consumption,
                    "process_time": process_time,
                    "efficiency": efficiency,
                    "productivity": productivity,
                    "energy_efficiency": energy_efficiency
                }
                
                # Save to database
                if database.save_kpi_data(kpi_data):
                    st.success("KPI data saved successfully!")
                    st.rerun()
                else:
                    st.error("Error saving KPI data")

def show_process_performance(kpi_data):
    st.subheader("Process Performance")
    
    # Convert to dataframe
    df = pd.DataFrame(kpi_data)
    
    # Extract field
    field = df.iloc[0]['field']
    
    # Create performance radar chart based on industry
    if field == "Oil and Gas":
        # Create radar chart
        categories = ['Flow Efficiency', 'Energy Efficiency', 'Temperature Control', 'Pressure Control']
        
        # Calculate normalized values (0-100 scale)
        flow_eff = df['flow_efficiency'].mean()  # Already percentage
        
        # Normalize energy efficiency to 0-100 scale
        energy_values = df['energy_efficiency']
        energy_eff = (energy_values / energy_values.max() * 100).mean() if energy_values.max() > 0 else 0
        
        # Temperature stability (100 - standard deviation percentage)
        temp_std = df['temperature'].std() if 'temperature' in df.columns else 0
        temp_mean = df['temperature'].mean() if 'temperature' in df.columns else 1
        temp_stability = 100 - (temp_std / temp_mean * 100) if temp_mean > 0 else 0
        
        # Pressure stability (100 - standard deviation percentage)
        pressure_std = df['pressure'].std() if 'pressure' in df.columns else 0
        pressure_mean = df['pressure'].mean() if 'pressure' in df.columns else 1
        pressure_stability = 100 - (pressure_std / pressure_mean * 100) if pressure_mean > 0 else 0
        
        values = [flow_eff, energy_eff, temp_stability, pressure_stability]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Performance',
            line_color='rgb(31, 119, 180)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif field == "Food and Beverage":
        # Create radar chart
        categories = ['Yield Rate', 'Waste Reduction', 'Water Efficiency', 'Energy Efficiency']
        
        # Calculate normalized values (0-100 scale)
        yield_rate = df['yield_rate'].mean()  # Already percentage
        
        # Waste reduction (100 - waste rate)
        waste_reduction = 100 - df['waste_rate'].mean() if 'waste_rate' in df.columns else 0
        
        # Normalize water efficiency to 0-100 scale
        water_values = df['water_efficiency'] if 'water_efficiency' in df.columns else pd.Series([0])
        water_eff = (water_values / water_values.max() * 100).mean() if water_values.max() > 0 else 0
        
        # Normalize energy efficiency to 0-100 scale
        energy_values = df['energy_efficiency'] if 'energy_efficiency' in df.columns else pd.Series([0])
        energy_eff = (energy_values / energy_values.max() * 100).mean() if energy_values.max() > 0 else 0
        
        values = [yield_rate, waste_reduction, water_eff, energy_eff]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Performance',
            line_color='rgb(31, 119, 180)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif field == "Pharmaceutical":
        # Create radar chart
        categories = ['Yield Efficiency', 'Production Rate', 'Right First Time', 'Cycle Time Efficiency']
        
        # Calculate normalized values (0-100 scale)
        yield_eff = df['yield_efficiency'].mean() if 'yield_efficiency' in df.columns else 0
        right_first_time = df['right_first_time'].mean() if 'right_first_time' in df.columns else 0
        
        # Normalize production rate to 0-100 scale
        prod_values = df['production_rate'] if 'production_rate' in df.columns else pd.Series([0])
        prod_rate = (prod_values / prod_values.max() * 100).mean() if prod_values.max() > 0 else 0
        
        # Cycle time efficiency
        cycle_values = df['cycle_time'] if 'cycle_time' in df.columns else pd.Series([0])
        min_cycle = cycle_values.min() if not cycle_values.empty else 0
        cycle_eff = (min_cycle / cycle_values.mean() * 100) if cycle_values.mean() > 0 else 0
        
        values = [yield_eff, prod_rate, right_first_time, cycle_eff]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Performance',
            line_color='rgb(31, 119, 180)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Generic radar chart
        # Create radar chart
        categories = ['Efficiency', 'Productivity', 'Energy Efficiency', 'Time Efficiency']
        
        # Calculate normalized values (0-100 scale)
        efficiency = df['efficiency'].mean() if 'efficiency' in df.columns else 0
        
        # Normalize productivity to 0-100 scale
        prod_values = df['productivity'] if 'productivity' in df.columns else pd.Series([0])
        productivity = (prod_values / prod_values.max() * 100).mean() if prod_values.max() > 0 else 0
        
        # Normalize energy efficiency to 0-100 scale
        energy_values = df['energy_efficiency'] if 'energy_efficiency' in df.columns else pd.Series([0])
        energy_eff = (energy_values / energy_values.max() * 100).mean() if energy_values.max() > 0 else 0
        
        # Time efficiency
        time_values = df['process_time'] if 'process_time' in df.columns else pd.Series([0])
        min_time = time_values.min() if not time_values.empty else 0
        time_eff = (min_time / time_values.mean() * 100) if time_values.mean() > 0 else 0
        
        values = [efficiency, productivity, energy_eff, time_eff]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Performance',
            line_color='rgb(31, 119, 180)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display process comparison table
    st.subheader("Process Comparison")
    
    # Group by process name and calculate averages for numeric columns only
    if 'process_name' in df.columns:
        # Get only numeric columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        
        # Make sure we have numeric columns to operate on
        if len(numeric_columns) > 0:
            # Include process_name column for grouping
            columns_to_use = ['process_name'] + [col for col in numeric_columns if col != 'process_name']
            df_numeric = df[columns_to_use]
            
            # Group by process_name and calculate mean of numeric columns
            process_comparison = df_numeric.groupby('process_name').mean().reset_index()
            
            # Display comparison table
            st.dataframe(process_comparison, use_container_width=True)
        else:
            st.info("No numeric data available for comparison")
    else:
        st.info("No process name data available for comparison")

def show_trends(kpi_data):
    st.subheader("KPI Trends")
    
    # Convert to dataframe
    df = pd.DataFrame(kpi_data)
    
    # Ensure date is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
    
    # Extract field
    field = df.iloc[0]['field']
    
    # Display trends based on industry
    if field == "Oil and Gas":
        # Flow efficiency trend
        if 'flow_efficiency' in df.columns:
            st.subheader("Flow Efficiency Trend")
            fig = px.line(df, x='date', y='flow_efficiency', title='Flow Efficiency Over Time')
            fig.update_layout(yaxis_title='Flow Efficiency (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Energy efficiency trend
        if 'energy_efficiency' in df.columns:
            st.subheader("Energy Efficiency Trend")
            fig = px.line(df, x='date', y='energy_efficiency', title='Energy Efficiency Over Time')
            fig.update_layout(yaxis_title='Energy Efficiency (m³/kWh)')
            st.plotly_chart(fig, use_container_width=True)
    
    elif field == "Food and Beverage":
        # Yield rate trend
        if 'yield_rate' in df.columns:
            st.subheader("Yield Rate Trend")
            fig = px.line(df, x='date', y='yield_rate', title='Yield Rate Over Time')
            fig.update_layout(yaxis_title='Yield Rate (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Waste rate trend
        if 'waste_rate' in df.columns:
            st.subheader("Waste Rate Trend")
            fig = px.line(df, x='date', y='waste_rate', title='Waste Rate Over Time')
            fig.update_layout(yaxis_title='Waste Rate (%)')
            st.plotly_chart(fig, use_container_width=True)
    
    elif field == "Pharmaceutical":
        # Yield efficiency trend
        if 'yield_efficiency' in df.columns:
            st.subheader("Yield Efficiency Trend")
            fig = px.line(df, x='date', y='yield_efficiency', title='Yield Efficiency Over Time')
            fig.update_layout(yaxis_title='Yield Efficiency (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Right first time trend
        if 'right_first_time' in df.columns:
            st.subheader("Right First Time Trend")
            fig = px.line(df, x='date', y='right_first_time', title='Right First Time Over Time')
            fig.update_layout(yaxis_title='Right First Time (%)')
            st.plotly_chart(fig, use_container_width=True)
    
    else:  # Generic trends
        # Efficiency trend
        if 'efficiency' in df.columns:
            st.subheader("Efficiency Trend")
            fig = px.line(df, x='date', y='efficiency', title='Efficiency Over Time')
            fig.update_layout(yaxis_title='Efficiency (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Productivity trend
        if 'productivity' in df.columns:
            st.subheader("Productivity Trend")
            fig = px.line(df, x='date', y='productivity', title='Productivity Over Time')
            fig.update_layout(yaxis_title='Productivity (units/h)')
            st.plotly_chart(fig, use_container_width=True)

def show_recommendations(kpi_data, user_data):
    st.subheader("Recommendations")
    
    # Convert to dataframe
    df = pd.DataFrame(kpi_data)
    
    # Extract field
    field = df.iloc[0]['field']
    
    # Generate recommendations based on industry and KPI values
    if field == "Oil and Gas":
        # Check flow efficiency
        if 'flow_efficiency' in df.columns:
            flow_eff = df['flow_efficiency'].mean()
            if flow_eff < 80:
                st.info("🔍 **Flow Efficiency Improvement**: Your flow efficiency is below optimal levels. Consider these actions:")
                st.markdown("""
                - Check for leaks in the system
                - Optimize pipeline design to reduce pressure drops
                - Evaluate pump performance and maintenance schedules
                - Implement flow control optimization strategies
                """)
        
        # Check energy efficiency
        if 'energy_efficiency' in df.columns:
            # Compare to industry benchmarks
            energy_eff = df['energy_efficiency'].mean()
            if energy_eff < 1.5:  # Example threshold
                st.info("⚡ **Energy Efficiency Opportunity**: Your energy consumption could be optimized:")
                st.markdown("""
                - Evaluate heat integration opportunities
                - Check equipment insulation 
                - Implement energy recovery systems
                - Optimize operating conditions (temperature, pressure)
                - Consider upgrading to more efficient equipment
                """)
    
    elif field == "Food and Beverage":
        # Check yield rate
        if 'yield_rate' in df.columns:
            yield_rate = df['yield_rate'].mean()
            if yield_rate < 90:
                st.info("🌾 **Yield Improvement Potential**: Your yield rate has room for improvement:")
                st.markdown("""
                - Review raw material quality control procedures
                - Optimize process parameters (temperature, mixing time)
                - Check for product loss points in the process
                - Implement statistical process control
                - Consider equipment modifications to reduce material losses
                """)
        
        # Check waste rate
        if 'waste_rate' in df.columns:
            waste_rate = df['waste_rate'].mean()
            if waste_rate > 5:
                st.info("♻️ **Waste Reduction Opportunity**: Your waste rate is above optimal levels:")
                st.markdown("""
                - Implement more precise dosing systems
                - Optimize batch sizes to reduce leftover materials
                - Review handling procedures to minimize product damage
                - Consider by-product valorization opportunities
                - Implement lean manufacturing principles
                """)
    
    elif field == "Pharmaceutical":
        # Check yield efficiency
        if 'yield_efficiency' in df.columns:
            yield_eff = df['yield_efficiency'].mean()
            if yield_eff < 95:
                st.info("🧪 **Yield Optimization Potential**: Your pharmaceutical yield can be improved:")
                st.markdown("""
                - Review reaction conditions and parameters
                - Evaluate catalyst performance and loading
                - Check for impurity formation pathways
                - Implement Process Analytical Technology (PAT)
                - Consider reaction mechanism optimization
                """)
        
        # Check right first time
        if 'right_first_time' in df.columns:
            rft = df['right_first_time'].mean()
            if rft < 98:
                st.info("✅ **Quality Improvement Opportunity**: Your right-first-time rate can be enhanced:")
                st.markdown("""
                - Implement more robust quality control procedures
                - Review operator training programs
                - Consider automated inspection systems
                - Implement error-proofing mechanisms
                - Review batch records for common deviation patterns
                """)
    
    else:  # Generic recommendations
        # Check efficiency
        if 'efficiency' in df.columns:
            efficiency = df['efficiency'].mean()
            if efficiency < 85:
                st.info("📈 **Efficiency Improvement Potential**: Your process efficiency has room for optimization:")
                st.markdown("""
                - Conduct a detailed process analysis to identify bottlenecks
                - Review equipment performance and maintenance schedules
                - Optimize process parameters
                - Consider automation opportunities
                - Implement continuous improvement methodologies
                """)
        
        # Check energy efficiency
        if 'energy_efficiency' in df.columns:
            energy_eff = df['energy_efficiency'].mean()
            if energy_eff < df['energy_efficiency'].max() * 0.7:
                st.info("⚡ **Energy Efficiency Opportunity**: Your energy consumption could be optimized:")
                st.markdown("""
                - Conduct an energy audit
                - Identify major energy consumers in the process
                - Implement energy recovery systems
                - Optimize operating schedules
                - Consider equipment upgrades
                """)
    
    # General recommendations for all industries
    st.subheader("General Recommendations")
    st.markdown("""
    📊 **Data Collection Improvement**:
    - Increase data collection frequency
    - Implement automated data collection systems
    - Validate measurement equipment regularly
    
    🔄 **Continuous Improvement**:
    - Establish regular KPI review meetings
    - Set specific targets for each KPI
    - Implement PDCA (Plan-Do-Check-Act) cycles
    
    👥 **Employee Engagement**:
    - Share KPI performance with operators
    - Implement suggestion schemes for process improvements
    - Provide training on process optimization
    """)