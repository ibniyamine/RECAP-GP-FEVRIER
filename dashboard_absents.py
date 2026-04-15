import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Absences",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1f77b4;
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 1rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
    }
    
    .data-table {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stDataFrame {
        border-radius: 10px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Titre du dashboard
st.markdown('<h1 class="main-header">📊 Dashboard des Absences</h1>', unsafe_allow_html=True)

# Chargement des données
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('clients_numero_absents_mars_2026.csv', sep=';')
        # Nettoyage des données
        df = df.dropna(subset=['Client'])
        df['Client'] = df['Client'].str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

# Charger les données
df = load_data()

if df.empty:
    st.error("Impossible de charger les données. Vérifiez que le fichier 'absents.csv' est dans le même répertoire.")
    st.stop()

# Sidebar avec filtres
st.sidebar.markdown('<div class="sidebar-title">🔍 Filtres</div>', unsafe_allow_html=True)

# Filtre multi-sélection sur les clients
clients_disponibles = sorted(df['Client'].unique())
clients_selectionnes = st.sidebar.multiselect(
    "Sélectionner les clients",
    options=clients_disponibles,
    default=[],  # Champ vide par défaut
    key="client_filter"
)

# Appliquer les filtres
df_filtre = df.copy()
if clients_selectionnes:
    df_filtre = df_filtre[df_filtre['Client'].isin(clients_selectionnes)]

# KPIs
st.markdown("## 📈 Indicateurs Clés")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Total Absences</div>
        <div class="metric-value">{}</div>
    </div>
    """.format(len(df_filtre)), unsafe_allow_html=True)

with col2:
    nb_clients = df_filtre['Client'].nunique()
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Clients Concernés</div>
        <div class="metric-value">{}</div>
    </div>
    """.format(nb_clients), unsafe_allow_html=True)

with col3:
    if len(df_filtre) > 0:
        moyenne_par_client = len(df_filtre) / nb_clients if nb_clients > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Moyenne/Client</div>
            <div class="metric-value">{:.1f}</div>
        </div>
        """.format(moyenne_par_client), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Moyenne/Client</div>
            <div class="metric-value">0</div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    pourcentage_filtre = (len(df_filtre) / len(df) * 100) if len(df) > 0 else 0
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">% du Total</div>
        <div class="metric-value">{:.1f}%</div>
    </div>
    """.format(pourcentage_filtre), unsafe_allow_html=True)

# Visualisations
st.markdown("## 📊 Visualisations")

# Graphique en barres par client
if len(df_filtre) > 0:
    # Préparation des données pour le graphique
    client_counts = df_filtre['Client'].value_counts().reset_index()
    client_counts.columns = ['Client', 'Nombre d\'absences']
    
    # Limiter aux 15 premiers clients pour une meilleure lisibilité
    if len(client_counts) > 15:
        client_counts_top = client_counts.head(15)
        autres_count = client_counts.iloc[15:]['Nombre d\'absences'].sum()
        client_counts_top = pd.concat([
            client_counts_top,
            pd.DataFrame([{'Client': 'Autres', 'Nombre d\'absences': autres_count}])
        ])
    else:
        client_counts_top = client_counts
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_bar = px.bar(
            client_counts_top,
            x='Client',
            y='Nombre d\'absences',
            title="Répartition des absences par client",
            color='Nombre d\'absences',
            color_continuous_scale='Blues',
            height=400
        )
        fig_bar.update_layout(
            xaxis_title="Clients",
            yaxis_title="Nombre d'absences",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Graphique en camembert
        fig_pie = px.pie(
            client_counts_top.head(10),  # Top 10 pour le camembert
            values='Nombre d\'absences',
            names='Client',
            title="Top 10 Clients",
            height=400
        )
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Tableau des données filtrées
st.markdown("## 📋 Données Détaillées")

if len(df_filtre) > 0:
    # Statistiques supplémentaires
    col1, col3 = st.columns(2)
    
    with col1:
        st.info(f"**Client avec le plus d'absences:** {df_filtre['Client'].value_counts().index[0]} ({df_filtre['Client'].value_counts().iloc[0]} absences)")

    
    with col3:
        st.info(f"**Période analysée:** Mars 2026")
    
    # Tableau interactif
    st.markdown('<div class="data-table">', unsafe_allow_html=True)
    
    # Préparation des données pour l'affichage
    display_df = df_filtre.copy()
    display_df = display_df.reset_index(drop=True)
    display_df.index = display_df.index + 1  # Commencer à 1
    
    # Affichage du tableau avec st.dataframe pour l'interactivité
    st.dataframe(
        display_df,
        column_config={
            "Client": st.column_config.TextColumn("Client", width="medium"),
            "Numero": st.column_config.TextColumn("Numéro", width="small"),
            "Matricule": st.column_config.TextColumn("Matricule", width="medium"),
            "present": st.column_config.TextColumn("Présence", width="small")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Options d'export
    col1, col2 = st.columns(2)
    
    with col1:
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les données filtrées (CSV)",
            data=csv,
            file_name='absences_filtrees.csv',
            mime='text/csv',
        )
    
    with col2:
        # Statistiques détaillées
        with st.expander("📊 Statistiques détaillées"):
            stats_par_client = df_filtre.groupby('Client').agg({
                'Matricule': 'count',
                'Numero': 'nunique'
            }).rename(columns={
                'Matricule': 'Nombre d\'absences',
                'Numero': 'Nombre de numéros uniques'
            }).sort_values('Nombre d\'absences', ascending=False)
            
            st.write(stats_par_client)
else:
    st.warning("Aucune donnée à afficher. Veuillez sélectionner au moins un client dans le filtre.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d; padding: 1rem;'>"
    "Dashboard des Absences - Février 2026 | "
    "Généré avec Streamlit"
    "</div>",
    unsafe_allow_html=True
)
