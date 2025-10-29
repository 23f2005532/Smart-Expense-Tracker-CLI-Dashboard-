<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-md p-8">
      <h2 class="text-2xl font-semibold text-center mb-6">Welcome back</h2>

      <form @submit.prevent="onSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input
            v-model="email"
            type="email"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2"
            autocomplete="email"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input
            v-model="password"
            type="password"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2"
            autocomplete="current-password"
          />
        </div>

        <div class="flex items-center justify-between">
          <div class="text-sm">
            <router-link to="/forgot-password" class="text-blue-600 hover:underline">Forgot?</router-link>
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">{{ error }}</div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full mt-2 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md"
        >
          <span v-if="!loading">Log in</span>
          <span v-else>Logging in...</span>
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-4">
        Don't have an account?
        <router-link to="/register" class="text-blue-600 hover:underline">Create one</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useAuthStore } from "../store/auth"

const auth = useAuthStore()
const email = ref("")
const password = ref("")
const loading = computed(() => auth.loading)
const error = computed(() => auth.error)

const onSubmit = async () => {
  try {
    await auth.login(email.value, password.value)
  } catch (err) {
    // error is set in store; no-op here
  }
}
</script>

<style scoped>
/* small page-level styles */
</style>
