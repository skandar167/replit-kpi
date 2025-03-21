import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
import database

def show_optimization():
    st.title("Process Optimization")
    
    # Get user data
    user_data = database.get_user_data(st.session_state.username)
    if not user_data:
        st.error("Error fetching user data")
        return
    
    # Get user's KPI data
    kpi_data = database.get_user_kpi_data(st.session_state.username)
    
    if not kpi_data or len(kpi_data) == 0:
        st.warning("No process data available for optimization. Please add process data in the Dashboard first.")
        return
    
    # Convert to dataframe
    df = pd.DataFrame(kpi_data)
    
    # Extract field
    field = df.iloc[0]['field']
    
    # Left column for optimization targets and options
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Optimization Targets")
        
        # Select optimization target based on industry
        if field == "Oil and Gas":
            optimization_target = st.selectbox(
                "Select Parameter to Optimize",
                ["Flow Efficiency", "Energy Efficiency"]
            )
            
            if optimization_target == "Flow Efficiency":
                target_column = "flow_efficiency"
                unit = "%"
            else:  # Energy Efficiency
                target_column = "energy_efficiency"
                unit = "m³/kWh"
            
            # Input variables
            input_variables = st.multiselect(
                "Select Input Variables",
                ["inlet_flow", "outlet_flow", "temperature", "pressure"],
                ["inlet_flow", "temperature"]
            )
            
        elif field == "Food and Beverage":
            optimization_target = st.selectbox(
                "Select Parameter to Optimize",
                ["Yield Rate", "Waste Rate", "Energy Efficiency"]
            )
            
            if optimization_target == "Yield Rate":
                target_column = "yield_rate"
                unit = "%"
            elif optimization_target == "Waste Rate":
                target_column = "waste_rate"
                unit = "%"
            else:  # Energy Efficiency
                target_column = "energy_efficiency"
                unit = "kg/kWh"
            
            # Input variables
            input_variables = st.multiselect(
                "Select Input Variables",
                ["raw_material", "final_product", "energy_consumption", "water_usage"],
                ["raw_material", "energy_consumption"]
            )
            
        elif field == "Pharmaceutical":
            optimization_target = st.selectbox(
                "Select Parameter to Optimize",
                ["Yield Efficiency", "Production Rate", "Right First Time"]
            )
            
            if optimization_target == "Yield Efficiency":
                target_column = "yield_efficiency"
                unit = "%"
            elif optimization_target == "Production Rate":
                target_column = "production_rate"
                unit = "kg/h"
            else:  # Right First Time
                target_column = "right_first_time"
                unit = "%"
            
            # Input variables
            input_variables = st.multiselect(
                "Select Input Variables",
                ["batch_size", "cycle_time", "defect_rate"],
                ["batch_size", "cycle_time"]
            )
            
        else:  # Generic
            optimization_target = st.selectbox(
                "Select Parameter to Optimize",
                ["Efficiency", "Productivity", "Energy Efficiency"]
            )
            
            if optimization_target == "Efficiency":
                target_column = "efficiency"
                unit = "%"
            elif optimization_target == "Productivity":
                target_column = "productivity"
                unit = "units/h"
            else:  # Energy Efficiency
                target_column = "energy_efficiency"
                unit = "units/kWh"
            
            # Input variables
            input_variables = st.multiselect(
                "Select Input Variables",
                ["input_quantity", "output_quantity", "energy_consumption", "process_time"],
                ["input_quantity", "process_time"]
            )
        
        # Optimization method
        optimization_method = st.radio(
            "Optimization Method",
            ["Linear Regression", "Polynomial Regression", "Multi-factor Analysis"]
        )
        
        # Optimization goal
        optimization_goal = st.radio(
            "Optimization Goal",
            ["Maximize", "Minimize", "Target Value"]
        )
        
        if optimization_goal == "Target Value":
            target_value = st.number_input(f"Target Value ({unit})", min_value=0.0, format="%.2f")
        
        # Button to run optimization
        run_optimization = st.button("Run Optimization", type="primary")
    
    # Right column for optimization results
    with col2:
        if run_optimization:
            if target_column not in df.columns:
                st.error(f"Target column '{target_column}' not found in the data")
            elif not all(var in df.columns for var in input_variables):
                st.error("Some input variables are not found in the data")
            elif len(input_variables) == 0:
                st.error("Please select at least one input variable")
            else:
                # Drop rows with NaN in target or input variables
                analysis_df = df.dropna(subset=[target_column] + input_variables)
                
                if len(analysis_df) < 3:
                    st.error("Not enough data points for analysis. Please add more process data.")
                else:
                    show_optimization_results(
                        analysis_df,
                        target_column,
                        input_variables,
                        optimization_method,
                        optimization_goal,
                        target_value if optimization_goal == "Target Value" else None,
                        unit,
                        field
                    )

