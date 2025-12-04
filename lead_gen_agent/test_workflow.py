"""Quick test script to verify the lead generation workflow."""

import sys
sys.path.insert(0, "c:\\Users\\ayusi\\Desktop\\New folder\\lead_gen_agent")

from lead_gen_agent.graph import create_workflow
from lead_gen_agent.models import Lead

def test_workflow():
    """Test the lead generation workflow."""
    print("=" * 60)
    print("Testing Lead Generation Workflow")
    print("=" * 60)
    
    # Create workflow
    workflow = create_workflow()
    
    # Run with a test query
    result = workflow.run(
        query="AI startups",
        sources=["web_search"],
        icp_config={
            "target_industries": ["Technology", "Artificial Intelligence"],
            "target_geographies": ["California", "New York"],
            "preferred_tech_stack": ["Python", "AWS"],
        },
        max_results=5,
    )
    
    print(f"\nWorkflow Success: {result['success']}")
    print(f"Total Leads: {result['statistics'].get('total_leads', 0)}")
    print(f"Errors: {result.get('errors', [])}")
    
    print("\n" + "-" * 60)
    print("Generated Leads:")
    print("-" * 60)
    
    for i, lead_data in enumerate(result['leads'], 1):
        print(f"\n{i}. {lead_data.get('company_name', 'Unknown')}")
        print(f"   Industry: {lead_data.get('industry', 'N/A')}")
        print(f"   Location: {lead_data.get('location', 'N/A')}")
        print(f"   Website: {lead_data.get('company_website', 'N/A')}")
        print(f"   Score: {lead_data.get('lead_score', 0):.1f}")
        print(f"   Priority: {lead_data.get('priority', 'N/A')}")
        
        # Check company object
        company = lead_data.get('company', {})
        if company:
            tech_stack = company.get('tech_stack', [])
            if tech_stack:
                print(f"   Tech Stack: {', '.join(tech_stack)}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    test_workflow()
