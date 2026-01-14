"""
Fabric World State - Collect real-world context signals from distributed nodes

This module provides methods for submitting world_state jobs that dispatch
to multiple nodes across different geos and device types, then aggregating
the results into a unified "world-state trace."

Copyright 2025 Carmel Labs, Inc.
Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, Optional, List


class WorldStateClient:
    """
    World State client for collecting environmental context from distributed nodes.
    
    Access via FabricClient.world_state:
        >>> client = FabricClient(api_url="...", api_key="...")
        >>> result = client.world_state.collect({...})
    
    World State jobs dispatch to multiple nodes simultaneously based on
    geo and device_type filters, then aggregate results into a single trace.
    """
    
    def __init__(self, client):
        """
        Initialize with parent FabricClient
        
        Args:
            client: Parent FabricClient instance
        """
        self._client = client
    
    def collect(
        self,
        signals: List[str],
        targets: List[str],
        geos: Optional[List[str]] = None,
        device_types: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_ms: int = 8000,
        max_nodes: int = 20,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit a world_state collection request to multiple nodes.
        
        This dispatches jobs to nodes matching the geo/device criteria and
        returns immediately with a decision_id. Use get_results() or
        wait_for_results() to retrieve the aggregated data.
        
        Args:
            signals: What to collect. Options: "http", "dom", "latency", "device_profile"
            targets: URLs to probe (e.g., ["https://example.com/pricing"])
            geos: ISO country codes to filter nodes (e.g., ["us", "ng", "br"])
                  If None, nodes from any geo are selected.
            device_types: Device types to filter (e.g., ["desktop", "mobile"])
                          If None, any device type is selected.
            headers: Custom HTTP headers for requests (optional)
            timeout_ms: Timeout for each node's request in milliseconds (default: 8000)
            max_nodes: Maximum number of nodes to dispatch to (default: 20)
            metadata: Pass-through metadata included in results (e.g., policy_id)
        
        Returns:
            Dict containing:
                - decision_id: Unique ID linking all dispatched jobs
                - jobs_created: Number of jobs dispatched
                - nodes_selected: List of node IDs
                - estimated_total_cost: Estimated cost for all jobs
        
        Raises:
            JobSubmissionError: If submission fails
            InsufficientCreditsError: If insufficient credits
        
        Example:
            >>> probe = client.world_state.collect(
            ...     signals=["http", "dom", "latency"],
            ...     targets=["https://competitor.com/pricing"],
            ...     geos=["us", "br", "ng"],
            ...     device_types=["mobile"],
            ...     metadata={"policy_id": "renewal_v3"}
            ... )
            >>> print(f"Dispatched to {probe['jobs_created']} nodes")
            >>> print(f"Decision ID: {probe['decision_id']}")
        """
        params = {
            "signals": signals,
            "targets": targets,
            "timeoutMs": timeout_ms,
            "maxNodes": max_nodes
        }
        
        if geos:
            params["geos"] = geos
        if device_types:
            params["device_types"] = device_types
        if headers:
            params["headers"] = headers
        if metadata:
            params["metadata"] = metadata
        
        # Submit via standard job endpoint - backend handles multi-node dispatch
        return self._client._make_request(
            'POST',
            '/api/jobs/submit',
            data={
                'job_type': 'world_state',
                'params': params
            }
        )
    
    def get_results(self, decision_id: str) -> Dict[str, Any]:
        """
        Get aggregated results for a world_state collection.
        
        Args:
            decision_id: The decision_id returned from collect()
        
        Returns:
            Dict containing:
                - decision_id: The decision ID
                - status: "pending", "partial", or "complete"
                - total_jobs: Total jobs dispatched
                - completed_jobs: Number of completed jobs
                - failed_jobs: Number of failed jobs
                - metadata: Pass-through metadata from original request
                - world_state: List of node snapshots (each with node_id, geo, 
                              device, timestamp, results, errors)
        
        Raises:
            NetworkError: If request fails
        
        Example:
            >>> results = client.world_state.get_results(probe['decision_id'])
            >>> if results['status'] == 'complete':
            ...     for snapshot in results['world_state']:
            ...         print(f"{snapshot['geo']}: {snapshot['results']['http']['status']}")
        """
        return self._client._make_request(
            'GET',
            f'/api/jobs/world-state/{decision_id}/results'
        )
    
    def wait_for_results(
        self,
        decision_id: str,
        timeout: int = 120,
        poll_interval: int = 3,
        min_completion_ratio: float = 0.8
    ) -> Dict[str, Any]:
        """
        Wait for world_state results to complete.
        
        Polls until either:
        - All jobs complete
        - Timeout is reached
        - min_completion_ratio of jobs complete (to handle slow/failed nodes)
        
        Args:
            decision_id: The decision_id returned from collect()
            timeout: Maximum wait time in seconds (default: 120)
            poll_interval: Seconds between polls (default: 3)
            min_completion_ratio: Return early if this ratio completes (default: 0.8)
        
        Returns:
            Same as get_results()
        
        Raises:
            JobTimeoutError: If timeout reached before min_completion_ratio
        
        Example:
            >>> probe = client.world_state.collect(...)
            >>> results = client.world_state.wait_for_results(
            ...     probe['decision_id'],
            ...     timeout=60,
            ...     min_completion_ratio=0.7  # Return when 70% complete
            ... )
            >>> print(f"Got {len(results['world_state'])} snapshots")
        """
        from .exceptions import JobTimeoutError
        
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                # Get whatever we have
                results = self.get_results(decision_id)
                if results.get('completed_jobs', 0) == 0:
                    raise JobTimeoutError(
                        f"World state collection {decision_id} timed out after {timeout}s "
                        f"with no completed jobs"
                    )
                return results
            
            results = self.get_results(decision_id)
            
            total = results.get('total_jobs', 0)
            completed = results.get('completed_jobs', 0)
            failed = results.get('failed_jobs', 0)
            
            # Check if done
            if total > 0 and (completed + failed) >= total:
                return results
            
            # Check if we have enough
            if total > 0 and completed / total >= min_completion_ratio:
                return results
            
            time.sleep(poll_interval)


