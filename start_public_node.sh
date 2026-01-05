#!/bin/bash
# 9S Public Node Service - Linux/Mac Start Script

echo "================================================"
echo "    9S PUBLIC NODE SERVICE - STARTING"
echo "================================================"
echo ""
echo "PUBLIC TIER LIMITS:"
echo "  400 MAX slots"
echo "  Controlled mirroring (max 3)"
echo "  LOGOS-9.5 only"
echo "  8192 context window"
echo ""
echo "Starting public node: PUBLIC-001"
echo "================================================"
echo ""

cd "$(dirname "$0")"
python3 9s_public_node.py PUBLIC-001