import folium
import pandas as pd  # ExcelやCSVを扱うためのライブラリ
from streamlit_folium import st_folium
import streamlit as st

# これを最初に入れると、アプリが全画面幅を使えるようになります
st.set_page_config(layout="wide")

# ----------------------------------------------------
# 設定：お持ちのファイル名や列名に合わせて書き換えてください
# ----------------------------------------------------
FILE_NAME = 'kofun.csv'  # Excelの場合は 'places.xlsx'
COL_NAME = '陵墓'
COL_LAT = '緯度'
COL_LON = '経度'
COL_HIS = '被葬者'
COL_SIZ = '規模'
# ----------------------------------------------------

# 表データを読み込む
df = pd.read_csv(FILE_NAME, encoding="cp932")

# ----------------------------------------------------
# 地図タイルの設定（白地図 vs 航空写真）
# ----------------------------------------------------
st.title("古墳マップ")

# 切り替え用のラジオボタンをStreamlit上に配置
map_style = st.radio(
    "表示する地図を選んでください：",
    ["白地図 (CartoDB)", "航空写真 (Esri World Imagery)"],
    horizontal=True
)

API_KEY = "cb1_3oga_1_7ce961523b21f78b38542e16"

if map_style == "白地図 (CartoDB)":
    tiles_url = f"https://{{s}}.basemaps.cartocdn.com/rastertiles/light_nolabels/{{z}}/{{x}}/{{y}}.png?key={API_KEY}"
    attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    subdomains = 'abcd'
else:
    # Esriの衛星写真タイルURL
    tiles_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    attr = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
    subdomains = 'abc'

# 地図オブジェクトの作成
m = folium.Map(
    location=[34.563931, 135.487308], 
    zoom_start=11, 
    tiles=tiles_url,
    attr=attr,
    subdomains=subdomains
)

# 3. 表のデータを1行ずつループ処理して地図に追加
for index, row in df.iterrows():
    name = row[COL_NAME]
    lat = row[COL_LAT]
    lon = row[COL_LON]
    his = row[COL_HIS]
    siz = row[COL_SIZ]

    if pd.notna(his) and pd.notna(siz):
        popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}<br>被葬者: {his}<br>規模: {siz}"
    elif pd.notna(his) and pd.isna(siz):
        popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}<br>被葬者: {his}"
    elif pd.isna(his) and pd.notna(siz):
        popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}<br>規模: {siz}"
    else:
        popup_text = f"<b>{name}</b><br>緯度: {lat}<br>経度: {lon}"
    
    # 〇を描画（密集対策で少し小さめのサイズ「5」に調整）
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color='#cc0000',
        fill=True,
        fill_color='#cc0000',
        fill_opacity=0.8,
    ).add_to(m)

    # 文字（キャプション）を表示
    folium.map.Marker(
        location=[lat, lon], 
        icon=folium.DivIcon(
            html=f'''
            <div style="
                font-size: 9pt; 
                font-weight: bold; 
                color: #111111; 
                white-space: nowrap;
                position: absolute;
                transform: translate(-50%, -140%);
                background-color: rgba(255, 255, 255, 0.75);
                padding: 1px 4px;
                border-radius: 3px;
                border: 1px solid #dddddd;
            ">{name}</div>
            '''
        ),
        popup=folium.Popup(
            popup_text, max_width=300
        ),
    ).add_to(m)

# Streamlit上で地図を表示
st_folium(m, width=None, height=600)

st.subheader("📊 古墳の大きさランキング")

# ボタンを設置
if st.button("グラフを表示する"):
    # 規模データ（COL_SIZ）が文字列の場合を考慮し、数値に変換する処理
    df["規模_数値"] = (
        df[COL_SIZ]
        .astype(str)
        .str.extract(r"(\d+)")
        .astype(float)
    )

    # 規模データが存在する行だけに絞り込み、大きい順（降順）に並び替える
    df_sorted = df.dropna(subset=["規模_数値"]).sort_values(
        by="規模_数値", ascending=False
    )

    if not df_sorted.empty:
        # グラフ用のデータフレームを作成
        chart_data = df_sorted.set_index(COL_NAME)["規模_数値"]

        # Streamlitの棒グラフで表示
        st.bar_chart(chart_data, sort=False)
        st.success("古墳の規模順にグラフを表示しました！")
    else:
        st.warning("有効な規模データが見つかりませんでした。")

# 4. 保存
m.save('kofunmap2.html')
print(f"{len(df)}件のデータを地図にプロットしました！")
