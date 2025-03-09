import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import requests
from io import StringIO
import streamlit as st
from babel.numbers import format_currency


@st.cache_data(ttl=3600, show_spinner=False)
# load data
def load_data():
    aqi_df = pd.read_csv("all_data.csv")
    return aqi_df

aqi_df = load_data()

#konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Kualitas Udara",
    page_icon="🌍",
    layout="wide"
)

#judul dashboard
st.title("📊 Analisis Kualitas Udara Beijing Tahun 2013-2017")

#sidebar
st.sidebar.header("🔍Filter Data")
selected_years = st.sidebar.multiselect(
    "Pilih Tahun",
    options=aqi_df['year'].unique(),
    default=[aqi_df['year'].unique()[0]]
)

selected_station = st.sidebar.multiselect(
    "Pilih Kota",
    options=aqi_df['station'].unique(),
    default=aqi_df['station'].unique()
)

#filter data
filtered_data = aqi_df[
    (aqi_df['year'].isin(selected_years)) &
    (aqi_df['station'].isin(selected_station))
]

#membuat tab visualisasi
tab1, tab2, tab3 = st.tabs([
    "Pola Temporal",
    "Perbandingan Kota",
    "Korelasi dengan Cuaca"
])

with tab1:
    st.header("📈 Analisis Temporal Polusi Udara")

    col1, col2 = st.columns(2)
    with col1:
        time_resolution = st.radio(
            "Resolusi Waktu",
            ["Tahunan", "Bulanan", "Per Jam", "Bulan vs Jam", "Kategori AQI"],
            horizontal=True
        )
    
    with col2:
        if time_resolution not in ["Kategori AQI", "Tahunan"]:
            pollutant = st.selectbox(
                "Pilih Polutan",
                ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "AQI"]
            )
        else:
            pollutant = "AQI"

    #visualisasi
    if time_resolution == "Tahunan":
        col_x, col_y = st.columns([3, 1])

        with col_x:
            #tren tahunan
            yearly_data = filtered_data.groupby('year')[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean().reset_index()
            selected_pollutants = st.multiselect(
                "Pilih Polutan untuk Tren Tahunan",
                options=['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'],
                default=['PM2.5', 'PM10'],
                key="yearly_multiselect"
            )
            
            fig = px.line(
                yearly_data.melt(id_vars='year', value_vars=selected_pollutants),
                x='year',
                y='value',
                color='variable',
                markers=True,
                title="Tren Tahunan Konsentrasi Polutan",
                labels={'year': 'Tahun', 'value': 'Konsentrasi', 'variable': 'Polutan'},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_layout(
                xaxis=dict(tickmode='linear', dtick=1),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True, key="tren_tahunan")

        with col_y:    
            #rata-rata aqi per tahun
            yearly_avg = filtered_data.groupby('year', as_index=False)['AQI'].mean()

            st.metric("Rata-rata AQI Tahunan", 
                     f"{filtered_data['AQI'].mean():.1f}",
                     help="Nilai rata-rata AQI untuk tahun terpilih")
            
            st.write("**Polutan Dominan**")
            max_pollutant = yearly_data[selected_pollutants].mean().idxmax()
            st.metric("Polutan Tertinggi", 
                     max_pollutant,
                     delta=f"{yearly_data[max_pollutant].max():.1f} μg/m³")
            
            aqi_max = yearly_avg['AQI'].max()
            st.metric(
                "AQI Tertinggi",
                f"{aqi_max:.1f}",
                delta=f"Tahun {yearly_avg.loc[yearly_avg['AQI'] == aqi_max, 'year'].values[0]}"
            )
             
    elif time_resolution == "Bulanan":
        #tren bulanan
        monthly = filtered_data.groupby(['month', 'year'])[pollutant].mean().reset_index()
        fig = px.line(
            monthly,
            x='month',
            y=pollutant,
            color='year',
            title=f"Trend {pollutant} Bulanan per Tahun",
            labels={'month': 'Bulan', pollutant: 'Konsentrasi'}
        )            
        fig.update_xaxes(tickvals=list(range(1, 13)), 
        ticktext=['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des'])
        st.plotly_chart(fig, use_container_width=True, key="tren_bulanan")

    elif time_resolution == "Per Jam":
        #tren harian
        hourly = filtered_data.groupby(['hour', 'year'])[pollutant].mean().reset_index()
        fig = px.line(
            hourly,
            x='hour',
            y=pollutant,
            color='year',
            title=f"Pola Harian {pollutant} per Tahun",
            labels={'hour': 'Jam', pollutant: 'Konsentrasi'}
        )    
        fig.update_xaxes(tickvals=list(range(0, 24)))
        st.plotly_chart(fig, use_container_width=True, key="tren_harian")

    elif time_resolution == "Bulan vs Jam":
        #heatmap bulan vs jam
        heatmap_data = filtered_data.pivot_table(
            index='hour',
            columns='month',
            values=pollutant,
            aggfunc='mean',
            fill_value=0
        )  

        heatmap_data = heatmap_data.reindex(index=range(0, 24), columns=range(1, 13), fill_value=0)

        fig =px.imshow(
            heatmap_data,
            x=heatmap_data.columns.map(lambda x: f"{x:02d}"),
            y=heatmap_data.index,
            labels=dict(x="Bulan", y="Jam", color="Konsentrasi"),
            color_continuous_scale='Viridis',
            title=f"Distribusi {pollutant} per Jam dan Bulan",
            aspect="auto"
        )

        fig.update_layout(
            xaxis=dict(
                ticktext=['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des'],
                tickvals=heatmap_data.columns,
                title_standoff=20
            ),
            yaxis=dict(
                tickvals=np.arange(0, 24, 2),
                title_standoff=20
            ),
            coloraxis_colorbar=dict(
                title="μg/m³",
                thickness=20,
                len=0.75
            )
        )

        fig.update_traces(
            text=np.round(heatmap_data.values),
            texttemplate="%{text:.0f}",
            hovertemplate="Bulan : %{x}<br>Jam: %{y}<br>Konsentrasi: %{z:.1f} μg/m³"
        )
        st.plotly_chart(fig, use_container_width=True, key="bulan_vs_jam")

    elif time_resolution == "Kategori AQI":
        #distribusi kategori aqi
        aqi_counts = filtered_data['Category_AQI'].value_counts().reset_index()
        fig = px.pie(
            aqi_counts,
            names='Category_AQI',
            values='count',
            title='Distribusi Kategori AQI',
            hole=0.3,
            color='Category_AQI',
            color_discrete_map={
                'Good': 'green',
                'Moderate': 'yellow',
                'Unhealthy for Sensitive Groups': 'orange',
                'Unhealthy': 'red',
                'Hazardous': 'purple'
            },
            labels={'count': 'Jumlah', 'Category_AQI': 'Kategori'}
        )

        fig.update_layout(
            legend=dict(
                title='Kategori',
                orientation='v',
                yanchor='top',
                y=0.5,
                xanchor='right',
                x=1.1,
                font=dict(size=12)
            ),
            uniformtext_minsize=12,
            uniformtext_mode='hide',
            margin=dict(l=20, r=20, b=20, t=40)
        )
        st.plotly_chart(fig, use_container_width=True, key="kategori_aqi")


with tab2:
    st.header("🏙️ Perbandingan Tingkat Polusi Antar Kota")
    
    city_stats = filtered_data.groupby('station')[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean()
    
    #visualisasi heatmap
    fig = px.imshow(city_stats.T,
                    labels=dict(x="Kota", y="Polutan", color="Konsentrasi"),
                    x=city_stats.index,
                    y=city_stats.columns,
                    aspect="auto",
                    color_continuous_scale='Viridis',
                    title="Heatmap Konsentrasi Polutan per Kota"
                    )
    fig.update_layout(
        xaxis=dict(tickangle=45),
        font=dict(size=12),
        height=600 + 20*len(city_stats.columns)
        )
    fig.update_traces(
        text=np.round(city_stats.T.values),
        texttemplate="%{text:.0f}",
        textfont=dict(size=10, color="white")
    )
    st.plotly_chart(fig, use_container_width=True, key="kota_headmap")
    
    #bar chart polutan
    selected_pollutant = st.selectbox("Pilih Polutan untuk Perbandingan", city_stats.columns)
    fig2 = px.bar(city_stats.reset_index(), 
                 x='station', 
                 y=selected_pollutant,
                 title=f"Rata-rata {selected_pollutant} per Stasiun")
    st.plotly_chart(fig2, use_container_width=True, key="polutan_bar")

with tab3:
    st.header("🌤️ Hubungan Kondisi Cuaca dengan Polusi Udara")
    
    #menghitung korelasi polutan dengan faktor cuaca
    corr_matrix = filtered_data[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'WSPM', 'RAIN']].corr()
    
    # visualisasi heatmap
    fig = px.imshow(corr_matrix,
                    labels=dict(x="Variabel", y="Variabel", color="Korelasi"),
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    zmin=-1, 
                    zmax=1,
                    color_continuous_scale="RdBu_r",
                    title="Korelasi antara Polutan dan Faktor Cuaca"
                    )
    fig.update_layout(
        font=dict(size=10),
        height=700,
        width=800,
        margin=dict(l=50, r=50, b=100, t=100)
    )
    fig.update_traces(
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=9, color="black")
    )
    st.plotly_chart(fig, use_container_width=True, key="korelasi_heatmap")

#menampilkan data mentah
if st.checkbox("Tampilkan Data Mentah"):
    st.subheader("Data Mentah")
    st.dataframe(filtered_data)

st.caption('Copyright © Fitria 2025')
