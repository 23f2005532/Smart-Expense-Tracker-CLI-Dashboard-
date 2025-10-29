import { createRouter, createWebHistory } from "vue-router";

const LoginView = () => import("../pages/LoginView.vue");
const RegisterView = () => import("../pages/RegisterView.vue");
const DashboardView = () => import("../pages/DashboardView.vue");
const NotFound = () => import("../pages/NotFound.vue");
const ForgotPasswordView = () => import("../pages/ForgotPasswordView.vue");
const ResetPasswordView = () => import("../pages/ResetPasswordView.vue");

const routes = [
  { path: "/login", component: LoginView, meta: { guest: true } },
  { path: "/register", component: RegisterView, meta: { guest: true } },
  {
    path: "/dashboard",
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  { path: "/", redirect: "/dashboard" },
  { path: "/:pathMatch(.*)*", component: NotFound },
  {
    path: "/forgot-password",
    component: ForgotPasswordView,
    meta: { guest: true },
  },
  {
    path: "/reset-password",
    component: ResetPasswordView,
    meta: { guest: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuth = !!localStorage.getItem("token");
  if (to.meta.requiresAuth && !isAuth) next("/login");
  else if (to.meta.guest && isAuth) next("/dashboard");
  else next();
});

export default router;
