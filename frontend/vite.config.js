import { resolve } from 'node:path'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'
import Inspect from 'vite-plugin-inspect'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      include: [
        /\.[tj]sx?$/,
        /\.vue$/,
        /\.vue\?vue/,
      ],
      imports: [
        'vue',
        'vue-router',
        '@vueuse/core',
        {
          pinia: [
            'defineStore',
          ],
        },
      ],
      dts: true,
      dirs: [
        './src/composables/**/*.js',
        './src/store/**',
        './src/utils/**',
      ],
      vueTemplate: true,
      dumpUnimportItems: true,
      viteOptimizeDeps: true,
    }),

    Inspect(),
    Components({
      extensions: ['vue'],
      dts: true,
      include: [/\.vue$/],
    }),
  ],
  resolve: {
    alias: [
      { find: '@/', replacement: `${resolve(__dirname, 'src')}/`,
      },
    ],
  },
})
