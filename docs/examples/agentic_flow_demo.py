#!/usr/bin/env python3
"""
Agentic Flow Demonstration

This script demonstrates the agentic capabilities of the memory-map application.
It shows how Claude Desktop (or any MCP client) can use multiple tools in sequence
to answer complex queries like "What was I doing on October 15?"

The agentic flow:
1. User asks a question
2. Agent decides which tools to use
3. Agent calls multiple tools (text search, image search, date filtering)
4. Agent synthesizes results into a coherent story
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.memory_service import MemoryService
from datetime import datetime, timedelta


def demo_agentic_flow():
    """Demonstrate the complete agentic flow."""

    print("=" * 70)
    print("AGENTIC FLOW DEMONSTRATION")
    print("=" * 70)
    print()

    # Initialize the service
    print("Initializing memory service...")
    service = MemoryService()
    print("✓ Service initialized\n")

    # Step 1: Add some sample memories with dates
    print("Step 1: Adding sample memories with dates...")
    print("-" * 70)

    # Add memories for October 15
    service.add_text_memory(
        text="Started the day with a morning jog in the park. Weather was perfect!",
        title="Morning Exercise",
        tags="health, routine, outdoors",
        description="Daily morning routine on October 15, 2025"
    )

    service.add_text_memory(
        text="Had a productive team meeting about the Q4 roadmap. Discussed new features and timeline.",
        title="Team Meeting",
        tags="work, planning, team",
        description="Q4 planning session on October 15, 2025"
    )

    service.add_text_memory(
        text="Finished reading 'The Design of Everyday Things'. Great insights on user-centered design.",
        title="Evening Reading",
        tags="books, learning, design",
        description="Reading session on October 15, 2025"
    )

    # Add memories for other dates
    service.add_text_memory(
        text="Attended a virtual conference on AI and machine learning.",
        title="AI Conference",
        tags="conference, AI, learning",
        description="October 14, 2025"
    )

    print("✓ Added 4 text memories\n")

    # Step 2: Demonstrate different search approaches
    print("Step 2: Demonstrating Search Approaches")
    print("-" * 70)

    # Approach 1: Simple unified search
    print("\nApproach 1: UNIFIED SEARCH (non-agentic)")
    print("Query: 'October 15'")
    result = service.search_memories("October 15", n_results=3)
    print(f"Found {result.count} memories using unified search")
    for i, mem in enumerate(result.memories, 1):
        title = mem.get('metadata', {}).get('title', 'Untitled')
        print(f"  {i}. {title}")

    # Approach 2: Specialized searches
    print("\nApproach 2: SPECIALIZED SEARCHES (semi-agentic)")
    print("Searching text and images separately...")

    text_result = service.search_text_memories_only("October 15", n_results=5)
    print(f"Text memories: {text_result.count}")
    for i, mem in enumerate(text_result.memories, 1):
        title = mem.get('metadata', {}).get('title', 'Untitled')
        print(f"  {i}. {title}")

    # Approach 3: Date-aware search
    print("\nApproach 3: DATE-AWARE SEARCH (more agentic)")
    print("Query: 'activities' on date '2025-10-15'")

    date_result = service.search_memories_by_date(
        query="activities",
        start_date="2025-10-15",
        n_results=10
    )
    print(f"Found {date_result.count} memories on October 15")
    for i, mem in enumerate(date_result.memories, 1):
        title = mem.get('metadata', {}).get('title', 'Untitled')
        print(f"  {i}. {title}")

    # Approach 4: Full synthesis (AGENTIC)
    print("\nApproach 4: FULL SYNTHESIS (fully agentic)")
    print("Query: 'What was I doing on October 15?'")
    print()

    synthesis = service.synthesize_memories(
        query="daily activities October 15",
        start_date="2025-10-15",
        end_date="2025-10-15",
        n_results_per_type=10
    )

    print("SYNTHESIS RESULT:")
    print(synthesis.synthesis_summary)
    print()
    print(f"Timeline ({len(synthesis.timeline)} events):")
    for i, mem in enumerate(synthesis.timeline, 1):
        metadata = mem.get('metadata', {})
        title = metadata.get('title', 'Untitled')
        mem_type = metadata.get('type', 'unknown')
        date = metadata.get('date') or metadata.get('timestamp', 'Unknown')
        print(f"  [{date}] {title} ({mem_type})")

    # Step 3: Show how an agent would use this
    print("\n" + "=" * 70)
    print("Step 3: AGENTIC DECISION FLOW")
    print("=" * 70)
    print()
    print("User Query: 'What was I doing on October 15?'")
    print()
    print("Agent Decision Process:")
    print("1. ANALYZE QUERY:")
    print("   - Detected temporal intent: 'October 15'")
    print("   - Detected activity intent: 'doing'")
    print("   - Decision: Use date-filtered synthesis")
    print()
    print("2. TOOL SELECTION:")
    print("   ✓ synthesize_memory_story")
    print("     - query: 'daily activities'")
    print("     - start_date: '2025-10-15'")
    print("     - end_date: '2025-10-15'")
    print("     - n_results_per_type: 10")
    print()
    print("3. EXECUTE TOOL:")
    print(f"   - Searched {len(synthesis.text_memories)} text memories")
    print(f"   - Searched {len(synthesis.image_memories)} image memories")
    print(f"   - Created timeline with {len(synthesis.timeline)} events")
    print()
    print("4. SYNTHESIZE RESPONSE:")
    print()
    print("   'On October 15, 2025, you had a full day:")
    print()
    for mem in synthesis.timeline:
        metadata = mem.get('metadata', {})
        title = metadata.get('title', '')
        text = metadata.get('text', '')
        if text:
            # Extract first sentence
            first_sentence = text.split('.')[0] + '.'
            print(f"   - {title}: {first_sentence}")
    print()
    print("   You stayed active with exercise, had productive work meetings,")
    print("   and ended the day with some reading.'")
    print()

    # Step 4: Comparison
    print("=" * 70)
    print("COMPARISON: Non-Agentic vs Agentic")
    print("=" * 70)
    print()
    print("NON-AGENTIC (old approach):")
    print("  - Single search_memories() call")
    print("  - Returns mixed results, not organized")
    print("  - No temporal awareness")
    print("  - User must manually piece together the story")
    print()
    print("AGENTIC (new approach):")
    print("  - Multi-step reasoning")
    print("  - Specialized tool selection (text vs image vs date)")
    print("  - Automatic timeline creation")
    print("  - Coherent narrative synthesis")
    print("  - Context-aware responses")
    print()

    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_agentic_flow()
