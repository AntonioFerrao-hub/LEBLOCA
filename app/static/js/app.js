const authSection = document.getElementById("auth-section");
const dashboardSection = document.getElementById("dashboard");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const userInfo = document.getElementById("user-info");
const userName = document.getElementById("user-name");
const logoutButton = document.getElementById("logout");
const accountsGrid = document.getElementById("accounts-grid");
const newAccountButton = document.getElementById("new-account-button");
const accountDialog = document.getElementById("account-dialog");
const toast = document.getElementById("toast");
const cancelAccountButton = document.getElementById("cancel-account");

let currentToken = localStorage.getItem("accessToken");
let editingAccountId = null;

function showToast(message, type = "info") {
  toast.textContent = message;
  toast.classList.remove("hidden", "toast-visible");
  toast.classList.add("toast-visible");
  if (type === "error") {
    toast.style.borderColor = "rgba(248, 113, 113, 0.4)";
    toast.style.background = "rgba(239, 68, 68, 0.15)";
  } else {
    toast.style.borderColor = "rgba(59, 130, 246, 0.4)";
    toast.style.background = "rgba(59, 130, 246, 0.15)";
  }
  setTimeout(() => toast.classList.add("hidden"), 4000);
}

function setAuthState(isAuthenticated, user = null) {
  if (isAuthenticated) {
    authSection.classList.add("hidden");
    dashboardSection.classList.remove("hidden");
    userInfo.classList.remove("hidden");
    userName.textContent = user?.name ?? "";
    fetchAccounts();
  } else {
    authSection.classList.remove("hidden");
    dashboardSection.classList.add("hidden");
    userInfo.classList.add("hidden");
    userName.textContent = "";
    accountsGrid.innerHTML = "";
    localStorage.removeItem("accessToken");
    localStorage.removeItem("userName");
    currentToken = null;
  }
}

async function request(path, options = {}) {
  const headers = options.headers ?? {};
  if (currentToken) {
    headers["Authorization"] = `Bearer ${currentToken}`;
  }
  headers["Content-Type"] = "application/json";

  const response = await fetch(path, { ...options, headers });
  const contentType = response.headers.get("content-type");
  const data = contentType?.includes("application/json") ? await response.json() : null;
  if (!response.ok) {
    throw new Error(data?.message ?? "Erro ao processar a requisição.");
  }
  return data;
}

