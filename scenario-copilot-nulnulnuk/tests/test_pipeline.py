import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from controller.app import Challenge, INTERNAL_TOKEN, make_handler


class StubHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/report":
            payload = {
                "evidence": (
                    "glibc 2.19-18+deb8u10 (amd64) est chargée; "
                    "le resolver est dynamique et NSS utilise files puis dns."
                )
            }
        elif self.path == "/diagnostics":
            payload = {
                "evidence": (
                    "Le scénario utilise log4j-core 2.14.1; la résolution "
                    "JNDI est désactivée et l’entrée de test reste inerte."
                )
            }
        elif self.path == "/internal/flag":
            payload = {"principal": "archive", "flag": "HOSPITAL{test_only}"}
        else:
            self.send_error(404)
            return
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stub = ThreadingHTTPServer(("127.0.0.1", 0), StubHandler)
        self.stub_thread = threading.Thread(target=self.stub.serve_forever, daemon=True)
        self.stub_thread.start()
        service_url = "http://127.0.0.1:{}".format(self.stub.server_port)
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            make_handler(
                lambda: Challenge(
                    dns_client_url=service_url,
                    archive_url=service_url,
                    internal_token=INTERNAL_TOKEN,
                )
            ),
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = "http://127.0.0.1:{}".format(self.server.server_port)
        self.session_id = "a" * 32

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.stub.shutdown()
        self.stub.server_close()
        self.stub_thread.join()

    def request(
        self,
        path: str,
        payload: dict[str, str] | None = None,
        session_id: str | None = None,
    ) -> tuple[int, dict[str, object]]:
        body = None if payload is None else json.dumps(payload).encode()
        request = Request(
            self.base_url + path,
            data=body,
            headers={
                "X-Portal-Token": INTERNAL_TOKEN,
                "X-CTF-Session": session_id or self.session_id,
                "Content-Type": "application/json",
            },
            method="GET" if body is None else "POST",
        )
        try:
            response = urlopen(request)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.loads(response.read())

    def test_controller_rejects_requests_without_portal_auth(self) -> None:
        with urlopen(self.base_url + "/healthz") as response:
            self.assertEqual(response.status, 200)
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base_url + "/api/status")
        self.assertEqual(error.exception.code, 403)

    def test_evidence_is_sequential_and_the_flag_is_reachable(self) -> None:
        status, _ = self.request("/api/stages/2")
        self.assertEqual(status, 409)
        status, payload = self.request("/api/flag")
        self.assertEqual(status, 403)
        self.assertNotIn("flag", payload)

        for stage_id, answer in ((1, "not-proven"), (2, "patched"), (3, "mitigated")):
            status, stage = self.request("/api/stages/{}".format(stage_id))
            self.assertEqual(status, 200)
            self.assertEqual(stage["mode"], "simulation")
            if stage_id == 2:
                self.assertIn("2.19-18+deb8u10", stage["evidence"])
            status, _ = self.request(
                "/api/stages/{}/submit".format(stage_id), {"answer": answer}
            )
            self.assertEqual(status, 200)
            status, payload = self.request("/api/flag")
            if stage_id < 3:
                self.assertEqual(status, 403)
                self.assertNotIn("flag", payload)

        self.assertEqual(status, 200)
        self.assertEqual(
            payload, {"principal": "archive", "flag": "HOSPITAL{test_only}"}
        )
        status, state = self.request("/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(state["score"], 100)
        status, repeated = self.request("/api/flag")
        self.assertEqual(status, 200)
        self.assertEqual(repeated["flag"], "HOSPITAL{test_only}")
        self.assertEqual(self.request("/api/status")[1]["score"], 100)
        status, other_session = self.request(
            "/api/status", session_id="b" * 32
        )
        self.assertEqual(status, 200)
        self.assertEqual(other_session["score"], 0)
        self.assertEqual(other_session["completed_stages"], [])

    def test_wrong_answer_and_out_of_order_submission_do_not_advance(self) -> None:
        status, _ = self.request(
            "/api/stages/1/submit", {"answer": "confirmed"}
        )
        self.assertEqual(status, 422)
        status, payload = self.request("/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(payload["completed_stages"], [])


if __name__ == "__main__":
    unittest.main()
