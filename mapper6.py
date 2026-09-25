import folium
import pandas as pd
from streamlit_folium import st_folium
import streamlit as st

st.set_page_config(layout="wide")

# ----------------------------------------------------
# 設定：お持ちのファイル名や列名、APIキーを設定
# ----------------------------------------------------
FILE_NAME = 'chimei.csv'
COL_NAME = '地名'
COL_LAT = '緯度'
COL_LON = '経度'

API_KEY = "cb1_3oga_1_7ce961523b21f78b38542e16"
# ----------------------------------------------------

df = pd.read_csv(FILE_NAME)

st.title("漢代西域マップ")

# ラジオボタンで地図のスタイルを3択で選択
map_style = st.radio(
    "表示する地図のスタイルを選択してください：",
    ["白地図 (CARTO)", "航空写真 (Esri Satellite)", "標準マップ (OpenStreetMap)"],
    horizontal=True
)

# 選択されたスタイルに応じてタイルURL、属性、サブドメインを動的に切り替え
if map_style == "白地図 (CARTO)":
    tiles_url = f"https://{{s}}.basemaps.cartocdn.com/rastertiles/light_nolabels/{{z}}/{{x}}/{{y}}.png?key={API_KEY}"
    attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    subdomains = 'abcd'
elif map_style == "航空写真 (Esri Satellite)":
    tiles_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    subdomains = 'abc'
else:  # 標準マップ (OpenStreetMap)
    tiles_url = 'OpenStreetMap'
    attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    subdomains = 'abc'

# マップの初期化（古市古墳群あたりを見やすくする場合の初期座標例：[34.56, 135.60]）
m = folium.Map(
    location=[41.715556, 82.932222], 
    zoom_start=6, 
    tiles=tiles_url,
    attr=attr,
    subdomains=subdomains
)

# データのプロット処理
for index, row in df.iterrows():
    name = row[COL_NAME]
    lat = row[COL_LAT]
    lon = row[COL_LON]
    
    # ポップアップ用のテキストを作成
    popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}"
    
    # 赤丸と文字を一体化したHTMLアイコンを作成
    custom_icon = folium.DivIcon(
        html=f'''
        <div style="position: relative; width: 0px; height: 0px; cursor: pointer;">
            <!-- 赤丸部分 -->
            <div style="
                position: absolute;
                width: 10px;
                height: 10px;
                background-color: #cc0000;
                border: 1px solid #ffffff;
                border-radius: 50%;
                transform: translate(-50%, -50%);
            "></div>
            <!-- 文字（キャプション）部分 -->
            <div style="
                font-size: 9pt; 
                font-weight: bold; 
                color: #111111; 
                white-space: nowrap;
                position: absolute;
                transform: translate(-50%, -140%);
                background-color: rgba(255, 255, 255, 0.9);
                padding: 1px 4px;
                border-radius: 3px;
                border: 1px solid #bbbbbb;
            ">{name}</div>
        </div>
        '''
    )
    
    # 1つのMarkerとして地図に追加
    folium.Marker(
        location=[lat, lon],
        icon=custom_icon,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(m)

# Streamlit上に地図を表示
st_folium(m, width=None, height=600)