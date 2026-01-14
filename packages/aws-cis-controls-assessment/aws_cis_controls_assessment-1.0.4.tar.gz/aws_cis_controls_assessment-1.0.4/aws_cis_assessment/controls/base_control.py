"""Base class for AWS Config rule-based CIS Control assessments."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from botocore.exceptions import ClientError

from aws_cis_assessment.core.models import (
    ComplianceResult, ComplianceStatus, RemediationGuidance, ConfigRule
)
from aws_cis_assessment.core.aws_client_factory import AWSClientFactory
from aws_cis_assessment.core.error_handler import ErrorHandler, ErrorContext, ErrorCategory

logger = logging.getLogger(__name__)


class BaseConfigRuleAssessment(ABC):
    """Abstract base class for all AWS Config rule implementations."""
    
    def __init__(self, rule_name: str, control_id: str, resource_types: List[str], 
                 parameters: Optional[Dict[str, Any]] = None,
                 error_handler: Optional[ErrorHandler] = None):
        """Initialize Config rule assessment with rule specification.
        
        Args:
            rule_name: AWS Config rule name
            control_id: CIS Control ID (e.g., "1.1", "3.3")
            resource_types: List of AWS resource types to evaluate
            parameters: Optional parameters for rule evaluation
            error_handler: Optional error handler for graceful degradation
        """
        self.rule_name = rule_name
        self.control_id = control_id
        self.resource_types = resource_types
        self.parameters = parameters or {}
        self.error_handler = error_handler
        
        # Validate inputs
        if not rule_name:
            raise ValueError("Rule name cannot be empty")
        if not control_id:
            raise ValueError("Control ID cannot be empty")
        if not resource_types:
            raise ValueError("Must specify at least one resource type")
    
    def evaluate_compliance(self, aws_factory: AWSClientFactory, region: str = 'us-east-1') -> List[ComplianceResult]:
        """Evaluate compliance for all applicable resources.
        
        Args:
            aws_factory: AWS client factory for API access
            region: AWS region to evaluate
            
        Returns:
            List of ComplianceResult objects for all evaluated resources
        """
        results = []
        
        try:
            # Validate that we can access required services
            if not self._validate_service_access(aws_factory, region):
                return [self._create_error_result(
                    "SERVICE_UNAVAILABLE",
                    f"Required AWS services not accessible in region {region}",
                    region
                )]
            
            # Evaluate each resource type
            for resource_type in self.resource_types:
                try:
                    # Use error handler for resource discovery if available
                    def get_resources():
                        return self._get_resources(aws_factory, resource_type, region)
                    
                    if self.error_handler:
                        context = ErrorContext(
                            service_name=self._get_required_services()[0] if self._get_required_services() else "",
                            region=region,
                            resource_type=resource_type,
                            operation="get_resources",
                            control_id=self.control_id,
                            config_rule_name=self.rule_name
                        )
                        
                        resources = self.error_handler.handle_error(
                            Exception("Resource discovery"), context, get_resources
                        )
                        
                        if resources is None:
                            resources = get_resources()
                    else:
                        resources = get_resources()
                    
                    logger.debug(f"Found {len(resources)} resources of type {resource_type} in {region}")
                    
                    for resource in resources:
                        try:
                            # Use error handler for resource evaluation if available
                            def evaluate_resource():
                                return self._evaluate_resource_compliance(resource, aws_factory, region)
                            
                            if self.error_handler:
                                context = ErrorContext(
                                    service_name=self._get_required_services()[0] if self._get_required_services() else "",
                                    region=region,
                                    resource_type=resource_type,
                                    resource_id=resource.get('id', 'unknown'),
                                    operation="evaluate_compliance",
                                    control_id=self.control_id,
                                    config_rule_name=self.rule_name
                                )
                                
                                compliance = self.error_handler.handle_error(
                                    Exception("Resource evaluation"), context, evaluate_resource
                                )
                                
                                if compliance is None:
                                    compliance = evaluate_resource()
                            else:
                                compliance = evaluate_resource()
                            
                            results.append(compliance)
                            
                        except Exception as e:
                            logger.error(f"Error evaluating resource {resource.get('id', 'unknown')}: {e}")
                            
                            # Handle error with error handler if available
                            if self.error_handler:
                                context = ErrorContext(
                                    service_name=self._get_required_services()[0] if self._get_required_services() else "",
                                    region=region,
                                    resource_type=resource_type,
                                    resource_id=resource.get('id', 'unknown'),
                                    operation="evaluate_compliance",
                                    control_id=self.control_id,
                                    config_rule_name=self.rule_name
                                )
                                self.error_handler.handle_error(e, context)
                            
                            results.append(self._create_error_result(
                                resource.get('id', 'unknown'),
                                f"Evaluation error: {str(e)}",
                                region,
                                resource_type
                            ))
                
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    error_message = f"AWS API error: {str(e)}"
                    
                    # Handle error with error handler if available
                    if self.error_handler:
                        context = ErrorContext(
                            service_name=self._get_required_services()[0] if self._get_required_services() else "",
                            region=region,
                            resource_type=resource_type,
                            operation="get_resources",
                            control_id=self.control_id,
                            config_rule_name=self.rule_name
                        )
                        self.error_handler.handle_error(e, context)
                    
                    if error_code in ['AccessDenied', 'UnauthorizedOperation']:
                        results.append(self._create_error_result(
                            f"{resource_type}_PERMISSION_ERROR",
                            f"Insufficient permissions to evaluate {resource_type}",
                            region,
                            resource_type
                        ))
                    else:
                        results.append(self._create_error_result(
                            f"{resource_type}_API_ERROR",
                            error_message,
                            region,
                            resource_type
                        ))
                
                except Exception as e:
                    logger.error(f"Unexpected error evaluating {resource_type}: {e}")
                    
                    # Handle error with error handler if available
                    if self.error_handler:
                        context = ErrorContext(
                            service_name=self._get_required_services()[0] if self._get_required_services() else "",
                            region=region,
                            resource_type=resource_type,
                            operation="evaluate_resource_type",
                            control_id=self.control_id,
                            config_rule_name=self.rule_name
                        )
                        self.error_handler.handle_error(e, context)
                    
                    results.append(self._create_error_result(
                        f"{resource_type}_UNKNOWN_ERROR",
                        f"Unexpected error: {str(e)}",
                        region,
                        resource_type
                    ))
        
        except Exception as e:
            logger.error(f"Critical error in compliance evaluation: {e}")
            
            # Handle critical error with error handler if available
            if self.error_handler:
                context = ErrorContext(
                    service_name=self._get_required_services()[0] if self._get_required_services() else "",
                    region=region,
                    operation="evaluate_compliance",
                    control_id=self.control_id,
                    config_rule_name=self.rule_name
                )
                self.error_handler.handle_error(e, context)
            
            results.append(self._create_error_result(
                "CRITICAL_ERROR",
                f"Critical evaluation error: {str(e)}",
                region
            ))
        
        return results
    
    @abstractmethod
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], aws_factory: AWSClientFactory, region: str) -> ComplianceResult:
        """Evaluate compliance for individual resource.
        
        This method must be implemented by subclasses with specific Config rule logic.
        
        Args:
            resource: Resource data dictionary
            aws_factory: AWS client factory for additional API calls
            region: AWS region
            
        Returns:
            ComplianceResult for the resource
        """
        pass
    
    @abstractmethod
    def _get_resources(self, aws_factory: AWSClientFactory, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Discover resources of specified type in region.
        
        This method must be implemented by subclasses based on resource type.
        
        Args:
            aws_factory: AWS client factory for API access
            resource_type: AWS resource type (e.g., "AWS::EC2::Instance")
            region: AWS region
            
        Returns:
            List of resource dictionaries
        """
        pass
    
    def _validate_service_access(self, aws_factory: AWSClientFactory, region: str) -> bool:
        """Validate that required AWS services are accessible.
        
        Args:
            aws_factory: AWS client factory
            region: AWS region
            
        Returns:
            True if all required services are accessible
        """
        required_services = self._get_required_services()
        
        for service in required_services:
            if not aws_factory.test_service_access(service, region):
                logger.debug(f"Service {service} not accessible in region {region}")
                return False
        
        return True
    
    def _get_required_services(self) -> List[str]:
        """Get list of AWS services required for this assessment.
        
        Returns:
            List of AWS service names
        """
        # Map resource types to services
        service_mapping = {
            'AWS::EC2::': 'ec2',
            'AWS::IAM::': 'iam',
            'AWS::S3::': 's3',
            'AWS::RDS::': 'rds',
            'AWS::CloudTrail::': 'cloudtrail',
            'AWS::ElasticLoadBalancing::': 'elbv2',  # Classic ELB uses elbv2 client in boto3
            'AWS::ElasticLoadBalancingV2::': 'elbv2',  # ALB/NLB use elbv2 client
            'AWS::ApiGateway::': 'apigateway',
            'AWS::DynamoDB::': 'dynamodb',
            'AWS::::Account': 'sts'  # Special case for account-level resources
        }
        
        services = set()
        for resource_type in self.resource_types:
            for prefix, service in service_mapping.items():
                if resource_type.startswith(prefix):
                    services.add(service)
                    break
        
        return list(services)
    
    def _create_error_result(self, resource_id: str, error_message: str, region: str, resource_type: str = "Unknown") -> ComplianceResult:
        """Create a ComplianceResult for error conditions.
        
        Args:
            resource_id: Resource identifier
            error_message: Error description
            region: AWS region
            resource_type: AWS resource type
            
        Returns:
            ComplianceResult with ERROR status
        """
        return ComplianceResult(
            resource_id=resource_id,
            resource_type=resource_type,
            compliance_status=ComplianceStatus.ERROR,
            evaluation_reason=error_message,
            config_rule_name=self.rule_name,
            region=region
        )
    
    def get_remediation_guidance(self, non_compliant_resources: List[ComplianceResult]) -> RemediationGuidance:
        """Provide remediation guidance based on AWS Config rule documentation.
        
        Args:
            non_compliant_resources: List of non-compliant resources
            
        Returns:
            RemediationGuidance object with specific steps
        """
        return RemediationGuidance(
            config_rule_name=self.rule_name,
            control_id=self.control_id,
            remediation_steps=self._get_rule_remediation_steps(),
            aws_documentation_link=f"https://docs.aws.amazon.com/config/latest/developerguide/{self.rule_name}.html",
            priority=self._determine_priority(non_compliant_resources),
            estimated_effort=self._estimate_remediation_effort(non_compliant_resources)
        )
    
    def _get_rule_remediation_steps(self) -> List[str]:
        """Get remediation steps for this Config rule.
        
        Override in subclasses for rule-specific guidance.
        
        Returns:
            List of remediation step descriptions
        """
        return [
            f"Review non-compliant resources identified by {self.rule_name}",
            f"Apply remediation actions according to CIS Control {self.control_id}",
            "Verify compliance after remediation",
            "Monitor for future compliance drift"
        ]
    
    def _determine_priority(self, non_compliant_resources: List[ComplianceResult]) -> str:
        """Determine remediation priority based on non-compliant resources.
        
        Args:
            non_compliant_resources: List of non-compliant resources
            
        Returns:
            Priority level: HIGH, MEDIUM, or LOW
        """
        if not non_compliant_resources:
            return "LOW"
        
        # High priority for security-critical controls
        high_priority_controls = ["3.3", "5.2", "6.4", "8.1"]
        if self.control_id in high_priority_controls:
            return "HIGH"
        
        # Medium priority for most controls
        if len(non_compliant_resources) > 5:
            return "HIGH"
        elif len(non_compliant_resources) > 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_remediation_effort(self, non_compliant_resources: List[ComplianceResult]) -> str:
        """Estimate effort required for remediation.
        
        Args:
            non_compliant_resources: List of non-compliant resources
            
        Returns:
            Effort estimate: Low, Medium, High, or Very High
        """
        resource_count = len(non_compliant_resources)
        
        if resource_count == 0:
            return "None"
        elif resource_count <= 5:
            return "Low"
        elif resource_count <= 20:
            return "Medium"
        elif resource_count <= 50:
            return "High"
        else:
            return "Very High"