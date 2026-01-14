"""IG2 Enhanced Security Controls."""

from .control_3_10 import (
    APIGatewaySSLEnabledAssessment,
    ALBHTTPToHTTPSRedirectionAssessment,
    ELBTLSHTTPSListenersOnlyAssessment,
    S3BucketSSLRequestsOnlyAssessment,
    RedshiftRequireTLSSSLAssessment
)
from .control_3_11 import (
    EncryptedVolumesAssessment,
    RDSStorageEncryptedAssessment,
    S3DefaultEncryptionKMSAssessment,
    DynamoDBTableEncryptedKMSAssessment,
    BackupRecoveryPointEncryptedAssessment,
    EFSEncryptedCheckAssessment,
    SecretsManagerUsingKMSKeyAssessment,
    SNSTopicEncryptedKMSAssessment,
    SQSQueueEncryptedKMSAssessment,
    CloudWatchLogsEncryptedAssessment,
    KinesisStreamEncryptedAssessment,
    ElasticSearchDomainEncryptedAssessment
)
from .control_5_2 import (
    MFAEnabledForIAMConsoleAccessAssessment,
    RootAccountMFAEnabledAssessment,
    IAMUserUnusedCredentialsAssessment
)
from .control_encryption_transit import (
    ELBACMCertificateRequiredAssessment,
    ELBv2ACMCertificateRequiredAssessment,
    OpenSearchHTTPSRequiredAssessment
)
from .control_encryption_rest import (
    CloudTrailEncryptionEnabledAssessment,
    EFSEncryptedCheckAssessment as EFSEncryptedCheckIG2Assessment,
    EC2EBSEncryptionByDefaultAssessment,
    RDSSnapshotEncryptedAssessment
)

from .control_advanced_encryption import (
    SecretsManagerUsingCMKAssessment,
    SNSEncryptedKMSAssessment,
    SQSQueueEncryptedKMSAssessment,
    KinesisStreamEncryptedAssessment,
    ElasticsearchEncryptedAtRestAssessment
)

from .control_service_logging import (
    ElasticsearchLogsToCloudWatchAssessment,
    ELBLoggingEnabledAssessment,
    RDSLoggingEnabledAssessment,
    WAFv2LoggingEnabledAssessment,
    CodeBuildProjectLoggingEnabledAssessment,
    RedshiftClusterConfigurationCheckAssessment
)

# Import remaining encryption controls
from .control_remaining_encryption import (
    OpenSearchEncryptedAtRestAssessment,
    OpenSearchNodeToNodeEncryptionCheckAssessment,
    RedshiftClusterKMSEnabledAssessment,
    SageMakerEndpointConfigurationKMSKeyConfiguredAssessment,
    SageMakerNotebookInstanceKMSKeyConfiguredAssessment,
    CodeBuildProjectArtifactEncryptionAssessment
)

# Import network/HA controls
from .control_network_ha import (
    ELBCrossZoneLoadBalancingEnabledAssessment,
    ELBDeletionProtectionEnabledAssessment,
    ELBv2MultipleAZAssessment,
    RDSClusterMultiAZEnabledAssessment,
    RDSInstanceDeletionProtectionEnabledAssessment,
    RDSMultiAZSupportAssessment,
    VPCVPNTwoTunnelsUpAssessment
)

# Import CodeBuild security controls
from .control_codebuild_security import (
    CodeBuildProjectEnvironmentPrivilegedCheckAssessment,
    CodeBuildProjectEnvVarAWSCredCheckAssessment,
    CodeBuildProjectSourceRepoURLCheckAssessment
)

# Import remaining rules
from .control_remaining_rules import (
    ACMCertificateExpirationCheckAssessment,
    DynamoDBAutoScalingEnabledAssessment,
    RedshiftEnhancedVPCRoutingEnabledAssessment,
    RestrictedCommonPortsAssessment,
    AuditLogPolicyExistsAssessment
)

