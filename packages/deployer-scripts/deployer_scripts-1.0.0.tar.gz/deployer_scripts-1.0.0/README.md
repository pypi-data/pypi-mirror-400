# deployer-scripts

Web application deployment scripts for Claude Code.

## Installation

```bash
pip install deployer-scripts
```

## Commands

```bash
# Detect project framework and generate app-deploy.json
deploy-detect /path/to/project

# Package project into tar.gz
deploy-pack /path/to/project "" myapp 1.0.0

# Upload package to server
deploy-upload /tmp/myapp.tar.gz --server-url http://... --api-key xxx
```

## Supported Frameworks

- **Node.js**: Next.js, Vite, Express, Fastify, Remix, Astro, SvelteKit, Nuxt
- **Python**: Flask, FastAPI, Streamlit
