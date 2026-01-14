"""
CIS Control 3.3 - Network Security Controls
Critical network security rules to prevent public exposure and ensure proper network isolation.
"""

import logging
from typing import List, Dict, Any, Optional
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

from aws_cis_assessment.controls.base_control import BaseConfigRuleAssessment
from aws_cis_assessment.core.models import ComplianceResult, ComplianceStatus
from aws_cis_assessment.core.aws_client_factory import AWSClientFactory

logger = logging.getLogger(__name__)


class DMSReplicationNotPublicAssessment(BaseConfigRuleAssessment):
    """
    CIS Control 3.3 - Configure Data Access Control Lists
    AWS Config Rule: dms-replication-not-public
    
    Ensures DMS replication instances are not publicly accessible to prevent data exposure.
    """
    
    def __init__(self):
        super().__init__(
            rule_name="dms-replication-not-public",
            control_id="3.3",
            resource_types=["AWS::DMS::ReplicationInstance"]
        )
    
    def _get_resources(self, aws_factory: AWSClientFactory, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Get all DMS replication instances in the region."""
        if resource_type != "AWS::DMS::ReplicationInstance":
            return []
        
        try:
            dms_client = aws_factory.get_client('dms', region)
            
            # Get all DMS replication instances
            paginator = dms_client.get_paginator('describe_replication_instances')
            instances = []
            
            for page in paginator.paginate():
                for instance in page['ReplicationInstances']:
                    instances.append({
                        'ReplicationInstanceIdentifier': instance['ReplicationInstanceIdentifier'],
                        'ReplicationInstanceArn': instance['ReplicationInstanceArn'],
                        'ReplicationInstanceClass': instance.get('ReplicationInstanceClass', ''),
                        'PubliclyAccessible': instance.get('PubliclyAccessible', False),
                        'VpcSecurityGroups': [sg['VpcSecurityGroupId'] for sg in instance.get('VpcSecurityGroups', [])],
                        'ReplicationSubnetGroup': instance.get('ReplicationSubnetGroup', {}).get('ReplicationSubnetGroupIdentifier', ''),
                        'AvailabilityZone': instance.get('AvailabilityZone', ''),
                        'MultiAZ': instance.get('MultiAZ', False)
                    })
            
            logger.debug(f"Found {len(instances)} DMS replication instances in {region}")
            return instances
            
        except ClientError as e:
            logger.error(f"Error retrieving DMS replication instances in {region}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving DMS replication instances in {region}: {e}")
            raise
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], aws_factory: AWSClientFactory, region: str) -> ComplianceResult:
        """Evaluate if DMS replication instance is publicly accessible."""
        instance_id = resource.get('ReplicationInstanceIdentifier', 'unknown')
        is_public = resource.get('PubliclyAccessible', False)
        
        if is_public:
            return ComplianceResult(
                resource_id=instance_id,
                resource_type="AWS::DMS::ReplicationInstance",
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                evaluation_reason="DMS replication instance is publicly accessible",
                config_rule_name=self.rule_name,
                region=region
            )
        else:
            return ComplianceResult(
                resource_id=instance_id,
                resource_type="AWS::DMS::ReplicationInstance",
                compliance_status=ComplianceStatus.COMPLIANT,
                evaluation_reason="DMS replication instance is not publicly accessible",
                config_rule_name=self.rule_name,
                region=region
            )


class ElasticsearchInVPCOnlyAssessment(BaseConfigRuleAssessment):
    """
    CIS Control 3.3 - Configure Data Access Control Lists
    AWS Config Rule: elasticsearch-in-vpc-only
    
    Ensures Elasticsearch domains are deployed within VPC to prevent public access.
    """
    
    def __init__(self):
        super().__init__(
            rule_name="elasticsearch-in-vpc-only",
            control_id="3.3",
            resource_types=["AWS::Elasticsearch::Domain"]
        )
    
    def _get_resources(self, aws_factory: AWSClientFactory, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Get all Elasticsearch domains in the region."""
        if resource_type != "AWS::Elasticsearch::Domain":
            return []
        
        try:
            es_client = aws_factory.get_client('es', region)
            
            # Get all Elasticsearch domains
            response = es_client.list_domain_names()
            domains = []
            
            for domain_info in response.get('DomainNames', []):
                domain_name = domain_info['DomainName']
                
                try:
                    # Get detailed domain configuration
                    domain_response = es_client.describe_elasticsearch_domain(DomainName=domain_name)
                    domain = domain_response['DomainStatus']
                    
                    vpc_options = domain.get('VPCOptions', {})
                    
                    domains.append({
                        'DomainName': domain_name,
                        'DomainArn': domain.get('ARN', ''),
                        'ElasticsearchVersion': domain.get('ElasticsearchVersion', ''),
                        'VPCOptions': vpc_options,
                        'VPCId': vpc_options.get('VPCId', ''),
                        'SubnetIds': vpc_options.get('SubnetIds', []),
                        'SecurityGroupIds': vpc_options.get('SecurityGroupIds', []),
                        'Endpoint': domain.get('Endpoint', ''),
                        'Endpoints': domain.get('Endpoints', {})
                    })
                
                except ClientError as e:
                    logger.warning(f"Error getting details for Elasticsearch domain {domain_name}: {e}")
                    continue
            
            logger.debug(f"Found {len(domains)} Elasticsearch domains in {region}")
            return domains
            
        except ClientError as e:
            logger.error(f"Error retrieving Elasticsearch domains in {region}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving Elasticsearch domains in {region}: {e}")
            raise
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], aws_factory: AWSClientFactory, region: str) -> ComplianceResult:
        """Evaluate if Elasticsearch domain is deployed within VPC."""
        domain_name = resource.get('DomainName', 'unknown')
        vpc_id = resource.get('VPCId', '')
        
        if vpc_id:
            return ComplianceResult(
                resource_id=domain_name,
                resource_type="AWS::Elasticsearch::Domain",
                compliance_status=ComplianceStatus.COMPLIANT,
                evaluation_reason=f"Elasticsearch domain is deployed within VPC {vpc_id}",
                config_rule_name=self.rule_name,
                region=region
            )
        else:
            return ComplianceResult(
                resource_id=domain_name,
                resource_type="AWS::Elasticsearch::Domain",
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                evaluation_reason="Elasticsearch domain is not deployed within VPC",
                config_rule_name=self.rule_name,
                region=region
            )


