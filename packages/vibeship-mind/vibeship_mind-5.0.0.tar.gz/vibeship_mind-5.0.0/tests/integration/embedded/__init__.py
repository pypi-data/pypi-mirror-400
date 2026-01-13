"""Embedded PostgreSQL integration tests.

These tests use an embedded PostgreSQL instance for testing
without requiring Docker or a separate PostgreSQL server.

The embedded-postgres package downloads and runs a PostgreSQL
binary directly, making it ideal for:
- CI environments without Docker
- Local development without Docker
- Quick test iterations
"""