async function handleLogin(event) {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const data = await request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    currentToken = data.access_token;
    localStorage.setItem("accessToken", currentToken);
    localStorage.setItem("userName", data.user.name);
    setAuthState(true, data.user);
    showToast("Bem-vindo de volta!", "success");
    loginForm.reset();
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const formData = new FormData(registerForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    await request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast("Cadastro realizado! Agora entre com seu login.");
    registerForm.reset();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function openAccountDialog(account = null) {
  editingAccountId = account?.id ?? null;
  const form = accountDialog.querySelector("form");
  form.reset();
  if (account) {
    form.display_name.value = account.display_name;
    form.account_id.value = account.account_id;
    form.location_id.value = account.location_id;
    form.refresh_token.value = account.refresh_token;
    form.settings.value = JSON.stringify(account.settings ?? {}, null, 2);
  }
  accountDialog.showModal();
}

async function handleAccountSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const payload = {
    display_name: form.display_name.value.trim(),
    account_id: form.account_id.value.trim(),
    location_id: form.location_id.value.trim(),
    refresh_token: form.refresh_token.value.trim(),
  };

  if (form.settings.value) {
    try {
      payload.settings = JSON.parse(form.settings.value);
    } catch (error) {
      showToast("Configurações precisam ser um JSON válido.", "error");
      return;
    }
  }

  try {
    const method = editingAccountId ? "PUT" : "POST";
    const url = editingAccountId
      ? `/api/google-accounts/${editingAccountId}`
      : "/api/google-accounts";
    await request(url, { method, body: JSON.stringify(payload) });
    accountDialog.close();
    await fetchAccounts();
    showToast("Conta salva com sucesso!", "success");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function fetchAccounts() {
  try {
    const accounts = await request("/api/google-accounts");
    renderAccounts(accounts);
  } catch (error) {
    showToast(error.message, "error");
    if (error.message.includes("não encontrado")) {
      setAuthState(false);
    }
  }
}

function renderAccounts(accounts) {
  if (!accounts.length) {
    accountsGrid.innerHTML = `<div class="card text-center text-sm text-slate-300">Nenhuma conta cadastrada ainda. Clique em "Adicionar conta" para começar.</div>`;
    return;
  }

  accountsGrid.innerHTML = "";
  accounts.forEach((account) => {
    const totalReviews = account.reviews.length;
    const positive = account.reviews.filter((review) => review.rating >= 4).length;
    const neutral = account.reviews.filter((review) => review.rating === 3).length;
    const negative = totalReviews - positive - neutral;

    const card = document.createElement("div");
    card.className = "card space-y-6";
    card.innerHTML = `
      <div class="flex items-start justify-between">
        <div>
          <h3 class="text-lg font-semibold">${account.display_name}</h3>
          <p class="mt-1 text-xs text-slate-400">Location ID: ${account.location_id}</p>
        </div>
        <div class="flex gap-2">
          <button class="btn btn-ghost text-[10px]" data-action="edit">Editar</button>
          <button class="btn btn-ghost text-[10px]" data-action="sync">Sincronizar</button>
          <button class="btn btn-ghost text-[10px]" data-action="delete">Excluir</button>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-3 text-xs text-slate-300">
        <span class="badge badge-positive">${positive} Positivas</span>
        <span class="badge badge-neutral">${neutral} Neutras</span>
        <span class="badge badge-negative">${negative} Negativas</span>
        <span class="ml-auto text-[11px] uppercase tracking-widest text-slate-500">Total: ${totalReviews}</span>
      </div>
      <div class="space-y-3 text-sm text-slate-300">
        ${account.reviews
          .slice(0, 3)
          .map(
            (review) => `
              <div class="rounded-xl border border-white/5 bg-white/5 p-3">
                <div class="flex items-center justify-between text-xs text-slate-400">
                  <span>${review.reviewer_name ?? "Anônimo"}</span>
                  <span>${"★".repeat(review.rating)}${"☆".repeat(Math.max(0, 5 - review.rating))}</span>
                </div>
                <p class="mt-2 text-sm text-slate-200">${review.comment ?? "(Sem comentário)"}</p>
              </div>
            `
          )
          .join("") || '<div class="text-xs text-slate-400">Sem avaliações sincronizadas ainda.</div>'}
      </div>
    `;

    card.querySelector('[data-action="edit"]').addEventListener("click", () => openAccountDialog(account));
    card.querySelector('[data-action="delete"]').addEventListener("click", () => deleteAccount(account.id));
    card.querySelector('[data-action="sync"]').addEventListener("click", () => syncAccount(account.id));

    accountsGrid.appendChild(card);
  });
}

async function deleteAccount(id) {
  if (!confirm("Tem certeza que deseja remover esta conta?")) {
    return;
  }
  try {
    await request(`/api/google-accounts/${id}`, { method: "DELETE" });
    await fetchAccounts();
    showToast("Conta removida.");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function syncAccount(id) {
  try {
    await request(`/api/google-accounts/${id}/sync`, { method: "POST" });
    await fetchAccounts();
    showToast("Avaliações sincronizadas!", "success");
  } catch (error) {
    showToast(error.message, "error");
  }
}

loginForm.addEventListener("submit", handleLogin);
registerForm.addEventListener("submit", handleRegister);
logoutButton.addEventListener("click", () => setAuthState(false));
newAccountButton.addEventListener("click", () => openAccountDialog());
accountDialog.addEventListener("close", () => (editingAccountId = null));
accountDialog.querySelector("form").addEventListener("submit", handleAccountSubmit);
cancelAccountButton.addEventListener("click", () => accountDialog.close());

if (currentToken) {
  request("/api/google-accounts")
    .then((accounts) => {
      setAuthState(true, { name: localStorage.getItem("userName") ?? "" });
      renderAccounts(accounts);
    })
    .catch(() => setAuthState(false));
}
