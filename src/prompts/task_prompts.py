"""
Task-specific prompt templates for requirements analysis.
"""

from typing import Dict, Any


def STORY_ANALYSIS_PROMPT(
    title: str,
    description: str,
    acceptance_criteria: str,
    labels: list,
    components: list,
    similar_stories: list
) -> str:
    """
    Generate prompt for analyzing a user story.

    Args:
        title: Story title/summary
        description: Story description
        acceptance_criteria: Acceptance criteria text
        labels: List of Jira labels
        components: List of affected components
        similar_stories: List of similar past stories

    Returns:
        Formatted prompt string
    """
    similar_context = "\n".join([
        f"- {s.get('title', 'N/A')} ({s.get('key', 'N/A')}): {s.get('points', 'N/A')} points"
        for s in similar_stories[:5]
    ])

    return f"""Analyze this Jira user story comprehensively:

**Story Details:**
Title: {title}
Description: {description or "(No description provided)"}
Acceptance Criteria: {acceptance_criteria or "(No acceptance criteria provided)"}
Labels: {', '.join(labels) if labels else "None"}
Components: {', '.join(components) if components else "None"}

**Similar Past Stories:**
{similar_context or "No similar stories found"}

**Analysis Tasks:**

1. **Requirements Extraction:**
   - Extract actors, actions, and business value from the story
   - Identify implicit requirements not explicitly stated
   - List assumptions that need validation

2. **Completeness Assessment:**
   - Rate completeness on scale of 0-10
   - Identify missing elements by category:
     * Functional requirements
     * Security requirements (auth, data protection, input validation)
     * Performance requirements (response times, scalability)
     * Accessibility requirements (WCAG compliance)
     * Error handling scenarios
     * Edge cases and boundary conditions
     * Data validation rules

3. **Acceptance Criteria Analysis:**
   - Parse existing acceptance criteria
   - Identify gaps or ambiguities
   - Suggest additional criteria if needed
   - Convert to Given-When-Then format if not already

4. **Risk Assessment:**
   - Identify technical risks and unknowns
   - Flag dependencies on other teams/systems
   - Note complexity factors

5. **Recommendations:**
   - Suggest specific improvements to the story
   - Recommend questions for product owner
   - Identify areas needing architectural review

**Output Format (JSON):**
```json
{{
  "actors": ["list of user types/roles"],
  "actions": ["list of user actions"],
  "business_value": "why this story matters",
  "implicit_requirements": ["requirements not explicitly stated"],
  "assumptions": ["assumptions that need validation"],
  "completeness_score": 0.0,
  "missing_requirements": {{
    "functional": ["list"],
    "security": ["list"],
    "performance": ["list"],
    "accessibility": ["list"],
    "error_handling": ["list"],
    "edge_cases": ["list"]
  }},
  "acceptance_criteria_gaps": ["list of missing or unclear AC"],
  "risks": [
    {{"type": "technical|dependency|unknown", "description": "...", "severity": "high|medium|low"}}
  ],
  "recommendations": ["specific actionable suggestions"],
  "questions_for_po": ["questions needing clarification"]
}}
```

Provide thorough, specific analysis that helps engineers understand exactly what needs to be built.
"""


