#!/bin/sh
set -e

PGPASSWORD=vteme pg_dump --host postgres --dbname vteme_production_db --username vteme > tmp.sql
zip vteme_production_db_$(date +"%m_%d_%Y:%T").sql.zip tmp.sql
rm tmp.sql
zip -r production_media_data_$(date +"%m_%d_%Y:%T").zip /app/server_media
sync