__all__ = [
    # Control 3.10 - Encrypt Sensitive Data in Transit
    'APIGatewaySSLEnabledAssessment',
    'ALBHTTPToHTTPSRedirectionAssessment',
    'ELBTLSHTTPSListenersOnlyAssessment',
    'S3BucketSSLRequestsOnlyAssessment',
    'RedshiftRequireTLSSSLAssessment',
    'ELBACMCertificateRequiredAssessment',
    'ELBv2ACMCertificateRequiredAssessment',
    'OpenSearchHTTPSRequiredAssessment',
    
    # Control 3.11 - Encrypt Sensitive Data at Rest
    'EncryptedVolumesAssessment',
    'RDSStorageEncryptedAssessment',
    'S3DefaultEncryptionKMSAssessment',
    'DynamoDBTableEncryptedKMSAssessment',
    'BackupRecoveryPointEncryptedAssessment',
    'EFSEncryptedCheckAssessment',
    'SecretsManagerUsingKMSKeyAssessment',
    'SNSTopicEncryptedKMSAssessment',
    'SQSQueueEncryptedKMSAssessment',
    'CloudWatchLogsEncryptedAssessment',
    'KinesisStreamEncryptedAssessment',
    'ElasticSearchDomainEncryptedAssessment',
    'CloudTrailEncryptionEnabledAssessment',
    'EFSEncryptedCheckIG2Assessment',
    'EC2EBSEncryptionByDefaultAssessment',
    'RDSSnapshotEncryptedAssessment',
    
    # Advanced Encryption Controls
    'SecretsManagerUsingCMKAssessment',
    'SNSEncryptedKMSAssessment',
    'SQSQueueEncryptedKMSAssessment',
    'KinesisStreamEncryptedAssessment',
    'ElasticsearchEncryptedAtRestAssessment',
    
    # Service Logging Controls
    'ElasticsearchLogsToCloudWatchAssessment',
    'ELBLoggingEnabledAssessment',
    'RDSLoggingEnabledAssessment',
    'WAFv2LoggingEnabledAssessment',
    'CodeBuildProjectLoggingEnabledAssessment',
    'RedshiftClusterConfigurationCheckAssessment',
    
    # Remaining Encryption Controls
    'OpenSearchEncryptedAtRestAssessment',
    'OpenSearchNodeToNodeEncryptionCheckAssessment',
    'RedshiftClusterKMSEnabledAssessment',
    'SageMakerEndpointConfigurationKMSKeyConfiguredAssessment',
    'SageMakerNotebookInstanceKMSKeyConfiguredAssessment',
    'CodeBuildProjectArtifactEncryptionAssessment',
    
    # Network/HA Controls
    'ELBCrossZoneLoadBalancingEnabledAssessment',
    'ELBDeletionProtectionEnabledAssessment',
    'ELBv2MultipleAZAssessment',
    'RDSClusterMultiAZEnabledAssessment',
    'RDSInstanceDeletionProtectionEnabledAssessment',
    'RDSMultiAZSupportAssessment',
    'VPCVPNTwoTunnelsUpAssessment',
    
    # CodeBuild Security Controls
    'CodeBuildProjectEnvironmentPrivilegedCheckAssessment',
    'CodeBuildProjectEnvVarAWSCredCheckAssessment',
    'CodeBuildProjectSourceRepoURLCheckAssessment',
    
    # Remaining Rules
    'ACMCertificateExpirationCheckAssessment',
    'DynamoDBAutoScalingEnabledAssessment',
    'RedshiftEnhancedVPCRoutingEnabledAssessment',
    'RestrictedCommonPortsAssessment',
    'AuditLogPolicyExistsAssessment',
    
    # Control 5.2 - Use Unique Passwords
    'MFAEnabledForIAMConsoleAccessAssessment',
    'RootAccountMFAEnabledAssessment',
    'IAMUserUnusedCredentialsAssessment'
]