def ESTIMATION_PROMPT(
    story_summary: str,
    acceptance_criteria: list,
    similar_stories: list,
    team_velocity: float
) -> str:
    """
    Generate prompt for estimating story points.

    Args:
        story_summary: Brief story description
        acceptance_criteria: List of AC items
        similar_stories: List of similar completed stories with points
        team_velocity: Average team velocity (points per sprint)

    Returns:
        Formatted prompt string
    """
    ac_text = "\n".join([f"- {ac}" for ac in acceptance_criteria])

    similar_text = "\n".join([
        f"- {s.get('title', 'N/A')} ({s.get('key', 'N/A')}): {s.get('points', 'N/A')} points "
        f"(actual: {s.get('actual_points', 'N/A')})"
        for s in similar_stories[:10]
    ])

    return f"""Estimate story points for this user story based on historical data:

**Current Story:**
{story_summary}

**Acceptance Criteria:**
{ac_text}

**Historical Context (Similar Stories):**
{similar_text or "No similar stories available"}

**Team Context:**
- Average Velocity: {team_velocity} points/sprint
- Team Capacity: Standard Scrum team (5-7 developers)

**Estimation Factors to Consider:**

1. **Complexity:**
   - Algorithm complexity
   - Business logic complexity
   - UI/UX complexity
   - Data model changes required

2. **Uncertainty:**
   - Unknown technical challenges
   - Third-party dependencies
   - Research/spike work needed

3. **Integration Points:**
   - APIs to integrate
   - External services
   - Database changes
   - Frontend-backend coordination

4. **Testing Effort:**
   - Unit test coverage needed
   - Integration test scenarios
   - E2E test cases
   - Manual QA effort

5. **Technical Debt:**
   - Code quality in affected areas
   - Refactoring needed
   - Documentation gaps

**Story Point Scale:**
- 1 point: Trivial change, < 2 hours, no unknowns
- 2 points: Simple change, < 1 day, minimal risk
- 3 points: Moderate change, 1-2 days, some complexity
- 5 points: Complex change, 2-3 days, multiple components
- 8 points: Very complex, 3-5 days, significant unknowns
- 13 points: Epic-level, should be broken down

**Output Format (JSON):**
```json
{{
  "estimated_points": 5,
  "confidence": 0.75,
  "confidence_interval": [3, 8],
  "reasoning": "Detailed explanation of the estimate",
  "similar_stories_analyzed": 10,
  "comparison_to_similar": "How this compares to similar stories",
  "adjustment_factors": {{
    "complexity_multiplier": 1.2,
    "uncertainty_multiplier": 1.0,
    "team_familiarity": 0.9,
    "technical_debt": 1.1
  }},
  "risk_factors": ["list of factors that could increase effort"],
  "recommendations": ["suggestions like 'break into smaller stories' or 'need spike first'"]
}}
```

Provide data-driven estimate with clear reasoning. If confidence is low (<0.7), recommend a planning poker session or story breakdown.
"""


