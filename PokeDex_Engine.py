"""
Çalıştır: python pokemon_explorer.py
API Docs: https://pokeapi.co/docs/v2
"""

import sys, json, time, requests, threading
import pandas as pd
from io import BytesIO
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QProgressBar, QStatusBar, QMessageBox, QFileDialog, QGroupBox,
    QComboBox, QSplitter, QTabWidget, QFrame, QHeaderView,
    QScrollArea, QGridLayout, QSpinBox, QCheckBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QImage, QPainter,
    QLinearGradient, QBrush, QAction, QFontDatabase
)

try:
    import matplotlib
    matplotlib.use('QtAgg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

TYPE_COLORS = {
    "fire":     "#FF6B35", "water":    "#4FC3F7", "grass":    "#66BB6A",
    "electric": "#FFD54F", "psychic":  "#F06292", "ice":      "#80DEEA",
    "dragon":   "#7E57C2", "dark":     "#546E7A",  "fairy":   "#F48FB1",
    "fighting": "#EF5350", "poison":   "#AB47BC",  "ground":  "#BCAAA4",
    "flying":   "#90CAF9", "bug":      "#AED581",  "rock":    "#A1887F",
    "ghost":    "#7E57C2", "steel":    "#B0BEC5",  "normal":  "#CFD8DC",
}

STAT_COLORS = {
    "hp":              "#EF5350",
    "attack":          "#FF7043",
    "defense":         "#FFA726",
    "special-attack":  "#AB47BC",
    "special-defense": "#7E57C2",
    "speed":           "#26C6DA",
}

STYLE = """
* { font-family: 'Segoe UI', 'Helvetica Neue', sans-serif; }

QMainWindow, QWidget#root {
    background: #13111a;
    color: #e4e0f0;
}

QGroupBox {
    border: 1px solid #2a2440;
    border-radius: 10px;
    margin-top: 16px;
    padding: 12px 10px 10px 10px;
    font-size: 10px;
    font-weight: 700;
    color: #6c5ce7;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: #17152080;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    background: #13111a;
    color: #6c5ce7;
}

QLineEdit, QComboBox, QSpinBox {
    background: #1e1b2e;
    border: 1px solid #2a2440;
    border-radius: 8px;
    padding: 8px 14px;
    color: #e4e0f0;
    font-size: 13px;
    selection-background-color: #6c5ce7;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #6c5ce7;
    background: #211d30;
}
QLineEdit#search_bar {
    font-size: 15px;
    padding: 10px 16px;
    border-radius: 24px;
    border: 2px solid #2a2440;
}
QLineEdit#search_bar:focus {
    border: 2px solid #6c5ce7;
}

QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView {
    background: #1e1b2e;
    border: 1px solid #2a2440;
    selection-background-color: #2a2440;
    color: #e4e0f0;
    border-radius: 8px;
}

QPushButton {
    background: #2a2440;
    color: #a99de8;
    border: 1px solid #3d3560;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
QPushButton:hover { background: #3d3560; color: #e4e0f0; }
QPushButton:pressed { background: #6c5ce7; color: #fff; }
QPushButton:disabled { background: #1a1727; color: #3d3560; border-color: #2a2440; }
QPushButton#fetch_btn {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6c5ce7, stop:1 #a29bfe);
    color: #fff;
    border: none;
    border-radius: 24px;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 32px;
    letter-spacing: 1px;
}
QPushButton#fetch_btn:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7d6ff0, stop:1 #b3acff);
}
QPushButton#export_btn {
    background: #1e3a2f;
    color: #66bb6a;
    border: 1px solid #2e5c3e;
    border-radius: 8px;
}
QPushButton#export_btn:hover { background: #2e5c3e; }
QPushButton#danger_btn {
    background: #3a1e1e;
    color: #ef5350;
    border: 1px solid #5c2e2e;
}
QPushButton#danger_btn:hover { background: #5c2e2e; }

QTableWidget {
    background: #100e1a;
    gridline-color: #1e1b2e;
    border: 1px solid #2a2440;
    border-radius: 10px;
    color: #ccc8e8;
    font-size: 12px;
    alternate-background-color: #13111e;
}
QTableWidget::item { padding: 6px 10px; }
QTableWidget::item:selected { background: #2a2440; color: #a99de8; }
QHeaderView::section {
    background: #1e1b2e;
    color: #6c5ce7;
    padding: 10px 12px;
    border: none;
    border-right: 1px solid #2a2440;
    border-bottom: 1px solid #2a2440;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

QTabWidget::pane { border: 1px solid #2a2440; border-radius: 10px; background: #13111a; }
QTabBar::tab {
    background: #1e1b2e;
    color: #5a5275;
    padding: 10px 24px;
    border: 1px solid #2a2440;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-right: 2px;
}
QTabBar::tab:selected { background: #13111a; color: #a99de8; border-top: 2px solid #6c5ce7; }

QProgressBar {
    border: none;
    border-radius: 4px;
    background: #1e1b2e;
    text-align: center;
    color: transparent;
    height: 6px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6c5ce7, stop:1 #a29bfe);
    border-radius: 4px;
}

QStatusBar {
    background: #0e0c18;
    color: #4a4568;
    border-top: 1px solid #1e1b2e;
    font-size: 11px;
    padding: 4px 12px;
}

QScrollBar:vertical { background: #100e1a; width: 6px; border-radius: 3px; }
QScrollBar::handle:vertical { background: #2a2440; border-radius: 3px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #6c5ce7; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 6px; background: #100e1a; }
QScrollBar::handle:horizontal { background: #2a2440; border-radius: 3px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""
class PokemonWorker(QThread):
    progress  = pyqtSignal(int, int)
    log       = pyqtSignal(str, str)
    result    = pyqtSignal(list)
    error     = pyqtSignal(str)

    BASE = "https://pokeapi.co/api/v2"

    def __init__(self, limit=151, types_filter=None, search_name=""):
        super().__init__()
        self._abort = False
        self.limit = limit
        self.types_filter = types_filter or []
        self.search_name = search_name.lower().strip()
    def abort(self): self._abort = True
    def _get(self, url, retries=3):
        for i in range(retries):
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                if i == retries - 1:
                    raise
                time.sleep(0.5 * (i + 1))
    def run(self):
        try:
            self.log.emit(f"PokéAPI bağlantısı kuruluyor... (İlk {self.limit} Pokémon)", "info")
            data = self._get(f"{self.BASE}/pokemon?limit={self.limit}&offset=0")
            entries = data["results"]
            total = len(entries)
            self.log.emit(f"✓ {total} Pokémon listelendi", "ok")

            results = []
            for i, entry in enumerate(entries):
                if self._abort:
                    self.log.emit(" Durduruldu.", "warn")
                    break

                name = entry["name"]
                if self.search_name and self.search_name not in name:
                    self.progress.emit(i + 1, total)
                    continue

                try:
                    poke = self._get(entry["url"])
                    row = self._parse(poke)
                    if self.types_filter:
                        poke_types = [t.lower() for t in row["Tipler"].split(" / ")]
                        if not any(tf in poke_types for tf in self.types_filter):
                            self.progress.emit(i + 1, total)
                            continue
                    results.append(row)
                except Exception as e:
                    self.log.emit(f"⚠ {name}: {e}", "warn")

                self.progress.emit(i + 1, total)
                if (len(results)) % 10 == 0 and results:
                    self.log.emit(f"  ... {len(results)} Pokémon işlendi", "info")

            self.log.emit(f"✓ Tamamlandı: {len(results)} Pokémon yüklendi", "ok")
            self.result.emit(results)

        except Exception as e:
            self.error.emit(str(e))

    def _parse(self, p: dict) -> dict:
        types = [t["type"]["name"] for t in p["types"]]
        stats = {s["stat"]["name"]: s["base_stat"] for s in p["stats"]}
        abilities = [a["ability"]["name"] for a in p["abilities"]]
        sprite_url = (p.get("sprites", {}).get("other", {})
                      .get("official-artwork", {})
                      .get("front_default") or
                      p.get("sprites", {}).get("front_default") or "")

        return {
            "#":              p["id"],
            "Ad":             p["name"].title(),
            "Tip 1":          types[0].title() if len(types) > 0 else "—",
            "Tip 2":          types[1].title() if len(types) > 1 else "—",
            "Tipler":         " / ".join(types),
            "HP":             stats.get("hp", 0),
            "Atak":           stats.get("attack", 0),
            "Savunma":        stats.get("defense", 0),
            "Öz Atak":        stats.get("special-attack", 0),
            "Öz Savunma":     stats.get("special-defense", 0),
            "Hız":            stats.get("speed", 0),
            "Toplam Stat":    sum(stats.values()),
            "Boy (dm)":       p.get("height", 0),
            "Kilo (hg)":      p.get("weight", 0),
            "Yetenekler":     ", ".join(abilities),
            "Sprite URL":     sprite_url,
            "_raw_types":     types,
            "_raw_stats":     stats,
        }
class SpriteLoader(QThread):
    loaded = pyqtSignal(QPixmap, str)

    def __init__(self, url, name):
        super().__init__()
        self.url = url
        self.name = name

    def run(self):
        try:
            r = requests.get(self.url, timeout=8)
            img = QImage()
            img.loadFromData(r.content)
            px = QPixmap.fromImage(img).scaled(
                220, 220, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.loaded.emit(px, self.name)
        except:
            pass
class PokemonCard(QFrame):
    def __init__(self, row: dict):
        super().__init__()
        self.row = row
        self._sprite_loader = None
        self.setFixedSize(200, 270)
        self.setStyleSheet(self._card_style())
        self._build()

    def _primary_type(self):
        types = self.row.get("_raw_types", ["normal"])
        return types[0] if types else "normal"

    def _card_style(self):
        t = self._primary_type()
        c = TYPE_COLORS.get(t, "#CFD8DC")
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        return f"""
        QFrame {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 rgba({r},{g},{b},40), stop:1 rgba(20,18,30,255));
            border: 1px solid rgba({r},{g},{b},80);
            border-radius: 16px;
        }}
        QFrame:hover {{
            border: 1px solid rgba({r},{g},{b},200);
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 rgba({r},{g},{b},70), stop:1 rgba(25,22,38,255));
        }}
        QLabel {{ background: transparent; border: none; }}
        """

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(4)
        id_lbl = QLabel(f"#{self.row['#']:03d}")
        id_lbl.setStyleSheet("color:#5a5275; font-size:11px; font-weight:700; letter-spacing:1px;")
        lay.addWidget(id_lbl)
        self.sprite_lbl = QLabel()
        self.sprite_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_lbl.setFixedHeight(120)
        self.sprite_lbl.setText("◌")
        self.sprite_lbl.setStyleSheet("color:#2a2440; font-size:40px;")
        lay.addWidget(self.sprite_lbl)
        name_lbl = QLabel(self.row["Ad"])
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet("color:#e4e0f0; font-size:14px; font-weight:700; letter-spacing:0.5px;")
        lay.addWidget(name_lbl)
        types_row = QHBoxLayout()
        types_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        types_row.setSpacing(6)
        for t in self.row.get("_raw_types", []):
            c = TYPE_COLORS.get(t, "#ccc")
            badge = QLabel(t.upper())
            badge.setStyleSheet(f"""
                background: {c}33; color: {c};
                border: 1px solid {c}66;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 9px; font-weight: 700; letter-spacing: 1px;
            """)
            types_row.addWidget(badge)
        lay.addLayout(types_row)
        lay.addStretch()
        stat_lbl = QLabel(f"⚡ {self.row['Toplam Stat']} BST")
        stat_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stat_lbl.setStyleSheet("color:#6c5ce7; font-size:11px; font-weight:600;")
        lay.addWidget(stat_lbl)
        url = self.row.get("Sprite URL", "")
        if url:
            self._sprite_loader = SpriteLoader(url, self.row["Ad"])
            self._sprite_loader.loaded.connect(self._set_sprite)
            self._sprite_loader.start()
    def _set_sprite(self, px: QPixmap, name: str):
        self.sprite_lbl.setPixmap(px)
        self.sprite_lbl.setText("")
class DetailPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(280)
        self._build()

    def _build(self):
        self.main_lay = QVBoxLayout(self)
        self.main_lay.setContentsMargins(16, 16, 16, 16)
        self.main_lay.setSpacing(10)

        self.placeholder = QLabel("← Tablodan bir\nPokémon seçin")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color:#2a2440; font-size:16px; font-weight:600;")
        self.main_lay.addWidget(self.placeholder)

    def show_pokemon(self, row: dict):
        while self.main_lay.count():
            item = self.main_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        types = row.get("_raw_types", ["normal"])
        t = types[0]
        c = TYPE_COLORS.get(t, "#CFD8DC")
        self.sprite_lbl = QLabel()
        self.sprite_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_lbl.setFixedHeight(180)
        self.sprite_lbl.setText("⟳")
        self.sprite_lbl.setStyleSheet(f"color:{c}; font-size:36px;")
        self.main_lay.addWidget(self.sprite_lbl)
        name = QLabel(f"{row['Ad']}")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setStyleSheet(f"color:#e4e0f0; font-size:22px; font-weight:800;")
        self.main_lay.addWidget(name)

        num = QLabel(f"#{row['#']:03d}")
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setStyleSheet("color:#4a4568; font-size:12px;")
        self.main_lay.addWidget(num)
        types_row = QHBoxLayout()
        types_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for tp in types:
            c2 = TYPE_COLORS.get(tp, "#ccc")
            b = QLabel(tp.upper())
            b.setStyleSheet(f"""
                background:{c2}22; color:{c2}; border:1px solid {c2}55;
                border-radius:12px; padding:3px 14px;
                font-size:10px; font-weight:700; letter-spacing:1px;
            """)
            types_row.addWidget(b)
        self.main_lay.addLayout(types_row)
        info_row = QHBoxLayout()
        for label, val in [("Boy", f"{row['Boy (dm)'] / 10:.1f} m"),
                            ("Kilo", f"{row['Kilo (hg)'] / 10:.1f} kg")]:
            box = QFrame()
            box.setStyleSheet("background:#1e1b2e; border-radius:8px; border:1px solid #2a2440;")
            b_lay = QVBoxLayout(box)
            b_lay.setContentsMargins(8, 6, 8, 6)
            b_lay.setSpacing(2)
            lbl = QLabel(val)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color:#e4e0f0; font-size:14px; font-weight:700;")
            sub = QLabel(label)
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub.setStyleSheet("color:#5a5275; font-size:10px;")
            b_lay.addWidget(lbl)
            b_lay.addWidget(sub)
            info_row.addWidget(box)
        self.main_lay.addLayout(info_row)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#1e1b2e; border:none; max-height:1px;")
        self.main_lay.addWidget(sep)

        stats_lbl = QLabel("BASE STATS")
        stats_lbl.setStyleSheet("color:#4a4568; font-size:10px; font-weight:700; letter-spacing:2px;")
        self.main_lay.addWidget(stats_lbl)

        raw_stats = row.get("_raw_stats", {})
        stat_display = [
            ("hp",             "HP",     row["HP"]),
            ("attack",         "ATK",    row["Atak"]),
            ("defense",        "DEF",    row["Savunma"]),
            ("special-attack", "SPA",    row["Öz Atak"]),
            ("special-defense","SPD",    row["Öz Savunma"]),
            ("speed",          "SPE",    row["Hız"]),
        ]
        for key, short, val in stat_display:
            color = STAT_COLORS.get(key, "#6c5ce7")
            row_w = QWidget()
            r_lay = QHBoxLayout(row_w)
            r_lay.setContentsMargins(0, 0, 0, 0)
            r_lay.setSpacing(8)

            name_l = QLabel(short)
            name_l.setFixedWidth(32)
            name_l.setStyleSheet(f"color:{color}; font-size:10px; font-weight:700;")

            val_l = QLabel(str(val))
            val_l.setFixedWidth(28)
            val_l.setAlignment(Qt.AlignmentFlag.AlignRight)
            val_l.setStyleSheet("color:#8880a8; font-size:11px;")

            bar_bg = QFrame()
            bar_bg.setFixedHeight(6)
            bar_bg.setStyleSheet("background:#1e1b2e; border-radius:3px;")

            bar_fill = QFrame(bar_bg)
            bar_fill.setFixedHeight(6)
            pct = min(val / 255.0, 1.0)
            bar_fill.setFixedWidth(int(pct * 140))
            bar_fill.setStyleSheet(f"background:{color}; border-radius:3px;")

            r_lay.addWidget(name_l)
            r_lay.addWidget(val_l)
            r_lay.addWidget(bar_bg, 1)
            self.main_lay.addWidget(row_w)
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background:#1e1b2e; border:none; max-height:1px;")
        self.main_lay.addWidget(sep2)

        ab_lbl = QLabel("YETENEKLERİ")
        ab_lbl.setStyleSheet("color:#4a4568; font-size:10px; font-weight:700; letter-spacing:2px;")
        self.main_lay.addWidget(ab_lbl)

        ab_val = QLabel(row.get("Yetenekler", "—"))
        ab_val.setWordWrap(True)
        ab_val.setStyleSheet("color:#a99de8; font-size:12px;")
        self.main_lay.addWidget(ab_val)

        self.main_lay.addStretch()

        # Sprite yükle
        url = row.get("Sprite URL", "")
        if url:
            self._sl = SpriteLoader(url, row["Ad"])
            self._sl.loaded.connect(lambda px, n: self.sprite_lbl.setPixmap(px))
            self._sl.start()
if HAS_MPL:
    class Dashboard(QWidget):
        def __init__(self):
            super().__init__()
            self.df = None
            lay = QVBoxLayout(self)

            ctrl = QHBoxLayout()
            ctrl.setSpacing(10)

            self.chart_combo = QComboBox()
            self.chart_combo.addItems([
                "Tip Dağılımı (Pasta)",
                "Ortalama Stat Karşılaştırması (Bar)",
                "Toplam BST Dağılımı (Histogram)",
                "HP vs Hız (Scatter)",
                "Top 15 — Toplam Stat",
            ])
            ctrl.addWidget(QLabel("Grafik:"))
            ctrl.addWidget(self.chart_combo, 1)

            draw_btn = QPushButton("Çiz")
            draw_btn.clicked.connect(self.draw)
            ctrl.addWidget(draw_btn)
            lay.addLayout(ctrl)

            self.figure = Figure(facecolor='#13111a')
            self.canvas = FigureCanvas(self.figure)
            lay.addWidget(self.canvas)

        def set_df(self, df):
            self.df = df
            self.draw()

        def draw(self):
            if self.df is None or self.df.empty:
                return
            self.figure.clear()
            chart = self.chart_combo.currentText()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#17152a')
            self.figure.patch.set_facecolor('#13111a')
            for sp in ax.spines.values():
                sp.set_edgecolor('#2a2440')
            ax.tick_params(colors='#5a5275', labelsize=9)

            try:
                if "Pasta" in chart:
                    type_counts = self.df["Tip 1"].value_counts()
                    colors = [TYPE_COLORS.get(t.lower(), "#888") for t in type_counts.index]
                    wedges, texts, autotexts = ax.pie(
                        type_counts.values, labels=type_counts.index,
                        autopct='%1.0f%%', colors=colors,
                        textprops={'color': '#c8c0e0', 'fontsize': 8},
                        startangle=140, pctdistance=0.82,
                        wedgeprops={'linewidth': 0.5, 'edgecolor': '#13111a'}
                    )
                    for at in autotexts:
                        at.set_fontsize(7)
                        at.set_color('#e4e0f0')
                    ax.set_title("Birincil Tip Dağılımı", color='#a99de8', fontsize=12, pad=14)

                elif "Ortalama Stat" in chart:
                    stats = ["HP", "Atak", "Savunma", "Öz Atak", "Öz Savunma", "Hız"]
                    means = [self.df[s].mean() for s in stats]
                    colors = list(STAT_COLORS.values())
                    bars = ax.barh(stats, means, color=colors, edgecolor='#13111a', linewidth=0.5)
                    for bar, v in zip(bars, means):
                        ax.text(v + 1, bar.get_y() + bar.get_height()/2,
                                f'{v:.0f}', va='center', color='#8880a8', fontsize=9)
                    ax.set_xlabel("Ortalama", color='#5a5275')
                    ax.set_title("Ortalama Base Stat Karşılaştırması", color='#a99de8', fontsize=12)
                    ax.invert_yaxis()

                elif "Histogram" in chart:
                    ax.hist(self.df["Toplam Stat"], bins=20,
                            color='#6c5ce7', edgecolor='#13111a', linewidth=0.5, alpha=0.85)
                    ax.set_xlabel("Toplam BST", color='#5a5275')
                    ax.set_ylabel("Pokémon Sayısı", color='#5a5275')
                    ax.set_title("Toplam Base Stat Dağılımı", color='#a99de8', fontsize=12)
                    mean = self.df["Toplam Stat"].mean()
                    ax.axvline(mean, color='#a29bfe', linestyle='--', linewidth=1.5, alpha=0.7)
                    ax.text(mean + 3, ax.get_ylim()[1] * 0.9, f'Ort: {mean:.0f}',
                            color='#a29bfe', fontsize=9)

                elif "Scatter" in chart:
                    types = self.df["Tip 1"].str.lower()
                    colors = [TYPE_COLORS.get(t, "#888") for t in types]
                    ax.scatter(self.df["HP"], self.df["Hız"], c=colors,
                               alpha=0.75, s=55, edgecolors='#13111a', linewidths=0.5)
                    ax.set_xlabel("HP", color='#5a5275')
                    ax.set_ylabel("Hız", color='#5a5275')
                    ax.set_title("HP vs Hız (renk = Tip)", color='#a99de8', fontsize=12)

                elif "Top 15" in chart:
                    top = self.df.nlargest(15, "Toplam Stat")[["Ad", "Toplam Stat", "Tip 1"]].iloc[::-1]
                    colors = [TYPE_COLORS.get(t.lower(), "#888") for t in top["Tip 1"]]
                    bars = ax.barh(top["Ad"], top["Toplam Stat"],
                                   color=colors, edgecolor='#13111a', linewidth=0.5)
                    for bar, v in zip(bars, top["Toplam Stat"]):
                        ax.text(v + 2, bar.get_y() + bar.get_height()/2,
                                str(v), va='center', color='#e4e0f0', fontsize=9)
                    ax.set_xlabel("Toplam BST", color='#5a5275')
                    ax.set_title("En Güçlü 15 Pokémon", color='#a99de8', fontsize=12)

                self.figure.tight_layout(pad=1.5)
                self.canvas.draw()

            except Exception as e:
                ax.text(0.5, 0.5, f"Grafik çizilemedi:\n{e}",
                        ha='center', va='center', color='#ef5350',
                        transform=ax.transAxes, fontsize=11)
                self.canvas.draw()

class PokedexApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pokemon_data = []
        self.df = None
        self.worker = None
        self._build()

    def _build(self):
        self.setWindowTitle("Pokédex Explorer — PokéAPI v2")
        self.resize(1400, 900)
        self.setMinimumSize(1000, 700)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(16, 12, 16, 8)
        main.setSpacing(10)

        main.addWidget(self._header())
        main.addWidget(self._controls())

        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setValue(0)
        main.addWidget(self.progress)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tabs = QTabWidget()
        self.tabs.setMinimumWidth(700)

        self._build_table_tab()
        self._build_cards_tab()
        if HAS_MPL:
            self.dashboard = Dashboard()
            self.tabs.addTab(self.dashboard, "📊  DASHBOARD")

        self.splitter.addWidget(self.tabs)

        self.detail = DetailPanel()
        detail_scroll = QScrollArea()
        detail_scroll.setWidget(self.detail)
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setFixedWidth(300)
        detail_scroll.setStyleSheet("background:#13111a; border:1px solid #1e1b2e; border-radius:10px;")
        self.splitter.addWidget(detail_scroll)

        main.addWidget(self.splitter, 1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Hazır — Filtrele ve 'Pokémon Yükle' butonuna bas.")

        self._menu()

    def _header(self):
        w = QWidget()
        w.setFixedHeight(64)
        w.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)

        icon = QLabel("⬟")
        icon.setStyleSheet("color:#6c5ce7; font-size:32px;")
        lay.addWidget(icon)

        txt = QVBoxLayout()
        t1 = QLabel("POKÉDEX EXPLORER")
        t1.setStyleSheet("color:#e4e0f0; font-size:22px; font-weight:900; letter-spacing:3px;")
        t2 = QLabel("PokéAPI v2  ·  REST API Demo  ·  PyQt6")
        t2.setStyleSheet("color:#3d3560; font-size:11px; letter-spacing:2px;")
        txt.addWidget(t1)
        txt.addWidget(t2)
        lay.addLayout(txt)
        lay.addStretch()

        self.count_lbl = QLabel("— Pokémon")
        self.count_lbl.setStyleSheet("color:#6c5ce7; font-size:28px; font-weight:900;")
        lay.addWidget(self.count_lbl)
        return w

    def _controls(self):
        grp = QGroupBox("ARAMA & FİLTRE")
        lay = QHBoxLayout(grp)
        lay.setSpacing(12)

        self.search_in = QLineEdit()
        self.search_in.setObjectName("search_bar")
        self.search_in.setPlaceholderText("🔍  Pokémon ara...  (örn: char, pika, bul)")
        self.search_in.textChanged.connect(self._live_filter)
        lay.addWidget(self.search_in, 2)

        lay.addWidget(QLabel("Tip:"))
        self.type_combo = QComboBox()
        self.type_combo.setMinimumWidth(130)
        self.type_combo.addItem("Tümü")
        for t in sorted(TYPE_COLORS.keys()):
            self.type_combo.addItem(t.title())
        self.type_combo.currentTextChanged.connect(self._live_filter)
        lay.addWidget(self.type_combo)

        lay.addWidget(QLabel("Limit:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(10, 1025)
        self.limit_spin.setValue(151)
        self.limit_spin.setToolTip("Kaç Pokémon yüklensin? (Max 1025 — tüm Pokémon)")
        lay.addWidget(self.limit_spin)


        lay.addWidget(QLabel("Sırala:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["#", "Ad", "Toplam Stat", "HP", "Atak", "Hız"])
        self.sort_combo.currentTextChanged.connect(self._live_filter)
        lay.addWidget(self.sort_combo)

        self.fetch_btn = QPushButton("▶  Pokémon Yükle")
        self.fetch_btn.setObjectName("fetch_btn")
        self.fetch_btn.setMinimumHeight(44)
        self.fetch_btn.clicked.connect(self.start_fetch)
        lay.addWidget(self.fetch_btn)

        self.stop_btn = QPushButton("■")
        self.stop_btn.setObjectName("danger_btn")
        self.stop_btn.setToolTip("Durdur")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedSize(40, 44)
        self.stop_btn.clicked.connect(self.stop_fetch)
        lay.addWidget(self.stop_btn)

        return grp

    def _build_table_tab(self):
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_table_select)
        self.tabs.addTab(self.table, "📋  TABLO")

    def _build_cards_tab(self):
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(12)
        self.cards_grid.setContentsMargins(12, 12, 12, 12)
        self.cards_scroll.setWidget(self.cards_container)
        self.tabs.addTab(self.cards_scroll, "🃏  KARTLAR")

    def _menu(self):
        mb = self.menuBar()
        mb.setStyleSheet("background:#0e0c18; color:#5a5275; border-bottom:1px solid #1e1b2e;")

        fm = mb.addMenu("Dosya")
        ex = QAction("Excel'e Aktar", self)
        ex.triggered.connect(lambda: self._export("excel"))
        cv = QAction("CSV'ye Aktar", self)
        cv.triggered.connect(lambda: self._export("csv"))
        fm.addAction(ex)
        fm.addAction(cv)
        fm.addSeparator()
        fm.addAction(QAction("Çıkış", self, triggered=self.close))

        hm = mb.addMenu("Yardım")
        hm.addAction(QAction("PokéAPI Hakkında", self, triggered=self._about))
    def start_fetch(self):
        self.fetch_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)
        self.pokemon_data = []
        self.count_lbl.setText("Yükleniyor...")

        type_f = self.type_combo.currentText()
        self.worker = PokemonWorker(
            limit=self.limit_spin.value(),
            types_filter=([type_f.lower()] if type_f != "Tümü" else []),
            search_name=self.search_in.text(),
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.log.connect(self._log)
        self.worker.result.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def stop_fetch(self):
        if self.worker:
            self.worker.abort()
        self.fetch_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _on_progress(self, cur, total):
        self.progress.setValue(int(cur / total * 100))
        self.status.showMessage(f"Yükleniyor... {cur}/{total}")

    def _log(self, msg, level):
        if level in ("ok", "error", "warn"):
            self.status.showMessage(msg)

    def _on_result(self, data: list):
        self.fetch_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setValue(100)

        if not data:
            self.status.showMessage("⚠ Hiç veri gelmedi. İnternet bağlantını kontrol et.")
            self.count_lbl.setText("0 Pokémon")
            return

        self.pokemon_data = data
        self.df = pd.DataFrame(data)

        # Sütun adı kontrolü
        if "Ad" not in self.df.columns:
            self.status.showMessage(f"⚠ Beklenmedik veri formatı. Sütunlar: {list(self.df.columns)[:5]}")
            return

        self._live_filter()
        self.status.showMessage(f"✓ {len(data)} Pokémon yüklendi!")

        if HAS_MPL and self.df is not None:
            self.dashboard.set_df(self.df)

    def _on_error(self, msg):
        self.fetch_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setValue(0)
        QMessageBox.critical(self, "Hata", f"API Hatası:\n{msg}\n\nİnternet bağlantını kontrol et.")

    def _live_filter(self):
        if self.df is None or self.df.empty or "Ad" not in self.df.columns:
            return

        df = self.df.copy()
        txt = self.search_in.text().lower().strip()
        if txt:
            df = df[df["Ad"].str.lower().str.contains(txt)]
        tp = self.type_combo.currentText()
        if tp != "Tümü":
            df = df[df["Tipler"].str.lower().str.contains(tp.lower())]
        sort_col = self.sort_combo.currentText()
        col_map = {"#": "#", "Ad": "Ad", "Toplam Stat": "Toplam Stat",
                   "HP": "HP", "Atak": "Atak", "Hız": "Hız"}
        sc = col_map.get(sort_col, "#")
        asc = sc in ["#", "Ad"]
        df = df.sort_values(sc, ascending=asc)

        self.count_lbl.setText(f"{len(df)} Pokémon")
        self._populate_table(df)
        self._populate_cards(df.head(100))

    def _populate_table(self, df: pd.DataFrame):
        COLS = ["#", "Ad", "Tip 1", "Tip 2", "HP", "Atak", "Savunma",
                "Öz Atak", "Öz Savunma", "Hız", "Toplam Stat", "Boy (dm)", "Kilo (hg)"]
        show_cols = [c for c in COLS if c in df.columns]

        self.table.setSortingEnabled(False)
        self.table.setColumnCount(len(show_cols))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(show_cols)

        for i, (_, row) in enumerate(df.iterrows()):
            for j, col in enumerate(show_cols):
                val = str(row[col])
                item = QTableWidgetItem()
                # Sayısal sıralama için
                try:
                    item.setData(Qt.ItemDataRole.DisplayRole, int(row[col]))
                except (ValueError, TypeError):
                    item.setText(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Tip renkli badge efekti
                if col in ("Tip 1", "Tip 2") and val not in ("—", "nan"):
                    c = TYPE_COLORS.get(val.lower(), "#ccc")
                    item.setForeground(QColor(c))
                    item.setText(val)

                self.table.setItem(i, j, item)
            # Satırda raw data sakla
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, row.to_dict())

        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)

    def _populate_cards(self, df: pd.DataFrame):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 5
        for i, (_, row) in enumerate(df.iterrows()):
            card = PokemonCard(row.to_dict())
            self.cards_grid.addWidget(card, i // cols, i % cols)

    def _on_table_select(self):
        rows = self.table.selectedItems()
        if not rows:
            return
        row_idx = self.table.currentRow()
        item = self.table.item(row_idx, 0)
        if item:
            data = item.data(Qt.ItemDataRole.UserRole)
            if data:
                self.detail.show_pokemon(data)
    def _export(self, fmt):
        if self.df is None or self.df.empty:
            QMessageBox.information(self, "Veri Yok", "Önce Pokémon yükle!")
            return

        exp_cols = ["#", "Ad", "Tip 1", "Tip 2", "HP", "Atak", "Savunma",
                    "Öz Atak", "Öz Savunma", "Hız", "Toplam Stat",
                    "Boy (dm)", "Kilo (hg)", "Yetenekler"]
        export_df = self.df[[c for c in exp_cols if c in self.df.columns]]

        if fmt == "excel":
            path, _ = QFileDialog.getSaveFileName(self, "Excel Kaydet",
                "pokedex_export.xlsx", "Excel (*.xlsx)")
            if path:
                try:
                    export_df.to_excel(path, index=False, engine='openpyxl')
                    self.status.showMessage(f"✓ Excel kaydedildi: {path}")
                except ImportError:
                    QMessageBox.critical(self, "Hata", "pip install openpyxl")
        else:
            path, _ = QFileDialog.getSaveFileName(self, "CSV Kaydet",
                "pokedex_export.csv", "CSV (*.csv)")
            if path:
                export_df.to_csv(path, index=False, encoding="utf-8-sig")
                self.status.showMessage(f"✓ CSV kaydedildi: {path}")

    def _about(self):
        QMessageBox.about(self, "Hakkında",
            "<h3>Pokédex Explorer</h3>"
            "<p>PokéAPI v2'yi kullanan açık kaynaklı Pokémon veri görüntüleyici.</p>"
            "<b>API:</b> <a href='https://pokeapi.co'>pokeapi.co</a> — ücretsiz, key gerektirmez<br>"
            "<b>Teknoloji:</b> Python 3 · PyQt6 · Pandas · Matplotlib · Requests<br><br>"
            "<i>REST API Data Manager — Generic Edition demo projesi</i>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor("#13111a"))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor("#e4e0f0"))
    pal.setColor(QPalette.ColorRole.Base,            QColor("#1e1b2e"))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor("#13111e"))
    pal.setColor(QPalette.ColorRole.Text,            QColor("#e4e0f0"))
    pal.setColor(QPalette.ColorRole.Button,          QColor("#2a2440"))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor("#a99de8"))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor("#6c5ce7"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)
    app.setStyleSheet(STYLE)

    win = PokedexApp()
    win.show()
    sys.exit(app.exec())
