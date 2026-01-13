#!/bin/bash
set -e
conda_env_path=$1

py_version=$(${conda_env_path}/bin/python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")

PIP_PRE=""
CORE_PKG="dataflow-core"
DBT_PKG="dataflow-dbt"
AIRFLOW_PKG="dataflow-airflow"

if [ -n "${DATAFLOW_CORE_VERSION}" ] \
   && [ -n "${DATAFLOW_DBT_VERSION}" ] \
   && [ -n "${DATAFLOW_AIRFLOW_VERSION}" ]; then
    CORE_PKG="dataflow-core==${DATAFLOW_CORE_VERSION}"
    DBT_PKG="dataflow-dbt==${DATAFLOW_DBT_VERSION}"
    AIRFLOW_PKG="dataflow-airflow==${DATAFLOW_AIRFLOW_VERSION}"
else
    PIP_PRE="--pre"
fi

# make sure to install dataflow deps from pypi only
${conda_env_path}/bin/pip install ${PIP_PRE} --index-url https://pypi.org/simple/ dash==3.0.3 dash-renderer==1.9.1 plotly==6.0.1 typing==3.7.4.3 streamlit==1.45.1 ipython==8.37.0 ipykernel==6.29.5 ipython-sql==0.4.1 jupysql==0.10.14 psycopg2-binary==2.9.10 sqlalchemy==1.4.54 ${CORE_PKG} ${DBT_PKG}

# 3. Install Dataflow Airflow to a separate path in environment 
${conda_env_path}/bin/pip install ${PIP_PRE} \
    --force-reinstall --root-user-action ignore \
    --no-warn-conflicts ${AIRFLOW_PKG} \
    --constraint /dataflow/setup/pip_constraints/airflow_constraints${py_version}.txt \
    --target ${conda_env_path}/bin/airflow-libraries/

files=(
    ${conda_env_path}/lib/python${py_version}/site-packages/dbt/config/profile.py 
    ${conda_env_path}/lib/python${py_version}/site-packages/dbt/task/debug.py
)
for file in ${files[@]}
do      
    awk '{gsub("from dbt.clients.yaml_helper import load_yaml_text", "from dbt.dataflow_config.secrets_manager import load_yaml_text"); print}' $file > temp 
    mv temp $file
done

# Create pth file to include airflow-libraries in sys.path
site_packages_path="${conda_env_path}/lib/python${py_version}/site-packages"
mkdir -p "$site_packages_path"
echo "${conda_env_path}/bin/airflow-libraries" > "${site_packages_path}/airflow_custom.pth"

echo "Environment Creation Successful"
