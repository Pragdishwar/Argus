import requests
import time
import threading

class ManifestClient:
    def __init__(self, api_url="https://uqoxensqmbcmanyulqsk.supabase.co/rest/v1/manifests?select=*"):
        self.api_url = api_url
        self.headers = {
            "apikey": "sb_publishable_xcCThN3in7kOknQillUqEQ_EXor3IdR",
            "Authorization": "Bearer sb_publishable_xcCThN3in7kOknQillUqEQ_EXor3IdR"
        }
        self.manifest_data = []
        self.destinations = []
        self.running = False
        self.poll_thread = None

    def start_polling(self, interval=30):
        """Starts a background thread to poll the manifest API every 'interval' seconds."""
        if self.running:
            return
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, args=(interval,), daemon=True)
        self.poll_thread.start()
        print(f"ManifestClient started polling {self.api_url} every {interval}s")

    def stop_polling(self):
        """Stops the polling thread."""
        self.running = False

    def _poll_loop(self, interval):
        while self.running:
            self.fetch_manifest()
            time.sleep(interval)

    def fetch_manifest(self):
        """Fetches the latest manifest data from the API."""
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=5)
            response.raise_for_status()
            self.manifest_data = response.json()
            # Extract unique destinations for fuzzy matching
            self.destinations = list(set([item.get("destination", "").upper() for item in self.manifest_data]))
            print(f"Manifest fetched successfully. Destinations: {self.destinations}")
        except Exception as e:
            print(f"Error fetching manifest: {e}")

    def get_known_destinations(self):
        return self.destinations

if __name__ == "__main__":
    # Test the client
    client = ManifestClient()
    client.fetch_manifest()
    print("Test fetch complete.")
