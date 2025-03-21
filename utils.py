import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

# Function to format KPI values
def format_kpi_value(value, unit="%"):
    if isinstance(value, (int, float)):
        if math.isnan(value):
            return "N/A"
        if unit == "%":
            return f"{value:.2f}%"
        else:
            return f"{value:.2f} {unit}"
    return str(value)

# Function to calculate change and trend indicator
def calculate_trend(current_value, previous_value):
    if previous_value is None or not isinstance(previous_value, (int, float)) or not isinstance(current_value, (int, float)):
        return None, ""
    
    change = current_value - previous_value
    percentage_change = (change / previous_value * 100) if previous_value != 0 else 0
    
    if percentage_change > 5:
        trend = "↗️"  # Significant increase
    elif percentage_change > 0:
        trend = "↑"  # Small increase
    elif percentage_change < -5:
        trend = "↘️"  # Significant decrease
    elif percentage_change < 0:
        trend = "↓"  # Small decrease
    else:
        trend = "→"  # No significant change
    
    return change, trend

# Function to create a radar chart
def create_radar_chart(categories, values, title=None):
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
        showlegend=False,
        title=title
    )
    
    return fig

# Function to create a comparison table
def create_comparison_table(df, groupby_column, value_columns):
    # Group by the specified column and calculate averages for value columns
    comparison = df.groupby(groupby_column)[value_columns].mean().reset_index()
    return comparison

# Function to create a trend chart
def create_trend_chart(df, date_column, value_column, title=None):
    # Ensure date column is datetime
    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])
    
    # Sort by date
    df_sorted = df.sort_values(date_column)
    
    # Create line chart
    fig = px.line(df_sorted, x=date_column, y=value_column, title=title)
    
    return fig

# Function to generate recommendations based on KPI values
def generate_recommendations(kpi_values, field):
    recommendations = []
    
    # Common recommendations for all industries
    recommendations.append("General Recommendations:")
    recommendations.append("- Regularly review your KPIs and set improvement targets")
    recommendations.append("- Implement a continuous improvement program")
    recommendations.append("- Train operators on process optimization techniques")
    
    # Industry-specific recommendations
    if field == "Oil and Gas":
        if "flow_efficiency" in kpi_values and kpi_values["flow_efficiency"] < 80:
            recommendations.append("\nFlow Efficiency Improvement:")
            recommendations.append("- Check for leaks in the system")
            recommendations.append("- Optimize pipeline design")
            recommendations.append("- Review pump performance")
        
        if "energy_efficiency" in kpi_values and kpi_values["energy_efficiency"] < 1.5:
            recommendations.append("\nEnergy Efficiency Improvement:")
            recommendations.append("- Implement heat integration")
            recommendations.append("- Check insulation")
            recommendations.append("- Consider waste heat recovery")
    
    elif field == "Food and Beverage":
        if "yield_rate" in kpi_values and kpi_values["yield_rate"] < 90:
            recommendations.append("\nYield Improvement:")
            recommendations.append("- Review raw material quality")
            recommendations.append("- Optimize process parameters")
            recommendations.append("- Reduce material losses")
        
        if "waste_rate" in kpi_values and kpi_values["waste_rate"] > 5:
            recommendations.append("\nWaste Reduction:")
            recommendations.append("- Implement precision dosing")
            recommendations.append("- Optimize batch sizes")
            recommendations.append("- Consider by-product recovery")
    
    elif field == "Pharmaceutical":
        if "yield_efficiency" in kpi_values and kpi_values["yield_efficiency"] < 95:
            recommendations.append("\nYield Optimization:")
            recommendations.append("- Fine-tune reaction parameters")
            recommendations.append("- Review catalyst performance")
            recommendations.append("- Implement PAT (Process Analytical Technology)")
        
        if "right_first_time" in kpi_values and kpi_values["right_first_time"] < 98:
            recommendations.append("\nQuality Improvement:")
            recommendations.append("- Enhance quality control procedures")
            recommendations.append("- Review operator training")
            recommendations.append("- Implement error-proofing")
    
    else:  # Generic recommendations
        if "efficiency" in kpi_values and kpi_values["efficiency"] < 85:
            recommendations.append("\nEfficiency Improvement:")
            recommendations.append("- Identify and eliminate bottlenecks")
            recommendations.append("- Optimize process parameters")
            recommendations.append("- Review equipment maintenance")
        
        if "energy_efficiency" in kpi_values and kpi_values["energy_efficiency"] < 0.7:
            recommendations.append("\nEnergy Efficiency:")
            recommendations.append("- Conduct energy audit")
            recommendations.append("- Identify energy-intensive operations")
            recommendations.append("- Implement energy-saving technologies")
    
    return "\n".join(recommendations)

# Function to check for KPI alerts
def check_kpi_alerts(kpi_values, field):
    alerts = []
    
    # Industry-specific alert thresholds
    if field == "Oil and Gas":
        if "flow_efficiency" in kpi_values and kpi_values["flow_efficiency"] < 70:
            alerts.append(("Flow efficiency is below target (70%)", "warning"))
        if "energy_efficiency" in kpi_values and kpi_values["energy_efficiency"] < 1.0:
            alerts.append(("Energy efficiency is below target (1.0 m³/kWh)", "warning"))
    
    elif field == "Food and Beverage":
        if "yield_rate" in kpi_values and kpi_values["yield_rate"] < 85:
            alerts.append(("Yield rate is below target (85%)", "warning"))
        if "waste_rate" in kpi_values and kpi_values["waste_rate"] > 8:
            alerts.append(("Waste rate is above threshold (8%)", "warning"))
    
    elif field == "Pharmaceutical":
        if "yield_efficiency" in kpi_values and kpi_values["yield_efficiency"] < 92:
            alerts.append(("Yield efficiency is below target (92%)", "warning"))
        if "right_first_time" in kpi_values and kpi_values["right_first_time"] < 95:
            alerts.append(("Right-first-time is below target (95%)", "warning"))
    
    else:  # Generic alerts
        if "efficiency" in kpi_values and kpi_values["efficiency"] < 80:
            alerts.append(("Process efficiency is below target (80%)", "warning"))
        
        if "productivity" in kpi_values and kpi_values["productivity"] < 0.5:
            alerts.append(("Productivity is below target", "warning"))
    
    # Critical alerts (for all industries)
    if "efficiency" in kpi_values and kpi_values["efficiency"] < 60:
        alerts.append(("Critical: Process efficiency is severely degraded", "error"))
    
    return alerts