def TEST_GENERATION_PROMPT(
    story_title: str,
    acceptance_criteria: list,
    tech_stack: Dict[str, str],
    test_framework: str
) -> str:
    """
    Generate prompt for creating test cases.

    Args:
        story_title: Story summary
        acceptance_criteria: List of AC items
        tech_stack: Technology stack details
        test_framework: Testing framework to use

    Returns:
        Formatted prompt string
    """
    ac_text = "\n".join([f"{i+1}. {ac}" for i, ac in enumerate(acceptance_criteria)])

    return f"""Generate comprehensive test cases for this user story:

**Story:** {story_title}

**Acceptance Criteria:**
{ac_text}

**Technical Context:**
- Backend: {tech_stack.get('backend', 'Unknown')}
- Frontend: {tech_stack.get('frontend', 'Unknown')}
- Database: {tech_stack.get('database', 'Unknown')}
- Test Framework: {test_framework}

**Test Suite Requirements:**

1. **Unit Tests** (Test business logic in isolation)
   - Test each acceptance criterion
   - Test error handling
   - Test edge cases and boundary conditions
   - Test input validation
   - Mock external dependencies

2. **Integration Tests** (Test component interactions)
   - API endpoint tests with real requests/responses
   - Database integration tests
   - Service layer integration
   - Error propagation across layers

3. **End-to-End Tests** (Test complete user journeys)
   - Happy path scenarios
   - Error scenarios with user feedback
   - Multi-step workflows
   - Cross-browser compatibility (if UI)

4. **QA Test Scenarios** (Manual testing guide)
   - Step-by-step test procedures
   - Test data requirements
   - Expected results at each step
   - Screenshots/evidence to capture

**Output Format (JSON):**
```json
{{
  "test_framework": "{test_framework}",
  "total_test_cases": 0,
  "coverage_analysis": {{
    "acceptance_criteria_covered": "90%",
    "edge_cases_covered": "85%",
    "error_scenarios_covered": "80%"
  }},
  "unit_tests": [
    {{
      "test_id": "UT-001",
      "test_name": "test_validates_email_format",
      "type": "unit",
      "priority": "high",
      "description": "Validates that email format is checked before submission",
      "given": "User submits form with invalid email",
      "when": "Form validation runs",
      "then": "Error message is displayed and submission is blocked",
      "test_data": {{"invalid_emails": ["test@", "test.com", "@test.com"]}},
      "code_snippet": "// Example test code if applicable",
      "assertions": ["error message is shown", "form is not submitted"]
    }}
  ],
  "integration_tests": [
    {{
      "test_id": "IT-001",
      "test_name": "test_user_creation_api",
      "type": "integration",
      "priority": "high",
      "description": "Tests user creation through API endpoint",
      "setup": "Initialize test database",
      "steps": ["Send POST to /api/users", "Verify 201 status", "Check database"],
      "teardown": "Clean up test data",
      "assertions": ["User created in DB", "Response includes user ID"]
    }}
  ],
  "e2e_tests": [
    {{
      "test_id": "E2E-001",
      "test_name": "test_complete_user_registration_flow",
      "type": "e2e",
      "priority": "high",
      "description": "Tests full user registration from UI to database",
      "user_journey": "Navigate to signup -> Fill form -> Submit -> Verify email -> Login",
      "steps": ["Step 1 details", "Step 2 details"],
      "expected_results": ["User can log in", "Welcome email received"]
    }}
  ],
  "qa_scenarios": [
    {{
      "scenario_id": "QA-001",
      "title": "User Registration - Happy Path",
      "priority": "P0",
      "preconditions": ["Browser is open", "User is not logged in"],
      "steps": [
        {{"step": 1, "action": "Navigate to /signup", "expected": "Signup form displayed"}},
        {{"step": 2, "action": "Enter valid email and password", "expected": "Fields accept input"}},
        {{"step": 3, "action": "Click Submit", "expected": "Success message shown"}}
      ],
      "test_data": {{"valid_email": "test@example.com", "valid_password": "SecurePass123!"}},
      "expected_result": "User is created and redirected to dashboard"
    }}
  ],
  "missing_test_coverage": ["List any AC not fully covered"],
  "recommendations": ["Suggestions for additional test scenarios"]
}}
```

Generate thorough test coverage that catches bugs before production. Focus on real-world scenarios and edge cases.
"""


