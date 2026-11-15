"""Step 4: build a single self-contained HTML dashboard from the CSVs in outputs/.

The page is written to docs/index.html. GitHub Pages serves the docs/ folder,
so pushing this file publishes the dashboard. Plotly's JavaScript is copied
into the page, so it works offline and needs no other files.
"""
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
PAGE_PATH = os.path.join(ROOT, "docs", "index.html")

LAKH = 100_000  # Indian prices are usually quoted in lakh (1 lakh = 100,000 rupees)

# Colours (light theme). The page switches to dark colours with a small script.
BLUE = "#2a78d6"      # main series colour, and "below market"
RED = "#e34948"       # "above market"
NEUTRAL = "#d6d5cf"   # "in line"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"


def read(name):
    return pd.read_csv(os.path.join(OUT, name + ".csv"))


def base_layout(fig, height=380):
    """Apply the same clean look to every chart."""
    fig.update_layout(
        height=height,
        margin=dict(l=56, r=20, t=16, b=48),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=13, color=MUTED),
        hoverlabel=dict(bgcolor="white", font_color=INK, bordercolor=AXIS),
        showlegend=False,
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False)
    return fig


def chart_buy_map():
    """Scatter: how often a model is listed vs how well it keeps its value."""
    df = read("07_value_retention_by_model")
    df["name"] = df["brand"] + " " + df["model"]

    # Label the busiest models plus a few luxury ones for contrast.
    labelled = set(df.nlargest(7, "listings")["name"]) | {
        "Maruti Celerio", "Maruti Ertiga", "Mercedes-Benz C-Class", "BMW 3 Series", "Toyota Fortuner",
    }
    df["label"] = df["name"].where(df["name"].isin(labelled), "")

    # Move a few labels so neighbouring dots don't print on top of each other.
    positions = {
        "Maruti Alto": "top right", "Maruti Wagon R": "top left", "Maruti Swift": "top left",
        "Hyundai i20": "middle left", "Maruti Swift Dzire": "bottom left",
        "Mercedes-Benz C-Class": "middle left",
    }
    df["position"] = df["name"].map(positions).fillna("top center")

    fig = go.Figure(go.Scatter(
        x=df["listings"],
        y=df["retention_pct"],
        mode="markers+text",
        text=df["label"],
        textposition=df["position"],
        textfont=dict(size=11),
        marker=dict(size=11, color=BLUE, line=dict(width=2, color=SURFACE)),
        customdata=df[["name", "median_price_2_4_yrs", "median_price_7_9_yrs"]].assign(
            median_price_2_4_yrs=lambda d: d["median_price_2_4_yrs"] / LAKH,
            median_price_7_9_yrs=lambda d: d["median_price_7_9_yrs"] / LAKH,
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>%{x} listings<br>Keeps %{y:.0f}% of its value"
            "<br>2-4 yrs: ₹%{customdata[1]:.1f} lakh<br>7-9 yrs: ₹%{customdata[2]:.1f} lakh<extra></extra>"
        ),
    ))
    base_layout(fig, height=440)
    fig.update_layout(margin=dict(l=64))
    fig.update_xaxes(type="log", title="Listings in the market (log scale)", range=[0.6, 3.2])
    fig.update_yaxes(title="Value kept at 7-9 yrs vs 2-4 yrs", ticksuffix="%")
    return fig


def chart_segments():
    """Horizontal bars: the most-listed model + age segments."""
    df = read("06_most_listed_segments").head(12)
    df["segment"] = df["brand"] + " " + df["model"] + " · " + df["age_band"]
    fig = go.Figure(go.Bar(
        x=df["listings"],
        y=df["segment"],
        orientation="h",
        marker=dict(color=BLUE, cornerradius=4),
        customdata=pd.DataFrame({"price": df["median_price"] / LAKH, "km": df["median_km"]}),
        hovertemplate="<b>%{y}</b><br>%{x} listings<br>Median ₹%{customdata[0]:.1f} lakh"
                      "<br>Median %{customdata[1]:,.0f} km<extra></extra>",
    ))
    base_layout(fig, height=420)
    fig.update_layout(margin=dict(l=190), bargap=0.25)
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(title="Listings")
    return fig


