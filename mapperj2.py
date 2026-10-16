import altair as alt
import folium
import pandas as pd  # ExcelやCSVを扱うためのライブラリ
from streamlit_folium import st_folium
import streamlit as st
import datetime  # 現在年を自動取得するため

# これを最初に入れると、アプリが全画面幅を使えるようになります
st.set_page_config(layout="wide")

# ----------------------------------------------------
# 設定：お持ちのファイル名や列名に合わせて書き換えてください
# ----------------------------------------------------
FILE_NAME = 'jiin.csv'  
COL_NAME = '寺院名'
COL_LAT = '緯度'
COL_LON = '経度'
COL_NEN = '創建年'
COL_SOU = '創建者'
COL_SHU = '宗派'
# ----------------------------------------------------

# 表データを読み込む
try:
    df = pd.read_csv(FILE_NAME, encoding="cp932")
except FileNotFoundError:
    st.error(f"ファイル '{FILE_NAME}' が見つかりません。ファイル名を確認してください。")
    st.stop()

# ----------------------------------------------------
# 地図タイルの設定（通常マップ vs 白地図 vs 航空写真）
# ----------------------------------------------------
st.title("寺院マップ")

# 切り替え用のラジオボタンをStreamlit上に配置
map_style = st.radio(
    "表示する地図を選んでください：",
    ["通常マップ (OpenStreetMap)", "白地図 (CartoDB)", "航空写真 (Esri World Imagery)"],
    horizontal=True
)

API_KEY = "cb1_3oga_1_7ce961523b21f78b38542e16"

if map_style == "通常マップ (OpenStreetMap)":
    tiles_url = "OpenStreetMap"
    attr = None
    subdomains = 'abc'
elif map_style == "白地図 (CartoDB)":
    tiles_url = f"https://{{s}}.basemaps.cartocdn.com/rastertiles/light_nolabels/{{z}}/{{x}}/{{y}}.png?key={API_KEY}"
    attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    subdomains = 'abcd'
else:
    # Esriの衛星写真タイルURL
    tiles_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    attr = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
    subdomains = 'abc'

# ----------------------------------------------------
# 陵墓の選択リストボックスを追加
# ----------------------------------------------------
kofun_options = ["（全体を表示）"] + df[COL_NAME].dropna().tolist()
selected_kofun = st.selectbox("🔍 特定の陵墓を選択して中心に表示：", kofun_options)

# 選択された古墳に応じて中心座標とズームレベルを動的に変更
if selected_kofun != "（全体を表示）":
    target_row = df[df[COL_NAME] == selected_kofun].iloc[0]
    center_lat = target_row[COL_LAT]
    center_lon = target_row[COL_LON]
    zoom_level = 15  # 選択時は拡大表示
else:
    center_lat = 34.614739
    center_lon = 135.734172
    zoom_level = 11  # 全体表示

# 地図オブジェクトの作成
m = folium.Map(
    location=[center_lat, center_lon], 
    zoom_start=zoom_level, 
    tiles=tiles_url,
    attr=attr,
    subdomains=subdomains
)

