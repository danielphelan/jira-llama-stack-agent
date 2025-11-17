#!/usr/bin/env python3
"""
Example usage of the Jira-Confluence Requirements Analysis Agent.

This script demonstrates how to use the agent for various tasks.
"""

import asyncio
import logging
from pathlib import Path

from src.agent.core import RequirementsAgent
from src.utils.logging import setup_logging
from src.utils.helpers import load_env


async def example_analyze_single_story():
    """Example: Analyze a single Jira story."""
    print("\n" + "="*60)
    print("Example 1: Analyze Single Story")
    print("="*60 + "\n")

    # Initialize agent
    agent = RequirementsAgent(config_path="config/agent_config.yaml")

    # Analyze a story
    ticket_id = "PROJ-123"  # Replace with actual ticket ID

    print(f"Analyzing story: {ticket_id}...")

    results = await agent.analyze_story(
        ticket_id=ticket_id,
        post_comment=True,
        estimate_points=True,
        generate_tests=True
    )

    if results["success"]:
        print(f"✅ Analysis complete!")
        print(f"   Completeness: {results['analysis'].completeness_score}/10")

        if results["estimation"]:
            print(f"   Story Points: {results['estimation'].estimated_points}")
            print(f"   Confidence: {results['estimation'].confidence:.2f}")

        if results["tests"]:
            print(f"   Test Cases: {results['tests'].total_test_cases}")

        if results["comment_posted"]:
            print(f"   ✓ Comment posted to Jira")
    else:
        print(f"❌ Analysis failed")


async def example_batch_analysis():
    """Example: Analyze multiple stories in batch."""
    print("\n" + "="*60)
    print("Example 2: Batch Analysis")
    print("="*60 + "\n")

    agent = RequirementsAgent()

    # List of tickets to analyze
    ticket_ids = [
        "PROJ-123",
        "PROJ-124",
        "PROJ-125"
    ]

    print(f"Analyzing {len(ticket_ids)} stories in batch...")

    results = await agent.batch_analyze_stories(
        ticket_ids=ticket_ids,
        post_comments=True
    )

    print(f"\n✅ Batch analysis complete!")
    print(f"   Successful: {results['successful']}/{results['total']}")
    print(f"   Failed: {results['failed']}/{results['total']}")


async def example_generate_epic_spec():
    """Example: Generate technical specification for an Epic."""
    print("\n" + "="*60)
    print("Example 3: Generate Epic Technical Specification")
    print("="*60 + "\n")

    agent = RequirementsAgent()

    epic_id = "PROJ-100"  # Replace with actual Epic ID

    print(f"Generating technical spec for Epic: {epic_id}...")

    results = await agent.generate_epic_spec(
        epic_id=epic_id,
        confluence_space="TECH",
        post_to_confluence=True
    )

    if results["success"]:
        print(f"✅ Technical spec generated!")
        if results["confluence_url"]:
            print(f"   Confluence URL: {results['confluence_url']}")
    else:
        print(f"❌ Spec generation failed")


async def example_health_check():
    """Example: Perform system health check."""
    print("\n" + "="*60)
    print("Example 4: Health Check")
    print("="*60 + "\n")

    agent = RequirementsAgent()

    print("Checking system health...")

    health = await agent.health_check()

    print(f"\nHealth Status:")
    print(f"   MCP Connection: {'✅' if health['mcp_connection'] else '❌'}")
    print(f"   Llama Stack: {'✅' if health['llama_stack'] else '❌'}")
    print(f"   Overall: {'✅' if health['overall'] else '❌'}")


async def example_custom_workflow():
    """Example: Custom workflow using lower-level APIs."""
    print("\n" + "="*60)
    print("Example 5: Custom Workflow")
    print("="*60 + "\n")

    agent = RequirementsAgent()

    ticket_id = "PROJ-123"

    # Step 1: Analyze story
    print(f"Step 1: Analyzing {ticket_id}...")
    analysis = await agent.tools.analyze_user_story(ticket_id)

    if analysis:
        print(f"   Completeness: {analysis.completeness_score}/10")

        # Step 2: Only estimate if complete enough
        if analysis.completeness_score >= 7.0:
            print(f"\nStep 2: Estimating story points...")
            estimation = await agent.tools.estimate_story_points(ticket_id)

            if estimation:
                print(f"   Estimate: {estimation.estimated_points} points")
                print(f"   Confidence: {estimation.confidence:.2f}")

        # Step 3: Generate tests
        print(f"\nStep 3: Generating test cases...")
        tests = await agent.tools.generate_test_cases(ticket_id)

        if tests:
            print(f"   Total tests: {tests.total_test_cases}")
            print(f"   Unit tests: {len(tests.unit_tests)}")
            print(f"   Integration tests: {len(tests.integration_tests)}")
            print(f"   E2E tests: {len(tests.e2e_tests)}")

        # Step 4: Format and post comment
        print(f"\nStep 4: Posting analysis to Jira...")
        comment = await agent.tools.format_analysis_comment(
            ticket_id, analysis, estimation, tests
        )

        print(f"   Comment preview:\n{comment[:200]}...")


async def main():
    """Run all examples."""
    # Setup logging
    setup_logging(level="INFO")

    # Load environment variables
    load_env()

    print("\n" + "="*60)
    print("Jira-Confluence Requirements Analysis Agent")
    print("Examples and Usage Demonstrations")
    print("="*60)

    # Run examples (comment out as needed)
    try:
        # Example 1: Single story analysis
        # await example_analyze_single_story()

        # Example 2: Batch analysis
        # await example_batch_analysis()

        # Example 3: Epic technical spec
        # await example_generate_epic_spec()

        # Example 4: Health check
        await example_health_check()

        # Example 5: Custom workflow
        # await example_custom_workflow()

        print("\n" + "="*60)
        print("Examples complete!")
        print("="*60 + "\n")

    except Exception as e:
        logging.error(f"Example failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
