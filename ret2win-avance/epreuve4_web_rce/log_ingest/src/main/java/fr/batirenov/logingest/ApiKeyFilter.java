package fr.batirenov.logingest;

import org.springframework.stereotype.Component;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Vérifie le header X-Api-Key sur toutes les routes sauf /api/health.
 * La clé attendue vient de la variable d'environnement API_KEY (voir .env,
 * généré par init_env.sh et partagé avec config_sync.py).
 */
@Component
public class ApiKeyFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest httpReq = (HttpServletRequest) req;
        HttpServletResponse httpRes = (HttpServletResponse) res;

        if ("/api/health".equals(httpReq.getRequestURI())) {
            chain.doFilter(req, res);
            return;
        }

        String expected = System.getenv("API_KEY");
        String provided = httpReq.getHeader("X-Api-Key");

        if (expected == null || provided == null || !expected.equals(provided)) {
            httpRes.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid API key");
            return;
        }

        chain.doFilter(req, res);
    }
}
