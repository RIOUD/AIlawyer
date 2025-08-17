#!/usr/bin/env python3
"""
Intelligent Document Workflow Automation

AI-powered document workflow system that manages the complete document lifecycle,
from generation to finalization, with intelligent analysis and optimization.

Features:
- Automated document generation from templates
- AI-powered document review and risk analysis
- Client feedback tracking and integration
- Document version control and collaboration
- Automated workflow progression and notifications
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class DocumentWorkflow:
    """Data class for document workflow."""
    workflow_id: str
    document_type: str
    client_data: Dict[str, Any]
    status: str  # draft, review, client_review, finalize, completed
    current_step: int
    total_steps: int
    created_at: datetime
    updated_at: datetime
    lawyer_id: str
    client_id: str
    estimated_completion: Optional[datetime]
    priority: str  # high, medium, low


@dataclass
class DocumentStep:
    """Data class for document workflow steps."""
    step_id: str
    workflow_id: str
    step_number: int
    step_type: str  # generate_draft, ai_review, client_review, finalize
    status: str  # pending, in_progress, completed, failed
    description: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    output: Optional[Dict[str, Any]]
    ai_analysis: Optional[Dict[str, Any]]


@dataclass
class DocumentTemplate:
    """Data class for document templates."""
    template_id: str
    document_type: str
    template_name: str
    template_content: str
    variables: List[str]
    version: str
    created_at: datetime
    updated_at: datetime
    is_active: bool


class DocumentWorkflowAI:
    """
    AI-powered document workflow automation system.
    
    Manages complete document lifecycle from generation to finalization,
    with intelligent analysis, risk assessment, and workflow optimization.
    """
    
    def __init__(self):
        """Initialize the document workflow AI system."""
        self.document_types = {
            "employment_contract": {
                "template": "employment_contract_v2",
                "estimated_duration": "2-3 days",
                "required_variables": ["employee_name", "position", "salary", "start_date"],
                "ai_review_enabled": True,
                "client_review_required": True
            },
            "non_disclosure_agreement": {
                "template": "nda_standard",
                "estimated_duration": "1-2 days",
                "required_variables": ["company_name", "recipient_name", "confidential_info"],
                "ai_review_enabled": True,
                "client_review_required": False
            },
            "service_agreement": {
                "template": "service_agreement_v1",
                "estimated_duration": "3-5 days",
                "required_variables": ["service_provider", "client_name", "services", "payment_terms"],
                "ai_review_enabled": True,
                "client_review_required": True
            },
            "settlement_agreement": {
                "template": "settlement_agreement",
                "estimated_duration": "1-3 days",
                "required_variables": ["parties", "settlement_amount", "release_terms"],
                "ai_review_enabled": True,
                "client_review_required": True
            }
        }
        
        # In-memory storage (replace with database in production)
        self.workflows = []
        self.steps = []
        self.templates = []
        
        # Initialize default templates
        self._initialize_templates()
        
        logger.info("Document Workflow AI initialized")
    
    def auto_document_pipeline(self, document_type: str, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically handle complete document workflow.
        
        Args:
            document_type: Type of document to create
            client_data: Client information for document generation
            
        Returns:
            Complete document workflow status
        """
        try:
            # Validate document type
            if document_type not in self.document_types:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Generate workflow ID
            workflow_id = self._generate_workflow_id()
            
            # Create workflow
            workflow = DocumentWorkflow(
                workflow_id=workflow_id,
                document_type=document_type,
                client_data=client_data,
                status="draft",
                current_step=1,
                total_steps=self._get_total_steps(document_type),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                lawyer_id=client_data.get("lawyer_id"),
                client_id=client_data.get("client_id"),
                estimated_completion=self._calculate_estimated_completion(document_type),
                priority=client_data.get("priority", "medium")
            )
            
            # Store workflow
            self.workflows.append(workflow)
            
            # Initialize workflow steps
            self._initialize_workflow_steps(workflow)
            
            # Start first step
            self._execute_step(workflow_id, 1)
            
            # Get workflow status
            workflow_status = self._get_workflow_status(workflow_id)
            
            logger.info(f"Document workflow started: {document_type} ({workflow_id})")
            return workflow_status
            
        except Exception as e:
            logger.error(f"Error in document workflow: {e}")
            raise
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow identifier."""
        import uuid
        return f"WORKFLOW-{str(uuid.uuid4())[:8].upper()}"
    
    def _get_total_steps(self, document_type: str) -> int:
        """Get total number of steps for document type."""
        config = self.document_types[document_type]
        total_steps = 1  # generate_draft
        
        if config["ai_review_enabled"]:
            total_steps += 1  # ai_review
        
        if config["client_review_required"]:
            total_steps += 1  # client_review
        
        total_steps += 1  # finalize
        
        return total_steps
    
    def _calculate_estimated_completion(self, document_type: str) -> datetime:
        """Calculate estimated completion date."""
        config = self.document_types[document_type]
        duration_str = config["estimated_duration"]
        
        # Parse duration (e.g., "2-3 days")
        if "days" in duration_str:
            days = int(duration_str.split()[0].split("-")[-1])  # Take max days
            return datetime.utcnow() + timedelta(days=days)
        
        return datetime.utcnow() + timedelta(days=3)  # Default 3 days
    
    def _initialize_workflow_steps(self, workflow: DocumentWorkflow):
        """Initialize workflow steps."""
        step_number = 1
        
        # Step 1: Generate draft
        step = DocumentStep(
            step_id=self._generate_step_id(),
            workflow_id=workflow.workflow_id,
            step_number=step_number,
            step_type="generate_draft",
            status="pending",
            description="Generate initial document draft from template",
            start_time=None,
            end_time=None,
            output=None,
            ai_analysis=None
        )
        self.steps.append(step)
        step_number += 1
        
        # Step 2: AI review (if enabled)
        if self.document_types[workflow.document_type]["ai_review_enabled"]:
            step = DocumentStep(
                step_id=self._generate_step_id(),
                workflow_id=workflow.workflow_id,
                step_number=step_number,
                step_type="ai_review",
                status="pending",
                description="AI-powered document review and risk analysis",
                start_time=None,
                end_time=None,
                output=None,
                ai_analysis=None
            )
            self.steps.append(step)
            step_number += 1
        
        # Step 3: Client review (if required)
        if self.document_types[workflow.document_type]["client_review_required"]:
            step = DocumentStep(
                step_id=self._generate_step_id(),
                workflow_id=workflow.workflow_id,
                step_number=step_number,
                step_type="client_review",
                status="pending",
                description="Client review and feedback collection",
                start_time=None,
                end_time=None,
                output=None,
                ai_analysis=None
            )
            self.steps.append(step)
            step_number += 1
        
        # Step 4: Finalize
        step = DocumentStep(
            step_id=self._generate_step_id(),
            workflow_id=workflow.workflow_id,
            step_number=step_number,
            step_type="finalize",
            status="pending",
            description="Final document preparation and signature readiness",
            start_time=None,
            end_time=None,
            output=None,
            ai_analysis=None
        )
        self.steps.append(step)
    
    def _generate_step_id(self) -> str:
        """Generate unique step identifier."""
        import uuid
        return f"STEP-{str(uuid.uuid4())[:8].upper()}"
    
    def _execute_step(self, workflow_id: str, step_number: int):
        """Execute a specific workflow step."""
        try:
            # Find the step
            step = self._get_step(workflow_id, step_number)
            if not step:
                raise ValueError(f"Step {step_number} not found for workflow {workflow_id}")
            
            # Update step status
            step.status = "in_progress"
            step.start_time = datetime.utcnow()
            
            # Execute based on step type
            if step.step_type == "generate_draft":
                self._execute_generate_draft(step)
            elif step.step_type == "ai_review":
                self._execute_ai_review(step)
            elif step.step_type == "client_review":
                self._execute_client_review(step)
            elif step.step_type == "finalize":
                self._execute_finalize(step)
            
            # Mark step as completed
            step.status = "completed"
            step.end_time = datetime.utcnow()
            
            # Update workflow
            workflow = self._get_workflow(workflow_id)
            if workflow:
                workflow.current_step = step_number + 1
                workflow.updated_at = datetime.utcnow()
                
                # Check if workflow is complete
                if step_number == workflow.total_steps:
                    workflow.status = "completed"
            
            logger.info(f"Step {step_number} completed for workflow {workflow_id}")
            
        except Exception as e:
            logger.error(f"Error executing step {step_number} for workflow {workflow_id}: {e}")
            # Mark step as failed
            step.status = "failed"
            step.end_time = datetime.utcnow()
            raise
    
    def _execute_generate_draft(self, step: DocumentStep):
        """Execute document draft generation."""
        workflow = self._get_workflow(step.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {step.workflow_id} not found")
        
        # Get template
        template = self._get_template(workflow.document_type)
        if not template:
            raise ValueError(f"Template not found for {workflow.document_type}")
        
        # Generate document content
        document_content = self._generate_document_content(template, workflow.client_data)
        
        # Create output
        step.output = {
            "document_content": document_content,
            "template_used": template.template_name,
            "variables_filled": list(workflow.client_data.keys()),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _execute_ai_review(self, step: DocumentStep):
        """Execute AI-powered document review."""
        workflow = self._get_workflow(step.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {step.workflow_id} not found")
        
        # Get previous step output
        prev_step = self._get_step(workflow.workflow_id, step.step_number - 1)
        if not prev_step or not prev_step.output:
            raise ValueError("No document content to review")
        
        document_content = prev_step.output["document_content"]
        
        # Perform AI analysis
        ai_analysis = self._analyze_document_risks(document_content, workflow.document_type)
        
        # Generate improvements
        improvements = self._generate_document_improvements(document_content, ai_analysis)
        
        # Create output
        step.output = {
            "original_content": document_content,
            "improved_content": self._apply_improvements(document_content, improvements),
            "ai_analysis": ai_analysis,
            "improvements": improvements,
            "reviewed_at": datetime.utcnow().isoformat()
        }
        
        step.ai_analysis = ai_analysis
    
    def _execute_client_review(self, step: DocumentStep):
        """Execute client review step."""
        workflow = self._get_workflow(step.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {step.workflow_id} not found")
        
        # Get previous step output
        prev_step = self._get_step(workflow.workflow_id, step.step_number - 1)
        if not prev_step or not prev_step.output:
            raise ValueError("No document content for client review")
        
        document_content = prev_step.output.get("improved_content", prev_step.output["document_content"])
        
        # Create client review interface
        step.output = {
            "document_content": document_content,
            "client_review_url": f"/client/review/{step.step_id}",
            "review_deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "awaiting_client_review",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Update workflow status
        workflow.status = "client_review"
    
    def _execute_finalize(self, step: DocumentStep):
        """Execute document finalization."""
        workflow = self._get_workflow(step.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {step.workflow_id} not found")
        
        # Get final document content
        prev_step = self._get_step(workflow.workflow_id, step.step_number - 1)
        if not prev_step or not prev_step.output:
            raise ValueError("No document content to finalize")
        
        document_content = prev_step.output.get("document_content", prev_step.output.get("improved_content"))
        
        # Prepare for signature
        signature_ready = self._prepare_for_signature(document_content, workflow.document_type)
        
        # Create final output
        step.output = {
            "final_document": document_content,
            "signature_ready": signature_ready,
            "download_url": f"/documents/{step.step_id}/download",
            "signature_url": f"/documents/{step.step_id}/sign" if signature_ready else None,
            "finalized_at": datetime.utcnow().isoformat()
        }
        
        # Update workflow status
        workflow.status = "completed"
    
    def _get_workflow(self, workflow_id: str) -> Optional[DocumentWorkflow]:
        """Get workflow by ID."""
        for workflow in self.workflows:
            if workflow.workflow_id == workflow_id:
                return workflow
        return None
    
    def _get_step(self, workflow_id: str, step_number: int) -> Optional[DocumentStep]:
        """Get workflow step by number."""
        for step in self.steps:
            if step.workflow_id == workflow_id and step.step_number == step_number:
                return step
        return None
    
    def _get_template(self, document_type: str) -> Optional[DocumentTemplate]:
        """Get template for document type."""
        for template in self.templates:
            if template.document_type == document_type and template.is_active:
                return template
        return None
    
    def _generate_document_content(self, template: DocumentTemplate, client_data: Dict[str, Any]) -> str:
        """Generate document content from template and client data."""
        content = template.template_content
        
        # Replace variables with client data
        for variable in template.variables:
            if variable in client_data:
                placeholder = f"{{{{{variable}}}}}"
                content = content.replace(placeholder, str(client_data[variable]))
        
        return content
    
    def _analyze_document_risks(self, document_content: str, document_type: str) -> Dict[str, Any]:
        """Analyze document for potential risks and issues."""
        risks = []
        suggestions = []
        risk_score = 0
        
        # Legal compliance checks
        if "employment_contract" in document_type:
            if "non-compete" in document_content.lower():
                risks.append("Non-compete clause may be unenforceable in some jurisdictions")
                risk_score += 20
            
            if "at-will" not in document_content.lower():
                risks.append("Consider adding at-will employment clause")
                suggestions.append("Add standard at-will employment language")
                risk_score += 15
        
        # Clarity and completeness checks
        if len(document_content) < 500:
            risks.append("Document may be too brief for comprehensive coverage")
            risk_score += 25
        
        if "confidential" in document_content.lower() and "definition" not in document_content.lower():
            risks.append("Confidentiality clause lacks clear definition")
            suggestions.append("Define what constitutes confidential information")
            risk_score += 15
        
        # Liability protection checks
        if "indemnification" not in document_content.lower():
            risks.append("Consider adding indemnification clause")
            suggestions.append("Add standard indemnification language")
            risk_score += 10
        
        return {
            "risk_score": min(risk_score, 100),
            "risk_level": "high" if risk_score >= 50 else "medium" if risk_score >= 25 else "low",
            "risks": risks,
            "suggestions": suggestions,
            "compliance_issues": len(risks),
            "improvement_opportunities": len(suggestions)
        }
    
    def _generate_document_improvements(self, document_content: str, ai_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific improvements for the document."""
        improvements = []
        
        for suggestion in ai_analysis.get("suggestions", []):
            improvements.append({
                "type": "addition",
                "description": suggestion,
                "priority": "high" if "clause" in suggestion.lower() else "medium",
                "estimated_impact": "risk_reduction"
            })
        
        # Add standard improvements
        if "employment_contract" in document_content.lower():
            improvements.append({
                "type": "clause_addition",
                "description": "Add standard termination clause",
                "priority": "high",
                "estimated_impact": "compliance_improvement"
            })
        
        return improvements
    
    def _apply_improvements(self, document_content: str, improvements: List[Dict[str, Any]]) -> str:
        """Apply improvements to document content."""
        improved_content = document_content
        
        for improvement in improvements:
            if improvement["type"] == "clause_addition":
                # Add standard clauses based on improvement description
                if "termination" in improvement["description"].lower():
                    improved_content += "\n\nTERMINATION: This agreement may be terminated by either party with 30 days written notice."
                elif "indemnification" in improvement["description"].lower():
                    improved_content += "\n\nINDEMNIFICATION: Each party shall indemnify and hold harmless the other party from any claims arising from their breach of this agreement."
        
        return improved_content
    
    def _prepare_for_signature(self, document_content: str, document_type: str) -> bool:
        """Prepare document for electronic signature."""
        # Check if document is ready for signature
        required_elements = ["parties", "terms", "signature_block"]
        
        for element in required_elements:
            if element not in document_content.lower():
                return False
        
        return True
    
    def _get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status."""
        workflow = self._get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_steps = [step for step in self.steps if step.workflow_id == workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "document_type": workflow.document_type,
            "status": workflow.status,
            "current_step": workflow.current_step,
            "total_steps": workflow.total_steps,
            "progress_percentage": (workflow.current_step - 1) / workflow.total_steps * 100,
            "estimated_completion": workflow.estimated_completion.isoformat(),
            "priority": workflow.priority,
            "steps": [
                {
                    "step_number": step.step_number,
                    "step_type": step.step_type,
                    "status": step.status,
                    "description": step.description,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "output_summary": self._get_step_output_summary(step)
                }
                for step in sorted(workflow_steps, key=lambda x: x.step_number)
            ],
            "ai_insights": self._generate_workflow_insights(workflow, workflow_steps),
            "next_actions": self._get_next_actions(workflow, workflow_steps)
        }
    
    def _get_step_output_summary(self, step: DocumentStep) -> Dict[str, Any]:
        """Get summary of step output."""
        if not step.output:
            return {"status": "no_output"}
        
        summary = {"status": "completed"}
        
        if step.step_type == "generate_draft":
            summary["document_length"] = len(step.output.get("document_content", ""))
            summary["variables_filled"] = step.output.get("variables_filled", [])
        elif step.step_type == "ai_review":
            summary["risk_score"] = step.output.get("ai_analysis", {}).get("risk_score", 0)
            summary["improvements_count"] = len(step.output.get("improvements", []))
        elif step.step_type == "client_review":
            summary["review_status"] = step.output.get("status", "unknown")
        elif step.step_type == "finalize":
            summary["signature_ready"] = step.output.get("signature_ready", False)
        
        return summary
    
    def _generate_workflow_insights(self, workflow: DocumentWorkflow, steps: List[DocumentStep]) -> List[str]:
        """Generate AI insights about the workflow."""
        insights = []
        
        # Progress insights
        if workflow.current_step > 1:
            insights.append(f"Workflow is {workflow.current_step}/{workflow.total_steps} complete")
        
        # Time insights
        days_elapsed = (datetime.utcnow() - workflow.created_at).days
        if days_elapsed > 7:
            insights.append("Workflow is taking longer than expected - consider expediting")
        
        # Quality insights
        ai_review_step = next((s for s in steps if s.step_type == "ai_review"), None)
        if ai_review_step and ai_review_step.output:
            risk_score = ai_review_step.output.get("ai_analysis", {}).get("risk_score", 0)
            if risk_score > 50:
                insights.append("High-risk document detected - requires careful review")
            elif risk_score < 20:
                insights.append("Document quality is excellent - minimal risks identified")
        
        return insights
    
    def _get_next_actions(self, workflow: DocumentWorkflow, steps: List[DocumentStep]) -> List[Dict[str, Any]]:
        """Get recommended next actions for the workflow."""
        actions = []
        
        if workflow.status == "draft":
            actions.append({
                "action": "Review AI analysis",
                "description": "Review AI-generated improvements and risk analysis",
                "priority": "high",
                "timeline": "immediate"
            })
        elif workflow.status == "client_review":
            actions.append({
                "action": "Follow up with client",
                "description": "Check on client review progress",
                "priority": "medium",
                "timeline": "within 3 days"
            })
        elif workflow.status == "completed":
            actions.append({
                "action": "Send for signature",
                "description": "Document is ready for electronic signature",
                "priority": "high",
                "timeline": "immediate"
            })
        
        return actions
    
    def _initialize_templates(self):
        """Initialize default document templates."""
        templates = [
            DocumentTemplate(
                template_id="TEMPLATE-001",
                document_type="employment_contract",
                template_name="employment_contract_v2",
                template_content="""
EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is entered into on {start_date} between {company_name} (the "Company") and {employee_name} (the "Employee").

1. POSITION AND DUTIES
The Employee shall serve as {position} and shall perform all duties and responsibilities associated with this position.

2. COMPENSATION
The Employee shall receive an annual salary of {salary} payable in accordance with the Company's standard payroll practices.

3. TERM
This Agreement shall commence on {start_date} and shall continue until terminated by either party.

4. CONFIDENTIALITY
The Employee agrees to maintain the confidentiality of all proprietary information.

5. NON-COMPETE
The Employee agrees not to compete with the Company for a period of 12 months following termination.

SIGNATURE BLOCK:
Company: _________________
Employee: _________________
Date: _________________
                """,
                variables=["employee_name", "position", "salary", "start_date", "company_name"],
                version="2.0",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
        ]
        
        self.templates.extend(templates)
        logger.info(f"Initialized {len(templates)} document templates") 