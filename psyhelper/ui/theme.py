CSS = """
<style>
.stApp { color: #292724; }
.block-container { max-width: 1180px; padding-top: 2.3rem; padding-bottom: 4rem; }
.ph-eyebrow { color:#756f68; font-size:.78rem; font-weight:650; letter-spacing:.08em; text-transform:uppercase; }
.ph-lead { color:#625d57; font-size:1.08rem; max-width:720px; margin-top:-.4rem; }
.ph-patient { background:#fff; border:1px solid #e4ded7; border-radius:14px; padding:1.35rem 1.4rem .65rem; min-height:270px; }
.ph-patient h3 { margin:.15rem 0 .1rem; font-size:1.22rem; }
.ph-focus { color:#625d57; min-height:3.1rem; }
.ph-row { display:grid; grid-template-columns:7rem 1fr; gap:.6rem; padding:.38rem 0; border-top:1px solid #f0ece7; font-size:.91rem; }
.ph-label { color:#79736c; }
.ph-positive { color:#46705d; font-weight:650; }
.ph-attention { color:#90622f; font-weight:650; }
.ph-insight { border-left:3px solid #b8795e; padding:.2rem 0 .2rem 1rem; margin:1.1rem 0; }
.ph-insight p { margin:.25rem 0; }
.ph-timeline { border-left:1px solid #d8d1c9; padding:0 0 1.5rem 1.25rem; margin-left:.35rem; }
.ph-note { background:#fff; border:1px solid #e4ded7; border-radius:10px; padding:1rem 1.1rem; }
.ph-disclaimer { color:#79736c; font-size:.84rem; padding-top:1.5rem; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #e4ded7; border-radius:12px; padding:1rem; }
@media (max-width: 760px) { .block-container{padding-top:1.2rem}.ph-patient{min-height:auto}.ph-row{grid-template-columns:6.5rem 1fr} }
</style>
"""


def apply_theme(st):
    st.markdown(CSS, unsafe_allow_html=True)
