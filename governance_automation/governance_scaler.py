from kubernetes import client, config, watch
from prometheus_client import Counter, Gauge, Histogram
import asyncio
from typing import Dict, List, Any, Optional
import logging
import yaml
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GovernanceScaler:
    """Scalable governance automation for cloud environments."""
    
    def __init__(self, config_dir: str):
        """Initialize the governance scaler with configuration directory."""
        self.config_dir = config_dir
        self.initialize_metrics()
        self._init_kubernetes()

    def initialize_metrics(self):
        """Initialize Prometheus metrics for monitoring."""
        self.policy_violations = Counter(
            'governance_policy_violations',
            'Number of policy violations detected',
            ['policy_type', 'severity']
        )
        self.enforcement_latency = Histogram(
            'governance_enforcement_latency',
            'Time taken to enforce policies',
            ['policy_type']
        )
        self.active_policies = Gauge(
            'governance_active_policies',
            'Number of active governance policies',
            ['policy_type']
        )

    def _init_kubernetes(self):
        """Initialize Kubernetes client configuration."""
        try:
            config.load_kube_config()
            self.k8s_client = client.ApiClient()
            self.custom_objects = client.CustomObjectsApi()
            self.networking_v1 = client.NetworkingV1Api()
            logger.info("Kubernetes client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {str(e)}")
            raise

    async def enforce_policies(self, namespace: str) -> Dict[str, Any]:
        """
        Enforce multiple policies in parallel.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            Dictionary containing enforcement results
        """
        try:
            policies = self._load_policies()
            tasks = []
            
            for policy in policies:
                task = asyncio.create_task(
                    self._enforce_single_policy(policy, namespace)
                )
                tasks.append(task)
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return self._process_results(results, policies)
            
        except Exception as e:
            logger.error(f"Policy enforcement failed: {str(e)}")
            raise

    def _load_policies(self) -> List[Dict[str, Any]]:
        """Load policy configurations from directory."""
        policies = []
        try:
            for policy_file in os.listdir(self.config_dir):
                if policy_file.endswith('.yaml'):
                    with open(os.path.join(self.config_dir, policy_file)) as f:
                        policy = yaml.safe_load(f)
                        policies.append(policy)
                        logger.info(f"Loaded policy: {policy.get('metadata', {}).get('name')}")
            return policies
        except Exception as e:
            logger.error(f"Failed to load policies: {str(e)}")
            raise

    async def _enforce_single_policy(self,
                                   policy: Dict[str, Any],
                                   namespace: str) -> Dict[str, Any]:
        """Enforce a single policy asynchronously."""
        policy_type = policy.get('kind', 'unknown')
        try:
            with self.enforcement_latency.labels(policy_type).time():
                if policy_type == 'NetworkPolicy':
                    result = await self._apply_network_policy(policy, namespace)
                else:
                    result = await self._apply_generic_policy(policy, namespace)
                
            self.active_policies.labels(policy_type).inc()
            return result
            
        except Exception as e:
            self.policy_violations.labels(policy_type, 'error').inc()
            logger.error(f"Policy enforcement failed: {str(e)}")
            raise

    async def watch_policy_violations(self):
        """Watch for policy violations in real-time."""
        w = watch.Watch()
        try:
            async for event in w.stream(
                self.custom_objects.list_cluster_custom_object,
                group="policy",
                version="v1",
                plural="violations"
            ):
                await self._handle_violation(event['object'])
        except Exception as e:
            logger.error(f"Error watching violations: {str(e)}")
            raise

    async def _handle_violation(self, violation: Dict[str, Any]):
        """Process and handle detected policy violations."""
        try:
            violation_type = violation['spec']['type']
            severity = violation['spec']['severity']
            
            self.policy_violations.labels(
                violation_type, severity
            ).inc()
            
            if severity == 'critical':
                await self._remediate_violation(violation)
                
            logger.warning(
                f"Policy violation detected: {violation_type} - {severity}"
            )
            
        except Exception as e:
            logger.error(f"Error handling violation: {str(e)}")
            raise

    async def _remediate_violation(self, violation: Dict[str, Any]):
        """Attempt automated remediation of policy violations."""
        try:
            remediation = violation['spec'].get('remediation')
            if remediation:
                remediation_type = remediation.get('type')
                if remediation_type == 'update_policy':
                    await self._enforce_single_policy(
                        remediation['policy'],
                        violation['metadata']['namespace']
                    )
                elif remediation_type == 'scale_resources':
                    await self._scale_resources(remediation['resources'])
                elif remediation_type == 'apply_constraints':
                    await self._apply_constraints(remediation['constraints'])
                    
                logger.info(f"Remediation completed for violation: {violation['metadata']['name']}")
        except Exception as e:
            logger.error(f"Remediation failed: {str(e)}")
            raise

    async def _apply_network_policy(self, 
                                  policy: Dict[str, Any], 
                                  namespace: str) -> Dict[str, Any]:
        """Apply network policy to the cluster."""
        try:
            name = policy['metadata']['name']
            
            try:
                # Check if policy exists
                self.networking_v1.read_namespaced_network_policy(name, namespace)
                # Update existing policy
                self.networking_v1.replace_namespaced_network_policy(
                    name=name,
                    namespace=namespace,
                    body=policy
                )
                logger.info(f"Updated NetworkPolicy: {name}")
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # Create new policy
                    self.networking_v1.create_namespaced_network_policy(
                        namespace=namespace,
                        body=policy
                    )
                    logger.info(f"Created NetworkPolicy: {name}")
                else:
                    raise
                    
            return {
                'status': 'success',
                'policy': name,
                'type': 'NetworkPolicy',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Network policy application failed: {str(e)}")
            raise

    async def _apply_generic_policy(self,
                                  policy: Dict[str, Any],
                                  namespace: str) -> Dict[str, Any]:
        """Apply generic policy types."""
        try:
            name = policy['metadata']['name']
            kind = policy['kind']
            
            # Use dynamic client for generic policy types
            api = client.CustomObjectsApi()
            
            try:
                # Try to update existing policy
                api.patch_namespaced_custom_object(
                    group="policy",
                    version="v1",
                    namespace=namespace,
                    plural=f"{kind.lower()}s",
                    name=name,
                    body=policy
                )
                logger.info(f"Updated {kind}: {name}")
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # Create new policy
                    api.create_namespaced_custom_object(
                        group="policy",
                        version="v1",
                        namespace=namespace,
                        plural=f"{kind.lower()}s",
                        body=policy
                    )
                    logger.info(f"Created {kind}: {name}")
                else:
                    raise
                    
            return {
                'status': 'success',
                'policy': name,
                'type': kind,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Generic policy application failed: {str(e)}")
            raise

    def _process_results(self,
                        results: List[Dict[str, Any]],
                        policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and summarize enforcement results."""
        summary = {
            'total_policies': len(policies),
            'successful': 0,
            'failed': 0,
            'failures': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for result, policy in zip(results, policies):
            if isinstance(result, Exception):
                summary['failed'] += 1
                summary['failures'].append({
                    'policy_name': policy.get('metadata', {}).get('name'),
                    'error': str(result)
                })
            else:
                summary['successful'] += 1
        
        return summary

    async def _scale_resources(self, resources: Dict[str, Any]):
        """Scale cluster resources based on remediation rules."""
        try:
            apps_v1 = client.AppsV1Api()
            for resource in resources:
                kind = resource.get('kind')
                name = resource.get('name')
                namespace = resource.get('namespace')
                replicas = resource.get('replicas')
                
                if kind == 'Deployment':
                    await self._scale_deployment(
                        apps_v1, name, namespace, replicas
                    )
                elif kind == 'StatefulSet':
                    await self._scale_statefulset(
                        apps_v1, name, namespace, replicas
                    )
        except Exception as e:
            logger.error(f"Resource scaling failed: {str(e)}")
            raise

    async def _apply_constraints(self, constraints: Dict[str, Any]):
        """Apply constraint configurations."""
        try:
            for constraint in constraints:
                await self._enforce_single_policy(
                    constraint,
                    constraint.get('metadata', {}).get('namespace', 'default')
                )
        except Exception as e:
            logger.error(f"Constraint application failed: {str(e)}")
            raise

if __name__ == "__main__":
    async def main():
        try:
            scaler = GovernanceScaler('config')
            results = await scaler.enforce_policies('default')
            print("Enforcement results:", results)
            
            # Start violation monitoring
            await scaler.watch_policy_violations()
            
        except Exception as e:
            logger.error(f"Error in main execution: {str(e)}")

    asyncio.run(main())
    