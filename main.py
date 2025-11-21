import pathlib

import pandas as pd
import simplekml

class KMLGenerator:
    def __init__(self, name="Ehime", title="楽天モバイル基地局（愛媛県）"):
        self.kml = simplekml.Kml(name=name)
        self.kml.document.name = title
        self.icons = ["open.png", "5g.png", "close.png", "ready.png", "check.png"]
        self.fol = self.kml.newfolder()

    def make_style(self, fn, scale=1):
        kmlstyle = simplekml.Style()
        kmlstyle.iconstyle.scale = scale
        kmlstyle.iconstyle.icon.href = fn
        return kmlstyle

    def generate_style_maps(self):
        for icon in self.icons:
            fn = self.kml.addfile(icon)
            kmlstylemap = simplekml.StyleMap()
            kmlstylemap.normalstyle = self.make_style(fn)
            kmlstylemap.highlightstyle = self.make_style(fn)
            self.kml.document.stylemaps.append(kmlstylemap)

    def add_point(self, longitude, latitude, name, status, eNB_LCID):
        pnt = self.fol.newpoint(name=name)
        pnt.coords = [(longitude, latitude)]

        if status == "open":
            pnt.stylemap = self.kml.document.stylemaps[0]
            pnt.description = f"eNB-LCID: {eNB_LCID}"

        elif status == "5G":
            pnt.stylemap = self.kml.document.stylemaps[1]
            pnt.description = f"eNB-LCID: {eNB_LCID}"

        elif status == "close":
            pnt.stylemap = self.kml.document.stylemaps[2]

        elif status == "ready":
            pnt.stylemap = self.kml.document.stylemaps[3]

        else:
            pnt.stylemap = self.kml.document.stylemaps[4]

    def save_kml(self, file_path):
        self.kml.savekmz(file_path)

def generate_kml_for_area(df, fn, name, title):

    kml_generator = KMLGenerator(name, title)
    kml_generator.generate_style_maps()

    for _, r in df.iterrows():
        kml_generator.add_point(
            longitude=r["経度"],
            latitude=r["緯度"],
            name=r["場所"],
            status=r["状況"],
            eNB_LCID=r["eNB-LCID"],
        )

    kmz_path = pathlib.Path("kmz", fn)
    kmz_path.parent.mkdir(parents=True, exist_ok=True)
    kml_generator.save_kml(kmz_path)

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN5xiHhlnPTkv3auHkYLT9NPvvjayj5AdPrH5VBQdbELOzfONi236Vub6eSshv8jAxQw3V1rgbbgE/pub?gid=0&single=true&output=csv"

df_ehime = (
    pd.read_csv(
        url, usecols=[1, 2, 3, 5, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19], dtype=str
    )
    .dropna(how="all")
    .fillna("")
)

df_ehime

df_ehime["場所"] = df_ehime["場所"].str.strip()

df_ehime["緯度"] = df_ehime["緯度"].astype(float)
df_ehime["経度"] = df_ehime["経度"].astype(float)

df_ehime["eNB-LCID"] = df_ehime["eNB-LCID"].fillna("")
df_ehime["eNB-LCID_700"] = df_ehime["eNB-LCID_700"].fillna("")

df_ehime["eNB-LCID"] = df_ehime["eNB-LCID"].str.cat(df_ehime["eNB-LCID_700"], sep="\n").str.strip()

col = [
    "場所",
    "市区町村",
    "設置タイプ",
    "更新日時",
    "状況",
    "eNB-LCID",
    "基地局ID",
    "sector",
    "sub6",
    "ミリ波",
]

# 5G
flag5G = df_ehime["sub6"].str.isnumeric() | df_ehime["ミリ波"].str.isnumeric()
df_ehime["場所"] = df_ehime["場所"].mask(flag5G, "【5G】" + df_ehime["場所"])
df_ehime["状況"] = df_ehime["状況"].mask(flag5G, "5G")

# 屋内
df_ehime["場所"] = df_ehime["場所"].mask(
    df_ehime["設置タイプ"] == "屋内", "【屋内】" + df_ehime["場所"]
)

# ピコセル
df_ehime["場所"] = df_ehime["場所"].mask(
    df_ehime["設置タイプ"] == "ピコセル", "【ピコセル】" + df_ehime["場所"]
)

# 衛星
df_ehime["場所"] = df_ehime["場所"].mask(
    df_ehime["設置タイプ"] == "衛星", "【衛星】" + df_ehime["場所"]
)

# 鉄塔
df_ehime["場所"] = df_ehime["場所"].mask(
    df_ehime["設置タイプ"] == "鉄塔", "【鉄塔】" + df_ehime["場所"]
)

# au共用
df_ehime["場所"] = df_ehime["場所"].mask(
    df_ehime["設置タイプ"] == "au共用", "【au共用】" + df_ehime["場所"]
)

# 東予地区
df_touyo = df_ehime[
    df_ehime["市区町村"].isin(["今治市", "新居浜市", "西条市", "四国中央市", "上島町"])
].copy()

# 中予地区
df_chuyo = df_ehime[
    df_ehime["市区町村"].isin(
        ["松山市", "伊予市", "東温市", "久万高原町", "松前町", "砥部町"]
    )
].copy()

# 南予地区
df_nanyo = df_ehime[
    df_ehime["市区町村"].isin(
        [
            "宇和島市",
            "八幡浜市",
            "大洲市",
            "西予市",
            "内子町",
            "伊方町",
            "松野町",
            "鬼北町",
            "愛南町",
        ]
    )
].copy()

generate_kml_for_area(df_ehime, "ehime.kmz", "Ehime", "楽天モバイル基地局（愛媛県）")
generate_kml_for_area(df_touyo, "touyo.kmz", "Touyo", "楽天モバイル基地局（東予）")
generate_kml_for_area(df_chuyo, "chuyo.kmz", "Chuyo", "楽天モバイル基地局（中予）")
generate_kml_for_area(df_nanyo, "nanyo.kmz", "Nanyo", "楽天モバイル基地局（南予）")