class EC2InstancesInVPCAssessment(BaseConfigRuleAssessment):
    """
    CIS Control 3.3 - Configure Data Access Control Lists
    AWS Config Rule: ec2-instances-in-vpc
    
    Ensures EC2 instances are deployed within VPC for network security.
    """
    
    def __init__(self):
        super().__init__(
            rule_name="ec2-instances-in-vpc",
            control_id="3.3",
            resource_types=["AWS::EC2::Instance"]
        )
    
    def _get_resources(self, aws_factory: AWSClientFactory, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Get all EC2 instances in the region."""
        if resource_type != "AWS::EC2::Instance":
            return []
        
        try:
            ec2_client = aws_factory.get_client('ec2', region)
            
            # Get all EC2 instances
            paginator = ec2_client.get_paginator('describe_instances')
            instances = []
            
            for page in paginator.paginate():
                for reservation in page['Reservations']:
                    for instance in reservation['Instances']:
                        instances.append({
                            'InstanceId': instance['InstanceId'],
                            'VpcId': instance.get('VpcId', ''),
                            'SubnetId': instance.get('SubnetId', ''),
                            'State': instance.get('State', {}).get('Name', ''),
                            'InstanceType': instance.get('InstanceType', ''),
                            'PublicIpAddress': instance.get('PublicIpAddress', ''),
                            'PrivateIpAddress': instance.get('PrivateIpAddress', '')
                        })
            
            logger.debug(f"Found {len(instances)} EC2 instances in {region}")
            return instances
            
        except ClientError as e:
            logger.error(f"Error retrieving EC2 instances in {region}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving EC2 instances in {region}: {e}")
            raise
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], aws_factory: AWSClientFactory, region: str) -> ComplianceResult:
        """Evaluate if EC2 instance is deployed within VPC."""
        instance_id = resource.get('InstanceId', 'unknown')
        vpc_id = resource.get('VpcId', '')
        state = resource.get('State', '')
        
        # Skip terminated instances
        if state == 'terminated':
            return ComplianceResult(
                resource_id=instance_id,
                resource_type="AWS::EC2::Instance",
                compliance_status=ComplianceStatus.NOT_APPLICABLE,
                evaluation_reason=f"Instance {instance_id} is terminated",
                config_rule_name=self.rule_name,
                region=region
            )
        
        if vpc_id:
            return ComplianceResult(
                resource_id=instance_id,
                resource_type="AWS::EC2::Instance",
                compliance_status=ComplianceStatus.COMPLIANT,
                evaluation_reason=f"EC2 instance is deployed within VPC {vpc_id}",
                config_rule_name=self.rule_name,
                region=region
            )
        else:
            return ComplianceResult(
                resource_id=instance_id,
                resource_type="AWS::EC2::Instance",
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                evaluation_reason="EC2 instance is not deployed within VPC (EC2-Classic)",
                config_rule_name=self.rule_name,
                region=region
            )


class EMRMasterNoPublicIPAssessment(BaseConfigRuleAssessment):
    """
    CIS Control 3.3 - Configure Data Access Control Lists
    AWS Config Rule: emr-master-no-public-ip
    
    Ensures EMR master nodes do not have public IP addresses.
    """
    
    def __init__(self):
        super().__init__(
            rule_name="emr-master-no-public-ip",
            control_id="3.3",
            resource_types=["AWS::EMR::Cluster"]
        )
    
    def _get_resources(self, aws_factory: AWSClientFactory, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Get all EMR clusters in the region."""
        if resource_type != "AWS::EMR::Cluster":
            return []
        
        try:
            emr_client = aws_factory.get_client('emr', region)
            
            # Get all EMR clusters
            paginator = emr_client.get_paginator('list_clusters')
            clusters = []
            
            for page in paginator.paginate():
                for cluster_summary in page['Clusters']:
                    cluster_id = cluster_summary['Id']
                    
                    try:
                        # Get detailed cluster information
                        cluster_response = emr_client.describe_cluster(ClusterId=cluster_id)
                        cluster = cluster_response['Cluster']
                        
                        # Get instance groups to check master node configuration
                        instance_groups_response = emr_client.list_instance_groups(ClusterId=cluster_id)
                        
                        master_public_ip = False
                        for instance_group in instance_groups_response['InstanceGroups']:
                            if instance_group['InstanceGroupType'] == 'MASTER':
                                # Check if master instances have public IPs
                                instances_response = emr_client.list_instances(
                                    ClusterId=cluster_id,
                                    InstanceGroupTypes=['MASTER']
                                )
                                
                                for instance in instances_response['Instances']:
                                    if instance.get('PublicIpAddress'):
                                        master_public_ip = True
                                        break
                                break
                        
                        clusters.append({
                            'ClusterId': cluster_id,
                            'Name': cluster.get('Name', ''),
                            'State': cluster.get('Status', {}).get('State', ''),
                            'MasterPublicDnsName': cluster.get('MasterPublicDnsName', ''),
                            'Ec2InstanceAttributes': cluster.get('Ec2InstanceAttributes', {}),
                            'MasterHasPublicIP': master_public_ip
                        })
                    
                    except ClientError as e:
                        logger.warning(f"Error getting details for EMR cluster {cluster_id}: {e}")
                        continue
            
            logger.debug(f"Found {len(clusters)} EMR clusters in {region}")
            return clusters
            
        except ClientError as e:
            logger.error(f"Error retrieving EMR clusters in {region}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving EMR clusters in {region}: {e}")
            raise
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], aws_factory: AWSClientFactory, region: str) -> ComplianceResult:
        """Evaluate if EMR master node has public IP address."""
        cluster_id = resource.get('ClusterId', 'unknown')
        state = resource.get('State', '')
        master_has_public_ip = resource.get('MasterHasPublicIP', False)
        
        # Skip terminated clusters
        if state in ['TERMINATED', 'TERMINATED_WITH_ERRORS']:
            return ComplianceResult(
                resource_id=cluster_id,
                resource_type="AWS::EMR::Cluster",
                compliance_status=ComplianceStatus.NOT_APPLICABLE,
                evaluation_reason=f"EMR cluster {cluster_id} is terminated",
                config_rule_name=self.rule_name,
                region=region
            )
        
        if master_has_public_ip:
            return ComplianceResult(
                resource_id=cluster_id,
                resource_type="AWS::EMR::Cluster",
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                evaluation_reason="EMR master node has public IP address",
                config_rule_name=self.rule_name,
                region=region
            )
        else:
            return ComplianceResult(
                resource_id=cluster_id,
                resource_type="AWS::EMR::Cluster",
                compliance_status=ComplianceStatus.COMPLIANT,
                evaluation_reason="EMR master node does not have public IP address",
                config_rule_name=self.rule_name,
                region=region
            )


