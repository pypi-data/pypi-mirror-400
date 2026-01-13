# core/reporting.py

import json
from pathlib import Path


class Reporting:
    @staticmethod
    def save_json(results: dict, file_path: Path) -> None:
        file_path.write_text(json.dumps(results, indent=4), encoding="utf-8")

    @staticmethod
    def save_html(results: dict, file_path: Path) -> None:
        html_content = "<html><body><h1>API Test Report</h1><table border='1'>"
        html_content += "<tr><th>Endpoint</th><th>Status</th><th>Response</th></tr>"
        for endpoint, data in results.items():
            status = data.get("status_code", data.get("error", "N/A"))
            response = data.get("response", "")
            html_content += f"<tr><td>{endpoint}</td><td>{status}</td><td>{response}</td></tr>"
        html_content += "</table></body></html>"
        file_path.write_text(html_content, encoding="utf-8")