def TECHNICAL_SPEC_PROMPT(
    epic_summary: str,
    child_stories: list,
    similar_projects: list,
    requirements: Dict[str, Any]
) -> str:
    """
    Generate prompt for creating technical specification.

    Args:
        epic_summary: Epic description
        child_stories: List of user stories under this epic
        similar_projects: Similar past implementations
        requirements: Consolidated requirements

    Returns:
        Formatted prompt string
    """
    stories_text = "\n".join([
        f"- {s.get('key', 'N/A')}: {s.get('summary', 'N/A')} ({s.get('points', '?')} pts)"
        for s in child_stories
    ])

    similar_text = "\n".join([
        f"- {p.get('title', 'N/A')}: {p.get('url', 'N/A')}"
        for p in similar_projects[:5]
    ])

    return f"""Generate a comprehensive technical design document for this Epic:

**Epic:** {epic_summary}

**User Stories (Total {len(child_stories)}):**
{stories_text}

**Similar Past Projects:**
{similar_text or "No similar projects found"}

**Consolidated Requirements:**
{requirements}

**Document Structure:**

# Technical Design: [Epic Title]

## 1. Overview
- **Epic ID**: [EPIC-XXX]
- **Estimated Effort**: [X points over Y sprints]
- **Target Release**: [Version/Date]
- **Owner**: [Team/Lead]

## 2. Business Context
- **Problem Statement**: What problem are we solving?
- **Business Value**: Why is this important?
- **Success Metrics**: How do we measure success?
- **User Impact**: Who benefits and how?

## 3. Requirements Summary
- **User Stories**: [Links to all stories]
- **Functional Requirements**: [Consolidated from all stories]
- **Non-Functional Requirements**: [Performance, security, scalability]
- **Out of Scope**: [What we're NOT doing]

## 4. Architecture & Design

### 4.1 System Architecture
```
[Mermaid diagram of system components]
```

### 4.2 Data Model
- Database schema changes
- New tables/collections
- Relationships and constraints
- Migration strategy

### 4.3 API Design
- New endpoints (REST/GraphQL)
- Request/response schemas
- Authentication/authorization
- Rate limiting and caching

### 4.4 Frontend Architecture
- Component structure
- State management approach
- Routing changes
- UI/UX flow diagrams

### 4.5 Integration Points
- External services/APIs
- Internal microservices
- Event/message flows
- Error handling and retries

### 4.6 Architecture Decision Records (ADRs)
- **ADR-001**: [Decision title]
  - Context: [Why we need to make this decision]
  - Decision: [What we decided]
  - Consequences: [Trade-offs and implications]

## 5. Implementation Plan

### Phase 1: Foundation (Stories: X, Y)
- Tasks and deliverables
- Dependencies
- Timeline

### Phase 2: Core Features (Stories: A, B, C)
- Tasks and deliverables
- Dependencies
- Timeline

### Phase 3: Polish & Optimization (Stories: D, E)
- Tasks and deliverables
- Timeline

### Risk Mitigation
- Technical risks and mitigation plans
- Dependencies on other teams
- Unknowns requiring spikes/research

## 6. Testing Strategy

### Unit Testing
- Coverage targets (>80%)
- Key areas to test
- Mocking strategy

### Integration Testing
- API contract tests
- Database integration tests
- Service integration tests

### E2E Testing
- Critical user journeys
- Cross-browser testing
- Performance testing

### QA Testing
- Manual test scenarios
- Regression test suite
- Exploratory testing focus areas

## 7. Deployment Plan

### Infrastructure Changes
- New services/containers
- Database migrations
- Configuration changes
- Environment variables

### Deployment Strategy
- Blue-green deployment
- Feature flags
- Rollback plan
- Monitoring during rollout

### Migration Plan (if applicable)
- Data migration scripts
- Backward compatibility
- Migration validation
- Rollback procedures

## 8. Monitoring & Observability

### Metrics to Track
- Business metrics (conversion, usage)
- Technical metrics (latency, errors)
- Infrastructure metrics (CPU, memory)

### Alerts to Configure
- Error rate thresholds
- Performance degradation
- Service health checks

### Dashboards
- User-facing metrics
- System health metrics
- Business KPIs

## 9. Security Considerations
- Authentication/authorization approach
- Data encryption (at rest, in transit)
- Input validation and sanitization
- OWASP Top 10 mitigation
- Compliance requirements (GDPR, etc.)

## 10. Performance Considerations
- Expected load and scalability targets
- Caching strategy
- Database query optimization
- CDN usage
- Performance budget

## 11. Documentation & Training
- User documentation needed
- API documentation
- Runbooks for operations
- Team training requirements

## 12. Related Documentation
- [Auto-linked Confluence pages]
- [Related Jira epics/stories]
- [External references]

**Output Format:**
Return the complete technical specification in Markdown format, ready to be published to Confluence.
Include Mermaid diagrams for architecture, sequence diagrams for key flows, and ERD for data models.

Make it comprehensive yet scannable with clear sections, bullet points, and code examples where helpful.
"""


