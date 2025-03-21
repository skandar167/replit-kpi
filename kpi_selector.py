
import streamlit as st
import database
from datetime import datetime

def show_kpi_selector():
    st.title("Sélection des KPIs")
    
    # Get user data
    user_data = database.get_user_data(st.session_state.username)
    if not user_data:
        st.error("Erreur lors de la récupération des données utilisateur")
        return
    
    # Get current user KPI preferences
    user_kpi_prefs = database.get_user_kpi_preferences(st.session_state.username)
    
    st.write("Sélectionnez les KPIs que vous souhaitez calculer et afficher dans votre tableau de bord:")
    
    # Define available KPIs based on industry
    kpis_all = {
        "Général": {
            "oee": ("Prediction de Production", "Mesure l'efficacité globale d'un équipement en prenant en compte la disponibilité, la performance et la qualité."),
            "yield": ("Rendement (Yield)", "Indique le pourcentage de produits conformes par rapport au total produit."),
            "fpy": ("First Pass Yield (FPY)", "Mesure le pourcentage de produits qui passent la production sans nécessiter de retouches."),
            "cycle_time": ("Temps de Cycle", "Représente le temps moyen nécessaire pour produire une unité."),
            "productivity": ("Productivité", "Évalue la quantité produite par unité de temps ou par employé."),
            "defect_rate": ("Taux de Rebuts", "Mesure le pourcentage d'unités non conformes ou rejetées."),
            "nq_cost": ("Coûts de Non-Qualité", "Évalue l'impact financier des défauts de production."),
            "equipment_availability": ("Disponibilité des Équipements", "Part du temps durant lequel l'équipement est opérationnel."),
            "equipment_utilization": ("Taux d'Utilisation des Équipements", "Mesure l'usage effectif des équipements."),
            "on_time_delivery": ("Taux de Livraison à Temps", "Évalue l'efficacité du processus logistique."),
            "order_lead_time": ("Délais de Commande", "Temps moyen entre la réception de la commande et la livraison."),
            "maintenance_cost": ("Coûts de Maintenance", "Impact des coûts de maintenance sur la production."),
            "inventory_turnover": ("Rotation des Stocks", "Mesure la fréquence de renouvellement des stocks."),
            "safety_incidents": ("Incidents de Sécurité", "Suivi des accidents de travail."),
            "absence_rate": ("Taux d'Absence", "Pourcentage d'heures d'absence par rapport aux heures planifiées."),
            "roi_improvement": ("ROI Projets d'Amélioration", "Retour sur investissement des projets d'amélioration."),
            "flow_efficiency": ("Efficacité de Flux", "Mesure l'efficacité de la circulation des fluides."),
            "energy_efficiency": ("Efficacité Énergétique", "Évalue l'énergie consommée par rapport à la production.")
        },
        "Food and Beverage": {
            "yield_rate": ("Taux de Rendement", "Pourcentage de produit final obtenu à partir des matières premières."),
            "waste_rate": ("Taux de Déchets", "Pourcentage de déchets générés pendant la production."),
            "water_efficiency": ("Efficacité Hydrique", "Quantité d'eau utilisée par unité produite.")
        },
        "Pharmaceutical": {
            "yield_efficiency": ("Efficacité de Rendement", "Rendement réel par rapport au rendement théorique."),
            "production_rate": ("Taux de Production", "Quantité produite par unité de temps."),
            "right_first_time": ("Bon du Premier Coup", "Pourcentage de produits conformes dès la première fabrication.")
        }
    }
    
    # Combine general KPIs with industry-specific ones
    available_kpis = {**kpis_all["Général"]}
    if user_data['field'] in kpis_all:
        available_kpis.update(kpis_all[user_data['field']])
    
    # Create form for KPI selection
    with st.form("kpi_selection_form"):
        selected_kpis = {}
        
        st.subheader("KPIs généraux")
        cols = st.columns(2)
        kpi_idx = 0
        
        # Show general KPIs
        for kpi_id, (kpi_name, kpi_desc) in kpis_all["Général"].items():
            with cols[kpi_idx % 2]:
                # Check if the KPI was previously selected
                is_selected = kpi_id in user_kpi_prefs if user_kpi_prefs else False
                selected_kpis[kpi_id] = st.checkbox(
                    kpi_name, 
                    value=is_selected,
                    help=kpi_desc
                )
            kpi_idx += 1
        
        # Show industry-specific KPIs if applicable
        if user_data['field'] in kpis_all:
            st.subheader(f"KPIs spécifiques à {user_data['field']}")
            industry_kpis = kpis_all[user_data['field']]
            
            cols = st.columns(2)
            kpi_idx = 0
            
            for kpi_id, (kpi_name, kpi_desc) in industry_kpis.items():
                with cols[kpi_idx % 2]:
                    # Check if the KPI was previously selected
                    is_selected = kpi_id in user_kpi_prefs if user_kpi_prefs else False
                    selected_kpis[kpi_id] = st.checkbox(
                        kpi_name,
                        value=is_selected,
                        help=kpi_desc
                    )
                kpi_idx += 1
        
        if st.form_submit_button("Enregistrer les préférences"):
            # Save the preferences
            success = database.save_user_kpi_preferences(
                st.session_state.username, 
                {k: v for k, v in selected_kpis.items() if v}  # Only keep selected KPIs
            )
            
            if success:
                st.success("Préférences de KPI enregistrées avec succès!")
                # Log the activity
                database.log_user_activity(
                    st.session_state.username,
                    "kpi_preferences_update",
                    f"Updated KPI preferences: {', '.join([k for k, v in selected_kpis.items() if v])}"
                )
                st.rerun()
            else:
                st.error("Erreur lors de l'enregistrement des préférences")
