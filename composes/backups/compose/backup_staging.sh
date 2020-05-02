#!/bin/sh
set -e

PGPASSWORD=vteme pg_dump --host postgres --dbname vteme_staging_db --username vteme > tmp.sql
zip vteme_staging_db_$(date +"%m_%d_%Y:%T").sql.zip tmp.sql
rm tmp.sql
zip -r staging_media_data_$(date +"%m_%d_%Y:%T").zip /app/server_media
sync
