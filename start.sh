#!/bin/bash
export STREAMLIT_SERVER_PORT=81238
chmod 777 update.pl
chmod 777 download.pl
streamlit run app.py
