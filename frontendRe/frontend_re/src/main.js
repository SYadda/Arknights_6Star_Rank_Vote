import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import '@/styles/base.css'
import '@/styles/compare.css'
import '@/styles/table.css'
import '@/styles/transfer.css'

createApp(App).use(store).use(router).mount('#app')
