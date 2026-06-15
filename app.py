
# import streamlit as st
# import pickle
# import pandas as pd
# import numpy as np
# import datetime
# import json
# import io
# import time
# import streamlit as st

# # Page config 
# st.set_page_config(
#     page_title="MediAI - Disease Prediction",
#     page_icon="🏥",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ── PDF generation 
# try:
#     from fpdf import FPDF
#     PDF_AVAILABLE = True
# except ImportError:
#     PDF_AVAILABLE = False

# from gemini_helper import (
#     ask_ai,
#     ask_followup,
#     get_disease_risk_level,
#     generate_health_report_summary,
# )

# # ════════════════════════════════════════════════════════════════
# # PAGE CONFIG
# # ════════════════════════════════════════════════════════════════

# st.set_page_config(
#     page_title="MediAI — Disease Prediction",
#     page_icon="🩺",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # ════════════════════════════════════════════════════════════════
# # HELPERS
# # ════════════════════════════════════════════════════════════════

# def safe_latin1(text: str) -> str:
#     """Strip any character that Helvetica / Latin-1 can't handle."""
#     return text.encode("latin-1", errors="replace").decode("latin-1")


# def call_gemini_with_retry(fn, *args, max_retries=3, **kwargs):
#     """
#     Call any gemini_helper function with exponential back-off.
#     Handles 503 / ResourceExhausted / overload gracefully.
#     """
#     for attempt in range(max_retries):
#         try:
#             return fn(*args, **kwargs)
#         except Exception as e:
#             err = str(e).lower()
#             # Retryable: overloaded / quota / 503 / rate-limit
#             if any(k in err for k in ["503", "overload", "resource_exhausted",
#                                        "quota", "rate", "unavailable", "high demand"]):
#                 if attempt < max_retries - 1:
#                     wait = 2 ** attempt          # 1 s, 2 s, 4 s
#                     st.toast(f"AI busy – retrying in {wait}s… ({attempt+1}/{max_retries})")
#                     time.sleep(wait)
#                 else:
#                     raise RuntimeError(
#                         "Gemini AI is currently overloaded. Please wait a moment and try again."
#                     )
#             else:
#                 raise   # non-retryable error – surface immediately


# # ════════════════════════════════════════════════════════════════
# # CUSTOM CSS  
# # ════════════════════════════════════════════════════════════════

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

# :root {
#     --bg:        #0d1117;
#     --surface:   #161b22;
#     --card:      #1c2333;
#     --border:    #30363d;
#     --accent:    #1f8aff;
#     --accent2:   #0acf97;
#     --warn:      #f59e0b;
#     --danger:    #ef4444;
#     --text:      #e6edf3;
#     --muted:     #8b949e;
#     --radius:    12px;
# }

# html, body, [class*="css"] {
#     font-family: 'Inter', sans-serif;
#     background-color: var(--bg) !important;
#     color: var(--text) !important;
# }

# #MainMenu, footer, header { visibility: hidden; }
# .block-container { padding: 2rem 2rem 4rem; max-width: 1100px; }

# [data-testid="stSidebar"] {
#     background: var(--surface) !important;
#     border-right: 1px solid var(--border);
# }
# [data-testid="stSidebar"] * { color: var(--text) !important; }

# .medi-card {
#     background: var(--card);
#     border: 1px solid var(--border);
#     border-radius: var(--radius);
#     padding: 1.5rem;
#     margin-bottom: 1.2rem;
#     transition: box-shadow .2s;
# }
# .medi-card:hover { box-shadow: 0 0 0 1px var(--accent); }

# .hero {
#     background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #1a2a3a 100%);
#     border: 1px solid var(--border);
#     border-radius: var(--radius);
#     padding: 2.5rem 2rem;
#     margin-bottom: 2rem;
#     text-align: center;
# }
# .hero h1 {
#     font-family: 'Syne', sans-serif;
#     font-size: 2.6rem;
#     font-weight: 800;
#     background: linear-gradient(90deg, #1f8aff, #0acf97);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
#     margin: 0 0 .5rem;
# }
# .hero p { color: var(--muted); font-size: 1.05rem; margin: 0; }

# .badge {
#     display: inline-block;
#     padding: .3rem .9rem;
#     border-radius: 999px;
#     font-size: .8rem;
#     font-weight: 600;
#     letter-spacing: .04em;
#     text-transform: uppercase;
# }
# .badge-low    { background: #0d3321; color: var(--accent2); border: 1px solid #0acf9740; }
# .badge-medium { background: #2d2006; color: var(--warn);   border: 1px solid #f59e0b40; }
# .badge-high   { background: #2d0a0a; color: var(--danger); border: 1px solid #ef444440; }

# .conf-ring { text-align: center; padding: .5rem; }
# .conf-ring .number {
#     font-family: 'Syne', sans-serif;
#     font-size: 2.8rem;
#     font-weight: 800;
#     color: var(--accent2);
#     line-height: 1;
# }
# .conf-ring .label {
#     font-size: .75rem;
#     color: var(--muted);
#     text-transform: uppercase;
#     letter-spacing: .1em;
# }

# .disease-name {
#     font-family: 'Syne', sans-serif;
#     font-size: 1.9rem;
#     font-weight: 700;
#     color: var(--text);
#     margin: .4rem 0;
# }

# .prob-bar-wrap { margin: .5rem 0; }
# .prob-bar-label { font-size: .85rem; color: var(--muted); margin-bottom: .2rem; }
# .prob-bar-track { height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
# .prob-bar-fill {
#     height: 100%;
#     border-radius: 4px;
#     background: linear-gradient(90deg, var(--accent), var(--accent2));
#     transition: width .8s cubic-bezier(.4,0,.2,1);
# }

