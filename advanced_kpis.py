import streamlit as st

def process_csv_row(row, username):
    """Process a single row from uploaded CSV and save to database"""
    # Get user data and preferences
    user_data = database.get_user_data(username)
    user_kpi_prefs = database.get_user_kpi_preferences(username)
    
    # Initialize KPI data
    kpi_data = {}
    
    # Process OEE data if present
    if "oee" in user_kpi_prefs and all(col in row for col in ["planned_production_time", "actual_runtime", "total_units", "good_units", "theoretical_output"]):
        availability = row['actual_runtime'] / row['planned_production_time'] if row['planned_production_time'] > 0 else 0
        performance = (row['total_units'] / row['theoretical_output']) * (row['planned_production_time'] / row['actual_runtime']) if row['theoretical_output'] > 0 and row['actual_runtime'] > 0 else 0
        quality = row['good_units'] / row['total_units'] if row['total_units'] > 0 else 0
        oee = availability * performance * quality
        
        kpi_data["oee"] = {
            "oee_value": oee * 100,
            "availability": availability * 100,
            "performance": performance * 100,
            "quality": quality * 100
        }
    
    # Process Oil and Gas specific KPIs
    if "flow_efficiency" in user_kpi_prefs and all(col in row for col in ["inlet_flow", "outlet_flow"]):
        flow_eff = (row['outlet_flow'] / row['inlet_flow'] * 100) if row['inlet_flow'] > 0 else 0
        kpi_data["flow_efficiency"] = {"efficiency": flow_eff}
    
    if "energy_efficiency" in user_kpi_prefs and all(col in row for col in ["energy_consumption", "production_output"]):
        energy_eff = (row['production_output'] / row['energy_consumption']) if row['energy_consumption'] > 0 else 0
        kpi_data["energy_efficiency"] = {"efficiency": energy_eff}
    
    # Save to database
    for kpi_type, data in kpi_data.items():
        kpi_entry = {
            "username": username,
            "field": user_data['field'],
            "date": row['Date'],
            "process_name": row['Process_Name'],
            "kpi_type": kpi_type,
            "kpi_data": data
        }
        database.save_extended_kpi_data(kpi_entry)

import pandas as pd
import database
from datetime import datetime

