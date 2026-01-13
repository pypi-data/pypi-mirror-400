# Changelog

All notable changes to Coolhand Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-04

### Added

- **FeedbackService**: New service for collecting user feedback on LLM responses
  - `FeedbackService` class for submitting thumbs up/down ratings
  - `create_feedback()` method on `Coolhand` class for convenient access
  - Module-level `create_feedback()` function for standalone usage
  - `get_feedback_service()` function for accessing/creating service instances

- **Feedback Matching Options**: Multiple ways to link feedback to LLM requests
  - `llm_request_log_id`: Exact match via Coolhand log ID
  - `llm_provider_unique_id`: Exact match via provider's x-request-id header
  - `original_output`: Fuzzy match via the original LLM response text
  - `client_unique_id`: Match via your internal identifier

- **Feedback Data Fields**:
  - `like` (required): Boolean thumbs up/down
  - `explanation`: Why the response was good/bad
  - `revised_output`: User's corrected version of the response
  - `creator_unique_id`: ID of the user providing feedback

- **Type Definitions**: New TypedDict definitions in `types.py`
  - `FeedbackData`: Input type for feedback submissions
  - `FeedbackResponse`: Response type from feedback API

- **Comprehensive Test Suite**: Full test coverage for FeedbackService
  - Initialization tests (config, kwargs, env vars)
  - Feedback creation tests (success, fuzzy match, provider ID)
  - Error handling tests (missing fields, HTTP errors, URL errors)
  - Module-level function tests
  - Coolhand integration tests

### Changed

- Updated README with comprehensive FeedbackService documentation
- Added FeedbackService exports to `__init__.py`

## [0.1.0] - Initial Release

### Added

- Automatic LLM API monitoring via httpx patching
- Support for OpenAI and Anthropic APIs
- Streaming response capture
- Automatic credential sanitization
- Async logging for minimal performance impact
- Environment variable configuration
- Debug/silent mode options
