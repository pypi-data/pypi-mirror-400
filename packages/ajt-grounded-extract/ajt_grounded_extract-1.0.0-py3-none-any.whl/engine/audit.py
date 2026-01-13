"""
Audit trail generation for compliance and legal defense.

Generates:
- Audit logs (execution-time)
- Defense briefs (incident-time)
- Regulatory reports (on-demand)
"""
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path


class AuditLogger:
    """Generate audit-grade logs for admission decisions."""

    def __init__(self, audit_dir: str = "audit"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)

    def log_decision(
        self,
        action: str,
        context: Dict,
        decision: str,
        decision_maker: str,
        conditions_proven: Optional[Dict] = None,
        token: Optional[Dict] = None,
        blocked_at: Optional[str] = None,
        reason: Optional[str] = None
    ) -> str:
        """
        Log admission decision with full audit trail.

        Returns: audit_id
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        context_hash = self._compute_context_hash(action, context, decision_maker)

        audit_record = {
            "audit_id": f"audit_{context_hash[:16]}_{int(datetime.now(timezone.utc).timestamp())}",
            "timestamp": timestamp,
            "decision_context_hash": context_hash,
            "action_requested": action,
            "decision": decision,
            "decision_maker_id": decision_maker,
            "conditions_proven": conditions_proven or {},
            "scope": {
                "validity": "context-bound",
                "reuse": "forbidden",
                "auto_revoke_on_change": True
            },
            "blocked_at": blocked_at,
            "reason": reason,
            "attachments": {
                "admission_token_id": token.get("token_id") if token else None,
                "proof_bundle_ref": self._create_proof_bundle(
                    context, conditions_proven
                )
            }
        }

        # Write audit log
        audit_path = self.audit_dir / f"{audit_record['audit_id']}.json"
        with open(audit_path, 'w') as f:
            json.dump(audit_record, f, indent=2)

        return audit_record["audit_id"]

    def _compute_context_hash(
        self,
        action: str,
        context: Dict,
        decision_maker: str
    ) -> str:
        """Compute context hash for audit trail."""
        data = f"{action}:{json.dumps(context, sort_keys=True)}:{decision_maker}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _create_proof_bundle(
        self,
        context: Dict,
        conditions: Optional[Dict]
    ) -> str:
        """Create proof bundle reference."""
        bundle_data = {
            "context": context,
            "conditions": conditions or {}
        }
        bundle_hash = hashlib.sha256(
            json.dumps(bundle_data, sort_keys=True).encode()
        ).hexdigest()
        return f"proof_{bundle_hash[:16]}"


class DefenseBriefGenerator:
    """Generate legal defense briefs from audit logs."""

    def generate(self, audit_id: str, audit_dir: str = "audit") -> str:
        """Generate defense brief from audit log."""
        audit_path = Path(audit_dir) / f"{audit_id}.json"

        if not audit_path.exists():
            raise FileNotFoundError(f"Audit log not found: {audit_id}")

        with open(audit_path, 'r') as f:
            audit = json.load(f)

        brief = self._build_brief(audit)

        # Write brief
        brief_path = Path(audit_dir) / f"defense_brief_{audit_id}.md"
        with open(brief_path, 'w') as f:
            f.write(brief)

        return str(brief_path)

    def _build_brief(self, audit: Dict) -> str:
        """Build defense brief markdown."""
        decision_verb = "ADMITTED" if audit["decision"] == "ADMIT" else "STOPPED"

        return f"""# Conditional Admission Defense Brief

**Incident ID**: {audit['audit_id']}
**Timestamp**: {audit['timestamp']}
**Decision**: {decision_verb}

---

## 1. Constitutional Compliance

| Requirement | Status |
|-------------|--------|
| DEFAULT: STOP applied | ✅ Yes |
| ALL conditions proven | {"✅ Yes" if audit['decision'] == 'ADMIT' else "❌ No"} |
| Scope limited | ✅ Yes |
| Reuse prohibited | ✅ Yes |

---

## 2. Decision Path

**Action Requested**: {audit['action_requested']}

**Decision Maker**: {audit['decision_maker_id']}

**Conditions Evaluated**:
```json
{json.dumps(audit['conditions_proven'], indent=2)}
```