def show_advanced_kpi_entry():
    st.title("Saisie des KPIs - Tableau de Calcul Principal")
    
    # Add CSV template download/upload section
    st.subheader("Import/Export CSV")
    col1, col2 = st.columns(2)
    
    with col1:
        # Get user KPI preferences for CSV template
        user_kpi_prefs = database.get_user_kpi_preferences(st.session_state.username)
        user_data = database.get_user_data(st.session_state.username)
        if user_kpi_prefs:
            # Create CSV template
            csv_template = "Date,Process_Name"
            
            # Add fields for all selected KPIs
            for kpi_type in user_kpi_prefs:
                if kpi_type == "oee":
                    csv_template += ",planned_production_time,actual_runtime,total_units,good_units,theoretical_output"
                elif kpi_type == "yield":
                    csv_template += ",total_units,good_units"
                elif kpi_type == "fpy":
                    csv_template += ",total_units,first_pass_units"
                elif kpi_type == "cycle_time":
                    csv_template += ",production_time,total_units"
                elif kpi_type == "productivity":
                    csv_template += ",total_units,production_time,num_employees"
                elif kpi_type == "defect_rate":
                    csv_template += ",total_units,defective_units"
                elif kpi_type == "nq_cost":
                    csv_template += ",rework_cost,scrap_cost,warranty_cost"
                elif kpi_type == "flow_efficiency":
                    csv_template += ",inlet_flow,outlet_flow"
                elif kpi_type == "energy_efficiency":
                    csv_template += ",energy_consumption,production_output"
                elif kpi_type == "equipment_availability":
                    csv_template += ",planned_time,actual_runtime"
                elif kpi_type == "equipment_utilization":
                    csv_template += ",actual_runtime,total_time_available"
                elif kpi_type == "maintenance_cost":
                    csv_template += ",maintenance_cost,total_units"
                elif kpi_type == "inventory_turnover":
                    csv_template += ",cogs,avg_inventory"
                elif kpi_type == "safety_incidents":
                    csv_template += ",num_accidents,total_hours_worked"
                elif kpi_type == "absence_rate":
                    csv_template += ",absence_hours,planned_hours"
                elif kpi_type == "roi_improvement":
                    csv_template += ",project_cost,project_benefits"
            
            # Add example row
            csv_template += "\nYYYY-MM-DD,Process1"
            
            # Download button
            st.download_button(
                "📥 Télécharger le modèle CSV",
                csv_template,
                "kpi_template.csv",
                "text/csv"
            )
    
    with col2:
        # Upload CSV file
        uploaded_file = st.file_uploader("📤 Importer un fichier CSV", type=['csv'])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if st.button("Traiter les données CSV"):
                    results = []
                    for _, row in df.iterrows():
                        # Process each row and save to database
                        process_csv_row(row, st.session_state.username)
                        results.append({
                            'Date': row['Date'],
                            'Process': row['Process_Name'],
                            'Status': 'Success'
                        })
                    
                    # Show results in a new section
                    st.success("Données importées avec succès!")
                    st.subheader("Résultats de l'importation")
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Add button to view dashboard
                    if st.button("Voir le tableau de bord"):
                        st.session_state.page = "dashboard"
                        st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de l'importation: {str(e)}")
    
    # Get user data
    user_data = database.get_user_data(st.session_state.username)
    if not user_data:
        st.error("Erreur lors de la récupération des données utilisateur")
        return
    
    # Get user KPI preferences
    user_kpi_prefs = database.get_user_kpi_preferences(st.session_state.username)
    
    if not user_kpi_prefs or len(user_kpi_prefs) == 0:
        st.warning("Veuillez d'abord sélectionner les KPIs que vous souhaitez utiliser dans la page 'Sélection des KPIs'")
        if st.button("Aller à la page de sélection des KPIs"):
            st.session_state.page = "kpi_selector"
            st.rerun()
        return
    
    # Display entry forms for each selected KPI
    st.write("Saisissez les données pour calculer les KPIs sélectionnés:")
    
    # Common inputs for all KPIs
    with st.form("advanced_kpi_entry_form"):
        date = st.date_input("Date", value=datetime.now())
        process_name = st.text_input("Nom du Processus/Équipement")
        
        # OEE (Overall Equipment Effectiveness)
        if "oee" in user_kpi_prefs:
            st.subheader("OEE (Overall Equipment Effectiveness)")
            planned_production_time = st.number_input("Temps de production planifié (heures)", min_value=0.0, format="%.2f")
            actual_runtime = st.number_input("Temps de fonctionnement réel (heures)", min_value=0.0, format="%.2f")
            total_units = st.number_input("Nombre total d'unités produites", min_value=0, format="%d")
            good_units = st.number_input("Nombre d'unités conformes", min_value=0, format="%d")
            theoretical_output = st.number_input("Production théorique possible (unités)", min_value=0, format="%d")
        
        # Yield and First Pass Yield
        if "yield" in user_kpi_prefs or "fpy" in user_kpi_prefs:
            st.subheader("Rendement et First Pass Yield")
            if not "oee" in user_kpi_prefs:  # Avoid duplicate inputs if OEE is already selected
                total_units = st.number_input("Nombre total d'unités produites", min_value=0, format="%d")
                good_units = st.number_input("Nombre d'unités conformes", min_value=0, format="%d")
            
            if "fpy" in user_kpi_prefs:
                first_pass_units = st.number_input("Nombre d'unités acceptables dès la première production", 
                                                 min_value=0,format="%d")
        
        # Cycle Time and Productivity
        if "cycle_time" in user_kpi_prefs or "productivity" in user_kpi_prefs:
            st.subheader("Temps de Cycle et Productivité")
            if not ("oee" in user_kpi_prefs or "yield" in user_kpi_prefs or "fpy" in user_kpi_prefs):
                total_units = st.number_input("Nombre total d'unités produites", min_value=0, format="%d")
            
            production_time = st.number_input("Temps total de production (heures)", min_value=0.0, format="%.2f")
            
            if "productivity" in user_kpi_prefs:
                num_employees = st.number_input("Nombre d'employés", min_value=0, format="%d")
        
        # Defect Rate and Quality Costs
        if "defect_rate" in user_kpi_prefs or "nq_cost" in user_kpi_prefs:
            st.subheader("Taux de Rebuts et Coûts de Non-Qualité")
            if not ("oee" in user_kpi_prefs or "yield" in user_kpi_prefs or "fpy" in user_kpi_prefs):
                total_units = st.number_input("Nombre total d'unités produites", min_value=0, format="%d")
                defective_units = st.number_input("Nombre d'unités défectueuses", min_value=0, format="%d")
            else:
                defective_units = total_units - good_units if "good_units" in locals() else 0
            
            if "nq_cost" in user_kpi_prefs:
                rework_cost = st.number_input("Coût de retraitement (€)", min_value=0.0, format="%.2f")
                scrap_cost = st.number_input("Coût des rebuts (€)", min_value=0.0, format="%.2f")
                warranty_cost = st.number_input("Coût des garanties/réclamations (€)", min_value=0.0, format="%.2f")
        
        # Equipment Availability and Utilization
        if "equipment_availability" in user_kpi_prefs or "equipment_utilization" in user_kpi_prefs:
            st.subheader("Disponibilité et Utilisation des Équipements")
            if not "oee" in user_kpi_prefs:
                planned_production_time = st.number_input("Temps de production planifié (heures)", min_value=0.0, format="%.2f")
                actual_runtime = st.number_input("Temps de fonctionnement réel (heures)", min_value=0.0, format="%.2f")
            
            if "equipment_utilization" in user_kpi_prefs:
                total_time_available = st.number_input("Temps total disponible (heures, 24h/jour)", min_value=0.0, format="%.2f")
        
        # Delivery and Order Lead Time
        if "on_time_delivery" in user_kpi_prefs or "order_lead_time" in user_kpi_prefs:
            st.subheader("Livraison et Délais de Commande")
            total_deliveries = st.number_input("Nombre total de livraisons", min_value=0, format="%d")
            on_time_deliveries = st.number_input("Nombre de livraisons à temps", min_value=0, format="%d")
            
            if "order_lead_time" in user_kpi_prefs:
                avg_lead_time = st.number_input("Temps moyen entre commande et livraison (jours)", min_value=0.0, format="%.2f")
        
        # Maintenance Costs
        if "maintenance_cost" in user_kpi_prefs:
            st.subheader("Coûts de Maintenance")
            maintenance_cost = st.number_input("Coût total de maintenance (€)", min_value=0.0, format="%.2f")
            if not ("oee" in user_kpi_prefs or "yield" in user_kpi_prefs or "fpy" in user_kpi_prefs or 
                  "cycle_time" in user_kpi_prefs or "productivity" in user_kpi_prefs):
                total_units = st.number_input("Nombre total d'unités produites", min_value=0, format="%d")
        
        # Inventory Turnover
        if "inventory_turnover" in user_kpi_prefs:
            st.subheader("Rotation des Stocks")
            cogs = st.number_input("Coût des biens vendus (€)", min_value=0.0, format="%.2f")
            avg_inventory = st.number_input("Niveau moyen des stocks (€)", min_value=0.0, format="%.2f")
        
        # Safety Incidents
        if "safety_incidents" in user_kpi_prefs:
            st.subheader("Incidents de Sécurité")
            num_accidents = st.number_input("Nombre d'accidents", min_value=0, format="%d")
            total_hours_worked = st.number_input("Total des heures travaillées", min_value=0.0, format="%.2f")
        
        # Absence Rate
        if "absence_rate" in user_kpi_prefs:
            st.subheader("Taux d'Absence")
            absence_hours = st.number_input("Nombre d'heures d'absence", min_value=0.0, format="%.2f")
            planned_hours = st.number_input("Nombre total d'heures planifiées", min_value=0.0, format="%.2f")
        
        # ROI of Improvement Projects
        if "roi_improvement" in user_kpi_prefs:
            st.subheader("ROI des Projets d'Amélioration")
            project_cost = st.number_input("Coût total du projet (€)", min_value=0.0, format="%.2f")
            project_benefits = st.number_input("Bénéfices nets issus du projet (€)", min_value=0.0, format="%.2f")
        
        # Submit form and calculate KPIs
        if st.form_submit_button("Calculer les KPIs"):
            if not process_name:
                st.error("Veuillez entrer un nom de processus")
                return
            
            # Initialize KPI results
            kpi_results = {}
            
            # Calculate OEE
            if "oee" in user_kpi_prefs:
                if theoretical_output > 0 and planned_production_time > 0:
                    availability = actual_runtime / planned_production_time if planned_production_time > 0 else 0
                    performance = (total_units / theoretical_output) * (planned_production_time / actual_runtime) if theoretical_output > 0 and actual_runtime > 0 else 0
                    quality = good_units / total_units if total_units > 0 else 0
                    oee = availability * performance * quality
                    
                    kpi_results["oee"] = {
                        "oee_value": oee * 100,
                        "availability": availability * 100,
                        "performance": performance * 100,
                        "quality": quality * 100,
                        "planned_time": planned_production_time,
                        "actual_runtime": actual_runtime,
                        "total_units": total_units,
                        "good_units": good_units,
                        "theoretical_output": theoretical_output
                    }
            
            # Calculate Yield
            if "yield" in user_kpi_prefs:
                yield_rate = (good_units / total_units * 100) if total_units > 0 else 0
                kpi_results["yield"] = {
                    "yield_rate": yield_rate,
                    "total_units": total_units,
                    "good_units": good_units
                }
            
            # Calculate First Pass Yield
            if "fpy" in user_kpi_prefs:
                fpy = (first_pass_units / total_units * 100) if total_units > 0 else 0
                kpi_results["fpy"] = {
                    "fpy_rate": fpy,
                    "total_units": total_units,
                    "first_pass_units": first_pass_units
                }
            
            # Calculate Cycle Time
            if "cycle_time" in user_kpi_prefs:
                cycle_time = (production_time / total_units) if total_units > 0 else 0
                kpi_results["cycle_time"] = {
                    "cycle_time_hours": cycle_time,
                    "cycle_time_minutes": cycle_time * 60,
                    "production_time": production_time,
                    "total_units": total_units
                }
            
            # Calculate Productivity
            if "productivity" in user_kpi_prefs:
                productivity_time = total_units / production_time if production_time > 0 else 0
                productivity_employee = total_units / num_employees if num_employees > 0 else 0
                kpi_results["productivity"] = {
                    "productivity_per_hour": productivity_time,
                    "productivity_per_employee": productivity_employee,
                    "total_units": total_units,
                    "production_time": production_time,
                    "num_employees": num_employees
                }
            
            # Calculate Defect Rate
            if "defect_rate" in user_kpi_prefs:
                defect_rate = (defective_units / total_units * 100) if total_units > 0 else 0
                kpi_results["defect_rate"] = {
                    "defect_rate": defect_rate,
                    "total_units": total_units,
                    "defective_units": defective_units
                }
            
            # Calculate Non-Quality Costs
            if "nq_cost" in user_kpi_prefs:
                total_nq_cost = rework_cost + scrap_cost + warranty_cost
                nq_cost_per_unit = total_nq_cost / total_units if total_units > 0 else 0
                kpi_results["nq_cost"] = {
                    "total_nq_cost": total_nq_cost,
                    "nq_cost_per_unit": nq_cost_per_unit,
                    "rework_cost": rework_cost,
                    "scrap_cost": scrap_cost,
                    "warranty_cost": warranty_cost
                }
            
            # Calculate Equipment Availability
            if "equipment_availability" in user_kpi_prefs:
                equipment_availability = (actual_runtime / planned_production_time * 100) if planned_production_time > 0 else 0
                kpi_results["equipment_availability"] = {
                    "availability_rate": equipment_availability,
                    "planned_time": planned_production_time,
                    "actual_runtime": actual_runtime
                }
            
            # Calculate Equipment Utilization
            if "equipment_utilization" in user_kpi_prefs:
                equipment_utilization = (actual_runtime / total_time_available * 100) if total_time_available > 0 else 0
                kpi_results["equipment_utilization"] = {
                    "utilization_rate": equipment_utilization,
                    "actual_runtime": actual_runtime,
                    "total_time_available": total_time_available
                }
            
            # Calculate On-Time Delivery
            if "on_time_delivery" in user_kpi_prefs:
                otd_rate = (on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
                kpi_results["on_time_delivery"] = {
                    "otd_rate": otd_rate,
                    "total_deliveries": total_deliveries,
                    "on_time_deliveries": on_time_deliveries
                }
            
            # Calculate Order Lead Time
            if "order_lead_time" in user_kpi_prefs:
                kpi_results["order_lead_time"] = {
                    "avg_lead_time_days": avg_lead_time
                }
            
            # Calculate Maintenance Cost per Unit
            if "maintenance_cost" in user_kpi_prefs:
                maint_cost_per_unit = maintenance_cost / total_units if total_units > 0 else 0
                kpi_results["maintenance_cost"] = {
                    "total_maintenance_cost": maintenance_cost,
                    "maintenance_cost_per_unit": maint_cost_per_unit,
                    "total_units": total_units
                }
            
            # Calculate Inventory Turnover
            if "inventory_turnover" in user_kpi_prefs:
                inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
                kpi_results["inventory_turnover"] = {
                    "inventory_turnover_ratio": inventory_turnover,
                    "cogs": cogs,
                    "avg_inventory": avg_inventory
                }
            
            # Calculate Safety Incident Rate
            if "safety_incidents" in user_kpi_prefs:
                incident_rate = (num_accidents / total_hours_worked * 1000000) if total_hours_worked > 0 else 0
                kpi_results["safety_incidents"] = {
                    "incident_rate": incident_rate,
                    "num_accidents": num_accidents,
                    "total_hours_worked": total_hours_worked
                }
            
            # Calculate Absence Rate
            if "absence_rate" in user_kpi_prefs:
                absence_rate = (absence_hours / planned_hours * 100) if planned_hours > 0 else 0
                kpi_results["absence_rate"] = {
                    "absence_rate": absence_rate,
                    "absence_hours": absence_hours,
                    "planned_hours": planned_hours
                }
            
            # Calculate ROI of Improvement Projects
            if "roi_improvement" in user_kpi_prefs:
                roi = (project_benefits - project_cost) / project_cost * 100 if project_cost > 0 else 0
                kpi_results["roi_improvement"] = {
                    "roi_percentage": roi,
                    "project_cost": project_cost,
                    "project_benefits": project_benefits,
                    "net_benefit": project_benefits - project_cost
                }
            
            # Save all KPI results to the database
            for kpi_type, kpi_data in kpi_results.items():
                kpi_entry = {
                    "username": st.session_state.username,
                    "field": user_data['field'],
                    "date": date,
                    "process_name": process_name,
                    "kpi_type": kpi_type,
                    "kpi_data": kpi_data
                }
                
                if database.save_extended_kpi_data(kpi_entry):
                    st.success(f"Données du KPI {kpi_type} enregistrées avec succès!")
                else:
                    st.error(f"Erreur lors de l'enregistrement des données du KPI {kpi_type}")
            
            # Log the activity
            database.log_user_activity(
                st.session_state.username,
                "extended_kpi_entry",
                f"Added extended KPI data for process: {process_name}"
            )
            
            # Display summary of results
            st.subheader("Résumé des KPIs calculés")
            results_df = pd.DataFrame([
                {"KPI": k.upper(), "Valeur": list(v.values())[0] if isinstance(v, dict) and len(v) > 0 else v} 
                for k, v in kpi_results.items()
            ])
            st.dataframe(results_df, use_container_width=True)

def show_advanced_kpi_dashboard():
    st.title("Dashboard des KPIs Avancés")
    
    # Get user data
    user_data = database.get_user_data(st.session_state.username)
    if not user_data:
        st.error("Erreur lors de la récupération des données utilisateur")
        return
    
    # Get extended KPI data
    extended_kpi_data = database.get_user_extended_kpi_data(st.session_state.username)
    
    if not extended_kpi_data or len(extended_kpi_data) == 0:
        st.info("Aucune donnée de KPI avancé disponible. Veuillez saisir vos données de processus pour voir les métriques KPI.")
        if st.button("Aller à la page de saisie des KPIs avancés"):
            st.session_state.page = "advanced_kpi_entry"
            st.rerun()
        return
    
    # Group data by KPI type
    kpi_by_type = {}
    for entry in extended_kpi_data:
        kpi_type = entry['kpi_type']
        if kpi_type not in kpi_by_type:
            kpi_by_type[kpi_type] = []
        kpi_by_type[kpi_type].append(entry)
    
    # Display KPI summary cards
    st.subheader("Résumé des KPIs")
    
    col1, col2, col3 = st.columns(3)
    col_idx = 0
    
    # Display all selected KPIs
    user_kpi_prefs = database.get_user_kpi_preferences(st.session_state.username)
    if user_kpi_prefs:
        for kpi_type in user_kpi_prefs:
            kpi_data = database.get_user_kpi_data_by_type(st.session_state.username, kpi_type)
            if kpi_data:
                latest_data = kpi_data[0]
                with eval(f"col{col_idx % 3 + 1}"):
                    if 'efficiency' in latest_data:
                        st.metric(kpi_type.replace('_', ' ').title(), f"{latest_data['efficiency']:.2f}%")
                    elif 'value' in latest_data:
                        st.metric(kpi_type.replace('_', ' ').title(), f"{latest_data['value']:.2f}")
                col_idx += 1
    
    # Define function to get the latest value for a KPI
    def get_latest_kpi_value(kpi_type):
        if kpi_type not in kpi_by_type:
            return None
        
        # Sort by date (most recent first)
        sorted_entries = sorted(kpi_by_type[kpi_type], key=lambda x: x['date'], reverse=True)
        
        if not sorted_entries:
            return None
        
        # Get first key-value pair from the kpi_data
        latest_entry = sorted_entries[0]
        kpi_data = latest_entry['kpi_data']
        
        # Return the first value (usually the main KPI value)
        return list(kpi_data.values())[0] if isinstance(kpi_data, dict) and len(kpi_data) > 0 else None
    
    # Define KPI display names and units
    kpi_display_info = {
        "oee": ("OEE", "%"),
        "yield": ("Rendement", "%"),
        "fpy": ("First Pass Yield", "%"),
        "cycle_time": ("Temps de Cycle", "heures"),
        "productivity": ("Productivité", "unités/h"),
        "defect_rate": ("Taux de Rebuts", "%"),
        "nq_cost": ("Coûts de Non-Qualité", "€"),
        "equipment_availability": ("Disponibilité Équipement", "%"),
        "equipment_utilization": ("Utilisation Équipement", "%"),
        "on_time_delivery": ("Livraison à Temps", "%"),
        "order_lead_time": ("Délai de Commande", "jours"),
        "maintenance_cost": ("Coût Maintenance/Unité", "€"),
        "inventory_turnover": ("Rotation des Stocks", "ratio"),
        "safety_incidents": ("Incidents Sécurité", "par 1M h"),
        "absence_rate": ("Taux d'Absence", "%"),
        "roi_improvement": ("ROI Amélioration", "%")
    }
    
    # Display KPI cards
    for kpi_type in kpi_by_type.keys():
        latest_value = get_latest_kpi_value(kpi_type)
        
        if latest_value is not None:
            display_name, unit = kpi_display_info.get(kpi_type, (kpi_type.upper(), ""))
            
            if col_idx % 3 == 0:
                with col1:
                    st.metric(display_name, f"{latest_value:.2f} {unit}")
            elif col_idx % 3 == 1:
                with col2:
                    st.metric(display_name, f"{latest_value:.2f} {unit}")
            else:
                with col3:
                    st.metric(display_name, f"{latest_value:.2f} {unit}")
            
            col_idx += 1
    
    # Display detailed KPI analysis with tabs
    if kpi_by_type:
        st.subheader("Analyse détaillée des KPIs")
        
        # Create tabs for each KPI type
        kpi_tabs = st.tabs([kpi_display_info.get(kpi_type, (kpi_type.upper(), ""))[0] for kpi_type in kpi_by_type.keys()])
        
        for i, (kpi_type, kpi_entries) in enumerate(kpi_by_type.items()):
            with kpi_tabs[i]:
                display_name, unit = kpi_display_info.get(kpi_type, (kpi_type.upper(), ""))
                
                # Convert to dataframe
                rows = []
                for entry in kpi_entries:
                    row = {
                        "Date": entry['date'],
                        "Processus": entry['process_name'],
                    }
                    # Add all KPI data values
                    for k, v in entry['kpi_data'].items():
                        row[k] = v
                    rows.append(row)
                
                df = pd.DataFrame(rows)
                
                # Sort by date
                if 'Date' in df.columns:
                    df = df.sort_values('Date')
                
                # Display trend chart if we have date and the main value
                main_value_key = list(kpi_entries[0]['kpi_data'].keys())[0] if kpi_entries and 'kpi_data' in kpi_entries[0] else None
                
                if main_value_key and 'Date' in df.columns and main_value_key in df.columns:
                    st.subheader(f"Tendance: {display_name}")
                    
                    import plotly.express as px
                    fig = px.line(df, x='Date', y=main_value_key, title=f"{display_name} - Évolution")
                    fig.update_layout(yaxis_title=f"{display_name} ({unit})")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display the data table
                st.subheader(f"Données détaillées: {display_name}")
                st.dataframe(df, use_container_width=True)