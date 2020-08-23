#!/bin/bash

SPACY_REQ_STRING=${SPACY_REQ_STRING:-spacy==2.3.2}
export ONTONOTES_PERCENT=${ONTONOTES_PERCENT:-0.1}

pip install "${SPACY_REQ_STRING}"
pip install spacy-lookups-data
python -m spacy download en_core_web_md

export ONTONOTES_PATH=/ontonotes

echo y | bash scripts/pipeline.sh medium

mv build /output
mv dist /output
