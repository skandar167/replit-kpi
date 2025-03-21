import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime, timedelta
import database

def show_simulation():
    st.title("Process Simulation")
    
    # Get user data
    user_data = database.get_user_data(st.session_state.username)
    if not user_data:
        st.error("Error fetching user data")
        return
    
    # Left column for simulation parameters
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Simulation Parameters")
        
        # Different simulation parameters based on industry
        if user_data['field'] == "Oil and Gas":
            simulation_params = get_oil_gas_simulation_params()
        elif user_data['field'] == "Food and Beverage":
            simulation_params = get_food_beverage_simulation_params()
        elif user_data['field'] == "Pharmaceutical":
            simulation_params = get_pharmaceutical_simulation_params()
        else:
            simulation_params = get_generic_simulation_params()
        
        # Simulation duration
        simulation_duration = st.slider("Simulation Duration (minutes)", 1, 10, 5)
        
        # Simulation speed
        simulation_speed = st.select_slider(
            "Simulation Speed",
            options=["Slow", "Normal", "Fast"]
        )
        
        # Speed multiplier
        speed_multiplier = 1
        if simulation_speed == "Slow":
            speed_multiplier = 0.5
        elif simulation_speed == "Fast":
            speed_multiplier = 2
        
        # Disturbance options
        st.subheader("Process Disturbances")
        
        disturbance_type = st.selectbox(
            "Disturbance Type",
            ["None", "Step Change", "Random Fluctuation", "Sinusoidal"]
        )
        
        disturbance_magnitude = st.slider("Disturbance Magnitude (%)", 0, 50, 10)
        
        if disturbance_type == "Step Change":
            disturbance_time = st.slider(
                "Disturbance Time (% of simulation)",
                0, 100, 50
            )
        
        # Button to start simulation
        start_simulation = st.button("Start Simulation", type="primary")
    
    # Right column for simulation visualization
    with col2:
        st.subheader("Simulation Results")
        
        # Create empty placeholders for charts
        line_chart_placeholder = st.empty()
        gauge_chart_placeholder = st.empty()
        summary_placeholder = st.empty()
        
        # If start button is clicked, run simulation
        if start_simulation:
            # Run simulation
            simulation_results = run_simulation(
                simulation_params,
                simulation_duration,
                speed_multiplier,
                disturbance_type,
                disturbance_magnitude,
                disturbance_time if disturbance_type == "Step Change" else 50,
                line_chart_placeholder,
                gauge_chart_placeholder,
                user_data['field']
            )
            
            # Save simulation results to database
            simulation_data = {
                "username": st.session_state.username,
                "field": user_data['field'],
                "date": datetime.now(),
                "simulation_type": user_data['field'],
                "duration": simulation_duration,
                "parameters": str(simulation_params),
                "disturbance_type": disturbance_type,
                "disturbance_magnitude": disturbance_magnitude,
                "efficiency": simulation_results["efficiency"],
                "stability": simulation_results["stability"]
            }
            
            database.save_simulation_data(simulation_data)
            
            # Display summary
            with summary_placeholder.container():
                st.subheader("Simulation Summary")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average Efficiency", f"{simulation_results['efficiency']:.2f}%")
                
                with col2:
                    st.metric("Process Stability", f"{simulation_results['stability']:.2f}%")
                
                with col3:
                    if simulation_results['efficiency'] > 90:
                        st.success("Excellent performance!")
                    elif simulation_results['efficiency'] > 75:
                        st.info("Good performance, but room for improvement.")
                    else:
                        st.warning("Performance below target. Optimization needed.")
                
                st.subheader("Observations")
                st.markdown(generate_observations(
                    simulation_results,
                    disturbance_type,
                    disturbance_magnitude,
                    user_data['field']
                ))

# Function to get simulation parameters for Oil and Gas industry
def get_oil_gas_simulation_params():
    st.write("Oil and Gas Process Parameters")
    
    inlet_flow = st.slider("Inlet Flow Rate (m³/h)", 50, 200, 100)
    inlet_pressure = st.slider("Inlet Pressure (bar)", 1, 50, 25)
    inlet_temperature = st.slider("Inlet Temperature (°C)", 20, 150, 80)
    
    separator_pressure = st.slider("Separator Pressure (bar)", 1, 30, 15)
    
    recycle_ratio = st.slider("Recycle Ratio (%)", 0, 50, 10)
    
    return {
        "inlet_flow": inlet_flow,
        "inlet_pressure": inlet_pressure,
        "inlet_temperature": inlet_temperature,
        "separator_pressure": separator_pressure,
        "recycle_ratio": recycle_ratio
    }

