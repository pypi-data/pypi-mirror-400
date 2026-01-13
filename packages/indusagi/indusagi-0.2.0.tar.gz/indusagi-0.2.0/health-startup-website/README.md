# HealthCare Plus - Health Startup Website

A modern, professional health startup website built with pure HTML, CSS, and JavaScript. This project features a clean, trustworthy design with responsive layouts, smooth animations, and accessibility best practices.

## Features

- **Responsive Design**: Mobile-first approach that works seamlessly on all devices
- **Modern UI/UX**: Clean, professional healthcare design with smooth animations
- **4 Complete Pages**: Home, About, Services, and Contact pages
- **Interactive Elements**:
  - Animated statistics counters
  - Testimonial carousel
  - FAQ accordion
  - Contact form with validation
  - Mobile navigation menu
  - Scroll animations
  - Back to top button
- **Accessibility**: WCAG 2.1 AA compliant with keyboard navigation and screen reader support
- **Performance**: Optimized for fast loading with vanilla JavaScript (no frameworks)

## Project Structure

```
health-startup-website/
├── index.html              # Landing page
├── about.html              # About/Company page
├── services.html           # Services offerings
├── contact.html            # Contact form
├── css/
│   ├── main.css           # Main stylesheet
│   ├── responsive.css     # Media queries
│   └── animations.css     # CSS animations
├── js/
│   ├── navigation.js      # Mobile menu, scroll effects
│   ├── main.js            # Core JavaScript (stats, testimonials, etc.)
│   └── form-validation.js # Contact form validation
├── assets/
│   ├── images/            # Image assets
│   └── fonts/             # Font files
└── README.md              # This file
```

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- A local web server (optional, but recommended)

### Installation

1. **Clone or download** this repository to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd health-startup-website
   ```

3. **Open the website**:
   - **Option 1 - Direct file access**: Simply double-click `index.html` to open it in your browser
   - **Option 2 - Local server** (recommended):
     ```bash
     # Using Python 3
     python -m http.server 8000
     
     # Using Node.js (if you have http-server installed)
     npx http-server
     
     # Using PHP
     php -S localhost:8000
     ```
   - Then open `http://localhost:8000` in your browser

## Customization

### Colors

Edit the CSS variables in `css/main.css` to customize the color scheme:

```css
:root {
    --color-primary: #2563EB;      /* Blue - trust, professionalism */
    --color-secondary: #10B981;    /* Green - health, growth */
    --color-accent: #F59E0B;       /* Warm orange - energy */
    /* ... more variables */
}
```

### Content

- **Text content**: Edit directly in HTML files
- **Images**: Replace placeholder images in the `assets/images/` folder
- **Icons**: Using Font Awesome (CDN) - can be customized in each HTML file

### Form Behavior

The contact form currently simulates submission. To make it functional:

1. Edit `js/form-validation.js`
2. Replace the simulated submission with your actual form handling logic
3. Connect to your backend API or form service (e.g., Formspree, Netlify Forms)

## Features Breakdown

### Home Page (`index.html`)
- Hero section with call-to-action buttons
- Features grid highlighting key benefits
- Animated statistics counter
- Testimonial carousel with auto-play
- Newsletter signup
- Full footer with links and social media

### About Page (`about.html`)
- Mission and vision statements
- Company timeline/history
- Team member profiles
- Core values section
- Partner logos

### Services Page (`services.html`)
- Service cards with detailed descriptions
- Pricing plans (Basic, Premium, Executive)
- FAQ accordion
- Call-to-action section

### Contact Page (`contact.html`)
- Contact information cards
- Fully validated contact form
- Embedded Google Map
- Emergency banner
- Social media links

## JavaScript Functionality

### Navigation (`js/navigation.js`)
- Mobile hamburger menu
- Smooth scroll to sections
- Active link highlighting
- Sticky header on scroll
- Keyboard accessibility (ESC to close menu)

### Main (`js/main.js`)
- Statistics counter animation
- Testimonial carousel with auto-play
- FAQ accordion functionality
- Scroll-triggered animations
- Newsletter form handling
- Back to top button
- Lazy loading for images

### Form Validation (`js/form-validation.js`)
- Real-time field validation
- Email format validation
- Required field checks
- Error message display
- Form submission handling
- Loading states

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility Features

- Semantic HTML5 elements
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus visible indicators
- Skip to content link
- Alt text for images
- Form labels and error associations
- Color contrast compliance (WCAG AA)

## Performance Optimization

- No external JavaScript frameworks
- Minimal dependencies (Google Fonts, Font Awesome via CDN)
- CSS animations using transforms (GPU accelerated)
- Lazy loading for images
- Optimized CSS with custom properties

## Deployment

This is a static website and can be deployed to any static hosting service:

### Netlify (Recommended)
1. Drag and drop the project folder to Netlify Drop
2. Or connect to Git repository

### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel` in the project directory

### GitHub Pages
1. Create a GitHub repository
2. Push the code
3. Enable GitHub Pages in repository settings

### Other Options
- AWS S3 + CloudFront
- Azure Static Web Apps
- Firebase Hosting
- Any traditional web server

## Technologies Used

- **HTML5**: Semantic markup
- **CSS3**: Custom properties, Flexbox, Grid, Animations
- **JavaScript (ES6+)**: Vanilla JS, no frameworks
- **Font Awesome 6**: Icons (via CDN)
- **Google Fonts**: Inter font family

## Customization Tips

1. **Update company name**: Search and replace "HealthCare+" with your company name
2. **Change colors**: Modify CSS variables in `css/main.css`
3. **Add pages**: Copy existing HTML file and update content
4. **Modify form**: Update form fields in `contact.html` and validation in `js/form-validation.js`
5. **Add analytics**: Add Google Analytics or similar scripts before closing `</head>` tag

## License

This project is open source and available for personal and commercial use.

## Support

For issues or questions, please refer to the code comments or create an issue in the repository.

---

**Built with ❤️ using pure HTML, CSS, and JavaScript**