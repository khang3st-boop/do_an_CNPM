document.addEventListener("DOMContentLoaded", () => {
    if (API.getToken()) {
        window.location.href = "/ui/guests";
        return;
    }

    const form = document.getElementById("loginForm");
    const btn = document.getElementById("loginBtn");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideError("loginError");
        btn.disabled = true;
        btn.textContent = "Đang đăng nhập...";

        try {
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const result = await API.login(email, password);

            API.setSession(result.data.token, result.data.user);

            if (["admin", "manager"].includes(result.data.user.role)) {
                window.location.href = "/ui/users";
            } else {
                window.location.href = "/ui/guests";
            }
        } catch (error) {
            showError("loginError", error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = "Đăng nhập";
        }
    });
});
