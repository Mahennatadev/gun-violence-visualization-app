import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import datetime

# Load dataset
df = pd.read_csv("Data/GunViolenceInUSA.csv")
df['Incident Date'] = pd.to_datetime(df['Incident Date'])
df['Month'] = df['Incident Date'].dt.to_period('M')

# Sidebar for Navigation
with st.sidebar:
    st.header("Final Project Navigation")
    st.subheader("Visualisasi Data IF-45-DSIS.03 [UAI]")

     # Kelompok 1 Section
    st.subheader("Kelompok 1:")
    st.markdown(
        """
        👥 **Anggota Kelompok:**
        - Wahyu Nata Mahendra (1301213101)<br>
        - Muhammad Dzakiyuddin Haidar (1301213048)<br>
        - M. Rafi Athallah (1301210210)
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("---")  # Separator for clarity

    # Visualization Section
    st.subheader("Pilih visualisasi:")
    section = st.radio(
        label="Pilih salah satu visualisasi yang tersedia",
        options=[
            "🗃️ Tentang Dataset",
            "📈 Jumlah Korban per Bulan",
            "📊 Korban per Negara Bagian",
            "📊 Korban per Kota",
            "🗺️ Peta Insiden",
            "📝 Informasi Penting",
        ],
        label_visibility="collapsed",
    )
    
if section == "🗃️ Tentang Dataset":
    st.title("Penjelasan Dataset")
    
    st.image("image6.jpg")
    
    st.write("Dataset ini berisi informasi tentang insiden kekerasan dengan senjata api di Amerika Serikat, dengan total 427 baris data dan 14 kolom. Setiap baris dalam dataset merepresentasikan sebuah insiden, termasuk detail seperti ID insiden, tanggal kejadian, lokasi (negara bagian, kota, atau wilayah), dan alamat. Informasi lainnya mencakup jumlah korban tewas, korban terluka, pelaku tewas, pelaku terluka, dan pelaku yang ditangkap. Selain itu, dataset ini juga mencakup koordinat lokasi (lintang dan bujur) untuk setiap insiden. Beberapa contoh insiden dalam dataset ini menunjukkan berbagai tingkat keparahan, seperti insiden di Fall City, Washington, pada 21 Oktober 2024 yang menyebabkan 5 korban tewas dan 1 korban terluka, serta insiden di Jackson, Tennessee, pada 20 Oktober 2024 dengan 1 korban tewas dan 8 korban terluka. Dataset ini juga memiliki beberapa nilai yang hilang, terutama pada kolom 'Alamat' (satu baris kosong) dan 'Operations' (seluruh kolom kosong). Secara keseluruhan, dataset ini menyediakan data rinci yang dapat digunakan untuk menganalisis tren kekerasan dengan senjata api di Amerika Serikat, termasuk pola geografis, waktu, dan dampaknya terhadap masyarakat. Analisis lebih lanjut dapat dilakukan untuk memahami lebih dalam karakteristik insiden dan faktor-faktor yang mungkin berkontribusi terhadap kekerasan tersebut.")

# Time Series Visualization
elif section == "📈 Jumlah Korban per Bulan":
    # Title and Introduction
    st.title("Analisis Kekerasan Senjata di Amerika Serikat Tahun 2024")

    # Image
    st.image("image1.jpg")

    # Pastikan kolom 'Month' dalam format datetime
    df['Month'] = pd.to_datetime(df['Month'].astype(str))

    # Slider untuk memilih rentang bulan
    min_month, max_month = st.slider(
        "Pilih rentang bulan",
        min_value=df['Month'].min().date(),
        max_value=df['Month'].max().date(),
        value=(df['Month'].min().date(), df['Month'].max().date()),
        format="MMM YYYY"
    )

    # Filter data berdasarkan rentang bulan yang dipilih
    filtered_df = df[(df['Incident Date'].dt.date >= min_month) & (df['Incident Date'].dt.date <= max_month)]

    # Ringkasan bulanan dari data yang difilter
    monthly_summary = filtered_df.groupby(filtered_df['Month'].dt.to_period('M')).agg(
        Total_Killed=('Victims Killed', 'sum'),
        Total_Injured=('Victims Injured', 'sum')
    ).reset_index()

    # Konversi periode ke string untuk plotting
    monthly_summary['Month'] = monthly_summary['Month'].astype(str)

    # Update plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_summary['Month'], y=monthly_summary['Total_Killed'],
                             mode='lines+markers', name='Total Korban Meninggal'))
    fig.add_trace(go.Scatter(x=monthly_summary['Month'], y=monthly_summary['Total_Injured'],
                             mode='lines+markers', name='Total Korban Luka-Luka'))
    fig.update_layout(
        title="Jumlah Korban Meninggal dan Luka-Luka Per Bulan (Rentang Pilihan)",
        xaxis_title="Bulan",
        yaxis_title="Jumlah Korban",
        legend_title="Kategori Korban",
        template="plotly"
    )

    st.plotly_chart(fig)
    
    # Explanation
    st.subheader("Analisis Bulanan Korban Kekerasan Senjata di Amerika Serikat Tahun 2024")
    st.write("Pada tahun 2024, jumlah korban kekerasan senjata menunjukkan variasi signifikan setiap bulan. Januari 2024 mencatat korban meninggal tertinggi (69 orang), diikuti Juli (62 orang) dan Juni (57 orang), sedangkan Oktober 2024 memiliki korban meninggal paling rendah (19 orang). Untuk korban luka-luka, Juni 2024 mencatat angka tertinggi (373 orang), diikuti Juli (297 orang) dan Mei (215 orang), dengan Oktober 2024 sebagai bulan dengan korban cedera paling sedikit (101 orang). Secara keseluruhan, Juni 2024 menjadi bulan dengan dampak kekerasan tertinggi, sedangkan Oktober 2024 memiliki tingkat kekerasan terendah. Data ini menunjukkan fluktuasi yang signifikan dalam dampak kekerasan senjata sepanjang tahun.")

# Bar Chart by State and City
elif section == "📊 Korban per Negara Bagian":
    # Title and Introduction
    st.title("Analisis Kekerasan Senjata di Amerika Serikat Tahun 2024")
    
    # Image
    st.image("image2.jpg")

    statewise_summary = df.groupby('State').agg(
        Total_Killed=('Victims Killed', 'sum'),
        Total_Injured=('Victims Injured', 'sum')
    ).reset_index()

    fig_killed_state = px.bar(
        statewise_summary.sort_values(by='Total_Killed', ascending=False),
        x='State', y='Total_Killed',
        title="Total Korban Meninggal Per Negara Bagian",
        labels={'Total_Killed': 'Jumlah Korban Meninggal', 'State': 'Negara Bagian'},
        template="plotly", color_discrete_sequence=['red']
    )
    st.plotly_chart(fig_killed_state)

    fig_injured_state = px.bar(
        statewise_summary.sort_values(by='Total_Injured', ascending=False),
        x='State', y='Total_Injured',
        title="Total Korban Luka-Luka Per Negara Bagian",
        labels={'Total_Injured': 'Jumlah Korban Luka-Luka', 'State': 'Negara Bagian'},
        template="plotly", color_discrete_sequence=['blue']
    )
    st.plotly_chart(fig_injured_state)
    
    # Explanation
    st.subheader("Analisis Korban Kekerasan Senjata Berdasarkan Negara Bagian di Amerika Serikat Tahun 2024")
    st.write("Pada tahun 2024, Illinois menjadi negara bagian dengan tingkat kekerasan tertinggi, mencatat 38 korban meninggal dan 128 korban luka-luka. California dan Texas juga memiliki jumlah korban signifikan, masing-masing 37 dan 26 korban meninggal, serta 117 korban luka-luka. Alabama dan Florida menyusul dalam jumlah korban meninggal, sementara Pennsylvania dan Mississippi mencatat korban luka-luka yang tinggi, masing-masing 117 dan 110 orang. Sebaliknya, Nebraska, Delaware, dan West Virginia tidak melaporkan korban meninggal, meskipun terdapat sedikit korban luka-luka (7-9 orang). Hawaii dan Alaska mencatat jumlah korban luka-luka terendah, hanya 2 orang. Data ini menunjukkan distribusi geografis kekerasan senjata yang bervariasi, dengan Illinois sebagai negara bagian yang paling terdampak.")

elif section == "📊 Korban per Kota":
    # Title and Introduction
    st.title("Analisis Kekerasan Senjata di Amerika Serikat Tahun 2024")
    
    # Image
    st.image("image3.jpg")
    
    citywise_summary = df.groupby('City Or County').agg(
        Total_Killed=('Victims Killed', 'sum'),
        Total_Injured=('Victims Injured', 'sum')
    ).reset_index()

    fig_killed_city = px.bar(
        citywise_summary.sort_values(by='Total_Killed', ascending=False),
        x='City Or County', y='Total_Killed',
        title='Total Korban Meninggal Per Kota',
        labels={'Total_Killed': 'Jumlah Korban Meninggal', 'City Or County': 'Kota'},
        template="plotly"
    )
    st.plotly_chart(fig_killed_city)

    fig_injured_city = px.bar(
        citywise_summary.sort_values(by='Total_Injured', ascending=False),
        x='City Or County', y='Total_Injured',
        title='Total Korban Luka-Luka Per Kota',
        labels={'Total_Injured': 'Jumlah Korban Luka-Luka', 'City Or County': 'Kota'},
        template="plotly"
    )
    st.plotly_chart(fig_injured_city)
    
    # Explanation
    st.subheader("Analisis Korban Kekerasan Senjata Berdasarkan Kota di Amerika Serikat Tahun 2024")
    st.write("Pada tahun 2024, Chicago dan Birmingham menjadi kota dengan jumlah korban meninggal tertinggi, masing-masing 15 orang. Namun, Chicago mencatat korban luka-luka jauh lebih banyak (117 orang) dibandingkan Birmingham (35 orang). Kota seperti Philadelphia (12 korban meninggal), Richmond (10 korban), dan Charlotte (9 korban) juga mencatat angka korban meninggal yang signifikan. Sebaliknya, beberapa kota seperti Decatur, Daytona Beach, dan Boston tidak memiliki korban meninggal, tetapi melaporkan sejumlah kecil korban luka-luka, dengan Boston mencatat jumlah korban luka-luka tertinggi di antara kota-kota tersebut (10 orang). Chicago tetap menjadi kota dengan jumlah korban luka-luka tertinggi secara keseluruhan (117 orang), diikuti oleh Philadelphia (71 orang) dan Washington (49 orang). Sementara itu, kota seperti Rock Hill, Gallup, dan Champaign melaporkan jumlah korban meninggal dan luka-luka yang sama, yaitu masing-masing 2 orang. Data ini menunjukkan bahwa Chicago adalah kota dengan tingkat kekerasan tertinggi, baik dari segi korban meninggal maupun korban luka-luka, sementara beberapa kota lainnya mengalami dampak yang lebih ringan.")

# Map Visualization
elif section == "🗺️ Peta Insiden":
    # Title and Introduction
    st.title("Analisis Kekerasan Senjata di Amerika Serikat Tahun 2024")
    
    # Image
    st.image("image4.jpg")

    map_type = st.radio("Pilih jenis peta:", ("Peta Korban Meninggal", "Peta Korban Luka-Luka", "Klasterisasi Korban Meninggal", "Klasterisasi Korban Luka-Luka", "Heatmap Insiden"))

    if map_type == "Peta Korban Meninggal":
        map_killed = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        for i, row in df.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=row['Victims Killed'] * 2,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.6,
                popup=f"{row['City Or County']} - {row['Victims Killed']} killed"
            ).add_to(map_killed)
        st_folium(map_killed, width=800)

    elif map_type == "Peta Korban Luka-Luka":
        map_injured = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        for i, row in df.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=row['Victims Injured'] * 2,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6,
                popup=f"{row['City Or County']} - {row['Victims Injured']} injured"
            ).add_to(map_injured)
        st_folium(map_injured, width=800)
    
    elif map_type == "Klasterisasi Korban Meninggal":
        map_killed = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        killed_cluster = MarkerCluster(name="Korban Meninggal").add_to(map_killed)

        for i, row in df.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=row['Victims Killed'] * 2,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.6,
                popup=f"{row['City Or County']} - {row['Victims Killed']} killed"
            ).add_to(killed_cluster)

        st_folium(map_killed, width=800)
        
    elif map_type == "Klasterisasi Korban Luka-Luka":
        map_injured = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        injured_cluster = MarkerCluster(name="Korban Luka-Luka").add_to(map_injured)

        for i, row in df.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=row['Victims Injured'] * 2,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6,
                popup=f"{row['City Or County']} - {row['Victims Injured']} injured"
            ).add_to(injured_cluster)

        st_folium(map_injured, width=800)

    elif map_type == "Heatmap Insiden":
        heat_data = [[row['Latitude'], row['Longitude']] for _, row in df.iterrows()]
        heatmap = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        HeatMap(heat_data).add_to(heatmap)
        st_folium(heatmap, width=800)

elif section == "📝 Informasi Penting":
    st.title("Kesimpulan Analisis Kekerasan Senjata di Amerika Serikat Tahun 2024")
    
    # Image
    st.image("image5.jpg")
    
    st.write("Data ini menunjukkan pola geografis dan temporal kekerasan senjata yang signifikan di Amerika Serikat, dengan beberapa negara bagian dan kota menjadi pusat dampak  terbesar. Analisis rasio luka-luka terhadap kematian mengungkap bahwa banyak insiden menghasilkan lebih banyak korban luka-luka dibandingkan korban meninggal, memberikan wawasan tentang karakteristik insiden. Hasil analisis ini dapat digunakan untuk mengidentifikasi wilayah prioritas yang membutuhkan intervensi kebijakan untuk mengurangi insiden kekerasan senjata di masa depan.")

# Footer
st.markdown("---")
st.caption("Data ini diolah dan divisualisasikan menggunakan Streamlit, Folium, dan Plotly.")
