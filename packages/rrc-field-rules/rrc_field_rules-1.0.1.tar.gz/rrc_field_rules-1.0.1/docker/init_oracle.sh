#!/bin/bash
set -e

echo "STARTING AUTOMATED SETUP: Creating User and Importing Legacy Data..."

# 1. Create the User
sqlplus system/$ORACLE_PASSWORD@//localhost:1521/FREEPDB1 <<EOF
CREATE USER PROD_OG_OWNR IDENTIFIED BY ParserPassword123 QUOTA UNLIMITED ON USERS;
GRANT CONNECT, RESOURCE, CREATE VIEW TO PROD_OG_OWNR;
EXIT;
EOF

# 2. Find the dump file (Handles root or GUID subfolder automatically)
DUMP_FILE=$(find /opt/oracle/admin/FREE/dpdump -name "orr_og_field_001_prod.dmp" -print -quit)

if [ -z "$DUMP_FILE" ]; then
  echo "ERROR: Could not find orr_og_field_001_prod.dmp in /opt/oracle/admin/FREE/dpdump or its subfolders."
  exit 1
fi

echo "Found dump file at: $DUMP_FILE"

# 3. Run Legacy Import
imp system/$ORACLE_PASSWORD@//localhost:1521/FREEPDB1 \
  FILE="$DUMP_FILE" \
  FROMUSER=PROD_OG_OWNR \
  TOUSER=PROD_OG_OWNR \
  IGNORE=Y

echo "AUTOMATED SETUP COMPLETE."