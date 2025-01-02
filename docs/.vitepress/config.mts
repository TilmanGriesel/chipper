import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Chipper",
  description: "AI interface for tinkerers (Ollama, Haystack RAG, Python)",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Get Started', link: '/get-started' },
      { text: 'Demo', link: '/demo' }
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/TilmanGriesel/chipper' }
    ]
  }
})
