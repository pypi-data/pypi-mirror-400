from docker import from_env
from docker.errors import DockerException

from integrityguard.domain.scan_result import ScanResult
from integrityguard.domain.severity import Severity
from integrityguard.interfaces.vulnerability_check import VulnerabilityCheck


class EtcShadowCheck(VulnerabilityCheck):
    """
    Checks if the /etc/shadow file is readable via a Docker container.
    """

    ID = "DX-003"
    NAME = "Read /etc/shadow via Docker"

    def execute(self) -> ScanResult:
        trace = []
        is_vulnerable = False
        evidence = "Could not read /etc/shadow via Docker."
        
        try:
            trace.append("Connecting to Docker daemon...")
            client = from_env()
            
            trace.append("Attempting to run container with /etc/shadow mounted...")
            
            output = client.containers.run(
                "alpine",
                "head -n 1 /host_shadow",
                volumes={'/etc/shadow': {'bind': '/host_shadow', 'mode': 'ro'}},
                remove=True,
                stderr=True
            )
            
            output_str = output.decode('utf-8').strip()

            if "root:" in output_str:
                is_vulnerable = True
                evidence = "Successfully read /etc/shadow using a Docker container."
                trace.append("Content verification successful (found 'root:').")
            else:
                trace.append("Output did not look like shadow file content.")

        except DockerException as e:
            trace.append(f"Docker error: {str(e)}")
            evidence = f"Docker execution failed: {str(e)}"
        except Exception as e:
            trace.append(f"Unexpected error: {str(e)}")

        return ScanResult(
            check_id=self.ID,
            check_name=self.NAME,
            is_vulnerable=is_vulnerable,
            severity=Severity.CRITICAL if is_vulnerable else Severity.LOW,
            description="Checks if the user can use Docker to read the host's /etc/shadow file.",
            evidence=evidence,
            recommendation="Restrict access to the Docker socket/group. Only trusted users should have Docker access.",
            trace=trace
        )
