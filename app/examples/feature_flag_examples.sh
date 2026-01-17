#!/bin/bash

# Const

BASE_URL="http://localhost:8000"

echo "1. Create a feature flag with 25% rollout"
curl -X POST "$BASE_URL/api/v1/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "new_dashboard",
    "enabled": true,
    "description": "New dashboard design",
    "rules": {
      "strategy": "percentage",
      "percentage": 25
    },
    "metadata": {
      "team": "frontend",
      "jira": "DASH-456"
    }
  }'
echo -e "\n"

echo "2. List all flags"
curl "$BASE_URL/api/v1/flags"
echo -e "\n"

echo "3. Get specific flag"
curl "$BASE_URL/api/v1/flags/new_dashboard"
echo -e "\n"

echo "4. Evaluate flag for user1"
curl "$BASE_URL/api/v1/flags/new_dashboard/evaluate?user_id=user1"
echo -e "\n"

echo "5. Evaluate flag for user2"
curl "$BASE_URL/api/v1/flags/new_dashboard/evaluate?user_id=user2"
echo -e "\n"

echo "6. Update flag to 50% rollout"
curl -X PUT "$BASE_URL/api/v1/flags/new_dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": {
      "strategy": "percentage",
      "percentage": 50
    }
  }'
echo -e "\n"

echo "7. Create beta flag with user list"
curl -X POST "$BASE_URL/api/v1/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "beta_feature",
    "enabled": true,
    "description": "Beta feature",
    "rules": {
      "strategy": "user_list",
      "user_ids": ["beta1", "beta2", "beta3"]
    }
  }'
echo -e "\n"

echo "8. Evaluate beta flag for beta user"
curl "$BASE_URL/api/v1/flags/beta_feature/evaluate?user_id=beta1"
echo -e "\n"

echo "9. Evaluate beta flag for regular user"
curl "$BASE_URL/api/v1/flags/beta_feature/evaluate?user_id=regular_user"
echo -e "\n"

echo "10. Disable flag (kill switch)"
curl -X PUT "$BASE_URL/api/v1/flags/new_dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
echo -e "\n"

echo "11. Delete flag"
curl -X DELETE "$BASE_URL/api/v1/flags/beta_feature"
echo -e "\n"