class LambdaFunctionPublicAccessProhibitedAssessment(BaseConfigRuleAssessment):
    """
    CIS Control 3.3 - Configure Data Access Control Lists
    AWS Config Rule: lambda-function-public-access-prohibited
    
    Ensures Lambda functions cannot be publicly accessed.
    """
    
    def __init__(self):
        super().__init__(
            rule_name="lambda-function-public-access-prohibited",
            control_id="3.3",
            resource_types=["AWS::Lambda::Function"]
        )
    
    def _get_resources(self, aws_factory: AWSClientFactory, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Get all Lambda functions in the region."""
        if resource_type != "AWS::Lambda::Function":
            return []
        
        try:
            lambda_client = aws_factory.get_client('lambda', region)
            
            # Get all Lambda functions
            paginator = lambda_client.get_paginator('list_functions')
            functions = []
            
            for page in paginator.paginate():
                for function in page['Functions']:
                    function_name = function['FunctionName']
                    
                    try:
                        # Get function policy to check for public access
                        policy_response = lambda_client.get_policy(FunctionName=function_name)
                        policy_doc = json.loads(policy_response['Policy'])
                        
                        has_public_access = False
                        public_statements = []
                        
                        for statement in policy_doc.get('Statement', []):
                            if isinstance(statement, dict):
                                effect = statement.get('Effect', '')
                                principal = statement.get('Principal', {})
                                
                                if effect == 'Allow':
                                    if principal == '*' or (isinstance(principal, dict) and principal.get('AWS') == '*'):
                                        has_public_access = True
                                        public_statements.append(statement)
                        
                        functions.append({
                            'FunctionName': function_name,
                            'FunctionArn': function['FunctionArn'],
                            'Runtime': function.get('Runtime', ''),
                            'VpcConfig': function.get('VpcConfig', {}),
                            'HasPublicAccess': has_public_access,
                            'PublicStatements': public_statements
                        })
                    
                    except ClientError as e:
                        if e.response.get('Error', {}).get('Code') == 'ResourceNotFoundException':
                            # Function has no policy, so no public access
                            functions.append({
                                'FunctionName': function_name,
                                'FunctionArn': function['FunctionArn'],
                                'Runtime': function.get('Runtime', ''),
                                'VpcConfig': function.get('VpcConfig', {}),
                                'HasPublicAccess': False,
                                'PublicStatements': []
                            })
                        else:
                            logger.warning(f"Error getting policy for Lambda function {function_name}: {e}")
                            continue
            
            logger.debug(f"Found {len(functions)} Lambda functions in {region}")
            return functions
            
        except ClientError as e:
            logger.error(f"Error retrieving Lambda functions in {region}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving Lambda functions in {region}: {e}")
            raise
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], aws_factory: AWSClientFactory, region: str) -> ComplianceResult:
        """Evaluate if Lambda function has public access."""
        function_name = resource.get('FunctionName', 'unknown')
        has_public_access = resource.get('HasPublicAccess', False)
        
        if has_public_access:
            return ComplianceResult(
                resource_id=function_name,
                resource_type="AWS::Lambda::Function",
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                evaluation_reason="Lambda function allows public access",
                config_rule_name=self.rule_name,
                region=region
            )
        else:
            return ComplianceResult(
                resource_id=function_name,
                resource_type="AWS::Lambda::Function",
                compliance_status=ComplianceStatus.COMPLIANT,
                evaluation_reason="Lambda function does not allow public access",
                config_rule_name=self.rule_name,
                region=region
            )


class SageMakerNotebookNoDirectInternetAccessAssessment(BaseConfigRuleAssessment):
    """
    CIS Control 3.3 - Configure Data Access Control Lists
    AWS Config Rule: sagemaker-notebook-no-direct-internet-access
    
    Ensures SageMaker notebooks do not have direct internet access.
    """
    
    def __init__(self):
        super().__init__(
            rule_name="sagemaker-notebook-no-direct-internet-access",
            control_id="3.3",
            resource_types=["AWS::SageMaker::NotebookInstance"]
        )
    
    def _get_resources(self, aws_factory: AWSClientFactory, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Get all SageMaker notebook instances in the region."""
        if resource_type != "AWS::SageMaker::NotebookInstance":
            return []
        
        try:
            sagemaker_client = aws_factory.get_client('sagemaker', region)
            
            # Get all SageMaker notebook instances
            paginator = sagemaker_client.get_paginator('list_notebook_instances')
            notebooks = []
            
            for page in paginator.paginate():
                for notebook_summary in page['NotebookInstances']:
                    notebook_name = notebook_summary['NotebookInstanceName']
                    
                    try:
                        # Get detailed notebook instance information
                        notebook_response = sagemaker_client.describe_notebook_instance(
                            NotebookInstanceName=notebook_name
                        )
                        
                        notebooks.append({
                            'NotebookInstanceName': notebook_name,
                            'NotebookInstanceArn': notebook_response['NotebookInstanceArn'],
                            'NotebookInstanceStatus': notebook_response['NotebookInstanceStatus'],
                            'InstanceType': notebook_response['InstanceType'],
                            'SubnetId': notebook_response.get('SubnetId', ''),
                            'SecurityGroups': notebook_response.get('SecurityGroups', []),
                            'DirectInternetAccess': notebook_response.get('DirectInternetAccess', 'Enabled')
                        })
                    
                    except ClientError as e:
                        logger.warning(f"Error getting details for SageMaker notebook {notebook_name}: {e}")
                        continue
            
            logger.debug(f"Found {len(notebooks)} SageMaker notebook instances in {region}")
            return notebooks
            
        except ClientError as e:
            logger.error(f"Error retrieving SageMaker notebook instances in {region}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving SageMaker notebook instances in {region}: {e}")
            raise
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], aws_factory: AWSClientFactory, region: str) -> ComplianceResult:
        """Evaluate if SageMaker notebook has direct internet access."""
        notebook_name = resource.get('NotebookInstanceName', 'unknown')
        status = resource.get('NotebookInstanceStatus', '')
        direct_internet_access = resource.get('DirectInternetAccess', 'Enabled')
        
        # Skip deleted notebooks
        if status == 'Deleting':
            return ComplianceResult(
                resource_id=notebook_name,
                resource_type="AWS::SageMaker::NotebookInstance",
                compliance_status=ComplianceStatus.NOT_APPLICABLE,
                evaluation_reason=f"SageMaker notebook {notebook_name} is being deleted",
                config_rule_name=self.rule_name,
                region=region
            )
        
        if direct_internet_access == 'Enabled':
            return ComplianceResult(
                resource_id=notebook_name,
                resource_type="AWS::SageMaker::NotebookInstance",
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                evaluation_reason="SageMaker notebook has direct internet access enabled",
                config_rule_name=self.rule_name,
                region=region
            )
        else:
            return ComplianceResult(
                resource_id=notebook_name,
                resource_type="AWS::SageMaker::NotebookInstance",
                compliance_status=ComplianceStatus.COMPLIANT,
                evaluation_reason="SageMaker notebook does not have direct internet access",
                config_rule_name=self.rule_name,
                region=region
            )


