<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-md p-8">
      <h2 class="text-2xl font-semibold text-center mb-6">Create account</h2>

      <form @submit.prevent="onSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Full name</label>
          <input v-model="name" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input v-model="email" type="email" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input v-model="password" type="password" minlength="6" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Confirm password</label>
          <input v-model="confirmPassword" type="password" minlength="6" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2" />
        </div>

        <div v-if="passwordMismatch" class="text-red-600 text-sm text-center">Passwords do not match</div>
        <div v-if="error" class="text-red-600 text-sm text-center">{{ error }}</div>

        <button type="submit" :disabled="loading || passwordMismatch" class="w-full mt-2 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md">
          <span v-if="!loading">Create account</span>
          <span v-else>Creating...</span>
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-4">
        Already have an account?
        <router-link to="/login" class="text-blue-600 hover:underline">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useAuthStore } from "../store/auth"

const auth = useAuthStore()
const name = ref("")
const email = ref("")
const password = ref("")
const confirmPassword = ref("")

const passwordMismatch = computed(() => password.value !== confirmPassword.value)
const loading = computed(() => auth.loading)
const error = computed(() => auth.error)

const onSubmit = async () => {
  if (passwordMismatch.value) return
  try {
    await auth.register(name.value, email.value, password.value)
  } catch (err) {
    // store holds error
  }
}
</script>

<style scoped></style>