# .chat-user {
#     background: #1a2744;
#     border: 1px solid #1f3a6e;
#     border-radius: var(--radius) var(--radius) 4px var(--radius);
#     padding: .8rem 1.1rem;
#     margin: .5rem 0 .5rem 3rem;
#     font-size: .9rem;
# }
# .chat-ai {
#     background: var(--card);
#     border: 1px solid var(--border);
#     border-radius: var(--radius) var(--radius) var(--radius) 4px;
#     padding: .8rem 1.1rem;
#     margin: .5rem 3rem .5rem 0;
#     font-size: .9rem;
#     line-height: 1.6;
# }

# .stButton > button {
#     background: linear-gradient(135deg, var(--accent), #0d6bcc) !important;
#     color: white !important;
#     border: none !important;
#     border-radius: 8px !important;
#     font-weight: 600 !important;
#     padding: .55rem 1.4rem !important;
#     transition: opacity .2s !important;
# }
# .stButton > button:hover { opacity: .85 !important; }

# [data-baseweb="tag"] {
#     background: #1a2744 !important;
#     border: 1px solid var(--accent) !important;
#     color: var(--text) !important;
# }

# input, textarea, [data-baseweb="input"] {
#     background: var(--surface) !important;
#     border-color: var(--border) !important;
#     color: var(--text) !important;
#     border-radius: 8px !important;
# }

# .section-title {
#     font-family: 'Syne', sans-serif;
#     font-size: 1.1rem;
#     font-weight: 700;
#     color: var(--muted);
#     text-transform: uppercase;
#     letter-spacing: .12em;
#     border-bottom: 1px solid var(--border);
#     padding-bottom: .5rem;
#     margin: 1.5rem 0 1rem;
# }

# .medi-footer {
#     text-align: center;
#     color: var(--muted);
#     font-size: .78rem;
#     padding: 2rem 0 .5rem;
#     border-top: 1px solid var(--border);
#     margin-top: 3rem;
# }
# </style>
# """, unsafe_allow_html=True)


# # ════════════════════════════════════════════════════════════════
# # LOAD ARTIFACTS
# # ════════════════════════════════════════════════════════════════

# @st.cache_resource(show_spinner=False)
# def load_artifacts():
#     errors = []
#     try:
#         model = pickle.load(open("model.pkl", "rb"))
#     except FileNotFoundError:
#         model = None
#         errors.append("model.pkl not found.")
#     try:
#         symptom_index = pickle.load(open("symptom_index.pkl", "rb"))
#     except FileNotFoundError:
#         symptom_index = {}
#         errors.append("symptom_index.pkl not found.")
#     try:
#         desc_df = pd.read_csv("symptom_Description.csv")
#     except FileNotFoundError:
#         desc_df = pd.DataFrame()
#         errors.append("symptom_Description.csv not found.")
#     try:
#         prec_df = pd.read_csv("symptom_precaution.csv")
#     except FileNotFoundError:
#         prec_df = pd.DataFrame()
#         errors.append("symptom_precaution.csv not found.")
#     return model, symptom_index, desc_df, prec_df, errors

# model, symptom_index, description_df, precaution_df, load_errors = load_artifacts()


# # ════════════════════════════════════════════════════════════════
# # SESSION STATE DEFAULTS
# # ════════════════════════════════════════════════════════════════

# for key, default in {
#     "disease": None,
#     "selected_symptoms": [],
#     "confidence": None,
#     "probabilities": None,
#     "chat_history": [],
#     "prediction_time": None,
#     "risk_level": None,
#     "ai_explanation": None,
#     "history_log": [],
# }.items():
#     if key not in st.session_state:
#         st.session_state[key] = default


# # ════════════════════════════════════════════════════════════════
# # SIDEBAR
# # ════════════════════════════════════════════════════════════════

# with st.sidebar:
#     st.markdown("## 🩺 MediAI")
#     st.caption("AI-Powered Disease Prediction")
#     st.divider()

#     st.markdown("### 📋 Session Summary")
#     if st.session_state.disease:
#         st.markdown(f"**Last Prediction:** {st.session_state.disease}")
#         if st.session_state.confidence:
#             st.markdown(f"**Confidence:** {st.session_state.confidence:.1f}%")
#         if st.session_state.prediction_time:
#             st.markdown(f"**Time:** {st.session_state.prediction_time}")
#         if st.session_state.risk_level:
#             lvl = st.session_state.risk_level
#             color = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}.get(lvl, "gray")
#             st.markdown(f"**Risk:** :{color}[{lvl}]")
#     else:
#         st.caption("No prediction yet.")

#     st.divider()

#     st.markdown("### ⚖️ BMI Calculator")
#     bmi_weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.5)
#     bmi_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)
#     if st.button("Calculate BMI", key="bmi_btn"):
#         h_m = bmi_height / 100
#         bmi = bmi_weight / (h_m ** 2)
#         if bmi < 18.5:
#             cat, col = "Underweight", "🔵"
#         elif bmi < 25:
#             cat, col = "Normal", "🟢"
#         elif bmi < 30:
#             cat, col = "Overweight", "🟡"
#         else:
#             cat, col = "Obese", "🔴"
#         st.markdown(f"**BMI: {bmi:.1f}** {col} {cat}")

#     st.divider()

#     st.markdown("### 🕘 Prediction History")
#     if st.session_state.history_log:
#         for entry in reversed(st.session_state.history_log[-5:]):
#             st.caption(f"- {entry['disease']} ({entry['conf']:.0f}%) — {entry['time']}")
#         if st.button("Clear History"):
#             st.session_state.history_log = []
#             st.rerun()
#     else:
#         st.caption("No history yet.")

#     st.divider()
#     st.caption("For educational use only. Not a substitute for medical advice.")
#     st.caption("Built by **Krishna Yadav**")

#     if load_errors:
#         st.divider()
#         st.markdown("### Missing Files")
#         for e in load_errors:
#             st.error(e)


# # ════════════════════════════════════════════════════════════════
# # HERO
# # ════════════════════════════════════════════════════════════════

# st.markdown("""
# <div class="hero">
#   <h1>MediAI Disease Prediction</h1>
#   <p>Select your symptoms · Get an instant ML-powered prediction · Ask your AI doctor</p>
# </div>
# """, unsafe_allow_html=True)


