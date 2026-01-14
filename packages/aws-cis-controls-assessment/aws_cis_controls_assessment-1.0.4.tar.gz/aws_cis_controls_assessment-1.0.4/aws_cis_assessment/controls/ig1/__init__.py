"""IG1 Essential Cyber Hygiene Control implementations."""

from .control_1_1 import (
    EIPAttachedAssessment,
    EC2StoppedInstanceAssessment,
    VPCNetworkACLUnusedAssessment,
    EC2InstanceManagedBySSMAssessment,
    EC2SecurityGroupAttachedAssessment
)

from .control_2_2 import (
    ElasticBeanstalkManagedUpdatesEnabledAssessment,
    ECSFargateLatestPlatformVersionAssessment
)

from .control_3_3 import (
    IAMPasswordPolicyAssessment,
    IAMUserMFAEnabledAssessment,
    IAMRootAccessKeyAssessment,
    S3BucketPublicReadProhibitedAssessment,
    EC2InstanceNoPublicIPAssessment
)

from .control_3_4 import (
    S3VersionLifecyclePolicyAssessment,
    CloudWatchLogGroupRetentionAssessment
)

from .control_4_1 import (
    AccountPartOfOrganizationsAssessment,
    EC2VolumeInUseAssessment,
    RedshiftClusterMaintenanceSettingsAssessment,
    SecretsManagerRotationEnabledAssessment
)

from .control_access_keys import (
    AccessKeysRotatedAssessment,
    EC2IMDSv2CheckAssessment,
    EC2InstanceProfileAttachedAssessment
)

from .control_iam_policies import (
    IAMPolicyNoStatementsWithAdminAccessAssessment,
    IAMNoInlinePolicyCheckAssessment,
    IAMUserGroupMembershipCheckAssessment
)

from .control_s3_security import (
    S3BucketSSLRequestsOnlyAssessment,
    S3BucketServerSideEncryptionEnabledAssessment,
    S3BucketLoggingEnabledAssessment,
    S3BucketVersioningEnabledAssessment
)

from .control_data_protection import (
    EBSSnapshotPublicRestorableCheckAssessment,
    RDSSnapshotsPublicProhibitedAssessment,
    RDSInstancePublicAccessCheckAssessment,
    RedshiftClusterPublicAccessCheckAssessment,
    S3BucketLevelPublicAccessProhibitedAssessment
)

from .control_network_security import (
    DMSReplicationNotPublicAssessment,
    ElasticsearchInVPCOnlyAssessment,
    EC2InstancesInVPCAssessment,
    EMRMasterNoPublicIPAssessment,
    LambdaFunctionPublicAccessProhibitedAssessment,
    SageMakerNotebookNoDirectInternetAccessAssessment,
    SubnetAutoAssignPublicIPDisabledAssessment
)

from .control_iam_governance import (
    IAMGroupHasUsersCheckAssessment,
    IAMPolicyNoStatementsWithFullAccessAssessment,
    IAMUserNoPoliciesCheckAssessment,
    SSMDocumentNotPublicAssessment
)

from .control_advanced_security import (
    EC2ManagedInstanceAssociationComplianceStatusCheckAssessment,
    EMRKerberosEnabledAssessment,
    LambdaInsideVPCAssessment,
    ECSTaskDefinitionUserForHostModeCheckAssessment
)

from .control_iam_advanced import (
    IAMRootAccessKeyCheckAssessment,
    IAMUserUnusedCredentialsCheckAssessment,
    IAMCustomerPolicyBlockedKMSActionsAssessment,
    IAMInlinePolicyBlockedKMSActionsAssessment
)

from .control_cloudtrail_logging import (
    CloudTrailEnabledAssessment,
    CloudWatchLogGroupEncryptedAssessment
)

from .control_vpc_security import (
    VPCDefaultSecurityGroupClosedAssessment,
    RestrictedSSHAssessment
)

from .control_critical_security import (
    RootAccountHardwareMFAEnabledAssessment,
    OpenSearchInVPCOnlyAssessment,
    ECSTaskDefinitionNonRootUserAssessment,
    SecurityHubEnabledAssessment
)

from .control_network_enhancements import (
    ElasticsearchNodeToNodeEncryptionCheckAssessment,
    AutoScalingLaunchConfigPublicIPDisabledAssessment,
    EFSAccessPointEnforceRootDirectoryAssessment
)

from .control_backup_recovery import (
    DynamoDBInBackupPlanAssessment,
    EBSInBackupPlanAssessment,
    EFSInBackupPlanAssessment,
    DBInstanceBackupEnabledAssessment,
    RedshiftBackupEnabledAssessment,
    DynamoDBPITREnabledAssessment,
    ElastiCacheRedisClusterAutomaticBackupCheckAssessment,
    S3BucketReplicationEnabledAssessment
)

from .control_s3_enhancements import (
    S3AccountLevelPublicAccessBlocksPeriodicAssessment,
    S3BucketPublicWriteProhibitedAssessment
)