def show_optimization_results(df, target_column, input_variables, optimization_method, 
                             optimization_goal, target_value, unit, field):
    st.subheader("Optimization Analysis")
    
    # Prepare data
    X = df[input_variables].values
    y = df[target_column].values
    
    # Normalize variable names for display
    display_variables = [var.replace('_', ' ').title() for var in input_variables]
    
    # Apply optimization method
    if optimization_method == "Linear Regression":
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        # Display model quality
        st.markdown(f"**Model R² Score:** {r2:.4f}")
        
        if r2 < 0.5:
            st.warning("The linear model has low explanatory power. Consider using Polynomial Regression or adding more data.")
        
        # Display coefficients
        st.subheader("Model Coefficients")
        coefs = pd.DataFrame({
            'Variable': display_variables,
            'Coefficient': model.coef_
        })
        coefs['Absolute Impact'] = abs(coefs['Coefficient'])
        coefs = coefs.sort_values('Absolute Impact', ascending=False)
        
        st.dataframe(coefs)
        
        # Find optimal values
        find_optimal_values(model, X, input_variables, display_variables, target_column, 
                           optimization_goal, target_value, unit, is_polynomial=False)
        
        # Plot actual vs predicted
        fig = px.scatter(x=y, y=y_pred, 
                        labels={'x': f'Actual {target_column.replace("_", " ").title()} ({unit})', 
                                'y': f'Predicted {target_column.replace("_", " ").title()} ({unit})'},
                        title='Model Fit: Actual vs Predicted')
        fig.add_trace(
            go.Scatter(x=[min(y), max(y)], y=[min(y), max(y)], 
                      mode='lines', name='Perfect Fit', line=dict(dash='dash'))
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif optimization_method == "Polynomial Regression":
        # Transform features to polynomial
        poly = PolynomialFeatures(degree=2, include_bias=False)
        X_poly = poly.fit_transform(X)
        
        # Fit regression model
        model = LinearRegression()
        model.fit(X_poly, y)
        y_pred = model.predict(X_poly)
        r2 = r2_score(y, y_pred)
        
        # Display model quality
        st.markdown(f"**Model R² Score:** {r2:.4f}")
        
        if r2 < 0.5:
            st.warning("Even the polynomial model has low explanatory power. Consider adding more data or different variables.")
        
        # Plot actual vs predicted
        fig = px.scatter(x=y, y=y_pred, 
                        labels={'x': f'Actual {target_column.replace("_", " ").title()} ({unit})', 
                                'y': f'Predicted {target_column.replace("_", " ").title()} ({unit})'},
                        title='Polynomial Model Fit: Actual vs Predicted')
        fig.add_trace(
            go.Scatter(x=[min(y), max(y)], y=[min(y), max(y)], 
                      mode='lines', name='Perfect Fit', line=dict(dash='dash'))
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Find optimal values using grid search for polynomial model
        find_optimal_values_poly(poly, model, X, input_variables, display_variables, 
                                target_column, optimization_goal, target_value, unit)
        
    else:  # Multi-factor Analysis
        # Create correlation matrix
        corr_matrix = df[input_variables + [target_column]].corr()
        
        # Display correlation heatmap
        st.subheader("Correlation Matrix")
        fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r',
                       title='Parameter Correlation Matrix')
        st.plotly_chart(fig, use_container_width=True)
        
        # Display scatter plots for each input variable vs target
        st.subheader("Parameter Relationships")
        
        for i, var in enumerate(input_variables):
            fig = px.scatter(df, x=var, y=target_column, trendline="ols",
                            labels={'x': display_variables[i], 'y': target_column.replace('_', ' ').title()})
            st.plotly_chart(fig, use_container_width=True)
        
        # Fit linear model for reference
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        st.markdown(f"**Reference Linear Model R² Score:** {r2:.4f}")
    
    # Show industry-specific recommendations
    show_industry_recommendations(field, target_column, input_variables, model, X, y, 
                                 optimization_method != "Multi-factor Analysis")

def find_optimal_values(model, X, input_variables, display_variables, target_column, 
                       optimization_goal, target_value, unit, is_polynomial=False):
    st.subheader("Optimal Process Parameters")
    
    # Get min and max values for each input variable
    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    
    # Generate grid of values for optimization
    num_points = 1000
    grid_points = []
    
    for i in range(len(input_variables)):
        grid_points.append(np.linspace(X_min[i], X_max[i], num_points))
    
    # Create all combinations of input variables
    grid = np.meshgrid(*grid_points)
    grid_flat = [g.flatten() for g in grid]
    X_grid = np.column_stack(grid_flat)
    
    # Make predictions for all grid points
    if is_polynomial:
        # For polynomial, this function is expected to be called with already transformed X_grid
        y_grid = model.predict(X_grid)
    else:
        y_grid = model.predict(X_grid)
    
    # Find optimal point based on goal
    if optimization_goal == "Maximize":
        optimal_idx = np.argmax(y_grid)
    elif optimization_goal == "Minimize":
        optimal_idx = np.argmin(y_grid)
    else:  # Target Value
        optimal_idx = np.argmin(np.abs(y_grid - target_value))
    
    # Extract optimal values
    optimal_X = X_grid[optimal_idx]
    optimal_y = y_grid[optimal_idx]
    
    # Display results
    st.markdown(f"**Optimal {target_column.replace('_', ' ').title()}:** {optimal_y:.2f} {unit}")
    
    # Create dataframe for optimal values
    optimal_df = pd.DataFrame({
        'Parameter': display_variables,
        'Optimal Value': optimal_X,
        'Min Value': X_min,
        'Max Value': X_max,
        'Current %': (optimal_X - X_min) / (X_max - X_min) * 100
    })
    
    # Display as table
    st.dataframe(optimal_df)
    
    # Display as gauge charts
    st.subheader("Optimal Parameter Settings")
    
    # Create 2 columns per row
    for i in range(0, len(input_variables), 2):
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(input_variables):
                with cols[j]:
                    # Calculate percentage within range
                    var_idx = i + j
                    var_range = X_max[var_idx] - X_min[var_idx]
                    var_pct = (optimal_X[var_idx] - X_min[var_idx]) / var_range * 100 if var_range > 0 else 50
                    
                    # Create gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=optimal_X[var_idx],
                        title={'text': display_variables[var_idx]},
                        gauge={
                            'axis': {'range': [X_min[var_idx], X_max[var_idx]]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [X_min[var_idx], X_min[var_idx] + var_range*0.25], 'color': "lightgray"},
                                {'range': [X_min[var_idx] + var_range*0.75, X_max[var_idx]], 'color': "lightgray"}
                            ]
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)