# # ════════════════════════════════════════════════════════════════
# # SYMPTOM SELECTION + PREDICT
# # ════════════════════════════════════════════════════════════════

# if not symptom_index:
#     st.error("Cannot load symptom data. Please check that symptom_index.pkl exists.")
#     st.stop()

# all_symptoms = sorted(symptom_index.keys())

# col_sel, col_btn = st.columns([4, 1], vertical_alignment="bottom")
# with col_sel:
#     selected_symptoms = st.multiselect(
#         "🔎 Select Symptoms",
#         all_symptoms,
#         placeholder="Type to search symptoms…",
#     )
# with col_btn:
#     predict_clicked = st.button("Predict", use_container_width=True)


# # ════════════════════════════════════════════════════════════════
# # PREDICTION LOGIC
# # ════════════════════════════════════════════════════════════════

# if predict_clicked:
#     if not selected_symptoms:
#         st.warning("Please select at least one symptom before predicting.")
#     elif model is None:
#         st.error("Model not loaded. Cannot make predictions.")
#     else:
#         with st.spinner("Analysing symptoms…"):
#             input_vector = [0] * len(symptom_index)
#             for s in selected_symptoms:
#                 if s in symptom_index:
#                     input_vector[symptom_index[s]] = 1

#             prediction = model.predict([input_vector])
#             disease = prediction[0]

#             confidence = None
#             probabilities = None
#             try:
#                 probabilities = model.predict_proba([input_vector])
#                 confidence = float(np.max(probabilities[0]) * 100)
#             except Exception:
#                 pass

#             st.session_state.disease = disease
#             st.session_state.selected_symptoms = selected_symptoms
#             st.session_state.confidence = confidence
#             st.session_state.probabilities = probabilities
#             st.session_state.chat_history = []
#             st.session_state.prediction_time = datetime.datetime.now().strftime("%H:%M, %b %d")
#             st.session_state.ai_explanation = None

#             st.session_state.history_log.append({
#                 "disease": disease,
#                 "conf": confidence or 0,
#                 "time": st.session_state.prediction_time,
#             })

#             try:
#                 st.session_state.risk_level = call_gemini_with_retry(get_disease_risk_level, disease)
#             except Exception:
#                 st.session_state.risk_level = "MEDIUM"


# # ════════════════════════════════════════════════════════════════
# # RESULTS
# # ════════════════════════════════════════════════════════════════

# if st.session_state.disease:
#     disease    = st.session_state.disease
#     confidence = st.session_state.confidence
#     probabilities = st.session_state.probabilities
#     risk_level = st.session_state.risk_level or "MEDIUM"

#     # ── Result header ─────────────────────────────────────────
#     r1, r2, r3 = st.columns([3, 1.2, 1.2])

#     with r1:
#         badge_class = f"badge-{risk_level.lower()}"
#         st.markdown(f"""
#         <div class="medi-card">
#           <div style="font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;">Predicted Disease</div>
#           <div class="disease-name">{disease}</div>
#           <span class="badge {badge_class}">Risk: {risk_level}</span>
#         </div>
#         """, unsafe_allow_html=True)

#     with r2:
#         if confidence is not None:
#             st.markdown(f"""
#             <div class="medi-card conf-ring">
#               <div class="number">{confidence:.0f}%</div>
#               <div class="label">Confidence</div>
#             </div>
#             """, unsafe_allow_html=True)

#     with r3:
#         st.markdown(f"""
#         <div class="medi-card conf-ring">
#           <div class="number">{len(st.session_state.selected_symptoms)}</div>
#           <div class="label">Symptoms</div>
#         </div>
#         """, unsafe_allow_html=True)

#     # ── Top-3 ─────────────────────────────────────────────────
#     if probabilities is not None:
#         st.markdown('<div class="section-title">Top 3 Possible Diagnoses</div>', unsafe_allow_html=True)
#         top3_idx = np.argsort(probabilities[0])[-3:][::-1]
#         for rank, idx in enumerate(top3_idx):
#             name  = model.classes_[idx]
#             pct   = probabilities[0][idx] * 100
#             marker = "1st" if rank == 0 else ("2nd" if rank == 1 else "3rd")
#             st.markdown(f"""
#             <div class="prob-bar-wrap">
#               <div class="prob-bar-label">{marker} &nbsp; {name} &nbsp; <strong>{pct:.1f}%</strong></div>
#               <div class="prob-bar-track"><div class="prob-bar-fill" style="width:{pct:.1f}%"></div></div>
#             </div>
#             """, unsafe_allow_html=True)

#     # ── Tabs ──────────────────────────────────────────────────
#     tab_info, tab_ai, tab_chat, tab_export = st.tabs([
#         "📋 Disease Info",
#         "🤖 AI Explanation",
#         "💬 Ask AI Doctor",
#         "📥 Export Report",
#     ])

#     # ── TAB 1: Info ───────────────────────────────────────────
#     with tab_info:
#         col_desc, col_prec = st.columns(2)

#         with col_desc:
#             st.markdown('<div class="section-title">Description</div>', unsafe_allow_html=True)
#             if not description_df.empty:
#                 row = description_df[description_df["Disease"] == disease]
#                 if not row.empty:
#                     st.markdown(f'<div class="medi-card">{row.iloc[0][row.columns[1]]}</div>',
#                                 unsafe_allow_html=True)
#                 else:
#                     st.info("No description available.")
#             else:
#                 st.info("Description data not loaded.")

