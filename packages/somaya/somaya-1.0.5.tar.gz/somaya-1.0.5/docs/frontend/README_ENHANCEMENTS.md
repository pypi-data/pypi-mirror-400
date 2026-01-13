# SOMA Frontend Enhancements

This document outlines the production-grade enhancements applied to the SOMA frontend.

## 🚀 New Features

### 1. **Custom Hooks**
- `useDPR()` - Detects device pixel ratio for optimal image selection
- `usePrefersReducedMotion()` - Respects user's motion preferences
- `useScrollLock()` - Locks body scroll for modals/menus

### 2. **PWA Support**
- Service Worker for offline functionality
- App manifest for installability
- Offline page at `/offline`
- Runtime caching strategies

### 3. **ResponsiveImage Component**
- DPR-aware image loading (1x, 2x, 3x)
- Format fallback (AVIF → WebP → JPG)
- Next.js Image optimization
- Loading states and error handling

### 4. **Accessibility Improvements**
- Skip link for keyboard navigation
- Proper ARIA labels
- Semantic HTML structure
- Keyboard navigation support
- Reduced motion support

### 5. **Design Tokens**
- Comprehensive CSS custom properties
- Fluid typography with clamp()
- Consistent spacing scale
- Dark mode support
- High DPR optimizations

### 6. **Performance Optimizations**
- Critical CSS inline
- Image optimization (AVIF, WebP)
- Font preloading
- Bundle optimization
- Security headers

### 7. **Testing Setup**
- Jest + React Testing Library (unit tests)
- Playwright (E2E tests)
- Test configurations ready

## 📦 Installation

### Install Dependencies

```bash
npm install
```

### Install PWA Dependencies

```bash
npm install next-pwa
```

### Install Testing Dependencies

```bash
npm install --save-dev @playwright/test @testing-library/jest-dom @testing-library/react @testing-library/user-event @types/jest jest jest-environment-jsdom
```

## 🧪 Testing

### Unit Tests
```bash
npm test
npm run test:watch
```

### E2E Tests
```bash
npm run test:e2e
npm run test:e2e:ui
```

## 🎨 Usage Examples

### ResponsiveImage Component

```tsx
import { ResponsiveImage } from '@/components/responsive-image'

<ResponsiveImage
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  srcSet={{
    '1x': '/hero@1x.jpg',
    '2x': '/hero@2x.jpg',
    '3x': '/hero@3x.jpg'
  }}
  avif="/hero.avif"
  webp="/hero.webp"
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  priority
/>
```

### Using Custom Hooks

```tsx
import { useDPR } from '@/hooks/useDPR'
import { usePrefersReducedMotion } from '@/hooks/usePrefersReducedMotion'
import { useScrollLock } from '@/hooks/useScrollLock'

function MyComponent() {
  const dpr = useDPR()
  const prefersReducedMotion = usePrefersReducedMotion()
  const [isModalOpen, setIsModalOpen] = useState(false)
  
  useScrollLock(isModalOpen)
  
  return (
    <motion.div
      animate={prefersReducedMotion ? {} : { scale: 1.1 }}
    >
      DPR: {dpr}x
    </motion.div>
  )
}
```

## 🔧 Configuration

### PWA Configuration

PWA is configured in `next.config.js` and is automatically disabled in development mode.

### Image Optimization

Configured in `next.config.js`:
- AVIF and WebP formats
- Multiple device sizes
- Minimum cache TTL

### Design Tokens

Located in `styles/design-tokens.css`:
- Color system
- Typography scale
- Spacing scale
- Shadows and transitions

## 📱 PWA Features

- **Installable**: Users can install SOMA as a PWA
- **Offline Support**: Basic functionality works offline
- **Caching**: Smart caching strategies for performance
- **Manifest**: Complete app manifest with icons and shortcuts

## ♿ Accessibility

- WCAG AA+ compliant
- Keyboard navigation
- Screen reader support
- Reduced motion support
- Focus management
- Semantic HTML

## 🚀 Performance Targets

- Lighthouse Performance: ≥ 95
- Lighthouse Accessibility: ≥ 95
- Lighthouse Best Practices: ≥ 95
- Lighthouse SEO: ≥ 95

## 📝 Notes

- PWA service worker is disabled in development
- All hooks are SSR-safe
- Images are optimized automatically
- Critical CSS is inlined for faster initial render

