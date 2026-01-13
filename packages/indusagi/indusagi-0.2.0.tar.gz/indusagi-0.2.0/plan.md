# AI Mobile Company Website - Project Plan

## Project Overview
Build a modern, professional **multi-page website** for an AI mobile company using pure HTML, CSS, and JavaScript (no React). The website will showcase the company's AI-powered mobile products and services with a clean, tech-forward design.

## Design Philosophy
- **Modern & Clean**: Minimalist design with strategic use of whitespace
- **Mobile-First**: Fully responsive across all devices
- **Professional**: Corporate tech aesthetic with smooth animations
- **Accessible**: WCAG AA compliant with proper semantic HTML
- **Fast**: Optimized loading with vanilla JavaScript

## Folder Structure
```
ai-mobile-website/
├── index.html                 # Homepage
├── products.html              # Products page
├── about.html                 # About us page
├── contact.html               # Contact page
├── css/
│   ├── variables.css         # CSS variables (colors, fonts, spacing)
│   ├── reset.css             # CSS reset and base styles
│   ├── typography.css        # Font styles and heading system
│   ├── layout.css            # Grid, flexbox, container utilities
│   ├── components.css        # Buttons, cards, forms, badges
│   ├── navigation.css        # Header, footer, nav menu
│   └── pages.css             # Page-specific styles
├── js/
│   ├── main.js               # Core JavaScript functionality
│   ├── navigation.js         # Mobile menu, smooth scroll, active states
│   ├── animations.js         # Scroll animations, Intersection Observer
│   └── form-validation.js    # Contact form validation
├── assets/
│   ├── images/
│   │   ├── hero-bg.jpg
│   │   ├── logo.svg
│   │   └── product-*.jpg
│   └── icons/
│       └── *.svg
└── README.md
```

## Page Breakdown

### 1. Homepage (index.html)
**Purpose**: Create strong first impression, showcase key offerings

**Sections**:
- **Hero**: Compelling headline, subheadline, dual CTAs, animated background
- **Features**: 6 feature cards highlighting AI capabilities
- **Products Preview**: 3 featured products with "Learn More" links
- **Stats**: Animated counters (Users, Downloads, Countries, Satisfaction)
- **Testimonials**: 3 customer testimonials with photos
- **CTA Banner**: Final call-to-action section
- **Footer**: Links, social icons, newsletter signup

**Key Content**:
- Headline: "Transforming Mobile Experiences with AI"
- CTAs: "Explore Products" (primary), "Contact Us" (secondary)

### 2. Products Page (products.html)
**Purpose**: Showcase all AI mobile products in detail

**Sections**:
- **Page Header**: Title, breadcrumb, brief description
- **Category Filter**: All, AI Assistant, Productivity, Security, Health
- **Products Grid**: 8 product cards with:
  - Product image
  - Name and category badge
  - Description
  - Key features (3-4 bullet points)
  - Pricing (optional)
  - "Get Started" CTA
- **Feature Comparison**: Comparison table of top products
- **CTA Section**: Newsletter signup for product updates

**Default Products**:
1. NeuralVoice AI - Voice assistant
2. SmartLens Pro - AI camera
3. PredictiveType - Smart keyboard
4. HealthGuard AI - Health monitoring
5. NavMind Pro - AI navigation
6. SecureShield - Mobile security
7. FocusFlow - Productivity assistant
8. SleepSense AI - Sleep optimizer

### 3. About Page (about.html)
**Purpose**: Company story, mission, team, culture

**Sections**:
- **Hero**: Mission statement with background image
- **Our Story**: Timeline of company milestones
- **Mission & Values**: 6 core values with icons
- **Team**: 6-8 team members with photos, names, roles
- **Company Stats**: Animated counters
- **Awards & Recognition**: Logo strip of awards
- **Careers CTA**: "Join Our Team" section

**Team Members** (default):
- CEO, CTO, Product Lead, Head of AI, Design Director, etc.

### 4. Contact Page (contact.html)
**Purpose**: Lead generation and customer support

**Sections**:
- **Hero**: "Get in Touch" with contact info summary
- **Contact Form**: 
  - Name (required)
  - Email (required, validated)
  - Phone (optional)
  - Subject (dropdown)
  - Message (required, textarea)
  - Submit button with loading state
- **Contact Information**:
  - Email address
  - Phone number
  - Office address
  - Working hours
- **FAQ Accordion**: 6-8 common questions
- **Social Media Links**: With icons
- **Map Placeholder**: Embedded map (iframe)

## Design System

### Color Palette
```css
/* Primary Colors */
--primary: #2563EB;        /* Royal Blue */
--primary-dark: #1E40AF;   /* Darker Blue */
--primary-light: #3B82F6;  /* Lighter Blue */

/* Secondary Colors */
--secondary: #7C3AED;      /* Purple */
--secondary-dark: #5B21B6;
--secondary-light: #8B5CF6;

/* Accent Colors */
--accent: #06B6D4;         /* Cyan */
--accent-gradient: linear-gradient(135deg, #2563EB, #7C3AED);

/* Neutral Colors */
--dark: #0F172A;           /* Navy - Backgrounds */
--dark-light: #1E293B;     /* Light Navy - Cards */
--gray: #64748B;           /* Gray - Muted text */
--light: #F8FAFC;          /* Off-white - Light backgrounds */
--white: #FFFFFF;          /* White - Cards, text */

/* Semantic Colors */
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
```

