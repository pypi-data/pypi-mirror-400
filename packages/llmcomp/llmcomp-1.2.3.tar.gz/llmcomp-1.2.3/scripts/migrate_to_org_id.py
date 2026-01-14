#!/usr/bin/env python3
"""Migrate finetuning data from project_id to organization_id.

This script updates jobs.jsonl and files.jsonl to use actual OpenAI
organization IDs instead of the old fake project_id (first 20 chars of API key).

Usage:
    python scripts/migrate_to_org_id.py <data_dir>
    python scripts/migrate_to_org_id.py llmcomp_models

The script will:
1. Find all unique project_id values in jobs.jsonl and files.jsonl
2. For each project_id, find the matching API key and fetch the real org_id
3. Replace project_id with organization_id in both files
4. Create backups of the original files (.bak)

Requires OPENAI_API_KEY or OPENAI_API_KEY_0..9 environment variables.
"""

import argparse
import json
import os
import shutil
import sys

import openai


def read_jsonl(fname: str) -> list[dict]:
    with open(fname, "r") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(fname: str, data: list[dict]) -> None:
    with open(fname, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


def get_api_keys() -> list[str]:
    """Get all available OpenAI API keys from environment (OPENAI_API_KEY and OPENAI_API_KEY_*)."""
    keys = []
    for env_var in os.environ:
        if env_var == "OPENAI_API_KEY" or env_var.startswith("OPENAI_API_KEY_"):
            key = os.environ.get(env_var)
            if key:
                keys.append(key)
    return keys


def get_organization_id(api_key: str) -> str:
    """Get the organization ID for an API key."""
    client = openai.OpenAI(api_key=api_key)
    
    # Try to list fine-tuning jobs to get org_id
    jobs = client.fine_tuning.jobs.list(limit=1)
    if jobs.data:
        return jobs.data[0].organization_id
    
    # No jobs, try /v1/organization endpoint
    import requests
    response = requests.get(
        "https://api.openai.com/v1/organization",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    if response.status_code == 200:
        return response.json().get("id")
    
    raise ValueError(f"Could not determine organization ID (status {response.status_code})")


def find_key_for_project_id(project_id: str, api_keys: list[str]) -> str | None:
    """Find an API key that matches the old project_id (first 20 chars)."""
    for key in api_keys:
        if key.startswith(project_id):
            return key
    return None


def migrate_file(fname: str, project_to_org: dict[str, str], dry_run: bool) -> int:
    """Migrate a single JSONL file. Returns number of records updated."""
    if not os.path.exists(fname):
        return 0
    
    records = read_jsonl(fname)
    updated = 0
    
    for record in records:
        if "project_id" in record and "organization_id" not in record:
            project_id = record["project_id"]
            if project_id in project_to_org:
                record["organization_id"] = project_to_org[project_id]
                del record["project_id"]
                updated += 1
            else:
                print(f"  Warning: No mapping for project_id {project_id}")
    
    if updated > 0 and not dry_run:
        # Create backup
        shutil.copy(fname, fname + ".bak")
        write_jsonl(fname, records)
    
    return updated


def main():
    parser = argparse.ArgumentParser(
        description="Migrate finetuning data from project_id to organization_id"
    )
    parser.add_argument("data_dir", help="Directory containing jobs.jsonl and files.jsonl")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()
    
    jobs_file = os.path.join(args.data_dir, "jobs.jsonl")
    files_file = os.path.join(args.data_dir, "files.jsonl")
    
    if not os.path.exists(jobs_file) and not os.path.exists(files_file):
        print(f"Error: No jobs.jsonl or files.jsonl found in {args.data_dir}")
        sys.exit(1)
    
    # Collect all unique project_ids
    project_ids = set()
    
    if os.path.exists(jobs_file):
        for record in read_jsonl(jobs_file):
            if "project_id" in record and "organization_id" not in record:
                project_ids.add(record["project_id"])
    
    if os.path.exists(files_file):
        for record in read_jsonl(files_file):
            if "project_id" in record and "organization_id" not in record:
                project_ids.add(record["project_id"])
    
    if not project_ids:
        print("No records with project_id found. Nothing to migrate.")
        return
    
    print(f"Found {len(project_ids)} unique project_id(s) to migrate:")
    for pid in project_ids:
        print(f"  - {pid}...")
    
    # Get API keys and build mapping
    api_keys = get_api_keys()
    if not api_keys:
        print("\nError: No OpenAI API keys found in environment.")
        print("Set OPENAI_API_KEY or OPENAI_API_KEY_*")
        sys.exit(1)
    
    print(f"\nFound {len(api_keys)} API key(s)")
    
    project_to_org: dict[str, str] = {}
    
    for project_id in project_ids:
        api_key = find_key_for_project_id(project_id, api_keys)
        if not api_key:
            print(f"\nError: No API key found matching project_id {project_id}...")
            print("Make sure the corresponding API key is in the environment.")
            sys.exit(1)
        
        print(f"\nFetching org_id for {project_id}...")
        try:
            org_id = get_organization_id(api_key)
            project_to_org[project_id] = org_id
            print(f"  → {org_id}")
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)
    
    # Migrate files
    print()
    if args.dry_run:
        print("DRY RUN - no changes will be made")
    
    jobs_updated = migrate_file(jobs_file, project_to_org, args.dry_run)
    files_updated = migrate_file(files_file, project_to_org, args.dry_run)
    
    print(f"\nMigration complete:")
    print(f"  jobs.jsonl:  {jobs_updated} record(s) updated")
    print(f"  files.jsonl: {files_updated} record(s) updated")
    
    if not args.dry_run and (jobs_updated > 0 or files_updated > 0):
        print("\nBackup files created with .bak extension")


if __name__ == "__main__":
    main()

