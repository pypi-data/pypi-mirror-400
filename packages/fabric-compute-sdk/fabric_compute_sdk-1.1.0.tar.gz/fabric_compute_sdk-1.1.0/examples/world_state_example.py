"""
World State Example: Collect real-world context from distributed nodes

This example demonstrates how to use Fabric's World State workload to
gather environmental signals (HTTP responses, DOM content, latency, 
device profiles) from multiple nodes across different geographies.

Use cases:
- Monitor pricing pages across countries
- Detect geo-based content variations
- Measure real-world latency from consumer networks
- Verify mobile vs desktop experiences
"""

from fabric_sdk import FabricClient

# Initialize client with API key
client = FabricClient(
    api_url="https://api.fabric.carmel.so",
    api_key="fb_live_your_api_key_here"  # Replace with your API key
)

# Check credit balance
balance = client.get_credit_balance()
print(f"💰 Credit balance: ${balance['credits_balance']:.2f}")

# ============================================================================
# Example 1: Basic HTTP probe across geos
# ============================================================================
print("\n📡 Example 1: HTTP probe across geos")

probe = client.world_state.collect(
    signals=["http", "latency"],
    targets=["https://example.com"],
    geos=["us", "gb", "de"],
    max_nodes=5
)

print(f"✅ Dispatched to {probe['jobs_created']} nodes")
print(f"   Decision ID: {probe['decision_id']}")
print(f"   Estimated cost: ${probe['estimated_total_cost']:.4f}")

# Wait for results
results = client.world_state.wait_for_results(
    probe['decision_id'],
    timeout=60
)

print(f"\n📊 Results ({results['completed_jobs']}/{results['total_jobs']} completed):")
for snapshot in results['world_state']:
    http = snapshot['results'].get('http', {})
    latency = snapshot['results'].get('latency', {})
    print(f"   {snapshot['geo'].upper()} ({snapshot['device']}): "
          f"status={http.get('status', 'N/A')}, "
          f"latency={latency.get('ms', 'N/A')}ms")


# ============================================================================
# Example 2: DOM monitoring with metadata
# ============================================================================
print("\n📡 Example 2: DOM monitoring with metadata")

probe = client.world_state.collect(
    signals=["http", "dom"],
    targets=["https://competitor.com/pricing"],
    geos=["us", "ng", "br"],
    device_types=["mobile"],
    metadata={
        "policy_id": "pricing_monitor_v2",
        "decision_context": "quarterly_review"
    },
    max_nodes=3
)

print(f"✅ Dispatched to {probe['jobs_created']} nodes")

# Poll manually for more control
import time
for i in range(10):
    results = client.world_state.get_results(probe['decision_id'])
    print(f"   Poll {i+1}: {results['completed_jobs']}/{results['total_jobs']} complete")
    
    if results['status'] == 'complete':
        break
    time.sleep(3)

print(f"\n📊 DOM Results:")
for snapshot in results['world_state']:
    dom = snapshot['results'].get('dom', {})
    print(f"   {snapshot['geo'].upper()}: "
          f"title='{dom.get('title', 'N/A')}', "
          f"h1='{dom.get('h1', 'N/A')}'")

# Metadata is passed through
print(f"\n📎 Metadata: {results.get('metadata', {})}")


# ============================================================================
# Example 3: Device profile collection
# ============================================================================
print("\n📡 Example 3: Device profile collection")

probe = client.world_state.collect(
    signals=["device_profile"],
    targets=[],  # No URL needed for device_profile
    geos=["us"],
    device_types=["desktop", "mobile"],
    max_nodes=6
)

results = client.world_state.wait_for_results(probe['decision_id'])

print(f"\n🖥️ Device Profiles:")
for snapshot in results['world_state']:
    profile = snapshot['results'].get('device_profile', {})
    print(f"   Node {snapshot['node_id'][:8]}...: "
          f"os={profile.get('os', 'N/A')}, "
          f"browser={profile.get('browser', 'N/A')}")

print("\n✅ All examples complete!")


