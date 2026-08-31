CSS = """
<style>
.stApp { color: #292724; }
.block-container { max-width: 1180px; padding-top: 1.8rem; padding-bottom: 3rem; }
.ph-eyebrow { color:#756f68; font-size:.78rem; font-weight:650; letter-spacing:.08em; text-transform:uppercase; }
.ph-lead { color:#625d57; font-size:1.08rem; max-width:720px; margin-top:-.4rem; }
.ph-patient { background:#fff; border:1px solid #e4ded7; border-radius:14px; padding:1.35rem 1.4rem .65rem; min-height:270px; }
.ph-patient h3 { margin:.15rem 0 .1rem; font-size:1.22rem; }
.ph-focus { color:#625d57; min-height:3.1rem; }
.ph-row { display:grid; grid-template-columns:7rem 1fr; gap:.6rem; padding:.38rem 0; border-top:1px solid #f0ece7; font-size:.91rem; }
.ph-label { color:#79736c; }
.ph-positive { color:#46705d; font-weight:650; }
.ph-attention { color:#90622f; font-weight:650; }
.ph-insight { border-left:3px solid #b8795e; padding:.1rem 0 .1rem .85rem; margin:.75rem 0; }
.ph-insight p { margin:.25rem 0; }
.ph-timeline { border-left:1px solid #d8d1c9; padding:0 0 1rem 1.1rem; margin-left:.35rem; }
.ph-note { background:#fff; border:1px solid #e4ded7; border-radius:10px; padding:1rem 1.1rem; }
.ph-disclaimer { color:#79736c; font-size:.84rem; padding-top:1.5rem; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #e4ded7; border-radius:12px; padding:1rem; }
.ph-meta { color:#756f68; font-size:.88rem; }
.ph-badge { display:inline-block; border-radius:999px; padding:.25rem .65rem; font-size:.8rem; font-weight:650; background:#eeeae5; color:#625d57; }
.ph-completed { background:#e6eee9; color:#46705d; }.ph-expired { background:#f3e8df; color:#90622f; }
.ph-answer { border-top:1px solid #eee9e3; padding:.55rem 0; line-height:1.45; }
.ph-answer:first-child { border-top:0; padding-top:0; }
.ph-adherence { background:#fff; border:1px solid #e4ded7; border-radius:12px; padding:.9rem 1.1rem; display:flex; align-items:baseline; gap:1.25rem; flex-wrap:wrap; }
.ph-adherence strong { color:#292724; font-size:1.35rem; }.ph-adherence span { color:#756f68; }
.ph-semantic-metric { background:#fff; border:1px solid #e4ded7; border-radius:12px; padding:1rem; display:flex; flex-direction:column; gap:.18rem; }
.ph-semantic-metric > span { color:#625d57; font-size:.9rem; }.ph-semantic-metric > strong { font-size:2rem; line-height:1.2; }
.ph-semantic-metric small { font-weight:650; }.ph-delta-positive { color:#46705d; }.ph-delta-attention { color:#9a681f; }.ph-delta-neutral { color:#756f68; }
div[data-testid="stExpander"] details summary { padding-top:.55rem; padding-bottom:.55rem; }
@media (max-width: 760px) { .block-container{padding-top:1.2rem}.ph-patient{min-height:auto}.ph-row{grid-template-columns:6.5rem 1fr} }
</style>
"""


def apply_theme(st):
    st.markdown(CSS, unsafe_allow_html=True)
