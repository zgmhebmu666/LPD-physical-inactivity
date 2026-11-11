# LPD Postoperative Physical Inactivity Calculator

This folder contains a deployable Streamlit web calculator for the final calibrated model.

## Local test

```bash
cd web_calculator
pip install -r requirements.txt
streamlit run app.py
```

## Public deployment

1. Create a GitHub repository.
2. Upload all files in this `web_calculator` folder, including `app.py`, `requirements.txt`, and `app_assets/`.
3. Go to Streamlit Community Cloud.
4. Choose the repository and set the main file path to `app.py`.
5. Deploy the app and copy the public URL.

Suggested manuscript wording after deployment:

> We developed a publicly accessible web-based calculator based on the optimal calibrated prediction model to facilitate individualized prediction of postoperative physical inactivity after laparoscopic pancreaticoduodenectomy.