#         with col_prec:
#             st.markdown('<div class="section-title">Recommended Precautions</div>', unsafe_allow_html=True)
#             if not precaution_df.empty:
#                 row = precaution_df[precaution_df["Disease"] == disease]
#                 if not row.empty:
#                     prec_items = [row.iloc[0][c] for c in row.columns[1:] if pd.notna(row.iloc[0][c])]
#                     if prec_items:
#                         items_html = "".join(f"<li>✅ {p}</li>" for p in prec_items)
#                         st.markdown(
#                             f'<div class="medi-card"><ul style="margin:0;padding-left:1.2rem;">{items_html}</ul></div>',
#                             unsafe_allow_html=True)
#                     else:
#                         st.info("No precautions listed.")
#                 else:
#                     st.info("No precautions available.")
#             else:
#                 st.info("Precaution data not loaded.")

#         st.markdown('<div class="section-title">Symptoms You Reported</div>', unsafe_allow_html=True)
#         tags_html = " ".join(
#             f'<span style="background:#1a2744;border:1px solid #1f3a6e;border-radius:999px;'
#             f'padding:.2rem .7rem;font-size:.82rem;margin:.2rem;display:inline-block;">{s}</span>'
#             for s in st.session_state.selected_symptoms
#         )
#         st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)

#     # ── TAB 2: AI Explanation ─────────────────────────────────
#     with tab_ai:
#         if st.session_state.ai_explanation:
#             st.markdown(st.session_state.ai_explanation)
#         else:
#             if st.button("Generate AI Medical Explanation", key="gen_ai"):
#                 with st.spinner("AI Doctor is preparing your explanation…"):
#                     try:
#                         st.session_state.ai_explanation = call_gemini_with_retry(ask_ai, disease)
#                         st.rerun()
#                     except Exception as e:
#                         st.error(f"AI error: {e}")
#             st.info("Click the button above to get a detailed AI-generated medical overview.")

#     # ── TAB 3: AI Chat ────────────────────────────────────────
#     with tab_chat:
#         st.markdown(f"**Chatting about:** `{disease}`")

#         for msg in st.session_state.chat_history:
#             if msg["role"] == "user":
#                 st.markdown(f'<div class="chat-user">You: {msg["text"]}</div>', unsafe_allow_html=True)
#             else:
#                 st.markdown(f'<div class="chat-ai">AI Doctor: {msg["text"]}</div>', unsafe_allow_html=True)

#         st.markdown("**Quick questions:**")
#         quick_qs = [
#             "Can I exercise with this?",
#             "Is this contagious?",
#             "How long does recovery take?",
#             "What tests should I get?",
#         ]
#         qcols = st.columns(len(quick_qs))
#         for i, q in enumerate(quick_qs):
#             if qcols[i].button(q, key=f"quick_{i}"):
#                 with st.spinner("AI Doctor is thinking…"):
#                     try:
#                         answer = call_gemini_with_retry(ask_followup, disease, q)
#                         st.session_state.chat_history.append({"role": "user", "text": q})
#                         st.session_state.chat_history.append({"role": "ai", "text": answer})
#                         st.rerun()
#                     except Exception as e:
#                         st.error(str(e))

#         user_q = st.text_input(
#             "Or ask your own question:",
#             placeholder="e.g. Can I travel by flight with this condition?",
#             key="chat_input",
#         )
#         send_col, clear_col = st.columns([3, 1])
#         with send_col:
#             if st.button("Send", key="chat_send"):
#                 if user_q.strip():
#                     with st.spinner("AI Doctor is thinking…"):
#                         try:
#                             answer = call_gemini_with_retry(ask_followup, disease, user_q)
#                             st.session_state.chat_history.append({"role": "user", "text": user_q})
#                             st.session_state.chat_history.append({"role": "ai", "text": answer})
#                             st.rerun()
#                         except Exception as e:
#                             st.error(str(e))
#                 else:
#                     st.warning("Please type a question first.")
#         with clear_col:
#             if st.button("Clear chat"):
#                 st.session_state.chat_history = []
#                 st.rerun()

#     # ── TAB 4: Export ─────────────────────────────────────────
#     with tab_export:
#         st.markdown("### Export Your Health Report")
#         st.markdown("Download a summary of this prediction session for your records or to share with a doctor.")

#         # JSON export
#         report_data = {
#             "generated_at": datetime.datetime.now().isoformat(),
#             "predicted_disease": disease,
#             "confidence_percent": round(confidence, 2) if confidence else None,
#             "risk_level": risk_level,
#             "symptoms_reported": st.session_state.selected_symptoms,
#             "disclaimer": "This report is generated by an ML model and is not a medical diagnosis.",
#         }
#         json_bytes = json.dumps(report_data, indent=2).encode("utf-8")
#         st.download_button(
#             label="Download JSON Report",
#             data=json_bytes,
#             file_name=f"MediAI_Report_{disease.replace(' ', '_')}_{datetime.date.today()}.json",
#             mime="application/json",
#         )

#         # PDF export
#         if PDF_AVAILABLE:
#             if st.button("Generate and Download PDF Report"):
#                 with st.spinner("Generating PDF…"):

#                     # Get AI summary with retry
#                     try:
#                         summary_text = call_gemini_with_retry(
#                             generate_health_report_summary,
#                             disease,
#                             st.session_state.selected_symptoms,
#                             confidence or 0,
#                         )
#                     except Exception:
#                         summary_text = (
#                             "AI summary could not be generated at this time. "
#                             "Please consult a healthcare professional for a proper diagnosis."
#                         )

#                     # ── Build PDF ──────────────────────────────────
#                     pdf = FPDF()
#                     pdf.add_page()

#                     # Title
#                     pdf.set_font("Helvetica", "B", 18)
#                     pdf.set_text_color(31, 138, 255)
#                     pdf.cell(0, 12, "MediAI Health Report", ln=True, align="C")

#                     # Subtitle
#                     pdf.set_font("Helvetica", "", 10)
#                     pdf.set_text_color(100, 100, 100)
#                     pdf.cell(0, 6,
#                         safe_latin1(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"),
#                         ln=True, align="C")
#                     pdf.ln(8)

