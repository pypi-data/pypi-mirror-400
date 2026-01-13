# Changelog

All notable changes to the Tritonium Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-01-02

### Added

- `dashboards` module - Full CRUD operations for custom dashboards
  - `get_dashboards` - List all custom dashboards
  - `post_dashboard` - Create a new dashboard
  - `get_dashboard` - Get a specific dashboard
  - `put_dashboard` - Update a dashboard
  - `delete_dashboard` - Delete a dashboard
  - `post_duplicate_dashboard` - Duplicate a dashboard
  - `get_widget_types` - Get available widget types
- `review_tags` module - Full CRUD operations for review tags and auto-tagging rules
  - `get_review_tags` - List all review tags
  - `post_review_tag` - Create a new review tag
  - `get_review_tag` - Get a specific review tag
  - `put_review_tag` - Update a review tag
  - `delete_review_tag` - Delete a review tag
  - `get_review_tag_stats` - Get tag statistics
  - `get_auto_tag_rules` - List auto-tagging rules
  - `post_auto_tag_rule` - Create an auto-tagging rule
  - `get_auto_tag_rule` - Get a specific rule
  - `put_auto_tag_rule` - Update a rule
  - `delete_auto_tag_rule` - Delete a rule
- New billing endpoints in `billing` module:
  - `get_payment_methods` - List saved payment methods
  - `get_plans` - Get available subscription plans
  - `post_setup_intent` - Create Stripe setup intent
  - `post_calculate_price` - Calculate subscription price
  - `post_validate_promo` - Validate promo codes
  - `get_upcoming_invoice` - Preview upcoming invoice
  - `get_usage` - Get usage data
- New models: `Dashboard`, `Widget`, `WidgetType`, `ReviewTag`, `AutoTagRule`

## [2.0.1] - 2026-01-02

### Removed

- Removed deprecated magic link authentication endpoints (`post_magic_link_request`, `post_magic_link_verify`)
- Removed `MagicLinkRequest` model

## [2.0.0] - 2025-12-29

### Removed

- **BREAKING:** Removed `get_sentiment_trends` endpoint from predictions module. This endpoint was deprecated and removed from the backend API.

### Migration Guide

If you were using `get_sentiment_trends`, you can use the following alternatives:
- `get_rating_forecast` - For rating predictions
- `post_feature_impact_prediction` - For feature impact analysis

## [1.0.0] - 2025-12-01

### Added

- Initial release of the Tritonium Python SDK
- Full API coverage for all Tritonium endpoints
- Sync and async client support
- Webhook signature verification
- Type hints for all models and responses
