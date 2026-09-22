#!/usr/bin/env bash
set -euo pipefail
# Run from a Neo4j installation/container with neo4j-admin available.
# Example for a local Neo4j installation:
# neo4j-admin database dump neo4j --to-path=./database_dump --overwrite-destination=true
mkdir -p database_dump
neo4j-admin database dump neo4j --to-path=./database_dump --overwrite-destination=true
echo "Database dump written under ./database_dump"
