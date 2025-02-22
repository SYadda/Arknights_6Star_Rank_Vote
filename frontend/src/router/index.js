import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  }
]

export default createRouter({
  history: createWebHashHistory(),
  routes
})
