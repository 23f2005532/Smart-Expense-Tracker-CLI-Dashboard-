import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: () => import("../pages/Auth/LoginView.vue") },
  {
    path: "/register",
    component: () => import("../pages/Auth/RegisterView.vue"),
  },
  {
    path: "/dashboard",
    component: () => import("../pages/Dashboard/OverviewView.vue"),
  },
  {
    path: "/:pathMatch(.*)*",
    component: () => import("../pages/NotFoundView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