class SubnetAutoAssignPublicIPDisabledAssessment(BaseConfigRuleAssessment):
    """
    CIS Control 3.3 - Configure Data Access Control Lists
    AWS Config Rule: subnet-auto-assign-public-ip-disabled
    
    Ensures subnets do not automatically assign public IPs to prevent accidental exposure.
    """
    
    def __init__(self):
        super().__init__(
            rule_name="subnet-auto-assign-public-ip-disabled",
            control_id="3.3",
            resource_types=["AWS::EC2::Subnet"]
        )
    
    def _get_resources(self, aws_factory: AWSClientFactory, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Get all subnets in the region."""
        if resource_type != "AWS::EC2::Subnet":
            return []
        
        try:
            ec2_client = aws_factory.get_client('ec2', region)
            
            # Get all subnets
            paginator = ec2_client.get_paginator('describe_subnets')
            subnets = []
            
            for page in paginator.paginate():
                for subnet in page['Subnets']:
                    subnets.append({
                        'SubnetId': subnet['SubnetId'],
                        'VpcId': subnet['VpcId'],
                        'AvailabilityZone': subnet['AvailabilityZone'],
                        'CidrBlock': subnet['CidrBlock'],
                        'MapPublicIpOnLaunch': subnet.get('MapPublicIpOnLaunch', False),
                        'State': subnet.get('State', ''),
                        'Tags': subnet.get('Tags', [])
                    })
            
            logger.debug(f"Found {len(subnets)} subnets in {region}")
            return subnets
            
        except ClientError as e:
            logger.error(f"Error retrieving subnets in {region}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving subnets in {region}: {e}")
            raise
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], aws_factory: AWSClientFactory, region: str) -> ComplianceResult:
        """Evaluate if subnet auto-assigns public IPs."""
        subnet_id = resource.get('SubnetId', 'unknown')
        map_public_ip = resource.get('MapPublicIpOnLaunch', False)
        state = resource.get('State', '')
        
        # Skip subnets that are not available
        if state != 'available':
            return ComplianceResult(
                resource_id=subnet_id,
                resource_type="AWS::EC2::Subnet",
                compliance_status=ComplianceStatus.NOT_APPLICABLE,
                evaluation_reason=f"Subnet {subnet_id} is in state '{state}'",
                config_rule_name=self.rule_name,
                region=region
            )
        
        if map_public_ip:
            return ComplianceResult(
                resource_id=subnet_id,
                resource_type="AWS::EC2::Subnet",
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                evaluation_reason="Subnet automatically assigns public IP addresses",
                config_rule_name=self.rule_name,
                region=region
            )
        else:
            return ComplianceResult(
                resource_id=subnet_id,
                resource_type="AWS::EC2::Subnet",
                compliance_status=ComplianceStatus.COMPLIANT,
                evaluation_reason="Subnet does not automatically assign public IP addresses",
                config_rule_name=self.rule_name,
                region=region
            )