### Typography
```css
/* Font Families */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-display: 'Space Grotesk', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;   /* 12px */
--text-sm: 0.875rem;  /* 14px */
--text-base: 1rem;    /* 16px */
--text-lg: 1.125rem;  /* 18px */
--text-xl: 1.25rem;   /* 20px */
--text-2xl: 1.5rem;   /* 24px */
--text-3xl: 1.875rem; /* 30px */
--text-4xl: 2.25rem;  /* 36px */
--text-5xl: 3rem;     /* 48px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing System
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

### Components

#### Buttons
```css
/* Primary Button */
- Background: Gradient (primary to secondary)
- Text: White
- Padding: 12px 28px
- Border radius: 8px
- Hover: Lift effect, shadow increase
- Transition: All 0.3s ease

/* Secondary Button */
- Background: Transparent
- Border: 2px solid primary
- Text: Primary
- Hover: Background primary, text white
```

#### Cards
```css
- Background: White or dark-light
- Border radius: 12px
- Padding: 24px
- Shadow: Subtle (0 4px 6px rgba(0,0,0,0.1))
- Hover: Lift effect, shadow increase
- Transition: All 0.3s ease
```

#### Form Inputs
```css
- Background: White or dark-light
- Border: 1px solid gray
- Border radius: 6px
- Padding: 12px 16px
- Focus: Border color primary, box-shadow
- Transition: All 0.2s ease
```

## Implementation Steps

### Step 1: Project Setup (30 minutes)
1. Create folder structure
2. Set up HTML5 boilerplate for all 4 pages
3. Create CSS files (variables, reset, typography, layout, components, navigation, pages)
4. Create JavaScript files (main, navigation, animations, form-validation)
5. Set up external resources (Google Fonts, Font Awesome CDN)

### Step 2: Base CSS Foundation (45 minutes)
1. Define CSS variables in variables.css
2. Add CSS reset in reset.css
3. Set up typography system in typography.css
4. Create layout utilities in layout.css (container, grid, flex)
5. Build component styles in components.css (buttons, cards, forms)

### Step 3: Navigation Component (45 minutes)
1. Create header with logo and navigation menu
2. Build responsive mobile hamburger menu
3. Add smooth scroll to anchor links
4. Implement active state highlighting
5. Create footer with links and social icons

### Step 4: Homepage Development (2 hours)
1. Build hero section with gradient background
2. Create features grid (6 cards)
3. Build products preview section (3 cards)
4. Add animated stats counters
5. Create testimonials section (3 cards)
6. Build CTA banner
7. Add scroll-triggered animations

### Step 5: Products Page (1.5 hours)
1. Create page header with title
2. Build category filter with JavaScript
3. Create product cards grid (8 products)
4. Add hover effects and interactions
5. Build comparison table
6. Add newsletter signup CTA

### Step 6: About Page (1.5 hours)
1. Create hero section with mission
2. Build company timeline
3. Create values section with icons
4. Build team grid with photos
5. Add animated stats
6. Create awards section
7. Add careers CTA

### Step 7: Contact Page (1 hour)
1. Create hero section
2. Build contact form with validation
3. Add contact information section
4. Create FAQ accordion
5. Add social media links
6. Embed map placeholder

### Step 8: JavaScript Functionality (1.5 hours)
1. Implement mobile menu toggle
2. Add smooth scroll behavior
3. Create Intersection Observer for scroll animations
4. Build form validation with error messages
5. Add animated counters for stats
6. Implement category filter for products
7. Add FAQ accordion functionality

### Step 9: Responsive Design (1 hour)
1. Test and adjust for mobile (320px - 767px)
2. Test and adjust for tablet (768px - 1023px)
3. Test and adjust for desktop (1024px+)
4. Optimize touch interactions
5. Test on multiple devices/browsers

### Step 10: Content & Assets (45 minutes)
1. Add placeholder images (Lorem Picsum or similar)
2. Create SVG icons inline
3. Write compelling copy for all sections
4. Add realistic testimonials
5. Ensure consistent tone throughout

### Step 11: Testing & Polish (1 hour)
1. Cross-browser testing (Chrome, Firefox, Safari, Edge)
2. Device testing (iPhone, Android, tablet, desktop)
3. Accessibility audit (keyboard navigation, screen readers, ARIA)
4. Performance optimization (minify, compress images)
5. Final code cleanup and commenting
6. Validate HTML and CSS

## Technical Specifications

### HTML Standards
- Semantic HTML5 elements (header, nav, main, section, article, footer)
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA labels for accessibility
- Alt text for all images
- Meta tags for SEO and social sharing
- Structured data markup (JSON-LD)

### CSS Standards
- CSS custom properties (variables) for theming
- Flexbox and Grid for layouts
- Mobile-first media queries
- BEM naming convention (block__element--modifier)
- Smooth transitions (0.2s - 0.3s ease)
- Minimal use of !important

### JavaScript Standards
- ES6+ syntax (const/let, arrow functions, template literals)
- Modular code organization
- Event delegation for dynamic elements
- No jQuery or frameworks (vanilla JS only)
- Performance optimized (debounce, throttle, requestAnimationFrame)
- Error handling with try-catch

### Performance Targets
- Page load time: < 2 seconds
- First Contentful Paint: < 1 second
- Time to Interactive: < 3 seconds
- Lighthouse score: 90+ across all categories
- Minimal JavaScript bundle size

## Accessibility Features

### WCAG AA Compliance
- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support (Tab, Enter, Escape)
- Focus indicators on all interactive elements
- Skip to content link
- Proper color contrast (4.5:1 minimum)
- Alt text for all images
- Form labels and error messages
- Resizable text (up to 200% without breaking)

### Screen Reader Support
- Proper heading hierarchy
- Descriptive link text
- ARIA descriptions for icons
- Form validation announcements
- Live regions for dynamic content

## Browser Support
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile Safari iOS 12+
- Chrome Android

## Content Defaults

### Company Information
- **Name**: NeuralMobile AI
- **Tagline**: "Intelligent Mobile Solutions for Tomorrow"
- **Mission**: "Empowering users with AI-driven mobile experiences that enhance productivity, security, and everyday life."

### Default Copy Tone
- Professional yet approachable
- Focus on innovation and technology
- Emphasize user benefits
- Action-oriented CTAs
- Concise and scannable

### Placeholder Images
- Use placeholder services (Lorem Picsum, Unsplash Source)
- SVG icons created inline
- Consistent aspect ratios
- Optimized for web (WebP format when possible)

## Testing Checklist

### Functionality
- [ ] All navigation links work correctly
- [ ] Mobile menu opens/closes properly
- [ ] Smooth scrolling works on all pages
- [ ] Forms validate properly
- [ ] Form submission shows success/error messages
- [ ] Category filter works on products page
- [ ] FAQ accordion expands/collapses
- [ ] Animated counters trigger on scroll
- [ ] All buttons have hover/active states

### Responsive Design
- [ ] Mobile (320px - 767px) layouts work
- [ ] Tablet (768px - 1023px) layouts work
- [ ] Desktop (1024px+) layouts work
- [ ] Images scale properly
- [ ] Text doesn't overflow
- [ ] Touch targets are at least 44x44px

### Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader reads content correctly
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible
- [ ] Alt text present on all images
- [ ] Form labels are properly associated
- [ ] ARIA labels on interactive elements

### Performance
- [ ] Page loads in < 2 seconds
- [ ] No console errors
- [ ] Images are optimized
- [ ] CSS/JS is minified (production)
- [ ] Lazy loading implemented for images

### Cross-Browser
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works in Edge
- [ ] Works on iOS Safari
- [ ] Works on Chrome Android

## Success Criteria
1. ✅ All 4 pages fully functional and properly linked
2. ✅ Fully responsive across mobile, tablet, and desktop
3. ✅ Smooth animations and transitions throughout
4. ✅ Accessible to keyboard and screen reader users
5. ✅ Fast loading with optimized assets
6. ✅ Professional, modern design aesthetic
7. ✅ Cross-browser compatible
8. ✅ Contact form with proper validation
9. ✅ Clean, maintainable, well-commented code
10. ✅ Ready for production deployment

## Notes for Developer
- Keep code clean, semantic, and well-commented
- Use CSS variables extensively for easy customization
- Implement progressive enhancement (works without JS, enhanced with JS)
- Test on real devices when possible
- Consider adding dark mode toggle as bonus feature
- Use inline SVGs for icons (no external icon font dependency)
- All images should use placeholder services
- Make design easy to customize (colors, fonts, content)
- Follow mobile-first responsive design approach
- Prioritize accessibility throughout

## External Resources
- **Google Fonts**: Inter (400, 500, 600, 700), Space Grotesk (500, 700)
- **Font Awesome** (CDN): For social media icons
- **Placeholder Images**: Lorem Picsum (picsum.photos) or Unsplash Source
- **SVG Icons**: Create custom inline SVGs for feature icons

## Estimated Timeline
- Step 1: Project Setup - 30 min
- Step 2: Base CSS - 45 min
- Step 3: Navigation - 45 min
- Step 4: Homepage - 2 hours
- Step 5: Products Page - 1.5 hours
- Step 6: About Page - 1.5 hours
- Step 7: Contact Page - 1 hour
- Step 8: JavaScript - 1.5 hours
- Step 9: Responsive Design - 1 hour
- Step 10: Content & Assets - 45 min
- Step 11: Testing & Polish - 1 hour
- **Total: ~12-13 hours**

---

**Ready to build!** Start with Step 1 and work through each step sequentially. Focus on creating clean, maintainable code that's easy to customize and extend. All design decisions have been made with modern best practices in mind.
