import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Chipper",
  description: "AI interface for tinkerers (Ollama, Haystack RAG, Python)",
  head: [
    ['link', { rel: 'icon', href: '/assets/favicon/favicon.ico' }],
    ['link', { rel: "shortcut icon", href: "/assets/favicons/favicon.ico"}],
    ['link', { rel: "apple-touch-icon", sizes: "180x180", href: "/assets/favicons/apple-touch-icon.png"}],
    ['link', { rel: "icon", type: "image/png", sizes: "96x96", href: "/assets/favicons/favicon-96x96.png"}],
    ['link', { rel: "icon", type: "image/png", sizes: "192x192", href: "/assets/favicons/favicon-192x192.png"}],
    ['link', { rel: "icon", type: "image/png", sizes: "512x512", href: "/assets/favicons/favicon-512x512.png"}],
    ['link', { rel: "manifest", href: "/assets/favicons/site.webmanifest"}],
    ['meta', { property: "og:image", content: "/assets/social.png"}],
  ],
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