# 表のデータを1行ずつループ処理して地図に追加
for index, row in df.iterrows():
    name = row[COL_NAME]
    lat = row[COL_LAT]
    lon = row[COL_LON]
    nen = row[COL_NEN]
    sou = row[COL_SOU]
    shu = row[COL_SHU]

    # 現在選択されている古墳かどうかを判定
    is_selected = (selected_kofun != "（全体を表示）" and name == selected_kofun)

    if pd.notna(nen) and pd.notna(sou):
        popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}<br>創建年: {nen}<br>創建者: {sou}"
    elif pd.notna(nen) and pd.isna(sou):
        popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}<br>創建年: {nen}"
    elif pd.isna(nen) and pd.notna(sou):
        popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}<br>創建者: {nen}"
    else:
        popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}"

    if pd.notna(shu):
        popup_text = popup_text + f"<br>宗派: {shu}"

    # 選択中のものは色やサイズを目立たせる
    marker_color = '#0055ff' if is_selected else '#cc0000'
    marker_radius = 8 if is_selected else 5
    fill_opacity = 1.0 if is_selected else 0.8

    # 〇を描画
    folium.CircleMarker(
        location=[lat, lon],
        radius=marker_radius,
        color=marker_color,
        fill=True,
        fill_color=marker_color,
        fill_opacity=fill_opacity,
    ).add_to(m)

    # 文字（キャプション）を表示
    folium.map.Marker(
        location=[lat, lon], 
        icon=folium.DivIcon(
            html=f'''
            <div style="
                font-size: {'10pt' if is_selected else '9pt'}; 
                font-weight: bold; 
                color: {'#0033bb' if is_selected else '#111111'}; 
                white-space: nowrap;
                position: absolute;
                transform: translate(-50%, -140%);
                background-color: rgba(255, 255, 255, 0.85);
                padding: {'2px 5px' if is_selected else '1px 4px'};
                border-radius: 3px;
                border: {'2px solid #0055ff' if is_selected else '1px solid #dddddd'};
            ">{name}</div>
            '''
        ),
        popup=folium.Popup(
            popup_text, max_width=300
        ),
    ).add_to(m)

# Streamlit上で地図を表示
st_folium(m, width=None, height=600)

st.subheader("📊 寺院の創建年一覧表示")


# ボタンを設置
if st.button("グラフを表示する"):
    # 創建年データが文字列の場合を考慮し、数値に変換する処理
    df["創建年"] = (
        df[COL_NEN]
        .astype(str)
        .str.extract(r"(\d+)")
        .astype(float)
    )

    # 創建年が存在し、かつ 1700年以下のデータに絞り込む
    df_filtered = df.dropna(subset=["創建年"])
    df_filtered = df_filtered[df_filtered["創建年"] <= 1700]
    
    # 創建年の古い順（昇順）に並び替える
    df_sorted = df_filtered.sort_values(
        by="創建年", ascending=True
    )

    if not df_sorted.empty:
        # グラフ用のデータフレームを作成
        chart_df = df_sorted[[COL_NAME, "創建年"]].copy()

        # 【現在の年を自動取得】Pythonの機能で現在の西暦年（例: 2026）を取得する
        current_year = datetime.date.today().year

        # 現在の年を基準に「現在年 - 創建年」を計算し、古い寺ほど棒が高くなるようにする
        chart_df["経過年数"] = current_year - chart_df["創建年"]

        # 項目数に応じてグラフの横幅を動的に拡大（1本あたり約30ピクセル）
        dynamic_width = max(800, len(chart_df) * 30)

        # Altairを使って横スクロール可能な棒グラフを作成
        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X(
                    COL_NAME,
                    sort=None,  # 並び順を維持
                    axis=alt.Axis(
                        labelAngle=-45,      # 寺院名を斜めにして見やすくする
                        labelOverlap=False,  # ラベルが重なっても間引かずにすべて表示する
                    ),
                    title="寺院名",
                ),
                # 縦軸に「経過年数（高さ）」を指定
                y=alt.Y("経過年数:Q", title=f"現在({current_year}年)からの経過年数"),
                tooltip=[COL_NAME, "創建年", "経過年数"],  # マウスを合わせたときに寺院名と実際の創建年を表示
            )
            .properties(width=dynamic_width, height=450)
        )

        # use_container_width=False にすることで、枠を超えた分が自動で横スクロールになる
        st.altair_chart(chart, use_container_width=False)
        st.success(
            f"1700年以前の全 {len(chart_df)} 件のデータを表示しました（古い寺ほど棒が高くなります）！左右にスクロールしてご確認ください。"
        )

    else:
        st.warning("1700年以前の有効な創建年データが見つかりませんでした。")