def chart_depreciation():
    """Line: median price by age."""
    df = read("02_depreciation_by_age")
    df["age_label"] = df["age_years"].astype(str)
    df.loc[df["age_years"] == 15, "age_label"] = "15+"
    fig = go.Figure(go.Scatter(
        x=df["age_label"],
        y=df["median_price"] / LAKH,
        mode="lines+markers",
        line=dict(color=BLUE, width=2),
        marker=dict(size=8, color=BLUE, line=dict(width=2, color=SURFACE)),
        customdata=df[["pct_of_age2_price", "listings"]],
        hovertemplate="<b>%{x} years old</b><br>Median ₹%{y:.1f} lakh<br>%{customdata[0]:.0f}% of the 2-year price"
                      "<br>%{customdata[1]} listings<extra></extra>",
    ))
    base_layout(fig)
    fig.update_xaxes(title="Car age (years)", type="category")
    fig.update_yaxes(title="Median price (₹ lakh)", rangemode="tozero")
    return fig


def chart_km():
    """Line: price index (100 = same model and age) by km band."""
    df = read("03_price_vs_km")
    fig = go.Figure(go.Scatter(
        x=df["km_band"],
        y=df["median_price_index"],
        mode="lines+markers",
        line=dict(color=BLUE, width=2),
        marker=dict(size=8, color=BLUE, line=dict(width=2, color=SURFACE)),
        customdata=df[["listings"]],
        hovertemplate="<b>%{x} km</b><br>Price index %{y:.1f}<br>%{customdata[0]} listings<extra></extra>",
    ))
    base_layout(fig)
    fig.add_hline(y=100, line=dict(color=AXIS, width=1, dash="dot"))
    fig.update_layout(margin=dict(l=64))
    fig.update_xaxes(title="Kilometres driven", type="category")
    fig.update_yaxes(title="Price index (100 = typical)", range=[90, 106])
    return fig


def chart_flags():
    """Histogram: each listing's price as a % of its peer median, coloured by flag."""
    df = read("08_pricing_flags")
    # Very extreme values are squeezed to the edges so the chart stays readable.
    df["pct"] = df["price_vs_peers_pct"].clip(30, 200)
    fig = go.Figure()
    for flag, colour in [("Below market", BLUE), ("In line", NEUTRAL), ("Above market", RED)]:
        part = df[df["price_flag"] == flag]
        fig.add_trace(go.Histogram(
            x=part["pct"],
            name=f"{flag} ({len(part):,})",
            marker=dict(color=colour, line=dict(width=1, color=SURFACE)),
            xbins=dict(start=30, end=205, size=5),
            hovertemplate=flag + "<br>%{x}% of peer price<br>%{y} listings<extra></extra>",
        ))
    base_layout(fig)
    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=12)),
        margin=dict(t=56),
    )
    fig.update_xaxes(title="Asking price as % of similar cars' median", ticksuffix="%")
    fig.update_yaxes(title="Listings")
    return fig


def deals_table():
    """HTML table: below-market listings with the biggest peer groups."""
    df = read("08_pricing_flags")
    deals = (df[(df["price_flag"] == "Below market") & (df["peer_count"] >= 20)]
             .sort_values("price_vs_peers_pct")
             .head(10))
    rows = ""
    for _, r in deals.iterrows():
        rows += (
            "<tr>"
            f"<td>{r['car_name']}</td><td>{r['vehicle_age']} yrs</td>"
            f"<td class='num'>{r['km_driven']:,}</td><td>{r['fuel_type']} · {r['transmission_type']}</td>"
            f"<td class='num'>₹{r['selling_price'] / LAKH:.1f}L</td>"
            f"<td class='num'>₹{r['peer_median_price'] / LAKH:.1f}L</td>"
            f"<td class='num'>{r['price_vs_peers_pct']:.0f}%</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Car</th><th>Age</th><th class='num'>km</th><th>Fuel · gearbox</th>"
        "<th class='num'>Asking</th><th class='num'>Peer median</th><th class='num'>vs peers</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>"
    )