def find_optimal_values_poly(poly, model, X, input_variables, display_variables, 
                           target_column, optimization_goal, target_value, unit):
    st.subheader("Optimal Process Parameters (Polynomial Model)")
    
    # Get min and max values for each input variable
    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    
    # Generate grid of values for optimization
    num_points = 20  # Reduced for polynomial to avoid too many combinations
    grid_points = []
    
    for i in range(len(input_variables)):
        grid_points.append(np.linspace(X_min[i], X_max[i], num_points))
    
    # Create all combinations of input variables
    grid = np.meshgrid(*grid_points)
    grid_flat = [g.flatten() for g in grid]
    X_grid = np.column_stack(grid_flat)
    
    # Transform to polynomial features
    X_grid_poly = poly.transform(X_grid)
    
    # Make predictions for all grid points
    y_grid = model.predict(X_grid_poly)
    
    # Find optimal point based on goal
    if optimization_goal == "Maximize":
        optimal_idx = np.argmax(y_grid)
    elif optimization_goal == "Minimize":
        optimal_idx = np.argmin(y_grid)
    else:  # Target Value
        optimal_idx = np.argmin(np.abs(y_grid - target_value))
    
    # Extract optimal values
    optimal_X = X_grid[optimal_idx]
    optimal_y = y_grid[optimal_idx]
    
    # Display results
    st.markdown(f"**Optimal {target_column.replace('_', ' ').title()}:** {optimal_y:.2f} {unit}")
    
    # Create dataframe for optimal values
    optimal_df = pd.DataFrame({
        'Parameter': display_variables,
        'Optimal Value': optimal_X,
        'Min Value': X_min,
        'Max Value': X_max,
        'Current %': (optimal_X - X_min) / (X_max - X_min) * 100
    })
    
    # Display as table
    st.dataframe(optimal_df)
    
    # Display optimal settings
    st.subheader("Optimal Parameter Settings")
    
    # Create response surface plots for pairs of variables if we have more than one variable
    if len(input_variables) >= 2:
        # Choose first two variables for demonstration
        var1_idx, var2_idx = 0, 1
        var1, var2 = input_variables[var1_idx], input_variables[var2_idx]
        var1_display, var2_display = display_variables[var1_idx], display_variables[var2_idx]
        
        # Create grid for these two variables
        x_grid = np.linspace(X_min[var1_idx], X_max[var1_idx], 50)
        y_grid = np.linspace(X_min[var2_idx], X_max[var2_idx], 50)
        xx, yy = np.meshgrid(x_grid, y_grid)
        
        # For other variables, use the optimal value
        grid_data = np.zeros((xx.size, len(input_variables)))
        grid_data[:, var1_idx] = xx.flatten()
        grid_data[:, var2_idx] = yy.flatten()
        
        # Fill other variables with optimal values
        for i in range(len(input_variables)):
            if i != var1_idx and i != var2_idx:
                grid_data[:, i] = optimal_X[i]
        
        # Transform to polynomial and predict
        grid_data_poly = poly.transform(grid_data)
        z = model.predict(grid_data_poly).reshape(xx.shape)
        
        # Create contour plot
        fig = go.Figure(data=
            go.Contour(
                z=z,
                x=x_grid,
                y=y_grid,
                colorscale='Viridis',
                colorbar=dict(title=target_column.replace('_', ' ').title())
            )
        )
        
        # Add optimal point
        fig.add_trace(
            go.Scatter(
                x=[optimal_X[var1_idx]],
                y=[optimal_X[var2_idx]],
                mode='markers',
                marker=dict(color='red', size=10),
                name='Optimal Point'
            )
        )
        
        fig.update_layout(
            title=f'Response Surface for {target_column.replace("_", " ").title()}',
            xaxis_title=var1_display,
            yaxis_title=var2_display
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Create gauge charts for each variable
    for i in range(0, len(input_variables), 2):
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(input_variables):
                with cols[j]:
                    # Calculate percentage within range
                    var_idx = i + j
                    var_range = X_max[var_idx] - X_min[var_idx]
                    var_pct = (optimal_X[var_idx] - X_min[var_idx]) / var_range * 100 if var_range > 0 else 50
                    
                    # Create gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=optimal_X[var_idx],
                        title={'text': display_variables[var_idx]},
                        gauge={
                            'axis': {'range': [X_min[var_idx], X_max[var_idx]]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [X_min[var_idx], X_min[var_idx] + var_range*0.25], 'color': "lightgray"},
                                {'range': [X_min[var_idx] + var_range*0.75, X_max[var_idx]], 'color': "lightgray"}
                            ]
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)

