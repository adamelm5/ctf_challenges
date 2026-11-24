const challenge = document.querySelector("#challenge");
const score = document.querySelector("#score");
const steps = document.querySelector("#steps");
const notice = document.querySelector("#notice");

async function api(path, payload) {
  const response = await fetch(path, {
    method: payload ? "POST" : "GET",
    headers: payload ? { "Content-Type": "application/json" } : {},
    body: payload ? JSON.stringify(payload) : undefined,
    cache: "no-store",
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `Erreur HTTP ${response.status}`);
  }
  return data;
}

function text(tag, value, className) {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
}

async function render() {
  try {
    const state = await api("/api/status");
    score.textContent = `Score : ${state.score} / ${state.max_score}`;
    steps.textContent = `Étapes validées : ${state.completed_stages.length} / 3`;
    challenge.replaceChildren();

    if (state.next_stage === null) {
      challenge.append(text("h2", "Parcours terminé"));
      challenge.append(text("p", "Les trois analyses sont validées. Le flag est accessible dans le contexte archive."));
      const button = text("button", "Lire le flag");
      button.type = "button";
      button.addEventListener("click", async () => {
        try {
          const result = await api("/api/flag");
          challenge.append(text("p", `Principal : ${result.principal}`, "principal"));
          challenge.append(text("pre", result.flag, "flag"));
          const updated = await api("/api/status");
          score.textContent = `Score : ${updated.score} / ${updated.max_score}`;
          button.disabled = true;
        } catch (error) {
          notice.textContent = error.message;
        }
      });
      challenge.append(button);
      return;
    }

    const stage = await api(`/api/stages/${state.next_stage}`);
    challenge.append(text("p", `ÉTAPE ${stage.id} · ${stage.component}`, "eyebrow"));
    challenge.append(text("h2", stage.title));
    challenge.append(text("p", stage.evidence, "evidence"));
    challenge.append(text("h3", stage.question));
    const form = document.createElement("form");
    for (const [index, option] of stage.options.entries()) {
      const label = document.createElement("label");
      label.className = "option";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = "answer";
      input.value = option.value;
      input.required = index === 0;
      label.append(input, document.createTextNode(option.label));
      form.append(label);
    }
    const submit = text("button", "Valider l’analyse");
    submit.type = "submit";
    form.append(submit);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const selected = form.querySelector('input[name="answer"]:checked');
      if (!selected) return;
      try {
        await api(`/api/stages/${stage.id}/submit`, { answer: selected.value });
        notice.textContent = "Étape validée.";
        await render();
      } catch (error) {
        notice.textContent = error.message;
      }
    });
    challenge.append(form);
    notice.textContent = "";
  } catch (error) {
    challenge.replaceChildren(text("p", `Service indisponible : ${error.message}`));
  }
}

render();
