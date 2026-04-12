export default defineAppConfig({
    docus: {
        title: "Sysplant",
        description: "Your syscall factory — generate Windows syscall bypasses in C, C++, NIM, and Rust with 7 gate iterators and 4 caller methods.",
        url: "https://docs.circle-cyber.com/sysplant",
        image: "/cover.png",
        socials: {
            github: "x42en/sysplant",
        },
        github: {
            dir: "docs-site/content",
            branch: "main",
            repo: "sysplant",
            owner: "x42en",
            edit: true,
        },
        aside: {
            level: 1,
            collapsed: false,
        },
        header: {
            logo: true,
            showLinkIcon: true,
        },
        footer: {
            iconLinks: [
                {
                    href: "https://github.com/x42en/sysplant",
                    icon: "simple-icons:github",
                },
            ],
        },
    },
})
