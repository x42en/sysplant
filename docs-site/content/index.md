---
title: Sysplant
navigation: false
layout: page
---

::u-page-hero
---
title: "Your Syscall Factory"
description: "Generate Windows syscall bypasses — 7 gate iterators, 4 caller methods, 4 output languages. Defeat EDR hooks with a single command."
orientation: horizontal
---
  #links
  ::u-button
  ---
  label: "Get started"
  to: /docs/getting-started/introduction
  size: xl
  ---
  ::
  ::u-button
  ---
  label: "View on GitHub"
  to: "https://github.com/x42en/sysplant"
  variant: outline
  target: "_blank"
  size: xl
  ---
  ::
::

::u-page-section
  #title
  Everything you need to bypass EDR syscall hooks

  #features
  ::u-page-feature
  ---
  icon: "i-lucide-git-branch"
  title: "7 Gate Iterators"
  ---
  Hell's Gate, Halo's Gate, Tartarus' Gate, FreshyCalls, SysWhispers2/3, and Canterlot's Gate — pick the technique that fits your target environment.
  ::

  ::u-page-feature
  ---
  icon: "i-lucide-cpu"
  title: "4 Caller Methods"
  ---
  Direct, indirect, random, and egg-hunter execution — control exactly how your syscall instruction gets invoked at runtime.
  ::

  ::u-page-feature
  ---
  icon: "i-lucide-code-2"
  title: "4 Output Languages"
  ---
  Generate native stubs in C, C++, NIM, or Rust. Each output file is drop-in ready for your cross-compiler pipeline.
  ::

  ::u-page-feature
  ---
  icon: "i-lucide-terminal"
  title: "CLI & Python Library"
  ---
  Use the `sysplant` CLI for one-shot generation, or embed the `Sysplant` class directly in your Python toolchain.
  ::

  ::u-page-feature
  ---
  icon: "i-lucide-bot"
  title: "MCP Server"
  ---
  AI-native integration via Model Context Protocol — generate stubs, scan code for Nt functions, and fetch prototypes straight from your LLM.
  ::

  ::u-page-feature
  ---
  icon: "i-lucide-shuffle"
  title: "Symbol Scrambling"
  ---
  Randomize all 23 internal `SPT_*` symbol names at generation time to defeat static signature matching in binary analysis tools.
  ::
::