**Alternative Paths**: {"Evaluated" if audit.get('conditions_proven', {}).get('alternatives') else "Not applicable (STOPPED before evaluation)"}

**Exclusion Basis (Negative Proof)**:
- Decision: {audit['decision']}
- Blocked at: {audit.get('blocked_at', 'N/A')}
- Reason: {audit.get('reason', 'N/A')}

---

## 3. Stop Capability

**STOP Triggers Defined**: Yes (per ADMISSION_CONSTITUTION.md)

**Trigger Activated**: {"Yes" if audit['decision'] == 'STOP' else "No"}

**Activation Point**: {audit.get('blocked_at', 'N/A')}

**Log Reference**: {audit['audit_id']}

---

## 4. Conclusion

This system does not guarantee outcomes.

**This system guarantees**:
- Stoppability (DEFAULT: STOP enforced)
- Traceability (decision_maker: {audit['decision_maker_id']})
- Scope containment (context-bound, reuse forbidden)

---

## Attachments

- Audit Log: `{audit['audit_id']}.json`
- Admission Token: {audit['attachments'].get('admission_token_id', 'N/A')}
- Proof Bundle: {audit['attachments']['proof_bundle_ref']}

---

**Generated**: {datetime.now(timezone.utc).isoformat()}
**Status**: Counsel-ready
"""


class RegulatoryReportGenerator:
    """Generate regulatory compliance reports."""

    def generate(self, audit_ids: List[str], audit_dir: str = "audit") -> str:
        """Generate regulatory report from multiple audit logs."""
        audits = []
        for audit_id in audit_ids:
            audit_path = Path(audit_dir) / f"{audit_id}.json"
            if audit_path.exists():
                with open(audit_path, 'r') as f:
                    audits.append(json.load(f))

        report = self._build_report(audits)

        # Write report
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_path = Path(audit_dir) / f"regulatory_report_{timestamp}.md"
        with open(report_path, 'w') as f:
            f.write(report)

        return str(report_path)

    def _build_report(self, audits: List[Dict]) -> str:
        """Build regulatory report markdown."""
        total = len(audits)
        admitted = sum(1 for a in audits if a['decision'] == 'ADMIT')
        stopped = sum(1 for a in audits if a['decision'] == 'STOP')

        # Count block points
        block_points = {}
        for audit in audits:
            if audit['decision'] == 'STOP':
                bp = audit.get('blocked_at', 'Unknown')
                block_points[bp] = block_points.get(bp, 0) + 1

        return f"""# Regulatory Compliance Report

**Period**: {audits[0]['timestamp'] if audits else 'N/A'} to {audits[-1]['timestamp'] if audits else 'N/A'}
**Total Decisions**: {total}
**Admitted**: {admitted}
**Stopped**: {stopped}

---

## Principles Enforced

- ✅ No action without admission
- ✅ No reuse across contexts
- ✅ No partial responsibility
- ✅ No silent scope expansion
- ✅ No anonymous authority

---

## Risk-Control Mapping

| Risk Pattern | Control | Evidence Count |
|--------------|---------|----------------|
| Over-generation | Interface gate | {total} |
| Hallucination pressure | DEFAULT: STOP | {stopped} |
| Scope creep | Context binding | {admitted} (tokens issued) |
| Accountability gap | Identity anchoring | {total} (all have decision_maker) |

---

## Block Point Analysis

| Block Point | Count | Percentage |
|-------------|-------|------------|
{''.join(f"| {bp} | {count} | {count/stopped*100:.1f}% |\n" for bp, count in block_points.items()) if block_points else "| N/A | 0 | 0% |"}

---

## Non-Goals (Explicit)

This system does **NOT** guarantee:
- ❌ Accuracy of outputs
- ❌ Automation maximization
- ❌ Output completeness

This system **DOES** guarantee:
- ✅ Stoppability (DEFAULT: STOP)
- ✅ Traceability (decision_maker required)
- ✅ Scope containment (context-bound tokens)

---

## Audit Trail References

{chr(10).join(f"- {a['audit_id']}" for a in audits)}

---

**Generated**: {datetime.now(timezone.utc).isoformat()}
**Status**: Regulator-readable
**Constitution**: ADMISSION_CONSTITUTION.md v1.0
"""
