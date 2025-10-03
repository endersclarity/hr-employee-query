#!/bin/bash

# Environment Variable Validation Script
# Validates that all required environment variables are set

# Load .env file if it exists (safe parsing to prevent command injection)
if [ -f .env ]; then
    set -a
    source <(grep -v '^#' .env | sed 's/\r$//')
    set +a
fi

echo "Validating environment variables..."

# Required variables
required_vars=("OPENAI_API_KEY" "DATABASE_URL")

# Track validation status
all_valid=true

# Check each required variable
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ ERROR: $var is not set"
        all_valid=false
    else
        # Additional validation for OPENAI_API_KEY format
        if [ "$var" = "OPENAI_API_KEY" ]; then
            if [[ ! "${!var}" =~ ^sk- ]]; then
                echo "⚠️  WARNING: $var should start with 'sk-' (current value may be invalid)"
            else
                echo "✅ $var is set"
            fi
        else
            echo "✅ $var is set"
        fi
    fi
done

# Exit with appropriate status
if [ "$all_valid" = true ]; then
    echo ""
    echo "✅ All required environment variables are set!"
    exit 0
else
    echo ""
    echo "❌ Some required environment variables are missing."
    echo "Please copy .env.example to .env and fill in the required values:"
    echo "  cp .env.example .env"
    exit 1
fi
