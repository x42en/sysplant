export default defineNuxtConfig({
    extends: ["docus"],
    devtools: { enabled: false },

    app: {
        baseURL: process.env.NUXT_APP_BASE_URL ?? "/",
        head: {
            charset: "utf-8",
            viewport: "width=device-width, initial-scale=1",
            title: "Sysplant",
            link: [
                { rel: "icon", type: "image/svg+xml", href: "logo.svg" },
            ],
        },
    },

    nitro: {
        prerender: {
            failOnError: false,
        },
    },

    compatibilityDate: "2025-05-01",
})
