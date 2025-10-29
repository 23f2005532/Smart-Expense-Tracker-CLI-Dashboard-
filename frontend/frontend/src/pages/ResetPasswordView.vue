<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-md p-8">
      <h2 class="text-2xl font-semibold text-center mb-6">Set a new password</h2>

      <form @submit.prevent="onSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">New password</label>
          <input v-model="password" type="password" minlength="6" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Confirm password</label>
          <input v-model="confirmPassword" type="password" minlength="6" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2" />
        </div>

        <div v-if="passwordMismatch" class="text-red-600 text-sm text-center">Passwords do not match</div>
        <div v-if="error" class="text-red-600 text-sm text-center">{{ error }}</div>
        <div v-if="message" class="text-green-600 text-sm text-center">{{ message }}</div>

        <button type="submit" :disabled="loading || passwordMismatch" class="w-full mt-2 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md">
          <span v-if="!loading">Reset password</span>
          <span v-else>Processing...</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRoute } from "vue-router"
import { useAuthStore } from "../store/auth"

const route = useRoute()
const token = route.query.token || ""
const auth = useAuthStore()

const password = ref("")
const confirmPassword = ref("")
const passwordMismatch = computed(() => password.value !== confirmPassword.value)
const loading = computed(() => auth.loading)
const error = computed(() => auth.error)
const message = ref(null)

const onSubmit = async () => {
  try {
    await auth.confirmPasswordReset(token, password.value)
    message.value = "Password reset successful. Redirecting to login..."
    setTimeout(() => (window.location.href = "/login"), 1500)
  } catch (err) {
    // auth.error set
  }
}
</script>
