"""Scoring Engine for calculating CIS Controls compliance scores."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from aws_cis_assessment.core.models import (
    ComplianceResult, ComplianceStatus, ControlScore, IGScore, 
    AssessmentResult, ComplianceSummary, RemediationGuidance
)

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Calculate compliance scores based on Config rule evaluation results."""
    
    def __init__(self, control_weights: Optional[Dict[str, float]] = None,
                 ig_weights: Optional[Dict[str, float]] = None):
        """Initialize scoring engine with optional custom weights.
        
        Args:
            control_weights: Optional dictionary mapping control IDs to weights
            ig_weights: Optional dictionary mapping IG names to weights
        """
        # Default control weights based on CIS Controls importance
        self.control_weights = control_weights or {
            '1.1': 1.0,  # Asset Inventory - foundational
            '3.3': 1.5,  # Data Access Control - critical
            '4.1': 1.2,  # Secure Configuration - important
            '5.2': 1.3,  # Password Management - important
            '3.10': 1.4, # Encryption in Transit - critical
            '3.11': 1.4, # Encryption at Rest - critical
            '7.1': 1.1,  # Vulnerability Management - important
            '3.14': 1.2, # Sensitive Data Logging - important
            '12.8': 1.3, # Network Segmentation - important
            '13.1': 1.2, # Network Monitoring - important
        }
        
        # Default IG weights - higher IGs have more weight
        self.ig_weights = ig_weights or {
            'IG1': 1.0,
            'IG2': 1.5,
            'IG3': 2.0
        }
        
        logger.info("ScoringEngine initialized with control and IG weights")
    
    def calculate_control_score(self, control_id: str, rule_results: List[ComplianceResult],
                              control_title: str = "", implementation_group: str = "") -> ControlScore:
        """Calculate compliance score for individual CIS Control.
        
        Args:
            control_id: CIS Control identifier (e.g., '1.1', '3.3')
            rule_results: List of ComplianceResult objects for this control
            control_title: Optional title for the control
            implementation_group: Optional IG designation
            
        Returns:
            ControlScore object with calculated compliance metrics
        """
        if not rule_results:
            return ControlScore(
                control_id=control_id,
                title=control_title or f"CIS Control {control_id}",
                implementation_group=implementation_group,
                total_resources=0,
                compliant_resources=0,
                compliance_percentage=0.0,
                config_rules_evaluated=[],
                findings=[]
            )
        
        # Filter out error results for scoring (but keep them in findings)
        scorable_results = [r for r in rule_results 
                           if r.compliance_status in [ComplianceStatus.COMPLIANT, 
                                                     ComplianceStatus.NON_COMPLIANT,
                                                     ComplianceStatus.NOT_APPLICABLE]]
        
        # Calculate basic metrics
        total_resources = len(scorable_results)
        compliant_resources = sum(1 for r in scorable_results 
                                if r.compliance_status == ComplianceStatus.COMPLIANT)
        
        # Calculate compliance percentage
        if total_resources > 0:
            compliance_percentage = (compliant_resources / total_resources) * 100
        else:
            compliance_percentage = 0.0
        
        # Get unique config rules evaluated
        config_rules_evaluated = list(set(r.config_rule_name for r in rule_results))
        
        # Apply control-specific weighting if needed
        control_weight = self.control_weights.get(control_id, 1.0)
        weighted_compliance = compliance_percentage * control_weight
        
        logger.debug(f"Control {control_id}: {compliant_resources}/{total_resources} "
                    f"({compliance_percentage:.1f}%) compliant, weight: {control_weight}")
        
        return ControlScore(
            control_id=control_id,
            title=control_title or f"CIS Control {control_id}",
            implementation_group=implementation_group,
            total_resources=total_resources,
            compliant_resources=compliant_resources,
            compliance_percentage=compliance_percentage,
            config_rules_evaluated=config_rules_evaluated,
            findings=rule_results
        )
    
    def calculate_ig_score(self, implementation_group: str, 
                          control_scores: Dict[str, ControlScore]) -> IGScore:
        """Calculate Implementation Group compliance score.
        
        Args:
            implementation_group: IG1, IG2, or IG3
            control_scores: Dictionary mapping control IDs to ControlScore objects
            
        Returns:
            IGScore object with calculated IG-level metrics
        """
        if not control_scores:
            return IGScore(
                implementation_group=implementation_group,
                total_controls=0,
                compliant_controls=0,
                compliance_percentage=0.0,
                control_scores={}
            )
        
        total_controls = len(control_scores)
        
        # Calculate weighted average compliance
        total_weighted_score = 0.0
        total_weight = 0.0
        compliant_controls = 0
        
        for control_id, control_score in control_scores.items():
            control_weight = self.control_weights.get(control_id, 1.0)
            total_weighted_score += control_score.compliance_percentage * control_weight
            total_weight += control_weight
            
            # Consider control compliant if >= 80% compliance
            if control_score.compliance_percentage >= 80.0:
                compliant_controls += 1
        
        # Calculate overall IG compliance percentage
        if total_weight > 0:
            ig_compliance_percentage = total_weighted_score / total_weight
        else:
            ig_compliance_percentage = 0.0
        
        logger.info(f"IG {implementation_group}: {compliant_controls}/{total_controls} "
                   f"controls compliant, overall: {ig_compliance_percentage:.1f}%")
        
        return IGScore(
            implementation_group=implementation_group,
            total_controls=total_controls,
            compliant_controls=compliant_controls,
            compliance_percentage=ig_compliance_percentage,
            control_scores=control_scores
        )
    
    def calculate_overall_score(self, ig_scores: Dict[str, IGScore]) -> float:
        """Calculate overall compliance score across all Implementation Groups.
        
        Args:
            ig_scores: Dictionary mapping IG names to IGScore objects
            
        Returns:
            Overall compliance percentage (0-100)
        """
        if not ig_scores:
            return 0.0
        
        # Calculate weighted average across IGs
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for ig_name, ig_score in ig_scores.items():
            ig_weight = self.ig_weights.get(ig_name, 1.0)
            total_weighted_score += ig_score.compliance_percentage * ig_weight
            total_weight += ig_weight
        
        if total_weight > 0:
            overall_score = total_weighted_score / total_weight
        else:
            overall_score = 0.0
        
        logger.info(f"Overall compliance score: {overall_score:.1f}%")
        return overall_score
    
    def generate_compliance_summary(self, assessment_result: AssessmentResult) -> ComplianceSummary:
        """Generate executive summary of compliance status.
        
        Args:
            assessment_result: Complete assessment result
            
        Returns:
            ComplianceSummary with executive-level metrics and recommendations
        """
        # Extract IG-specific compliance percentages
        ig1_compliance = assessment_result.ig_scores.get('IG1', IGScore('IG1', 0, 0, 0.0)).compliance_percentage
        ig2_compliance = assessment_result.ig_scores.get('IG2', IGScore('IG2', 0, 0, 0.0)).compliance_percentage
        ig3_compliance = assessment_result.ig_scores.get('IG3', IGScore('IG3', 0, 0, 0.0)).compliance_percentage
        
        # Identify top risk areas (controls with lowest compliance)
        top_risk_areas = self._identify_risk_areas(assessment_result.ig_scores)
        
        # Generate remediation priorities
        remediation_priorities = self._generate_remediation_priorities(assessment_result.ig_scores)
        
        # Determine compliance trend (would require historical data)
        compliance_trend = self._determine_compliance_trend(assessment_result)
        
        return ComplianceSummary(
            overall_compliance_percentage=assessment_result.overall_score,
            ig1_compliance_percentage=ig1_compliance,
            ig2_compliance_percentage=ig2_compliance,
            ig3_compliance_percentage=ig3_compliance,
            top_risk_areas=top_risk_areas,
            remediation_priorities=remediation_priorities,
            compliance_trend=compliance_trend
        )
    
    def _identify_risk_areas(self, ig_scores: Dict[str, IGScore], 
                           max_risk_areas: int = 5) -> List[str]:
        """Identify top risk areas based on lowest compliance scores.
        
        Args:
            ig_scores: Dictionary of IG scores
            max_risk_areas: Maximum number of risk areas to return
            
        Returns:
            List of risk area descriptions
        """
        risk_areas = []
        
        # Collect all control scores across IGs
        all_control_scores = []
        for ig_score in ig_scores.values():
            for control_id, control_score in ig_score.control_scores.items():
                all_control_scores.append((control_id, control_score))
        
        # Sort by compliance percentage (lowest first)
        all_control_scores.sort(key=lambda x: x[1].compliance_percentage)
        
        # Generate risk area descriptions
        for control_id, control_score in all_control_scores[:max_risk_areas]:
            if control_score.compliance_percentage < 80.0:  # Only include non-compliant controls
                risk_description = f"Control {control_id} ({control_score.title}): " \
                                 f"{control_score.compliance_percentage:.1f}% compliant"
                risk_areas.append(risk_description)
        
        return risk_areas
    
    def _generate_remediation_priorities(self, ig_scores: Dict[str, IGScore],
                                       max_priorities: int = 10) -> List[RemediationGuidance]:
        """Generate prioritized remediation guidance.
        
        Args:
            ig_scores: Dictionary of IG scores
            max_priorities: Maximum number of remediation items to return
            
        Returns:
            List of RemediationGuidance objects prioritized by impact
        """
        remediation_priorities = []
        
        # Collect non-compliant findings across all controls
        non_compliant_findings = []
        for ig_score in ig_scores.values():
            for control_score in ig_score.control_scores.values():
                for finding in control_score.findings:
                    if finding.compliance_status == ComplianceStatus.NON_COMPLIANT:
                        non_compliant_findings.append((control_score, finding))
        
        # Group by config rule and prioritize
        rule_findings = defaultdict(list)
        for control_score, finding in non_compliant_findings:
            rule_findings[finding.config_rule_name].append((control_score, finding))
        
        # Generate remediation guidance for top rules
        for rule_name, findings in list(rule_findings.items())[:max_priorities]:
            control_score, sample_finding = findings[0]
            
            # Determine priority based on control weight and number of affected resources
            control_weight = self.control_weights.get(control_score.control_id, 1.0)
            affected_resources = len(findings)
            
            if control_weight >= 1.4 or affected_resources >= 10:
                priority = "HIGH"
            elif control_weight >= 1.2 or affected_resources >= 5:
                priority = "MEDIUM"
            else:
                priority = "LOW"
            
            # Generate basic remediation steps
            remediation_steps = self._generate_remediation_steps(rule_name)
            
            remediation_guidance = RemediationGuidance(
                config_rule_name=rule_name,
                control_id=control_score.control_id,
                remediation_steps=remediation_steps,
                aws_documentation_link=f"https://docs.aws.amazon.com/config/latest/developerguide/{rule_name}.html",
                priority=priority,
                estimated_effort=self._estimate_remediation_effort(rule_name, affected_resources)
            )
            
            remediation_priorities.append(remediation_guidance)
        
        # Sort by priority (HIGH, MEDIUM, LOW)
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        remediation_priorities.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        return remediation_priorities
    
    def _generate_remediation_steps(self, rule_name: str) -> List[str]:
        """Generate basic remediation steps for a Config rule.
        
        Args:
            rule_name: AWS Config rule name
            
        Returns:
            List of remediation step descriptions
        """
        # Basic remediation steps based on rule patterns
        if 'iam' in rule_name:
            return [
                "Review IAM policies and permissions",
                "Remove unnecessary privileges",
                "Enable MFA where required",
                "Update password policies if applicable"
            ]
        elif 'encrypt' in rule_name:
            return [
                "Enable encryption for the identified resources",
                "Use AWS KMS for key management",
                "Update resource configurations to require encryption",
                "Verify encryption settings are applied"
            ]
        elif 's3' in rule_name:
            return [
                "Review S3 bucket policies and ACLs",
                "Remove public access if not required",
                "Enable appropriate S3 security features",
                "Update bucket configurations"
            ]
        elif 'vpc' in rule_name or 'security-group' in rule_name:
            return [
                "Review network security group rules",
                "Remove overly permissive rules",
                "Implement principle of least privilege",
                "Update VPC configurations as needed"
            ]
        else:
            return [
                f"Review {rule_name} configuration",
                "Apply AWS security best practices",
                "Update resource settings to meet compliance requirements",
                "Verify changes resolve the compliance issue"
            ]
    
    def _estimate_remediation_effort(self, rule_name: str, affected_resources: int) -> str:
        """Estimate effort required for remediation.
        
        Args:
            rule_name: AWS Config rule name
            affected_resources: Number of affected resources
            
        Returns:
            Effort estimate string
        """
        # Base effort on rule complexity and resource count
        if affected_resources <= 5:
            base_effort = "Low"
        elif affected_resources <= 20:
            base_effort = "Medium"
        else:
            base_effort = "High"
        
        # Adjust for rule complexity
        complex_rules = ['iam-password-policy', 'vpc-sg-open-only-to-authorized-ports', 
                        'multi-region-cloudtrail-enabled']
        
        if rule_name in complex_rules:
            if base_effort == "Low":
                base_effort = "Medium"
            elif base_effort == "Medium":
                base_effort = "High"
        
        return base_effort
    
    def _determine_compliance_trend(self, assessment_result: AssessmentResult) -> Optional[str]:
        """Determine compliance trend (requires historical data).
        
        Args:
            assessment_result: Current assessment result
            
        Returns:
            Trend description or None if no historical data available
        """
        # This would require historical assessment data to implement properly
        # For now, return None to indicate no trend data available
        return None
    
    def calculate_resource_count_by_status(self, ig_scores: Dict[str, IGScore]) -> Dict[str, int]:
        """Calculate resource counts by compliance status across all IGs.
        
        Args:
            ig_scores: Dictionary of IG scores
            
        Returns:
            Dictionary mapping status names to resource counts
        """
        status_counts = defaultdict(int)
        
        for ig_score in ig_scores.values():
            for control_score in ig_score.control_scores.values():
                for finding in control_score.findings:
                    status_counts[finding.compliance_status.value] += 1
        
        return dict(status_counts)
    
    def get_control_weights(self) -> Dict[str, float]:
        """Get current control weights.
        
        Returns:
            Dictionary mapping control IDs to weights
        """
        return self.control_weights.copy()
    
    def get_ig_weights(self) -> Dict[str, float]:
        """Get current IG weights.
        
        Returns:
            Dictionary mapping IG names to weights
        """
        return self.ig_weights.copy()
    
    def update_control_weights(self, new_weights: Dict[str, float]):
        """Update control weights.
        
        Args:
            new_weights: Dictionary mapping control IDs to new weights
        """
        self.control_weights.update(new_weights)
        logger.info(f"Updated control weights: {new_weights}")
    
    def update_ig_weights(self, new_weights: Dict[str, float]):
        """Update IG weights.
        
        Args:
            new_weights: Dictionary mapping IG names to new weights
        """
        self.ig_weights.update(new_weights)
        logger.info(f"Updated IG weights: {new_weights}")