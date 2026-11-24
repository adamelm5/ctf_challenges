import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable
from urllib.error import URLError
from urllib.request import Request, urlopen


INTERNAL_TOKEN = os.environ.get("CTF_INTERNAL_TOKEN", "local-dev-token-change-me")
DNS_CLIENT_URL = os.environ.get("DNS_CLIENT_URL", "http://dns-client:8091")
ARCHIVE_URL = os.environ.get("ARCHIVE_URL", "http://archive:8093")
POINTS = {1: 30, 2: 35, 3: 25}
STAGES = {
    1: {
        "title": "Analyse du portail",
        "component": "TLS / CVE-2016-2107",
        "evidence": (
            "Le relevé du portail mentionne AES-CBC, mais ne fournit ni version "
            "d’OpenSSL ni preuve d’un comportement vulnérable."
        ),
        "question": "Quelle conclusion est justifiée par ce relevé ?",
        "options": [
            {"value": "confirmed", "label": "La CVE est démontrée"},
            {"value": "not-proven", "label": "Les éléments ne démontrent pas la CVE"},
            {"value": "fixed", "label": "La CVE est certainement corrigée"},
        ],
        "answer": "not-proven",
    },
    2: {
        "title": "Audit du résolveur",
        "component": "glibc / CVE-2015-7547",
        "question": "Quel statut peut-on attribuer à cette installation ?",
        "options": [
            {"value": "vulnerable", "label": "Vulnérable, un crash est établi"},
            {"value": "patched", "label": "Le paquet observé est corrigé"},
            {"value": "unknown", "label": "La bibliothèque n’est pas identifiée"},
        ],
        "answer": "patched",
    },
    3: {
        "title": "Revue de l’archive",
        "component": "Log4j / CVE-2021-44228",
        "question": "Quelle conclusion prudente faut-il retenir ?",
        "options": [
            {"value": "exploitable", "label": "Une exploitation est démontrée"},
            {"value": "mitigated", "label": "La résolution JNDI est désactivée dans ce scénario"},
            {"value": "not-installed", "label": "Log4j n’est pas présent"},
        ],
        "answer": "mitigated",
    },
}


class ProgressError(Exception):
    def __init__(self, message: str, status: int) -> None:
        super().__init__(message)
        self.status = status


