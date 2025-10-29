<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-md p-8">
      <h2 class="text-2xl font-semibold text-center mb-6">Reset password</h2>

      <form @submit.prevent="onSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input v-model="email" type="email" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2" />
        </div>

        <div v-if="message" class="text-green-600 text-sm text-center">{{ message }}</div>
        <div v-if="error" class="text-red-600 text-sm text-center">{{ error }}</div>

        <button type="submit" :disabled="loading" class="w-full mt-2 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md">
          <span v-if="!loading">Send reset link</span>
          <span v-else>Sending...</span>
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-4">
        Back to
        <router-link to="/login" class="text-blue-600 hover:underline">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useAuthStore } from "../store/auth"

const auth = useAuthStore()
const email = ref("")
const message = ref(null)
const loading = computed(() => auth.loading)
const error = computed(() => auth.error)

const onSubmit = async () => {
  message.value = null
  try {
    const res = await auth.requestPasswordReset(email.value)
    // backend for dev returns reset token; in prod you would NOT show token
    message.value = res.reset_token_dev ? `Reset token (dev): ${res.reset_token_dev}` : "If account exists, password reset link sent."
  } catch (err) {
    // auth.error is set by store
  }
}
</script>
