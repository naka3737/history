import folium
import pandas as pd
from streamlit_folium import st_folium
import streamlit as st
import altair as alt

# アプリのレイアウトを全画面幅に設定
st.set_page_config(layout="wide")

# ----------------------------------------------------
# 設定：ファイル名や列名、APIキーを設定
# ----------------------------------------------------
FILE_NAME = 'chimei.csv'
COL_NAME = '地名'
COL_LAT = '緯度'
COL_LON = '経度'
COL_POP = '前漢人口'
COL_POP2 = '後漢人口'

API_KEY = "cb1_3oga_1_7ce961523b21f78b38542e16"
# ----------------------------------------------------

# 表データを読み込む
try:
    df = pd.read_csv(FILE_NAME)
except FileNotFoundError:
    st.error(f"ファイル '{FILE_NAME}' が見つかりません。ファイル名と配置場所を確認してください。")
    st.stop()

st.title("漢代西域マップ")

# ----------------------------------------------------
# 1. 地図スタイルの選択（ラジオボタン）
# ----------------------------------------------------
map_style = st.radio(
    "表示する地図のスタイルを選択してください：",
    ["白地図 (CARTO)", "航空写真 (Esri Satellite)", "標準マップ (OpenStreetMap)"],
    horizontal=True
)

# スタイルに応じたタイルURL等の切り替え
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

# ----------------------------------------------------
# 2. 地名の選択リストボックスを追加
# ----------------------------------------------------
chimei_options = ["（全体を表示）"] + df[COL_NAME].dropna().tolist()
selected_chimei = st.selectbox("🔍 特定の地名を選択して中心に表示：", chimei_options)

# 選択された地名に応じて中心座標とズームレベルを動的に変更
if selected_chimei != "（全体を表示）":
    target_row = df[df[COL_NAME] == selected_chimei].iloc[0]
    center_lat = target_row[COL_LAT]
    center_lon = target_row[COL_LON]
    zoom_level = 9  # 選択時は拡大表示
else:
    center_lat = 41.715556
    center_lon = 82.932222
    zoom_level = 6  # 全体表示

# マップの初期化
m = folium.Map(
    location=[center_lat, center_lon], 
    zoom_start=zoom_level, 
    tiles=tiles_url,
    attr=attr,
    subdomains=subdomains
)

# ----------------------------------------------------
# 3. データのプロットとポップアップ構築
# ----------------------------------------------------
for index, row in df.iterrows():
    name = row[COL_NAME]
    lat = row[COL_LAT]
    lon = row[COL_LON]
    pop = row[COL_POP]
    pop2 = row[COL_POP2]
    
    # 現在選択されている地名かどうかを判定
    is_selected = (selected_chimei != "（全体を表示）" and name == selected_chimei)
    
    # f文字列内で直接整数化・文字列化、欠損値は「ー」にする処理
    pop_str = f"{int(pop):,}" if pd.notna(pop) else "ー"
    pop2_str = f"{int(pop2):,}" if pd.notna(pop2) else "ー"
    
    popup_text = (
        f"<b>{name}</b><br>"
        f"緯度: {lat}<br>"
        f"経度: {lon}<br>"
        f"前漢人口: {pop_str}<br>"
        f"後漢人口: {pop2_str}"
    )
    
    # 選択中のものは色やサイズを目立たせる
    marker_bg = '#0055ff' if is_selected else '#cc0000'
    marker_size = '14px' if is_selected else '10px'
    font_size = '10pt' if is_selected else '9pt'
    text_color = '#0033bb' if is_selected else '#111111'
    border_style = '2px solid #0055ff' if is_selected else '1px solid #bbbbbb'
    
    # 赤丸と文字を一体化したHTMLアイコンを作成
    custom_icon = folium.DivIcon(
        html=f'''
        <div style="position: relative; width: 0px; height: 0px; cursor: pointer;">
            <!-- 丸部分（選択時は青く大きく） -->
            <div style="
                position: absolute;
                width: {marker_size};
                height: {marker_size};
                background-color: {marker_bg};
                border: 1px solid #ffffff;
                border-radius: 50%;
                transform: translate(-50%, -50%);
            "></div>
            <!-- 文字（キャプション）部分 -->
            <div style="
                font-size: {font_size}; 
                font-weight: bold; 
                color: {text_color}; 
                white-space: nowrap;
                position: absolute;
                transform: translate(-50%, -140%);
                background-color: rgba(255, 255, 255, 0.9);
                padding: 1px 4px;
                border-radius: 3px;
                border: {border_style};
            ">{name}</div>
        </div>
        '''
    )
    
    # マーカーとして地図に追加
    folium.Marker(
        location=[lat, lon],
        icon=custom_icon,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(m)

# Streamlit上に地図を表示
st_folium(m, width=None, height=600)

# ----------------------------------------------------
# 4. 人口ランキングのグラフ表示セクション
# ----------------------------------------------------
st.subheader("📊 人口ランキング（前漢・後漢）")

if st.button("グラフを表示する"):
    # 前漢人口用のデータ処理（数値変換・降順ソート）
    df_pop1 = df[[COL_NAME, COL_POP]].copy()
    df_pop1[COL_POP] = pd.to_numeric(df_pop1[COL_POP], errors='coerce')
    df_pop1_sorted = df_pop1.dropna(subset=[COL_POP]).sort_values(by=COL_POP, ascending=False)

    # 後漢人口用のデータ処理（数値変換・降順ソート）
    df_pop2 = df[[COL_NAME, COL_POP2]].copy()
    df_pop2[COL_POP2] = pd.to_numeric(df_pop2[COL_POP2], errors='coerce')
    df_pop2_sorted = df_pop2.dropna(subset=[COL_POP2]).sort_values(by=COL_POP2, ascending=False)

    # 1. 前漢人口ランキングの描画
    if not df_pop1_sorted.empty:
        st.write("### 前漢人口ランキング（多い順）")
        dynamic_width1 = max(800, len(df_pop1_sorted) * 30)
        
        chart1 = (
            alt.Chart(df_pop1_sorted)
            .mark_bar(color='#4c78a8')
            .encode(
                x=alt.X(
                    COL_NAME,
                    sort=None,
                    axis=alt.Axis(labelAngle=-45, labelOverlap=False),
                    title="地名",
                ),
                y=alt.Y(COL_POP, title="前漢人口"),
            )
            .properties(width=dynamic_width1, height=350)
        )
        st.altair_chart(chart1, use_container_width=False)
    else:
        st.info("前漢人口の有効なデータが見つかりませんでした。")

    # 2. 後漢人口ランキングの描画
    if not df_pop2_sorted.empty:
        st.write("### 後漢人口ランキング（多い順）")
        dynamic_width2 = max(800, len(df_pop2_sorted) * 30)
        
        chart2 = (
            alt.Chart(df_pop2_sorted)
            .mark_bar(color='#f58518')
            .encode(
                x=alt.X(
                    COL_NAME,
                    sort=None,
                    axis=alt.Axis(labelAngle=-45, labelOverlap=False),
                    title="地名",
                ),
                y=alt.Y(COL_POP2, title="後漢人口"),
            )
            .properties(width=dynamic_width2, height=350)
        )
        st.altair_chart(chart2, use_container_width=False)
    else:
        st.info("後漢人口の有効なデータが見つかりませんでした。")
   