#                     # Prediction summary
#                     pdf.set_font("Helvetica", "B", 13)
#                     pdf.set_text_color(30, 30, 30)
#                     pdf.cell(0, 8, "Prediction Summary", ln=True)
#                     pdf.set_font("Helvetica", "", 11)
#                     pdf.cell(0, 7, safe_latin1(f"Predicted Disease: {disease}"), ln=True)
#                     pdf.cell(0, 7,
#                         safe_latin1(f"Confidence: {confidence:.1f}%" if confidence else "Confidence: N/A"),
#                         ln=True)
#                     pdf.cell(0, 7, safe_latin1(f"Risk Level: {risk_level}"), ln=True)
#                     pdf.ln(4)

#                     # Symptoms
#                     pdf.set_font("Helvetica", "B", 13)
#                     pdf.cell(0, 8, "Reported Symptoms", ln=True)
#                     pdf.set_font("Helvetica", "", 11)
#                     for s in st.session_state.selected_symptoms:
#                         pdf.cell(0, 6, safe_latin1(f"  - {s}"), ln=True)   # ← dash, not bullet
#                     pdf.ln(4)

#                     # AI Summary
#                     pdf.set_font("Helvetica", "B", 13)
#                     pdf.set_text_color(30, 30, 30)
#                     pdf.cell(0, 8, "AI Summary", ln=True)
#                     pdf.set_font("Helvetica", "", 10)
#                     pdf.multi_cell(0, 5.5, safe_latin1(summary_text))   # ← safe_latin1 strips unicode
#                     pdf.ln(4)

#                     # Disclaimer
#                     pdf.set_font("Helvetica", "I", 8)
#                     pdf.set_text_color(150, 150, 150)
#                     pdf.multi_cell(0, 5,
#                         "DISCLAIMER: This report is generated by a Machine Learning model "
#                         "and should not be considered a medical diagnosis. "
#                         "Please consult a qualified healthcare professional."
#                     )

#                     # Output
#                     buf = io.BytesIO()
#                     pdf.output(buf)
#                     buf.seek(0)
#                     st.download_button(
#                         label="Download PDF",
#                         data=buf,
#                         file_name=safe_latin1(
#                             f"MediAI_{disease.replace(' ', '_')}_{datetime.date.today()}.pdf"
#                         ),
#                         mime="application/pdf",
#                     )
#         else:
#             st.info("PDF export requires fpdf2. Run: python -m pip install fpdf2")


# # ════════════════════════════════════════════════════════════════
# # FOOTER
# # ════════════════════════════════════════════════════════════════

# st.markdown("""
# <div class="medi-footer">
#   MediAI &nbsp;·&nbsp; Built with Streamlit, Scikit-Learn and Gemini AI
#   &nbsp;·&nbsp; Developer: <strong>Krishna Yadav</strong><br>
#   This tool is for educational purposes only and does not constitute medical advice.
# </div>
# """, unsafe_allow_html=True)


import streamlit as st
import pickle
import pandas as pd
import numpy as np
import datetime
import json
import io
import time

# ════════════════════════════════════════════════════════════════
# PAGE CONFIG  (only once — at the very top)
# ════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="MediAI — Disease Prediction",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── PDF generation
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from gemini_helper import (
    ask_ai,
    ask_followup,
    get_disease_risk_level,
    generate_health_report_summary,
)

# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def safe_latin1(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


def call_gemini_with_retry(fn, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ["503", "overload", "resource_exhausted",
                                       "quota", "rate", "unavailable", "high demand"]):
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    st.toast(f"AI busy – retrying in {wait}s… ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                else:
                    raise RuntimeError(
                        "Gemini AI is currently overloaded. Please wait a moment and try again."
                    )
            else:
                raise


# ════════════════════════════════════════════════════════════════
# SESSION STATE DEFAULTS
# ════════════════════════════════════════════════════════════════

for key, default in {
    "disease": None,
    "selected_symptoms": [],
    "confidence": None,
    "probabilities": None,
    "chat_history": [],
    "prediction_time": None,
    "risk_level": None,
    "ai_explanation": None,
    "history_log": [],
    "theme": "🌙 Dark Mode",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🩺 MediAI")
    st.caption("AI-Powered Disease Prediction")
    st.divider()

    # ── THEME TOGGLE ──────────────────────────────────────────
    st.markdown("### 🎨 Theme")
    theme = st.radio(
        "Select theme",
        ["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state.theme == "🌙 Dark Mode" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.theme = theme
    st.divider()

    st.markdown("### 📋 Session Summary")
    if st.session_state.disease:
        st.markdown(f"**Last Prediction:** {st.session_state.disease}")
        if st.session_state.confidence:
            st.markdown(f"**Confidence:** {st.session_state.confidence:.1f}%")
        if st.session_state.prediction_time:
            st.markdown(f"**Time:** {st.session_state.prediction_time}")
        if st.session_state.risk_level:
            lvl = st.session_state.risk_level
            color = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}.get(lvl, "gray")
            st.markdown(f"**Risk:** :{color}[{lvl}]")
    else:
        st.caption("No prediction yet.")

    st.divider()

    st.markdown("### ⚖️ BMI Calculator")
    bmi_weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.5)
    bmi_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)
    if st.button("Calculate BMI", key="bmi_btn"):
        h_m = bmi_height / 100
        bmi = bmi_weight / (h_m ** 2)
        if bmi < 18.5:
            cat, col = "Underweight", "🔵"
        elif bmi < 25:
            cat, col = "Normal", "🟢"
        elif bmi < 30:
            cat, col = "Overweight", "🟡"
        else:
            cat, col = "Obese", "🔴"
        st.markdown(f"**BMI: {bmi:.1f}** {col} {cat}")

    st.divider()

    st.markdown("### 🕘 Prediction History")
    if st.session_state.history_log:
        for entry in reversed(st.session_state.history_log[-5:]):
            st.caption(f"- {entry['disease']} ({entry['conf']:.0f}%) — {entry['time']}")
        if st.button("Clear History"):
            st.session_state.history_log = []
            st.rerun()
    else:
        st.caption("No history yet.")

    st.divider()
    st.caption("For educational use only. Not a substitute for medical advice.")
    st.caption("Built by **Krishna Yadav**")


# ════════════════════════════════════════════════════════════════
# DYNAMIC CSS  (switches based on theme)
# ════════════════════════════════════════════════════════════════

is_dark = st.session_state.theme == "🌙 Dark Mode"

if is_dark:
    bg        = "#0d1117"
    surface   = "#161b22"
    card      = "#1c2333"
    border    = "#30363d"
    text      = "#e6edf3"
    muted     = "#8b949e"
    hero_grad = "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #1a2a3a 100%)"
    chat_user_bg     = "#1a2744"
    chat_user_border = "#1f3a6e"
    tag_bg           = "#1a2744"
    tag_border       = "#1f3a6e"
    input_bg         = "#161b22"
else:
    bg        = "#f0f4f8"
    surface   = "#ffffff"
    card      = "#ffffff"
    border    = "#d1d9e0"
    text      = "#1c2333"
    muted     = "#57606a"
    hero_grad = "linear-gradient(135deg, #dbeafe 0%, #ede9fe 50%, #d1fae5 100%)"
    chat_user_bg     = "#dbeafe"
    chat_user_border = "#93c5fd"
    tag_bg           = "#ede9fe"
    tag_border       = "#a78bfa"
    input_bg         = "#ffffff"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

:root {{
    --bg:        {bg};
    --surface:   {surface};
    --card:      {card};
    --border:    {border};
    --accent:    #1f8aff;
    --accent2:   #0acf97;
    --warn:      #f59e0b;
    --danger:    #ef4444;
    --text:      {text};
    --muted:     {muted};
    --radius:    12px;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}}

#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 2rem 2rem 4rem; max-width: 1100px; }}

[data-testid="stSidebar"] {{
    background: {surface} !important;
    border-right: 1px solid {border};
}}
[data-testid="stSidebar"] * {{ color: {text} !important; }}

.medi-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: box-shadow .2s;
}}
.medi-card:hover {{ box-shadow: 0 0 0 1px var(--accent); }}