from .control_instance_optimization import (
    EBSOptimizedInstanceAssessment
)

__all__ = [
    # Control 1.1 - Asset Inventory
    'EIPAttachedAssessment',
    'EC2StoppedInstanceAssessment',
    'VPCNetworkACLUnusedAssessment',
    'EC2InstanceManagedBySSMAssessment',
    'EC2SecurityGroupAttachedAssessment',
    
    # Control 2.2 - Authorized Software Support
    'ElasticBeanstalkManagedUpdatesEnabledAssessment',
    'ECSFargateLatestPlatformVersionAssessment',
    
    # Control 3.3 - Data Access Control
    'IAMPasswordPolicyAssessment',
    'IAMUserMFAEnabledAssessment',
    'IAMRootAccessKeyAssessment',
    'S3BucketPublicReadProhibitedAssessment',
    'EC2InstanceNoPublicIPAssessment',
    'EC2IMDSv2CheckAssessment',
    'EC2InstanceProfileAttachedAssessment',
    'IAMPolicyNoStatementsWithAdminAccessAssessment',
    'IAMNoInlinePolicyCheckAssessment',
    'IAMUserGroupMembershipCheckAssessment',
    'EBSSnapshotPublicRestorableCheckAssessment',
    'RDSSnapshotsPublicProhibitedAssessment',
    'RDSInstancePublicAccessCheckAssessment',
    'RedshiftClusterPublicAccessCheckAssessment',
    'S3BucketLevelPublicAccessProhibitedAssessment',
    'DMSReplicationNotPublicAssessment',
    'ElasticsearchInVPCOnlyAssessment',
    'EC2InstancesInVPCAssessment',
    'EMRMasterNoPublicIPAssessment',
    'LambdaFunctionPublicAccessProhibitedAssessment',
    'SageMakerNotebookNoDirectInternetAccessAssessment',
    'SubnetAutoAssignPublicIPDisabledAssessment',
    'IAMGroupHasUsersCheckAssessment',
    'IAMPolicyNoStatementsWithFullAccessAssessment',
    'IAMUserNoPoliciesCheckAssessment',
    'SSMDocumentNotPublicAssessment',
    'EC2ManagedInstanceAssociationComplianceStatusCheckAssessment',
    'EMRKerberosEnabledAssessment',
    'LambdaInsideVPCAssessment',
    'ECSTaskDefinitionUserForHostModeCheckAssessment',
    'IAMRootAccessKeyCheckAssessment',
    'IAMUserUnusedCredentialsCheckAssessment',
    'IAMCustomerPolicyBlockedKMSActionsAssessment',
    'IAMInlinePolicyBlockedKMSActionsAssessment',
    
    # Control 3.4 - Data Retention
    'S3VersionLifecyclePolicyAssessment',
    'CloudWatchLogGroupRetentionAssessment',
    
    # Control 4.1 - Secure Configuration Process
    'AccountPartOfOrganizationsAssessment',
    'EC2VolumeInUseAssessment',
    'RedshiftClusterMaintenanceSettingsAssessment',
    'SecretsManagerRotationEnabledAssessment',
    'AccessKeysRotatedAssessment',
    
    # Control 11.2 - Backup Management
    'S3BucketVersioningEnabledAssessment',
    
    # S3 Security Controls (Phase 5)
    'S3BucketSSLRequestsOnlyAssessment',
    'S3BucketServerSideEncryptionEnabledAssessment',
    'S3BucketLoggingEnabledAssessment',
    
    # CloudTrail & Logging Controls (Phase 6)
    'CloudTrailEnabledAssessment',
    'CloudWatchLogGroupEncryptedAssessment',
    
    # VPC Security Controls (Phase 6)
    'VPCDefaultSecurityGroupClosedAssessment',
    'RestrictedSSHAssessment',
    
    # Critical Security Controls
    'RootAccountHardwareMFAEnabledAssessment',
    'OpenSearchInVPCOnlyAssessment', 
    'ECSTaskDefinitionNonRootUserAssessment',
    'SecurityHubEnabledAssessment',
    
    # Network Security Enhancements
    'ElasticsearchNodeToNodeEncryptionCheckAssessment',
    'AutoScalingLaunchConfigPublicIPDisabledAssessment',
    'EFSAccessPointEnforceRootDirectoryAssessment',
    
    # Backup & Recovery Controls
    'DynamoDBInBackupPlanAssessment',
    'EBSInBackupPlanAssessment',
    'EFSInBackupPlanAssessment',
    'DBInstanceBackupEnabledAssessment',
    'RedshiftBackupEnabledAssessment',
    'DynamoDBPITREnabledAssessment',
    'ElastiCacheRedisClusterAutomaticBackupCheckAssessment',
    'S3BucketReplicationEnabledAssessment',
    
    # S3 Security Enhancements
    'S3AccountLevelPublicAccessBlocksPeriodicAssessment',
    'S3BucketPublicWriteProhibitedAssessment',
    
    # Instance Optimization
    'EBSOptimizedInstanceAssessment'
]