# Function to get simulation parameters for Food and Beverage industry
def get_food_beverage_simulation_params():
    st.write("Food and Beverage Process Parameters")
    
    feed_rate = st.slider("Feed Rate (kg/h)", 100, 1000, 500)
    process_temperature = st.slider("Process Temperature (°C)", 20, 150, 85)
    mixing_speed = st.slider("Mixing Speed (rpm)", 10, 500, 200)
    
    cook_time = st.slider("Cooking Time (min)", 5, 120, 45)
    
    cooling_rate = st.slider("Cooling Rate (°C/min)", 0.5, 10.0, 2.0)
    
    return {
        "feed_rate": feed_rate,
        "process_temperature": process_temperature,
        "mixing_speed": mixing_speed,
        "cook_time": cook_time,
        "cooling_rate": cooling_rate
    }

# Function to get simulation parameters for Pharmaceutical industry
def get_pharmaceutical_simulation_params():
    st.write("Pharmaceutical Process Parameters")
    
    reactor_temperature = st.slider("Reactor Temperature (°C)", 20, 150, 65)
    catalyst_concentration = st.slider("Catalyst Concentration (%)", 0.1, 5.0, 1.5)
    reaction_time = st.slider("Reaction Time (h)", 0.5, 24.0, 8.0)
    
    agitation_speed = st.slider("Agitation Speed (rpm)", 50, 500, 250)
    
    ph_value = st.slider("pH Value", 2.0, 12.0, 7.0)
    
    return {
        "reactor_temperature": reactor_temperature,
        "catalyst_concentration": catalyst_concentration,
        "reaction_time": reaction_time,
        "agitation_speed": agitation_speed,
        "ph_value": ph_value
    }

# Function to get generic simulation parameters
def get_generic_simulation_params():
    st.write("Process Parameters")
    
    input_rate = st.slider("Input Rate", 10, 100, 50)
    temperature = st.slider("Process Temperature", 20, 150, 80)
    pressure = st.slider("Process Pressure", 1, 50, 25)
    
    residence_time = st.slider("Residence Time", 1, 60, 30)
    
    mixing_factor = st.slider("Mixing Factor", 0, 100, 50)
    
    return {
        "input_rate": input_rate,
        "temperature": temperature,
        "pressure": pressure,
        "residence_time": residence_time,
        "mixing_factor": mixing_factor
    }