.hero {{
    background: {hero_grad};
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
}}
.hero h1 {{
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #1f8aff, #0acf97);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 .5rem;
}}
.hero p {{ color: var(--muted); font-size: 1.05rem; margin: 0; }}

.badge {{
    display: inline-block;
    padding: .3rem .9rem;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 600;
    letter-spacing: .04em;
    text-transform: uppercase;
}}
.badge-low    {{ background: #0d3321; color: #0acf97; border: 1px solid #0acf9740; }}
.badge-medium {{ background: #2d2006; color: #f59e0b; border: 1px solid #f59e0b40; }}
.badge-high   {{ background: #2d0a0a; color: #ef4444; border: 1px solid #ef444440; }}

.conf-ring {{ text-align: center; padding: .5rem; }}
.conf-ring .number {{
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #0acf97;
    line-height: 1;
}}
.conf-ring .label {{
    font-size: .75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .1em;
}}

.disease-name {{
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--text);
    margin: .4rem 0;
}}

.prob-bar-wrap {{ margin: .5rem 0; }}
.prob-bar-label {{ font-size: .85rem; color: var(--muted); margin-bottom: .2rem; }}
.prob-bar-track {{ height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }}
.prob-bar-fill {{
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #1f8aff, #0acf97);
    transition: width .8s cubic-bezier(.4,0,.2,1);
}}

.chat-user {{
    background: {chat_user_bg};
    border: 1px solid {chat_user_border};
    border-radius: var(--radius) var(--radius) 4px var(--radius);
    padding: .8rem 1.1rem;
    margin: .5rem 0 .5rem 3rem;
    font-size: .9rem;
    color: var(--text);
}}
.chat-ai {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius) var(--radius) var(--radius) 4px;
    padding: .8rem 1.1rem;
    margin: .5rem 3rem .5rem 0;
    font-size: .9rem;
    line-height: 1.6;
    color: var(--text);
}}

.stButton > button {{
    background: linear-gradient(135deg, #1f8aff, #0d6bcc) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: .55rem 1.4rem !important;
    transition: opacity .2s !important;
}}
.stButton > button:hover {{ opacity: .85 !important; }}

[data-baseweb="tag"] {{
    background: {tag_bg} !important;
    border: 1px solid {tag_border} !important;
    color: var(--text) !important;
}}

input, textarea, [data-baseweb="input"] {{
    background: {input_bg} !important;
    border-color: {border} !important;
    color: {text} !important;
    border-radius: 8px !important;
}}

.section-title {{
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .12em;
    border-bottom: 1px solid var(--border);
    padding-bottom: .5rem;
    margin: 1.5rem 0 1rem;
}}

.medi-footer {{
    text-align: center;
    color: var(--muted);
    font-size: .78rem;
    padding: 2rem 0 .5rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# LOAD ARTIFACTS
# ════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_artifacts():
    errors = []
    try:
        model = pickle.load(open("model.pkl", "rb"))
    except FileNotFoundError:
        model = None
        errors.append("model.pkl not found.")
    try:
        symptom_index = pickle.load(open("symptom_index.pkl", "rb"))
    except FileNotFoundError:
        symptom_index = {}
        errors.append("symptom_index.pkl not found.")
    try:
        desc_df = pd.read_csv("symptom_Description.csv")
    except FileNotFoundError:
        desc_df = pd.DataFrame()
        errors.append("symptom_Description.csv not found.")
    try:
        prec_df = pd.read_csv("symptom_precaution.csv")
    except FileNotFoundError:
        prec_df = pd.DataFrame()
        errors.append("symptom_precaution.csv not found.")
    return model, symptom_index, desc_df, prec_df, errors

model, symptom_index, description_df, precaution_df, load_errors = load_artifacts()

if load_errors:
    with st.sidebar:
        st.divider()
        st.markdown("### Missing Files")
        for e in load_errors:
            st.error(e)


# ════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero">
  <h1>MediAI Disease Prediction</h1>
  <p>Select your symptoms · Get an instant ML-powered prediction · Ask your AI doctor</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# SYMPTOM SELECTION + PREDICT
# ════════════════════════════════════════════════════════════════

if not symptom_index:
    st.error("Cannot load symptom data. Please check that symptom_index.pkl exists.")
    st.stop()

all_symptoms = sorted(symptom_index.keys())

col_sel, col_btn = st.columns([4, 1], vertical_alignment="bottom")
with col_sel:
    selected_symptoms = st.multiselect(
        "🔎 Select Symptoms",
        all_symptoms,
        placeholder="Type to search symptoms…",
    )
with col_btn:
    predict_clicked = st.button("Predict", use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PREDICTION LOGIC
# ════════════════════════════════════════════════════════════════

if predict_clicked:
    if not selected_symptoms:
        st.warning("Please select at least one symptom before predicting.")
    elif model is None:
        st.error("Model not loaded. Cannot make predictions.")
    else:
        with st.spinner("Analysing symptoms…"):
            input_vector = [0] * len(symptom_index)
            for s in selected_symptoms:
                if s in symptom_index:
                    input_vector[symptom_index[s]] = 1

            prediction = model.predict([input_vector])
            disease = prediction[0]

            confidence = None
            probabilities = None
            try:
                probabilities = model.predict_proba([input_vector])
                confidence = float(np.max(probabilities[0]) * 100)
            except Exception:
                pass

            st.session_state.disease = disease
            st.session_state.selected_symptoms = selected_symptoms
            st.session_state.confidence = confidence
            st.session_state.probabilities = probabilities
            st.session_state.chat_history = []
            st.session_state.prediction_time = datetime.datetime.now().strftime("%H:%M, %b %d")
            st.session_state.ai_explanation = None

            st.session_state.history_log.append({
                "disease": disease,
                "conf": confidence or 0,
                "time": st.session_state.prediction_time,
            })

            try:
                st.session_state.risk_level = call_gemini_with_retry(get_disease_risk_level, disease)
            except Exception:
                st.session_state.risk_level = "MEDIUM"


# ════════════════════════════════════════════════════════════════
# RESULTS
# ════════════════════════════════════════════════════════════════

if st.session_state.disease:
    disease       = st.session_state.disease
    confidence    = st.session_state.confidence
    probabilities = st.session_state.probabilities
    risk_level    = st.session_state.risk_level or "MEDIUM"

    r1, r2, r3 = st.columns([3, 1.2, 1.2])

    with r1:
        badge_class = f"badge-{risk_level.lower()}"
        st.markdown(f"""
        <div class="medi-card">
          <div style="font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;">Predicted Disease</div>
          <div class="disease-name">{disease}</div>
          <span class="badge {badge_class}">Risk: {risk_level}</span>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        if confidence is not None:
            st.markdown(f"""
            <div class="medi-card conf-ring">
              <div class="number">{confidence:.0f}%</div>
              <div class="label">Confidence</div>
            </div>
            """, unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
        <div class="medi-card conf-ring">
          <div class="number">{len(st.session_state.selected_symptoms)}</div>
          <div class="label">Symptoms</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Top-3
    if probabilities is not None:
        st.markdown('<div class="section-title">Top 3 Possible Diagnoses</div>', unsafe_allow_html=True)
        top3_idx = np.argsort(probabilities[0])[-3:][::-1]
        for rank, idx in enumerate(top3_idx):
            name   = model.classes_[idx]
            pct    = probabilities[0][idx] * 100
            marker = "1st" if rank == 0 else ("2nd" if rank == 1 else "3rd")
            st.markdown(f"""
            <div class="prob-bar-wrap">
              <div class="prob-bar-label">{marker} &nbsp; {name} &nbsp; <strong>{pct:.1f}%</strong></div>
              <div class="prob-bar-track"><div class="prob-bar-fill" style="width:{pct:.1f}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tabs
    tab_info, tab_ai, tab_chat, tab_export = st.tabs([
        "📋 Disease Info",
        "🤖 AI Explanation",
        "💬 Ask AI Doctor",
        "📥 Export Report",
    ])

    # TAB 1: Info
    with tab_info:
        col_desc, col_prec = st.columns(2)

        with col_desc:
            st.markdown('<div class="section-title">Description</div>', unsafe_allow_html=True)
            if not description_df.empty:
                row = description_df[description_df["Disease"] == disease]
                if not row.empty:
                    st.markdown(f'<div class="medi-card">{row.iloc[0][row.columns[1]]}</div>',
                                unsafe_allow_html=True)
                else:
                    st.info("No description available.")
            else:
                st.info("Description data not loaded.")

        with col_prec:
            st.markdown('<div class="section-title">Recommended Precautions</div>', unsafe_allow_html=True)
            if not precaution_df.empty:
                row = precaution_df[precaution_df["Disease"] == disease]
                if not row.empty:
                    prec_items = [row.iloc[0][c] for c in row.columns[1:] if pd.notna(row.iloc[0][c])]
                    if prec_items:
                        items_html = "".join(f"<li>✅ {p}</li>" for p in prec_items)
                        st.markdown(
                            f'<div class="medi-card"><ul style="margin:0;padding-left:1.2rem;">{items_html}</ul></div>',
                            unsafe_allow_html=True)
                    else:
                        st.info("No precautions listed.")
                else:
                    st.info("No precautions available.")
            else:
                st.info("Precaution data not loaded.")

        st.markdown('<div class="section-title">Symptoms You Reported</div>', unsafe_allow_html=True)
        tags_html = " ".join(
            f'<span style="background:{tag_bg};border:1px solid {tag_border};border-radius:999px;'
            f'padding:.2rem .7rem;font-size:.82rem;margin:.2rem;display:inline-block;color:{text};">{s}</span>'
            for s in st.session_state.selected_symptoms
        )
        st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)

    # TAB 2: AI Explanation
    with tab_ai:
        if st.session_state.ai_explanation:
            st.markdown(st.session_state.ai_explanation)
        else:
            if st.button("Generate AI Medical Explanation", key="gen_ai"):
                with st.spinner("AI Doctor is preparing your explanation…"):
                    try:
                        st.session_state.ai_explanation = call_gemini_with_retry(ask_ai, disease)
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI error: {e}")
            st.info("Click the button above to get a detailed AI-generated medical overview.")

    # TAB 3: AI Chat
    with tab_chat:
        st.markdown(f"**Chatting about:** `{disease}`")

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">You: {msg["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">AI Doctor: {msg["text"]}</div>', unsafe_allow_html=True)

        st.markdown("**Quick questions:**")
        quick_qs = [
            "Can I exercise with this?",
            "Is this contagious?",
            "How long does recovery take?",
            "What tests should I get?",
        ]
        qcols = st.columns(len(quick_qs))
        for i, q in enumerate(quick_qs):
            if qcols[i].button(q, key=f"quick_{i}"):
                with st.spinner("AI Doctor is thinking…"):
                    try:
                        answer = call_gemini_with_retry(ask_followup, disease, q)
                        st.session_state.chat_history.append({"role": "user", "text": q})
                        st.session_state.chat_history.append({"role": "ai", "text": answer})
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        user_q = st.text_input(
            "Or ask your own question:",
            placeholder="e.g. Can I travel by flight with this condition?",
            key="chat_input",
        )
        send_col, clear_col = st.columns([3, 1])
        with send_col:
            if st.button("Send", key="chat_send"):
                if user_q.strip():
                    with st.spinner("AI Doctor is thinking…"):
                        try:
                            answer = call_gemini_with_retry(ask_followup, disease, user_q)
                            st.session_state.chat_history.append({"role": "user", "text": user_q})
                            st.session_state.chat_history.append({"role": "ai", "text": answer})
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("Please type a question first.")
        with clear_col:
            if st.button("Clear chat"):
                st.session_state.chat_history = []
                st.rerun()

    # TAB 4: Export
    with tab_export:
        st.markdown("### Export Your Health Report")
        st.markdown("Download a summary of this prediction session for your records or to share with a doctor.")

        report_data = {
            "generated_at": datetime.datetime.now().isoformat(),
            "predicted_disease": disease,
            "confidence_percent": round(confidence, 2) if confidence else None,
            "risk_level": risk_level,
            "symptoms_reported": st.session_state.selected_symptoms,
            "disclaimer": "This report is generated by an ML model and is not a medical diagnosis.",
        }
        json_bytes = json.dumps(report_data, indent=2).encode("utf-8")
        st.download_button(
            label="Download JSON Report",
            data=json_bytes,
            file_name=f"MediAI_Report_{disease.replace(' ', '_')}_{datetime.date.today()}.json",
            mime="application/json",
        )

        if PDF_AVAILABLE:
            if st.button("Generate and Download PDF Report"):
                with st.spinner("Generating PDF…"):
                    try:
                        summary_text = call_gemini_with_retry(
                            generate_health_report_summary,
                            disease,
                            st.session_state.selected_symptoms,
                            confidence or 0,
                        )
                    except Exception:
                        summary_text = (
                            "AI summary could not be generated at this time. "
                            "Please consult a healthcare professional for a proper diagnosis."
                        )

                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", "B", 18)
                    pdf.set_text_color(31, 138, 255)
                    pdf.cell(0, 12, "MediAI Health Report", ln=True, align="C")
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(100, 100, 100)
                    pdf.cell(0, 6,
                        safe_latin1(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"),
                        ln=True, align="C")
                    pdf.ln(8)
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(30, 30, 30)
                    pdf.cell(0, 8, "Prediction Summary", ln=True)
                    pdf.set_font("Helvetica", "", 11)
                    pdf.cell(0, 7, safe_latin1(f"Predicted Disease: {disease}"), ln=True)
                    pdf.cell(0, 7,
                        safe_latin1(f"Confidence: {confidence:.1f}%" if confidence else "Confidence: N/A"),
                        ln=True)
                    pdf.cell(0, 7, safe_latin1(f"Risk Level: {risk_level}"), ln=True)
                    pdf.ln(4)
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.cell(0, 8, "Reported Symptoms", ln=True)
                    pdf.set_font("Helvetica", "", 11)
                    for s in st.session_state.selected_symptoms:
                        pdf.cell(0, 6, safe_latin1(f"  - {s}"), ln=True)
                    pdf.ln(4)
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(30, 30, 30)
                    pdf.cell(0, 8, "AI Summary", ln=True)
                    pdf.set_font("Helvetica", "", 10)
                    pdf.multi_cell(0, 5.5, safe_latin1(summary_text))
                    pdf.ln(4)
                    pdf.set_font("Helvetica", "I", 8)
                    pdf.set_text_color(150, 150, 150)
                    pdf.multi_cell(0, 5,
                        "DISCLAIMER: This report is generated by a Machine Learning model "
                        "and should not be considered a medical diagnosis. "
                        "Please consult a qualified healthcare professional."
                    )
                    buf = io.BytesIO()
                    pdf.output(buf)
                    buf.seek(0)
                    st.download_button(
                        label="Download PDF",
                        data=buf,
                        file_name=safe_latin1(
                            f"MediAI_{disease.replace(' ', '_')}_{datetime.date.today()}.pdf"
                        ),
                        mime="application/pdf",
                    )
        else:
            st.info("PDF export requires fpdf2. Run: python -m pip install fpdf2")


# ════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════

st.markdown("""
<div class="medi-footer">
  MediAI &nbsp;·&nbsp; Built with Streamlit, Scikit-Learn and Gemini AI
  &nbsp;·&nbsp; Developer: <strong>Krishna Yadav</strong><br>
  This tool is for educational purposes only and does not constitute medical advice.
</div>
""", unsafe_allow_html=True)