def tile(value, label):
    return f"<div class='tile'><div class='tile-value'>{value}</div><div class='tile-label'>{label}</div></div>"


def card(title, subtitle, body):
    return f"<section class='card'><h3>{title}</h3><p class='sub'>{subtitle}</p>{body}</section>"


def fig_html(fig):
    return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False, "responsive": True})


CSS = """
:root {
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e;
  --muted: #6f6e69; --border: rgba(11,11,11,0.10); --accent: #2a78d6;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7;
    --muted: #a3a29b; --border: rgba(255,255,255,0.10); --accent: #3987e5;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7;
  --muted: #a3a29b; --border: rgba(255,255,255,0.10); --accent: #3987e5;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height: 1.5; }
main { max-width: 1120px; margin: 0 auto; padding: 32px 16px 64px; }
h1 { font-size: 28px; margin: 0 0 6px; letter-spacing: -0.01em; }
h2 { font-size: 19px; margin: 40px 0 4px; }
h3 { font-size: 16px; margin: 0 0 2px; }
.lede { color: var(--ink-2); margin: 0 0 20px; max-width: 760px; }
.section-note { color: var(--ink-2); margin: 0 0 14px; }
.sub { color: var(--muted); font-size: 14px; margin: 0 0 8px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }
.tile { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
.tile-value { font-size: 26px; font-weight: 650; }
.tile-label { color: var(--ink-2); font-size: 13px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 18px 18px 8px; margin-top: 16px; min-width: 0; }
.grid .card { margin-top: 0; }
.table-wrap { overflow-x: auto; padding-bottom: 10px; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--border); white-space: nowrap; }
th { color: var(--muted); font-weight: 600; font-size: 13px; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
footer { color: var(--muted); font-size: 13px; margin-top: 40px; }
a { color: var(--accent); }
@media (max-width: 900px) {
  .grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  h1 { font-size: 23px; }
  .tile-value { font-size: 22px; }
}
"""

# Runs after the page has loaded:
# 1. resize every chart to fit its card (charts are drawn while the page is still loading),
#    and hide scatter labels on phones,
# 2. if the reader's system is in dark mode, recolour the charts to match.
PAGE_JS = """
(function () {
  var narrow = window.innerWidth < 600;
  document.querySelectorAll('.plotly-graph-div').forEach(function (div) {
    Plotly.Plots.resize(div);
    // On phones the scatter labels overlap, so show dots only (hover still works).
    if (narrow && div.data[0].mode === 'markers+text') {
      Plotly.restyle(div, {mode: 'markers'});
    }
  });
  var root = document.documentElement;
  var dark = root.dataset.theme === 'dark' ||
    (root.dataset.theme !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  if (!dark) return;
  document.querySelectorAll('.plotly-graph-div').forEach(function (div) {
    Plotly.relayout(div, {
      'font.color': '#c3c2b7',
      'xaxis.gridcolor': '#2c2c2a', 'yaxis.gridcolor': '#2c2c2a',
      'xaxis.linecolor': '#383835', 'yaxis.linecolor': '#383835',
      'hoverlabel.bgcolor': '#262624', 'hoverlabel.font.color': '#f0efec'
    });
    div.data.forEach(function (trace, i) {
      var update = {'marker.line.color': '#1a1a19'};
      if (trace.marker && trace.marker.color === '#2a78d6') { update['marker.color'] = '#3987e5'; }
      if (trace.line && trace.line.color === '#2a78d6') { update['line.color'] = '#3987e5'; }
      if (trace.marker && trace.marker.color === '#d6d5cf') { update['marker.color'] = '#4a4a46'; }
      if (trace.marker && trace.marker.color === '#e34948') { update['marker.color'] = '#e66767'; }
      Plotly.restyle(div, update, [i]);
    });
  });
})();
"""


