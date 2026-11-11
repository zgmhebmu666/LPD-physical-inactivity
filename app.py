# -*- coding: utf-8 -*-
"""
LPD postoperative physical inactivity prediction calculator.

Run locally:
    streamlit run app.py
"""

from pathlib import Path
import json

import joblib
import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "app_assets"


@st.cache_resource
def load_model():
    return joblib.load(ASSET_DIR / "best_model_calibrated.joblib")


@st.cache_data
def load_metadata():
    with (ASSET_DIR / "calculator_metadata.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    st.set_page_config(
        page_title="LPD Postoperative Physical Inactivity Calculator",
        page_icon="🧮",
        layout="centered",
    )

    model = load_model()
    meta = load_metadata()

    st.title("LPD Postoperative Physical Inactivity Calculator")
    st.caption(
        "This calculator estimates the probability of postoperative physical inactivity "
        "after laparoscopic pancreaticoduodenectomy (LPD) using a calibrated prediction model."
    )

    with st.expander("Model information", expanded=False):
        st.write(f"Best model: **{meta.get('best_model_display', meta.get('best_model', 'Model'))}**")
        if meta.get("validation_auc") is not None:
            st.write(f"Validation AUC: **{meta['validation_auc']:.3f}**")
        st.write(f"Decision threshold: **{meta.get('threshold', 0.5):.3f}**")
        st.write("Model outcome: postoperative physical inactivity = 1; active = 0.")

    fields = meta["fields"]
    values = {}

    with st.form("calculator_form"):
        st.subheader("Patient, perioperative, and postoperative variables")

        for field in fields:
            name = field["name"]
            label = field["label"]
            ftype = field["type"]
            default = field.get("default")

            if ftype == "numeric":
                min_value = field.get("min")
                max_value = field.get("max")
                q1 = field.get("q1")
                q3 = field.get("q3")
                help_text = None
                if q1 is not None and q3 is not None:
                    help_text = f"Typical interquartile range in the training cohort: {q1:.3g}–{q3:.3g}"

                values[name] = st.number_input(
                    label,
                    value=float(default) if default is not None else 0.0,
                    min_value=float(min_value) if min_value is not None else None,
                    max_value=float(max_value) if max_value is not None else None,
                    step=0.1,
                    help=help_text,
                )
            else:
                options = field["options"]
                option_labels = [x["label"] for x in options]
                option_values = [x["value"] for x in options]
                default_index = 0
                if default in option_values:
                    default_index = option_values.index(default)

                picked = st.selectbox(
                    label,
                    options=list(range(len(options))),
                    index=default_index,
                    format_func=lambda i, labels=option_labels: labels[i],
                )
                values[name] = option_values[picked]

        submitted = st.form_submit_button("Calculate risk")

    if submitted:
        row = pd.DataFrame([{name: values[name] for name in meta["selected_variables"]}])
        prob = float(model.predict_proba(row)[0, 1])
        threshold = float(meta.get("threshold", 0.5))
        risk_group = "High-risk" if prob >= threshold else "Low-risk"

        st.subheader("Prediction result")
        st.metric("Predicted probability of postoperative physical inactivity", f"{prob:.1%}")
        st.progress(min(max(prob, 0.0), 1.0))

        if prob >= threshold:
            st.error(f"{risk_group}: predicted probability is at or above the model threshold ({threshold:.1%}).")
        else:
            st.success(f"{risk_group}: predicted probability is below the model threshold ({threshold:.1%}).")

        st.caption(
            "This calculator is intended for research and auxiliary risk assessment only. "
            "It should not replace clinical judgment or multidisciplinary decision-making."
        )

        with st.expander("Input values used by the model"):
            display = {field["label"]: values[field["name"]] for field in fields}
            st.dataframe(pd.DataFrame([display]), use_container_width=True)


if __name__ == "__main__":
    main()
