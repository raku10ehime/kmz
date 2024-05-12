import pathlib

import pandas as pd
import simplekml


class KMLGenerator:
    def __init__(self):
        self.kml = simplekml.Kml(name="Densoku")
        self.kml.document.name = "楽天モバイル基地局（愛媛県）仮登録"

        # アイコンを指定（eNB-LCIDある、eNB-LCIDなし）
        self.icons = ["rakuten.png", "close.png"]

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

    def add_point(self, longitude, latitude, name, eNB_LCID):
        pnt = self.fol.newpoint(name=name)
        pnt.coords = [(longitude, latitude)]

        # eNB-LCIDがある場合、1番目のアイコン
        if eNB_LCID:
            pnt.stylemap = self.kml.document.stylemaps[0]
            pnt.description = f"eNB-LCID: {eNB_LCID}"

        # eNB-LCIDがない場合、2番目のアイコン
        else:
            pnt.stylemap = self.kml.document.stylemaps[1]

    def save_kml(self, file_path):
        self.kml.savekmz(file_path)


def generate_kml_for_area(df, fn):
    kml_generator = KMLGenerator()
    kml_generator.generate_style_maps()

    for i, r in df.iterrows():
        kml_generator.add_point(
            longitude=r["経度"],
            latitude=r["緯度"],
            name=r["場所"],
            eNB_LCID=r["eNB-LCID"],
        )

    kmz_path = pathlib.Path("kmz", fn)
    kmz_path.parent.mkdir(parents=True, exist_ok=True)
    kml_generator.save_kml(kmz_path)

# スプレッドシートのURL
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1y4_eNMmLm_cqc32Kc-2GE2U-wecpTUVpVGc9CR60QERERnW8fe9qeDqZT7GVhn3SMG3W1haykHi5/pub?gid=0&single=true&output=csv"

df = pd.read_csv(
    url,
    parse_dates=True,
    index_col=0,
    dtype={"eNB-LCID": str, "備考": str, "住所": str},
)

# データクレンジング
df["場所"] = df["場所"].str.strip()
df["eNB-LCID"] = df["eNB-LCID"].fillna("")

generate_kml_for_area(df, "densoku.kmz")
