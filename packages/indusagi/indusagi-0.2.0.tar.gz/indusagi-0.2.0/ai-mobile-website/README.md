# NeuralMobile AI - Company Website

A modern, professional multi-page website for NeuralMobile AI, an artificial intelligence mobile company. Built with pure HTML, CSS, and JavaScript (no frameworks).

## 🌟 Features

- **4 Complete Pages**: Home, Products, About, and Contact
- **Fully Responsive**: Mobile-first design that works on all devices
- **Modern UI/UX**: Clean, professional design with smooth animations
- **Interactive Elements**: Mobile menu, category filters, FAQ accordion, form validation
- **Animated Statistics**: Counter animations for company stats
- **Accessible**: WCAG AA compliant with proper semantic HTML
- **Fast Loading**: Optimized CSS and vanilla JavaScript
- **Cross-browser**: Works on Chrome, Firefox, Safari, and Edge

## 📁 Project Structure

```
ai-mobile-website/
├── index.html              # Homepage
├── products.html           # Products page
├── about.html              # About us page
├── contact.html            # Contact page
├── css/
│   ├── variables.css       # CSS variables (colors, fonts, spacing)
│   ├── reset.css           # CSS reset and base styles
│   ├── typography.css      # Font styles and heading system
│   ├── layout.css          # Grid, flexbox, container utilities
│   ├── components.css      # Buttons, cards, forms, badges
│   ├── navigation.css      # Header, footer, nav menu
│   └── pages.css           # Page-specific styles
├── js/
│   ├── main.js             # Core JavaScript functionality
│   ├── navigation.js       # Mobile menu, smooth scroll, active states
│   ├── animations.js       # Scroll animations, counters
│   └── form-validation.js  # Contact form validation
├── assets/
│   ├── images/             # Image assets
│   └── icons/              # SVG icons
└── README.md               # This file
```

## 🎨 Design System

### Colors
- **Primary**: Royal Blue (#2563EB)
- **Secondary**: Purple (#7C3AED)
- **Accent**: Cyan (#06B6D4)
- **Dark**: Navy (#0F172A)
- **Light**: Off-white (#F8FAFC)

### Typography
- **Primary Font**: Inter (400, 500, 600, 700)
- **Display Font**: Space Grotesk (500, 700)

### Components
- Buttons (Primary, Secondary, Large, Small)
- Cards (Feature, Product, Testimonial, Team, Value, Award)
- Forms (Input, Select, Textarea)
- Badges (Primary, Secondary, Accent, Success, Warning)
- Navigation (Header, Footer, Mobile Menu)

## 🚀 Getting Started

### Prerequisites
- A modern web browser (Chrome, Firefox, Safari, Edge)
- A local web server (optional, for testing)

### Installation

1. **Clone or download the project**
   ```bash
   cd ai-mobile-website
   ```

2. **Open the website**
   - Simply open `index.html` in your web browser
   - Or use a local server:
     ```bash
     # Python 3
     python -m http.server 8000
     
     # Node.js (with npx)
     npx serve
     
     # PHP
     php -S localhost:8000
     ```

3. **Navigate to the website**
   - Open `http://localhost:8000` in your browser

## 📄 Pages Overview

### Homepage (index.html)
- Hero section with gradient background
- 6 feature cards highlighting AI capabilities
- 3 featured products preview
- Animated statistics counters
- 3 customer testimonials
- Call-to-action banner
- Footer with newsletter signup

### Products Page (products.html)
- Page header with breadcrumb
- Category filter (All, AI Assistant, Productivity, Security, Health)
- 8 product cards with detailed information
- Feature comparison table
- Newsletter signup CTA

### About Page (about.html)
- Mission hero section
- Company timeline (2018-2024)
- 6 core values with icons
- 6 team member cards
- Animated company stats
- Awards and recognition
- Careers CTA section

### Contact Page (contact.html)
- Contact hero section
- Contact form with validation
- Contact information (email, phone, address, hours)
- 8 FAQ accordion items
- Social media links
- Embedded Google Map

## ⚙️ Customization

### Changing Colors
Edit `css/variables.css`:
```css
:root {
    --primary: #2563EB;        /* Change primary color */
    --secondary: #7C3AED;      /* Change secondary color */
    --accent: #06B6D4;         /* Change accent color */
}
```

### Changing Fonts
Edit `css/variables.css`:
```css
:root {
    --font-primary: 'Inter', sans-serif;
    --font-display: 'Space Grotesk', sans-serif;
}
```

### Adding New Products
Edit the product cards in `products.html`:
```html
<div class="product-card product-card--full" data-category="your-category">
    <div class="product-card__image">
        <img src="your-image.jpg" alt="Product Name">
        <span class="badge badge--primary">Category</span>
    </div>
    <div class="product-card__content">
        <h3 class="product-card__title">Product Name</h3>
        <p class="product-card__description">Description</p>
        <ul class="product-card__features">
            <li><i class="fas fa-check"></i> Feature 1</li>
        </ul>
    </div>
</div>
```

### Adding Team Members
Edit the team cards in `about.html`:
```html
<div class="team-card">
    <div class="team-card__image">
        <img src="team-member.jpg" alt="Name">
    </div>
    <div class="team-card__content">
        <h3 class="team-card__name">Name</h3>
        <p class="team-card__role">Role</p>
    </div>
</div>
```

## 🔧 JavaScript Features

### Mobile Menu
- Hamburger menu toggle
- Smooth open/close animations
- Click outside to close
- Keyboard navigation (Escape key)

### Scroll Animations
- Fade-in animations on scroll
- Staggered card animations
- Parallax effects on hero images
- Animated counter statistics

### Form Validation
- Real-time validation feedback
- Email format validation
- Required field checks
- Loading state on submission
- Success message display

### Category Filter
- Filter products by category
- Smooth animations
- Active state highlighting

### FAQ Accordion
- Expand/collapse functionality
- Only one item open at a time
- Smooth animations

## 🌐 Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile Safari iOS 12+
- Chrome Android

## ♿ Accessibility Features

- Semantic HTML5 structure
- ARIA labels and roles
- Keyboard navigation support
- Skip to content link
- Focus indicators on interactive elements
- Proper color contrast (4.5:1 minimum)
- Alt text for all images
- Form labels and error messages

## 📱 Responsive Breakpoints

- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

## 🎯 Performance

- Page load time: < 2 seconds
- First Contentful Paint: < 1 second
- Minimal JavaScript bundle size
- Optimized CSS with variables
- Lazy loading for images

## 🔨 Built With

- **HTML5**: Semantic markup
- **CSS3**: Modern features (Grid, Flexbox, Custom Properties)
- **JavaScript (ES6+)**: Vanilla JS, no frameworks
- **Google Fonts**: Inter, Space Grotesk
- **Font Awesome**: Icon library (CDN)
- **Placeholder Images**: Lorem Picsum

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Contact

For questions or support, please visit the contact page or email:
- hello@neuralmobile.ai
- support@neuralmobile.ai

## 🎉 Acknowledgments

- Design inspired by modern tech companies
- Placeholder images from Lorem Picsum
- Icons from Font Awesome
- Fonts from Google Fonts

---

**Built with ❤️ using HTML, CSS, and JavaScript**