def main():
    clean_rows = int(read("cleaning_log")["rows_after"].iloc[-1])
    raw_rows = int(read("cleaning_log")["rows_before"].iloc[0])
    premium = read("05_like_for_like_premium").set_index("comparison")["median_premium_pct"]
    flags = read("08_pricing_flags")["price_flag"].value_counts()
    flagged_total = int(flags.sum())
    depreciation = read("02_depreciation_by_age").set_index("age_years")

    kpis = "<div class='tiles'>" + "".join([
        tile(f"{clean_rows:,}", f"clean listings (from {raw_rows:,} raw rows)"),
        tile(f"{100 - depreciation.loc[5, 'pct_of_age2_price']:.0f}%",
             "value lost between year 2 and year 5"),
        tile(f"+{premium['Automatic vs Manual']:.1f}%", "automatic premium, same model & age"),
        tile(f"+{premium['Diesel vs Petrol']:.1f}%", "diesel premium, same model & age"),
        tile(f"{flags.get('Below market', 0):,}",
             f"listings priced 25%+ under similar cars ({100 * flags.get('Below market', 0) / flagged_total:.1f}%)"),
    ]) + "</div>"

    acquire = (
        "<h2>Decision 1 · Which stock to acquire</h2>"
        "<p class='section-note'>Buy models that trade often (easy to resell) and lose value slowly (low holding risk).</p>"
        + card("Mass-market Maruti and Hyundai models keep their value best",
               "Each dot is a model. Up = keeps more value as it ages; right = listed more often. Hover for prices.",
               fig_html(chart_buy_map()))
        + "<div class='grid' style='margin-top:16px'>"
        + card("Most-listed segments", "Model + age band, by number of listings (a stand-in for demand).",
               fig_html(chart_segments()))
        + card("Typical price by age", "Median asking price falls roughly 7-16% a year after year 2.",
               fig_html(chart_depreciation()))
        + "</div>"
    )

    pricing = (
        "<h2>Decision 2 · What price to list at</h2>"
        "<p class='section-note'>Start from the median price of the same model and age, then adjust for gearbox, fuel and km.</p>"
        + "<div class='grid'>"
        + card("Kilometres move the price only a little",
               "Once model and age are fixed, a 150k+ km car is priced only ~4% under a 0-20k km one.",
               fig_html(chart_km()))
        + card("How listings compare with similar cars",
               "Peers = same model, age, fuel and gearbox (5+ cars). Flags at ±25% of the peer median.",
               fig_html(chart_flags()))
        + "</div>"
        + card("Below-market listings worth a closer look",
               "Priced 25%+ under the peer median, with at least 20 peers. Check condition before buying: some may be data errors.",
               "<div class='table-wrap'>" + deals_table() + "</div>")
    )

    html = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Used Car Pricing</title>"
        f"<style>{CSS}</style>"
        f"<script>{get_plotlyjs()}</script>"
        "</head><body><main>"
        "<h1>Used car pricing: what to buy and what to charge</h1>"
        f"<p class='lede'>Analysis of {clean_rows:,} CarDekho used-car listings (India) to help a dealer decide "
        "which cars to stock and how to price them. All prices are asking prices in rupees; 1 lakh = ₹100,000.</p>"
        + kpis + acquire + pricing
        + "<footer>Data: CarDekho used car listings, Kaggle (manishkr1754/cardekho-used-car-data). "
          "Medians computed in SQLite. Listing volume is used as a proxy for demand because the data has no sale dates.</footer>"
        + f"</main><script>{PAGE_JS}</script></body></html>"
    )

    os.makedirs(os.path.dirname(PAGE_PATH), exist_ok=True)
    with open(PAGE_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard written to {PAGE_PATH} ({os.path.getsize(PAGE_PATH) / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    main()
