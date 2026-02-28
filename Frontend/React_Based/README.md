# React_Based (Production UI) - EVA Data Science OS

This directory contains the production-ready frontend for EVA, built using Next.js (App Router), React, TypeScript, and Tailwind CSS.

## Experience & Aesthetics
The UI follows strict design guidelines outlined in the `EVA_Master_Website_Prompt.md`:
- **Cinematic & Technical**: Premium AI tool experience, highly polished.
- **Dark Mode Only**: Deep black backgrounds (OLED style).
- **Primary Colors**: Black (`#000000`), Primary Blue (`#3B82F6`), CTA Orange (`#F97316`).
- **Typography**: Fira Code / Fira Sans.
- **Animations**: Smooth reverse parallax motions, micro-interactions, and WebP frame sequences for the AI "Brain".

## Quick Start

### 1. Requirements
Ensure you have Node.js and npm installed.

### 2. Installation
Navigate to this directory and install the required standard dependencies:
```powershell
npm install
```

### 3. Running the Development Server
```powershell
npm run dev
```
The application will be available at `http://localhost:3000`.

## Architecture & Structure

| Directory | Description |
|-----------|-------------|
| `app/` | Next.js app router structure containing pages and global layouts. |
| `components/` | Modular, reusable UI components including the reverse parallax hero and chat interfaces. |
| `hooks/` | Custom React hooks for data fetching, SSE handling, and global state. |
| `lib/` | Utility functions, API connectors, and constants. |
| `styles/` | Global CSS and Tailwind configuration imports. |
| `public/` | Static assets like WebP sequences, fonts, and images. |
| `types/` | Global TypeScript definitions and interfaces mapping to the GAL schema. |

## Configuration
Tailwind configuration and global theme settings are managed via `tailwind.config.ts` (if available) and `app/globals.css`.

## Development Guidelines
- Strictly adhere to the cinematic, minimal, "Hacker aesthetic" style. No visual clutter.
- All animations should be smooth and performant. Component structure must support fluid scroll and transition effects.
- Implement strictly decoupled API calls referencing the Python Backend (`http://localhost:8000`).

## License
MIT
