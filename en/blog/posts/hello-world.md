---
title: "Hello World: Building a Multilingual Blog and Home Page"
category: "Engineering"
date: "Aug 11, 2026"
read_time: "3 min read"
---

Welcome to the first post on my new blog! I want to share a behind-the-scenes look at how this site is built, the reasoning behind my technology choices, and where I plan to take it next.

## How This Project Works

This blog is built from the ground up to be lightweight, easy to maintain, and automatically translated into multiple languages. Here is the breakdown of the architecture:

- **Static Site Hosting:** The site is hosted on GitHub Pages, ensuring high availability, speed, no server maintenance, high security, and zero hosting costs.
- **Content Creation:** All posts are written in standard Markdown (`.md` files) which makes formatting effortless and keeps the content independent of the presentation layer.
- **Build Pipeline:** When I push a new Markdown file to the `main` branch, a GitHub Actions workflow kicks off. A custom Python script (`build_blog.py`) reads the Markdown, extracts the YAML frontmatter, and injects the parsed HTML into a sleek, glassmorphism-styled template.
- **Automated Translation:** Another Python script (`translate.py`) detects changes and uses `deep-translator` to translate the new content.
- **LLM Review:** Simple machine translation can sometimes miss nuances. To ensure high quality, I've integrated Gemini (`llm_review.py`) to review and refine the translations. The workflow then automatically creates a Pull Request with the translated HTML files, ready for my final approval.

## Why I Chose This Tooling

When deciding on the stack, I had a few key priorities: **Simplicity, Speed, and Automation**.

1. **No Database, No Headaches:** By choosing a static site approach over a CMS like WordPress, I eliminated database management, security vulnerabilities (like [CVE-2026-63030 + CVE-2026-60137](https://github.com/0xsha/wp2shell)), and slow page loads.
2. **Python for the Pipeline:** Python is perfect for scripting build and translation tasks. Libraries like `BeautifulSoup4` for parsing HTML, `PyYAML` for frontmatter, and the `google-genai` SDK for the LLM review made the implementation straightforward and maintainable.
3. **AI-Powered Localization:** Manually translating technical posts is time-consuming. Leveraging standard translation APIs backed by an LLM review gives me the best of both worlds: speed and linguistic accuracy, allowing me to reach a wider audience effortlessly.

## What Comes Next

Now that the core infrastructure is up and running, here is what I have planned:

- **More Content:** Expect more posts about my projects, software engineering deep dives, tutorials and rants on technical and especially security and AI topics.
- **Enhanced Styling:** While I love the current dark-mode glassmorphism aesthetic, I plan to potentially add a light-mode toggle.
- **Interactive Elements:** I might add client-side search and filtering for the blog posts as the content grows.

Thanks for stopping by, and stay tuned for more!