def DESCRIPTION_GENERATION_PROMPT(
    story_title: str,
    story_type: str,
    similar_stories: list,
    project_context: str
) -> str:
    """
    Generate prompt for creating story description when missing.

    Args:
        story_title: Story title/summary
        story_type: Jira issue type (Story, Task, Bug)
        similar_stories: Similar completed stories
        project_context: Project/component context

    Returns:
        Formatted prompt string
    """
    similar_text = "\n".join([
        f"- {s.get('key', 'N/A')}: {s.get('summary', 'N/A')}\n  Description: {s.get('description', 'N/A')[:200]}..."
        for s in similar_stories[:3]
    ])

    return f"""Generate a proposed description for this Jira {story_type}:

**Title:** {story_title}
**Type:** {story_type}
**Project Context:** {project_context}

**Similar Stories for Reference:**
{similar_text or "No similar stories found"}

**Requirements:**

1. **User Story Format** (if type is Story):
   - As a [user type]
   - I want to [action/feature]
   - So that [business value/benefit]

2. **Description Content:**
   - Clear explanation of what needs to be done
   - Context on why this is needed
   - Any relevant background information
   - Links to related tickets or documentation

3. **Proposed Acceptance Criteria:**
   - At least 3-5 testable acceptance criteria
   - Use Given-When-Then format when appropriate
   - Cover happy path and key error scenarios
   - Include any non-functional requirements

4. **Unknowns/Questions:**
   - List anything that needs clarification
   - Flag assumptions being made
   - Identify information gaps

**Output Format (JSON):**
```json
{{
  "description": "Full description text",
  "acceptance_criteria": [
    "AC 1: ...",
    "AC 2: ...",
    "AC 3: ..."
  ],
  "unknowns": ["Question 1?", "Question 2?"],
  "assumptions": ["Assumption 1", "Assumption 2"],
  "confidence": 0.75,
  "similar_stories_used": ["PROJ-123", "PROJ-456"],
  "recommended_labels": ["label1", "label2"],
  "recommended_components": ["component1"]
}}
```

**Important:** This is AI-generated and MUST be reviewed by product owner and engineering.
Flag clearly that human review is required.
"""


def AC_GENERATION_PROMPT(
    story_title: str,
    story_description: str,
    similar_stories: list
) -> str:
    """
    Generate prompt for creating acceptance criteria when missing.

    Args:
        story_title: Story summary
        story_description: Story description
        similar_stories: Similar stories with AC

    Returns:
        Formatted prompt string
    """
    similar_text = "\n".join([
        f"- {s.get('key', 'N/A')}: {s.get('summary', 'N/A')}\n  AC: {s.get('acceptance_criteria', 'N/A')[:300]}..."
        for s in similar_stories[:3]
    ])

    return f"""Generate comprehensive acceptance criteria for this user story:

**Story:** {story_title}
**Description:** {story_description}

**Similar Stories with AC for Reference:**
{similar_text or "No similar stories found"}

**Generate AC covering:**

1. **Functional Criteria** (Happy Path)
   - Core feature functionality
   - Expected user workflows
   - Success conditions

2. **Error Handling**
   - Invalid input handling
   - Error messages shown to users
   - System behavior on failure

3. **Non-Functional Requirements**
   - Performance (response times, load handling)
   - Security (authentication, authorization, data protection)
   - Accessibility (WCAG 2.1 Level AA)
   - Browser/device compatibility

4. **Edge Cases**
   - Boundary conditions
   - Concurrent usage scenarios
   - Offline/degraded mode behavior

5. **Data Validation**
   - Input validation rules
   - Data format requirements
   - Required vs optional fields

**Format:**
- Use Given-When-Then format for behavior-driven scenarios
- Use checklist format for requirements
- Be specific and testable
- Include concrete examples

**Output Format (JSON):**
```json
{{
  "acceptance_criteria": [
    {{
      "id": "AC-001",
      "category": "functional",
      "priority": "high",
      "description": "Given [context], when [action], then [outcome]",
      "testable": true
    }},
    {{
      "id": "AC-002",
      "category": "security",
      "priority": "high",
      "description": "System validates user has permission before allowing action",
      "testable": true
    }}
  ],
  "total_criteria": 12,
  "confidence": 0.80,
  "coverage": {{
    "functional": 5,
    "security": 2,
    "performance": 1,
    "accessibility": 2,
    "edge_cases": 2
  }},
  "recommendations": ["Additional scenarios to consider"]
}}
```

Generate thorough, testable acceptance criteria that leave no ambiguity about what "done" means.
"""
