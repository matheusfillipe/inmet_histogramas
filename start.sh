#!/bin/bash
export STREAMLIT_SERVER_PORT=8123
chmod 777 update.pl
chmod 777 download.pl
streamlit run app.py --server.port $STREAMLIT_SERVER_PORT
