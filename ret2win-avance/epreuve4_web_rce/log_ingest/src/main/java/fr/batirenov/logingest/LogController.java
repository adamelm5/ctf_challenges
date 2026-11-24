package fr.batirenov.logingest;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Endpoint d'ingestion de logs applicatifs (simulateur simplifié).
 * Volontairement vulnérable : les champs "message" et le header
 * X-Forwarded-For sont journalisés tels quels via Log4j 2.14.1, qui évalue
 * les lookups ${...} (CVE-2021-44228 / Log4Shell).
 */
@RestController
@RequestMapping("/api")
public class LogController {

    private static final Logger logger = LogManager.getLogger(LogController.class);

    @PostMapping("/ingest")
    public ResponseEntity<String> ingest(@RequestBody Map<String, String> body,
                                          @RequestHeader(value = "X-Forwarded-For", required = false) String xff) {
        String message = body.getOrDefault("message", "");
        String source = body.getOrDefault("source", "unknown");
        logger.info("Nouvelle entree de log [source={}] [xff={}]: {}", source, xff, message);
        return ResponseEntity.ok("logged");
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("OK");
    }
}