def show_industry_recommendations(field, target_column, input_variables, model, X, y, has_model=True):
    st.subheader("Industry-Specific Recommendations")
    
    recommendations = []
    
    # Common recommendations
    if has_model:
        # Identify most influential variables
        coeffs = model.coef_
        abs_coeffs = np.abs(coeffs)
        sorted_idx = np.argsort(abs_coeffs)[::-1]  # Sort in descending order
        
        most_influential = input_variables[sorted_idx[0]] if len(input_variables) > 0 else None
        second_influential = input_variables[sorted_idx[1]] if len(input_variables) > 1 else None
        
        # Add recommendation based on most influential variable
        if most_influential:
            influence_dir = "positive" if coeffs[sorted_idx[0]] > 0 else "negative"
            recommendations.append(f"**{most_influential.replace('_', ' ').title()}** has the strongest {influence_dir} influence on {target_column.replace('_', ' ').title()}.")
    
    # Industry-specific recommendations
    if field == "Oil and Gas":
        if target_column == "flow_efficiency":
            recommendations.append("**Flow Efficiency Improvement**:")
            recommendations.append("- Ensure proper separator design and operation")
            recommendations.append("- Consider optimizing pressure drop across the system")
            recommendations.append("- Implement regular maintenance to prevent flow restrictions")
            
            if "temperature" in input_variables:
                recommendations.append("- Monitor and control process temperature for optimal separation")
            
            if "pressure" in input_variables:
                recommendations.append("- Maintain optimal pressure conditions for phase separation")
        
        elif target_column == "energy_efficiency":
            recommendations.append("**Energy Efficiency Improvement**:")
            recommendations.append("- Evaluate heat integration opportunities")
            recommendations.append("- Implement energy recovery systems")
            recommendations.append("- Optimize compression and pumping operations")
            
            if "inlet_flow" in input_variables:
                recommendations.append("- Optimize flow rates to balance throughput and energy consumption")
    
    elif field == "Food and Beverage":
        if target_column == "yield_rate":
            recommendations.append("**Yield Rate Optimization**:")
            recommendations.append("- Ensure consistent raw material quality")
            recommendations.append("- Optimize process parameters for maximum conversion")
            recommendations.append("- Implement statistical process control")
            
            if "raw_material" in input_variables:
                recommendations.append("- Consider raw material preparation techniques to improve processability")
                
        elif target_column == "waste_rate":
            recommendations.append("**Waste Reduction Strategies**:")
            recommendations.append("- Implement precision dosing systems")
            recommendations.append("- Optimize batch sizes to reduce leftover materials")
            recommendations.append("- Improve product handling procedures")
            
            if "water_usage" in input_variables:
                recommendations.append("- Implement water recycling and reuse systems")
                
        elif target_column == "energy_efficiency":
            recommendations.append("**Energy Efficiency Improvement**:")
            recommendations.append("- Optimize cooking and cooling cycles")
            recommendations.append("- Implement heat recovery systems")
            recommendations.append("- Ensure proper equipment insulation")
    
    elif field == "Pharmaceutical":
        if target_column == "yield_efficiency":
            recommendations.append("**Yield Optimization Strategies**:")
            recommendations.append("- Fine-tune reaction parameters for maximum API yield")
            recommendations.append("- Implement PAT (Process Analytical Technology)")
            recommendations.append("- Consider continuous manufacturing techniques")
            
            if "batch_size" in input_variables:
                recommendations.append("- Evaluate optimal batch size for maximum yield efficiency")
                
        elif target_column == "production_rate":
            recommendations.append("**Production Rate Improvement**:")
            recommendations.append("- Reduce cycle times through process optimization")
            recommendations.append("- Identify and eliminate bottlenecks")
            recommendations.append("- Implement lean manufacturing principles")
            
            if "cycle_time" in input_variables:
                recommendations.append("- Focus on reducing cycle time which has significant impact on production rate")
                
        elif target_column == "right_first_time":
            recommendations.append("**Quality Improvement Strategies**:")
            recommendations.append("- Implement robust quality-by-design principles")
            recommendations.append("- Enhance operator training programs")
            recommendations.append("- Implement error-proofing mechanisms")
            
            if "defect_rate" in input_variables:
                recommendations.append("- Implement statistical process control to identify and address variations")
    
    else:  # Generic recommendations
        if target_column == "efficiency":
            recommendations.append("**Efficiency Optimization Strategies**:")
            recommendations.append("- Conduct detailed process analysis to identify bottlenecks")
            recommendations.append("- Optimize process parameters")
            recommendations.append("- Consider automation opportunities")
            
        elif target_column == "productivity":
            recommendations.append("**Productivity Improvement Strategies**:")
            recommendations.append("- Reduce cycle times through process optimization")
            recommendations.append("- Optimize resource allocation")
            recommendations.append("- Implement continuous improvement methodologies")
            
        elif target_column == "energy_efficiency":
            recommendations.append("**Energy Efficiency Improvement**:")
            recommendations.append("- Conduct energy audit")
            recommendations.append("- Identify major energy consumers")
            recommendations.append("- Implement energy-saving technologies")
    
    # Display recommendations
    for rec in recommendations:
        st.markdown(rec)
    
    # Implementation plan
    st.subheader("Implementation Plan")
    
    st.markdown("""
    1. **Documentation**: Record the optimization findings in your process documentation
    2. **Small-Scale Testing**: Implement the recommended changes on a small scale first
    3. **Validation**: Validate that the changes produce the expected results
    4. **Full Implementation**: Roll out the changes to the full process
    5. **Monitoring**: Continue to monitor KPIs to ensure sustained improvement
    6. **Feedback Loop**: Use the results to inform future optimization efforts
    """)
