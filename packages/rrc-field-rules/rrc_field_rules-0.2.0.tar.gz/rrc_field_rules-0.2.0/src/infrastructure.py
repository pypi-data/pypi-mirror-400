import subprocess
import time


class OracleContainer:
    def __init__(self, compose_file="docker/docker-compose.yml"):
        self.compose_file = compose_file

    def start(self):
        print("🚀 Starting Oracle Container...")
        # Start Docker in detached mode
        subprocess.run(["docker-compose", "-f", self.compose_file, "up", "-d"], check=True)
        self._wait_for_import_completion()

    def stop(self):
        print("🛑 Shutting down Oracle Container...")
        subprocess.run(["docker-compose", "-f", self.compose_file, "down"], check=True)

    def _wait_for_import_completion(self):
        """Polls logs to ensure the .dmp file is fully imported before giving the green light."""
        print("⏳ Waiting for legacy data import to complete (this happens inside the container)...")
        container_name = "rrc_oracle_parser"

        # Poll for up to 5 minutes
        for _ in range(30):
            result = subprocess.run(
                ["docker", "logs", container_name],
                capture_output=True, text=True
            )

            # This matches the success message from our init_oracle.sh script
            if "AUTOMATED SETUP COMPLETE" in result.stdout:
                print("✅ Data Import Finished.")
                return

            time.sleep(10)

        raise TimeoutError("❌ Oracle started, but the data import script timed out.")
