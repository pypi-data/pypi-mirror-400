from pathlib import Path

from terraform_guardrail.scanner.scan import _schema_findings


def test_schema_validation_flags_unknown_attribute(tmp_path: Path) -> None:
    hcl_data = {
        "resource": [
            {
                "aws_s3_bucket": {
                    "logs": {
                        "bucket": "demo",
                        "bogus": "value",
                    }
                }
            }
        ]
    }
    schema = {
        "provider_schemas": {
            "registry.terraform.io/hashicorp/aws": {
                "resource_schemas": {
                    "aws_s3_bucket": {"block": {"attributes": {"bucket": {}}}}
                }
            }
        }
    }

    findings = _schema_findings(hcl_data, schema, tmp_path / "main.tf")
    assert any(finding.rule_id == "TG005" for finding in findings)