# Function to run the simulation
def run_simulation(params, duration, speed_multiplier, disturbance_type, disturbance_magnitude, 
                   disturbance_time, line_chart_placeholder, gauge_chart_placeholder, field):
    # Convert duration to seconds for simulation
    duration_seconds = duration * 60
    
    # Calculate number of data points based on speed
    num_points = int(duration_seconds / (1/speed_multiplier))
    
    # Initialize time points
    time_points = np.linspace(0, duration_seconds, num_points)
    
    # Initialize data arrays
    input_values = np.ones(num_points)
    output_values = np.ones(num_points)
    efficiency_values = np.ones(num_points)
    
    # Calculate disturbance point
    disturbance_point = int(num_points * disturbance_time / 100)
    
    # Create base values based on industry
    if field == "Oil and Gas":
        base_input = params["inlet_flow"]
        base_output = base_input * (0.8 + 0.1 * params["separator_pressure"] / 30)
        
        # Temperature effect
        temp_factor = params["inlet_temperature"] / 100
        base_output *= (0.8 + 0.4 * temp_factor)
        
        # Recycle effect
        recycle_factor = 1 - params["recycle_ratio"] / 200  # Higher recycle ratio slightly decreases output
        base_output *= recycle_factor
        
    elif field == "Food and Beverage":
        base_input = params["feed_rate"]
        temp_factor = min(1, params["process_temperature"] / 100)
        mix_factor = min(1, params["mixing_speed"] / 300)
        time_factor = min(1, params["cook_time"] / 60)
        
        base_output = base_input * 0.7 * temp_factor * mix_factor * time_factor
        
    elif field == "Pharmaceutical":
        base_input = 100  # Fixed batch size assumption
        temp_factor = params["reactor_temperature"] / 100
        catalyst_factor = params["catalyst_concentration"] / 2.5
        time_factor = min(1, params["reaction_time"] / 12)
        
        base_output = base_input * 0.6 * temp_factor * catalyst_factor * time_factor
        
    else:  # Generic
        base_input = params["input_rate"]
        temp_factor = params["temperature"] / 100
        pressure_factor = params["pressure"] / 30
        
        base_output = base_input * 0.7 * temp_factor * pressure_factor
    
    # Set initial values
    input_values[0] = base_input
    output_values[0] = base_output
    efficiency_values[0] = (output_values[0] / input_values[0]) * 100
    
    # Create empty dataframe for visualization
    df = pd.DataFrame({
        'Time': [0],
        'Input': [input_values[0]],
        'Output': [output_values[0]],
        'Efficiency': [efficiency_values[0]]
    })
    
    # Function for updating chart
    def create_line_chart(df):
        fig = px.line(df, x='Time', y=['Input', 'Output', 'Efficiency'],
                      labels={'value': 'Value', 'Time': 'Time (s)'},
                      title='Process Simulation')
        fig.update_layout(legend_title_text='Parameter')
        return fig
    
    # Function for updating gauge
    def create_gauge_chart(efficiency):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=efficiency,
            title={'text': "Process Efficiency"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 60], 'color': "red"},
                    {'range': [60, 80], 'color': "orange"},
                    {'range': [80, 90], 'color': "yellow"},
                    {'range': [90, 100], 'color': "green"}
                ]
            }
        ))
        return fig
    
    # Display initial charts
    line_chart_placeholder.plotly_chart(create_line_chart(df), use_container_width=True)
    gauge_chart_placeholder.plotly_chart(create_gauge_chart(efficiency_values[0]), use_container_width=True)
    
    # Simulation loop
    for i in range(1, num_points):
        # Apply disturbance to input
        if disturbance_type == "Step Change" and i >= disturbance_point:
            disturbance_factor = 1 + (disturbance_magnitude / 100)
            input_values[i] = base_input * disturbance_factor
        elif disturbance_type == "Random Fluctuation":
            random_factor = 1 + (np.random.random() - 0.5) * 2 * (disturbance_magnitude / 100)
            input_values[i] = base_input * random_factor
        elif disturbance_type == "Sinusoidal":
            sin_factor = 1 + np.sin(i/num_points * 10 * np.pi) * (disturbance_magnitude / 100)
            input_values[i] = base_input * sin_factor
        else:
            input_values[i] = base_input
        
        # Calculate output with some dynamics (first-order response)
        if field == "Oil and Gas":
            # First order response with time constant
            time_constant = 0.1  # Faster response
            output_values[i] = output_values[i-1] + (base_output * (input_values[i] / base_input) - output_values[i-1]) * time_constant
            
            # Add some noise
            output_values[i] += np.random.normal(0, base_output * 0.01)
            
        elif field == "Food and Beverage":
            # First order response with time constant
            time_constant = 0.05  # Even faster response
            output_values[i] = output_values[i-1] + (base_output * (input_values[i] / base_input) - output_values[i-1]) * time_constant
            
            # Add some noise
            output_values[i] += np.random.normal(0, base_output * 0.02)
            
        elif field == "Pharmaceutical":
            # First order response with time constant
            time_constant = 0.03  # Slow response (pharmaceutical processes are often slower)
            output_values[i] = output_values[i-1] + (base_output * (input_values[i] / base_input) - output_values[i-1]) * time_constant
            
            # Add some noise (less noise in pharmaceutical processes due to tight control)
            output_values[i] += np.random.normal(0, base_output * 0.005)
            
        else:  # Generic
            # First order response with time constant
            time_constant = 0.08
            output_values[i] = output_values[i-1] + (base_output * (input_values[i] / base_input) - output_values[i-1]) * time_constant
            
            # Add some noise
            output_values[i] += np.random.normal(0, base_output * 0.015)
        
        # Calculate efficiency
        efficiency_values[i] = (output_values[i] / input_values[i]) * 100
        
        # Update dataframe
        new_row = pd.DataFrame({
            'Time': [time_points[i]],
            'Input': [input_values[i]],
            'Output': [output_values[i]],
            'Efficiency': [efficiency_values[i]]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Update charts every few iterations to avoid excessive rendering
        if i % max(1, int(num_points / 50)) == 0 or i == num_points - 1:
            line_chart_placeholder.plotly_chart(create_line_chart(df), use_container_width=True)
            gauge_chart_placeholder.plotly_chart(create_gauge_chart(efficiency_values[i]), use_container_width=True)
            
            # Control simulation speed
            time.sleep(0.1 / speed_multiplier)
    
    # Calculate final metrics
    avg_efficiency = np.mean(efficiency_values)
    stability = 100 - (np.std(efficiency_values) / avg_efficiency * 100)
    
    return {
        "efficiency": avg_efficiency,
        "stability": stability,
        "data": df
    }

# Function to generate observations based on simulation results
def generate_observations(results, disturbance_type, disturbance_magnitude, field):
    observations = []
    
    # Efficiency observations
    if results['efficiency'] > 90:
        observations.append("✅ **High Efficiency**: The process maintained excellent efficiency throughout the simulation.")
    elif results['efficiency'] > 80:
        observations.append("✅ **Good Efficiency**: The process maintained good efficiency levels.")
    elif results['efficiency'] > 70:
        observations.append("⚠️ **Moderate Efficiency**: The process efficiency is acceptable but could be improved.")
    else:
        observations.append("❌ **Low Efficiency**: The process efficiency is below target levels. Process optimization is recommended.")
    
    # Stability observations
    if results['stability'] > 95:
        observations.append("✅ **Excellent Stability**: The process demonstrated very high stability despite disturbances.")
    elif results['stability'] > 85:
        observations.append("✅ **Good Stability**: The process maintained good stability.")
    elif results['stability'] > 75:
        observations.append("⚠️ **Moderate Stability**: The process showed some instability in response to disturbances.")
    else:
        observations.append("❌ **Poor Stability**: The process demonstrated significant instability. Control system tuning is recommended.")
    
    # Disturbance response observations
    if disturbance_type != "None":
        if disturbance_magnitude > 30:
            if results['stability'] > 80:
                observations.append(f"✅ **Excellent Disturbance Handling**: The process handled {disturbance_type.lower()} disturbances of {disturbance_magnitude}% magnitude very well.")
            else:
                observations.append(f"⚠️ **Disturbance Sensitivity**: The process was significantly affected by {disturbance_type.lower()} disturbances of {disturbance_magnitude}% magnitude.")
        else:
            if results['stability'] > 80:
                observations.append(f"✅ **Good Disturbance Handling**: The process effectively managed {disturbance_type.lower()} disturbances.")
            else:
                observations.append(f"⚠️ **Control Improvement Needed**: The process showed sensitivity to even small {disturbance_type.lower()} disturbances.")
    
    # Industry-specific observations
    if field == "Oil and Gas":
        if results['efficiency'] < 80:
            observations.append("🔍 **Recovery Optimization**: Consider optimizing separation conditions to improve product recovery.")
        if results['stability'] < 85:
            observations.append("🔄 **Flow Control**: Implement advanced flow control strategies to improve process stability.")
    
    elif field == "Food and Beverage":
        if results['efficiency'] < 85:
            observations.append("🍲 **Yield Improvement**: Evaluate cooking parameters to optimize product yield.")
        if results['stability'] < 90:
            observations.append("🌡️ **Temperature Control**: Improve temperature control systems for more consistent product quality.")
    
    elif field == "Pharmaceutical":
        if results['efficiency'] < 90:
            observations.append("⚗️ **Reaction Optimization**: Fine-tune reaction conditions to improve API yield.")
        if results['stability'] < 95:
            observations.append("📊 **Process Control**: Implement tighter process control to meet pharmaceutical quality requirements.")
    
    return "\n\n".join(observations)
