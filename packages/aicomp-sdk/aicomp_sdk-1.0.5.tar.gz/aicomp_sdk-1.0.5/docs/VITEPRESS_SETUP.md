# VitePress Documentation Setup

This directory contains the VitePress-powered documentation website for the JED Framework.

## Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd docs
npm install
```

## Development

### Local Development Server

```bash
cd docs
npm run docs:dev
```

This starts a local development server at `http://localhost:5173` with:
- Hot module replacement (HMR)
- Live preview of changes
- Full-text search

### Build for Production

```bash
cd docs
npm run docs:build
```

Generates static files in `docs/.vitepress/dist/`

### Preview Production Build

```bash
cd docs
npm run docs:preview
```

## Project Structure

```
docs/
├── .vitepress/
│   ├── config.ts          # VitePress configuration
│   ├── dist/              # Build output (gitignored)
│   └── cache/             # Build cache (gitignored)
├── index.md               # Home page
├── GETTING_STARTED.md     # Getting started guide
├── GUARDRAILS_GUIDE.md    # Guardrails guide
├── ATTACKS_GUIDE.md       # Attacks guide
├── API_REFERENCE.md       # API reference
├── SCORING.md             # Scoring system
├── COMPETITION_RULES.md   # Competition rules
├── FAQ.md                 # FAQ
└── ...                    # Other documentation files
```

## Configuration

The VitePress configuration is in `docs/.vitepress/config.ts`:

- **Base URL**: `/competitionscratch/` (GitHub Pages)
- **Theme**: Custom sidebar with organized sections
- **Features**: Search, edit links, dark mode, line numbers
- **Navigation**: Top nav + sidebar for easy browsing

## Deployment

### GitHub Pages (Automatic)

Documentation is automatically deployed to GitHub Pages when changes are pushed to the `master` branch:

1. GitHub Actions workflow (`.github/workflows/deploy-docs.yml`) triggers
2. VitePress builds the static site
3. Deploys to `https://mbhatt1.github.io/competitionscratch/`

### Manual Deployment

To deploy manually:

```bash
cd docs
npm run docs:build
# Upload docs/.vitepress/dist/ to your hosting provider
```

## Features

### Search
Full-text search is enabled using VitePress's built-in local search.

### Dark Mode
Automatic dark mode support with theme toggle.

### Mobile Responsive
Optimized for mobile devices with responsive sidebar.

### Edit on GitHub
Each page has an "Edit on GitHub" link for easy contributions.

### Code Highlighting
Syntax highlighting for Python, bash, JSON, and more.

## Customization

### Adding New Pages

1. Create a new `.md` file in the `docs/` directory
2. Add the page to the sidebar in `docs/.vitepress/config.ts`
3. Link to it from other pages as needed

### Modifying Navigation

Edit `docs/.vitepress/config.ts`:

```typescript
nav: [
  { text: 'Home', link: '/' },
  { text: 'New Page', link: '/NEW_PAGE' }
]
```

### Modifying Sidebar

Edit `docs/.vitepress/config.ts`:

```typescript
sidebar: [
  {
    text: 'New Section',
    items: [
      { text: 'New Page', link: '/NEW_PAGE' }
    ]
  }
]
```

## Troubleshooting

### Port Already in Use

If port 5173 is already in use:

```bash
npx vitepress dev --port 5174
```

### Build Errors

Clear the cache and rebuild:

```bash
rm -rf docs/.vitepress/cache docs/.vitepress/dist
npm run docs:build
```

### TypeScript Errors in config.ts

The TypeScript error is normal in development. VitePress will be installed when you run `npm install`.

## Links

- **VitePress Documentation**: https://vitepress.dev/
- **GitHub Repository**: https://github.com/mbhatt1/competitionscratch
- **Live Documentation**: https://mbhatt1.github.io/competitionscratch/

## Contributing

To contribute to the documentation:

1. Edit the relevant `.md` files
2. Test locally with `npm run docs:dev`
3. Submit a pull request

All documentation follows Markdown syntax with VitePress extensions.
