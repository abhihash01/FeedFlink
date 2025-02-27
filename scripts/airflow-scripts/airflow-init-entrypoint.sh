#!/bin/bash


USER=$(cat /run/secrets/airflow_user)
EMAIL=$(cat /run/secrets/airflow_email)
FIRSTNAME=$(cat /run/secrets/airflow_firstname)
LASTNAME=$(cat /run/secrets/airflow_lastname)
PASSWORD=$(cat /run/secrets/airflow_password)

airflow db migrate

airflow users create \
    --username "$USER" \
    --firstname "$FIRSTNAME" \
    --lastname "$LASTNAME" \
    --role "Admin" \
    --email "$EMAIL" \
    --password "$PASSWORD"


