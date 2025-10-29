// src/store/auth.js
import { defineStore } from "pinia"
import http from "../api/http"
import router from "../router"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("user") || "null"),
    token: localStorage.getItem("token") || null,
    loading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
    isAdmin: (s) => s.user?.role === "admin",
  },
  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem("token", token)
      localStorage.setItem("user", JSON.stringify(user))
      http.defaults.headers.common["Authorization"] = `Bearer ${token}`
    },
    clearAuth() {
      this.token = null
      this.user = null
      localStorage.removeItem("token")
      localStorage.removeItem("user")
      delete http.defaults.headers.common["Authorization"]
    },

    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const res = await http.post("/api/login", { email, password })
        // backend might use /api/auth/login; adjust path if needed
        // check returned shape
        const token = res.data.access_token || res.data.token || res.data.accessToken
        const user = res.data.user
        if (!token) throw new Error("No token in response")
        this.setAuth(token, user)
        router.push("/dashboard")
        return res
      } catch (err) {
        this.error = err.response?.data?.message || err.message || "Login failed"
        throw err
      } finally {
        this.loading = false
      }
    },

    async register(name, email, password) {
      this.loading = true
      this.error = null
      try {
        const res = await http.post("/api/register", { name, email, password })
        const token = res.data.access_token || res.data.token || res.data.accessToken
        const user = res.data.user
        if (!token) throw new Error("No token in response")
        this.setAuth(token, user)
        router.push("/dashboard")
        return res
      } catch (err) {
        this.error = err.response?.data?.message || err.message || "Registration failed"
        throw err
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        // attempt to call backend logout if exists
        await http.post("/api/logout").catch(() => {})
      } finally {
        this.clearAuth()
        router.push("/login")
      }
    },

    async requestPasswordReset(email) {
      this.loading = true
      this.error = null
      try {
        const res = await http.post("/api/password-reset/request", { email })
        return res.data
      } catch (err) {
        this.error = err.response?.data?.message || err.message || "Request failed"
        throw err
      } finally {
        this.loading = false
      }
    },

    async confirmPasswordReset(token, newPassword) {
      this.loading = true
      this.error = null
      try {
        const res = await http.post("/api/password-reset/confirm", { token, password: newPassword })
        return res.data
      } catch (err) {
        this.error = err.response?.data?.message || err.message || "Reset failed"
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