class Challenge:
    def __init__(
        self,
        dns_client_url: str = DNS_CLIENT_URL,
        archive_url: str = ARCHIVE_URL,
        internal_token: str = INTERNAL_TOKEN,
    ) -> None:
        self.dns_client_url = dns_client_url.rstrip("/")
        self.archive_url = archive_url.rstrip("/")
        self.internal_token = internal_token
        self.completed: set[int] = set()
        self.flag_claimed = False

    def _service_json(self, url: str) -> dict[str, Any]:
        request = Request(url, headers={"X-CTF-Internal-Token": self.internal_token})
        try:
            with urlopen(request, timeout=3) as response:
                result = json.loads(response.read(8192))
        except (URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
            raise ProgressError("A required laboratory service is unavailable", 503) from error
        if not isinstance(result, dict):
            raise ProgressError("A laboratory service returned invalid evidence", 502)
        return result

    def status(self) -> dict[str, Any]:
        next_stage = next(
            (stage_id for stage_id in range(1, len(STAGES) + 1)
             if stage_id not in self.completed),
            None,
        )
        return {
            "mode": "simulation",
            "completed_stages": sorted(self.completed),
            "next_stage": next_stage,
            "score": sum(POINTS[stage_id] for stage_id in self.completed)
            + (10 if self.flag_claimed else 0),
            "max_score": 100,
            "flag_available": next_stage is None,
        }

    def stage(self, stage_id: int) -> dict[str, Any]:
        stage = STAGES.get(stage_id)
        if stage is None:
            raise ProgressError("Unknown stage", 404)
        expected = self.status()["next_stage"]
        if stage_id not in self.completed and stage_id != expected:
            raise ProgressError("Complete the previous stage first", 409)

        evidence = stage.get("evidence")
        if stage_id == 2:
            report = self._service_json(self.dns_client_url + "/report")
            evidence = report.get("evidence")
        elif stage_id == 3:
            report = self._service_json(self.archive_url + "/diagnostics")
            evidence = report.get("evidence")
        if not isinstance(evidence, str) or not evidence:
            raise ProgressError("A laboratory service returned invalid evidence", 502)
        return {
            "id": stage_id,
            "mode": "simulation",
            "title": stage["title"],
            "component": stage["component"],
            "evidence": evidence,
            "question": stage["question"],
            "options": stage["options"],
        }

    def submit(self, stage_id: int, answer: str) -> None:
        stage = STAGES.get(stage_id)
        if stage is None:
            raise ProgressError("Unknown stage", 404)
        if self.status()["next_stage"] != stage_id:
            raise ProgressError("Stages must be completed in order", 409)
        if answer.strip().lower() not in {option["value"] for option in stage["options"]}:
            raise ProgressError("Choose one of the listed conclusions", 422)
        if answer.strip().lower() != stage["answer"]:
            raise ProgressError("That conclusion is not supported by the evidence", 422)
        self.completed.add(stage_id)

    def flag(self) -> dict[str, str]:
        if len(self.completed) != len(STAGES):
            raise ProgressError("The archive is still locked", 403)
        request = Request(
            self.archive_url + "/internal/flag",
            headers={"X-CTF-Internal-Token": self.internal_token},
        )
        try:
            with urlopen(request, timeout=3) as response:
                result = json.loads(response.read(8192))
        except (URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
            raise ProgressError("The archive service is unavailable", 503) from error
        if (
            not isinstance(result, dict)
            or result.get("principal") != "archive"
            or not isinstance(result.get("flag"), str)
            or not result["flag"].strip()
        ):
            raise ProgressError("The archive returned an invalid flag response", 502)
        self.flag_claimed = True
        return {"principal": "archive", "flag": result["flag"].strip()}


def make_handler(
    challenge_factory: Callable[[], Challenge] = Challenge,
) -> type[BaseHTTPRequestHandler]:
    sessions: dict[str, Challenge] = {}

    class Handler(BaseHTTPRequestHandler):
        server_version = "HospitalCTFController/1.0"

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; object-src 'none'; base-uri 'none'; "
                "frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def _authorized(self) -> bool:
            if self.headers.get("X-Portal-Token") == INTERNAL_TOKEN:
                session_id = self.headers.get("X-CTF-Session", "")
                if not re.fullmatch(r"[0-9a-f]{32}", session_id):
                    self._send_json(400, {"error": "Invalid session"})
                    return False
                if session_id not in sessions and len(sessions) >= 1024:
                    self._send_json(503, {"error": "Session capacity reached"})
                    return False
                if session_id not in sessions:
                    sessions[session_id] = challenge_factory()
                self.challenge: Challenge = sessions[session_id]
                return True
            self._send_json(403, {"error": "Forbidden"})
            return False

        def do_GET(self) -> None:
            if self.path == "/healthz":
                self._send_json(200, {"status": "ok"})
                return
            if not self._authorized():
                return
            if self.path == "/api/status":
                self._send_json(200, self.challenge.status())
                return
            if self.path == "/api/flag":
                try:
                    self._send_json(200, self.challenge.flag())
                except ProgressError as error:
                    self._send_json(error.status, {"error": str(error)})
                return
            match = re.fullmatch(r"/api/stages/([1-9][0-9]*)", self.path)
            if match:
                try:
                    self._send_json(200, self.challenge.stage(int(match.group(1))))
                except ProgressError as error:
                    self._send_json(error.status, {"error": str(error)})
                return
            self._send_json(404, {"error": "Not found"})

        def do_POST(self) -> None:
            if not self._authorized():
                return
            match = re.fullmatch(r"/api/stages/([1-9][0-9]*)/submit", self.path)
            if not match:
                self._send_json(404, {"error": "Not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 1024:
                    raise ValueError("Invalid request size")
                payload = json.loads(self.rfile.read(length))
                answer = payload["answer"]
                if not isinstance(answer, str):
                    raise ValueError("Answer must be a string")
                self.challenge.submit(int(match.group(1)), answer)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                self._send_json(400, {"error": "Invalid request"})
                return
            except ProgressError as error:
                self._send_json(error.status, {"error": str(error)})
                return
            self._send_json(200, self.challenge.status())

        def log_message(self, format: str, *args: Any) -> None:
            super().log_message(format, *args)

    return Handler


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8080), make_handler())
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
