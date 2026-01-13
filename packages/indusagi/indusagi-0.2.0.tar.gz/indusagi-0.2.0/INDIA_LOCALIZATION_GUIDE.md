# Indian Localization, Cultural, and UX Requirements for AI Systems

*Comprehensive Implementation Guide - 2024/2025*

---

## Table of Contents
1. [Date, Time, and Number Formatting](#1-date-time-and-number-formatting)
2. [Currency and Financial Formats](#2-currency-and-financial-formats)
3. [Cultural Considerations](#3-cultural-considerations)
4. [User Experience Patterns](#4-user-experience-patterns)
5. [Address and Location](#5-address-and-location)
6. [Documentation and Help](#6-documentation-and-help)
7. [Payment Integration](#7-payment-integration)
8. [Data Privacy and Compliance](#8-data-privacy-and-compliance)

---

## 1. Date, Time, and Number Formatting

### 1.1 Date Formats

**Primary Format**: Day-Month-Year (DD/MM/YYYY or DD-MM-YYYY)

```javascript
// JavaScript Implementation
const formatIndianDate = (date) => {
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(date);
};

// Example: 06/11/2025
console.log(formatIndianDate(new Date()));
```

```python
# Python Implementation
from datetime import datetime
import locale

# Set Indian locale
locale.setlocale(locale.LC_TIME, 'en_IN.UTF-8')

def format_indian_date(date):
    return date.strftime('%d/%m/%Y')

# Example: 06/11/2025
print(format_indian_date(datetime.now()))
```

**Important Notes**:
- DD/MM/YYYY is standard for CBSE and official documents
- ISO 8601 (YYYY-MM-DD) is used in databases and digital systems
- Avoid MM/DD/YYYY format (American style) for user-facing interfaces

### 1.2 Time Zones

**Indian Standard Time (IST)**: UTC+5:30

```javascript
// JavaScript Implementation
const getISTTime = () => {
  return new Date().toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true  // 12-hour format is common in India
  });
};

// Example: 02:30:45 PM
console.log(getISTTime());
```

```python
# Python Implementation
from datetime import datetime
import pytz

def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%I:%M:%S %p')

# Example: 02:30:45 PM
print(get_ist_time())
```

### 1.3 Indian Numbering System (Lakhs and Crores)

**Structure**:
- 1 Lakh = 100,000 (1,00,000 in Indian format)
- 1 Crore = 10,000,000 (1,00,00,000 in Indian format)
- Grouping: Last 3 digits together, then pairs of 2

**JavaScript Implementation**:

```javascript
// Method 1: Using toLocaleString (Recommended)
const formatIndianNumber = (num) => {
  return num.toLocaleString('en-IN');
};

// Examples:
console.log(formatIndianNumber(1000));        // 1,000
console.log(formatIndianNumber(100000));      // 1,00,000 (1 Lakh)
console.log(formatIndianNumber(10000000));    // 1,00,00,000 (1 Crore)
console.log(formatIndianNumber(12345678.90)); // 1,23,45,678.9

// Method 2: Custom Regex (For more control)
const formatIndianNumberCustom = (num) => {
  const [integer, decimal] = num.toString().split('.');

  // Get last 3 digits
  const lastThree = integer.substring(integer.length - 3);
  const otherNumbers = integer.substring(0, integer.length - 3);

  // Format with Indian comma pattern
  const formatted = otherNumbers !== ''
    ? otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree
    : lastThree;

  return decimal ? formatted + '.' + decimal : formatted;
};

// Method 3: With Words (Lakhs/Crores)
const formatIndianNumberWithWords = (num) => {
  const absNum = Math.abs(num);
  const sign = num < 0 ? '-' : '';

  if (absNum >= 10000000) {
    return sign + (absNum / 10000000).toFixed(2) + ' Cr';
  } else if (absNum >= 100000) {
    return sign + (absNum / 100000).toFixed(2) + ' L';
  } else if (absNum >= 1000) {
    return sign + (absNum / 1000).toFixed(2) + ' K';
  }
  return sign + absNum.toString();
};

console.log(formatIndianNumberWithWords(12500000)); // 1.25 Cr
console.log(formatIndianNumberWithWords(850000));   // 8.50 L
```

**Python Implementation**:

```python
# Method 1: Using locale (Recommended)
import locale

locale.setlocale(locale.LC_NUMERIC, 'en_IN')

def format_indian_number(num):
    return locale.format_string('%d', num, grouping=True)

# Examples:
print(format_indian_number(100000))      # 1,00,000
print(format_indian_number(10000000))    # 1,00,00,000

# Method 2: Custom String Manipulation
def format_indian_number_custom(num):
    s = str(int(num))
    if len(s) <= 3:
        return s

    # Get last 3 digits
    last_three = s[-3:]
    remaining = s[:-3]

    # Group remaining in pairs from right
    groups = []
    while remaining:
        groups.append(remaining[-2:])
        remaining = remaining[:-2]

    # Reverse and join
    result = ','.join(reversed(groups)) + ',' + last_three
    return result

# Method 3: With decimal support
def format_indian_currency(num):
    """Format number with Indian comma pattern and 2 decimal places"""
    integer_part = int(num)
    decimal_part = num - integer_part

    formatted_int = format_indian_number_custom(integer_part)

    if decimal_part > 0:
        return f"{formatted_int}.{int(decimal_part * 100):02d}"
    return formatted_int
```

### 1.4 Calendar Systems

**Primary**: Gregorian calendar (official use)
**Secondary**: Hindu calendar, Islamic calendar (religious/cultural events)

```javascript
// Multi-calendar date display
const displayMultiCalendarDate = (date) => {
  return {
    gregorian: date.toLocaleDateString('en-IN'),
    islamic: date.toLocaleDateString('en-IN-u-ca-islamic'),
    hindu: date.toLocaleDateString('en-IN-u-ca-indian')
  };
};

console.log(displayMultiCalendarDate(new Date()));
// {
//   gregorian: "06/11/2025",
//   islamic: "08/05/1447",
//   hindu: "16/08/1947"
// }
```

### 1.5 Indian Fiscal Year

**Period**: April 1 to March 31
**Format**: FY 2024-25 (April 1, 2024 - March 31, 2025)

```javascript
// Get current fiscal year
const getCurrentFiscalYear = () => {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth(); // 0-11

  // If month is Jan-Mar (0-2), fiscal year started previous calendar year
  if (currentMonth < 3) {
    return `FY ${currentYear - 1}-${currentYear.toString().slice(-2)}`;
  }
  // If month is Apr-Dec (3-11), fiscal year started current calendar year
  return `FY ${currentYear}-${(currentYear + 1).toString().slice(-2)}`;
};

console.log(getCurrentFiscalYear()); // FY 2024-25

// Get fiscal year date range
const getFiscalYearRange = (fiscalYearStart) => {
  const startYear = fiscalYearStart;
  const endYear = fiscalYearStart + 1;

  return {
    start: new Date(startYear, 3, 1),  // April 1
    end: new Date(endYear, 2, 31)      // March 31
  };
};

const fy2024 = getFiscalYearRange(2024);
console.log(fy2024);
// { start: 2024-04-01, end: 2025-03-31 }
```

```python
from datetime import datetime, date

def get_current_fiscal_year():
    """Get current Indian fiscal year"""
    now = datetime.now()

    # Fiscal year starts April 1
    if now.month < 4:  # Jan-Mar
        return f"FY {now.year - 1}-{str(now.year)[-2:]}"
    else:  # Apr-Dec
        return f"FY {now.year}-{str(now.year + 1)[-2:]}"

def get_fiscal_year_dates(fiscal_year_start):
    """Get fiscal year date range"""
    return {
        'start': date(fiscal_year_start, 4, 1),
        'end': date(fiscal_year_start + 1, 3, 31)
    }

print(get_current_fiscal_year())  # FY 2024-25
```

**Assessment Year (AY)**: Year following the financial year for tax evaluation
- Income earned in FY 2023-24 → File ITR in AY 2024-25
- ITR deadline: July 31 for individuals, October 31 for businesses

---

## 2. Currency and Financial Formats

### 2.1 Indian Rupee (INR) Formatting

**Symbol**: ₹ (Unicode: U+20B9)
**Code**: INR
**Subdivision**: 100 paise = 1 rupee

```javascript
// Method 1: Using Intl.NumberFormat (Recommended)
const formatINR = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

console.log(formatINR(1234567.89));     // ₹12,34,567.89
console.log(formatINR(100000));         // ₹1,00,000.00

// Method 2: With custom symbol position
const formatINRCustom = (amount) => {
  const formatted = amount.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  return `₹${formatted}`;
};

// Method 3: With words for large amounts
const formatINRWithWords = (amount) => {
  const formatted = formatINR(amount);
  const absAmount = Math.abs(amount);

  let words = '';
  if (absAmount >= 10000000) {
    words = ` (${(absAmount / 10000000).toFixed(2)} Crore)`;
  } else if (absAmount >= 100000) {
    words = ` (${(absAmount / 100000).toFixed(2)} Lakh)`;
  }

  return formatted + words;
};

console.log(formatINRWithWords(12500000));
// ₹1,25,00,000.00 (12.50 Crore)
```

```python
import locale

# Set Indian locale
locale.setlocale(locale.LC_MONETARY, 'en_IN')

def format_inr(amount):
    """Format amount as Indian Rupees"""
    return locale.currency(amount, grouping=True)

print(format_inr(1234567.89))   # ₹ 12,34,567.89
print(format_inr(100000))       # ₹ 1,00,000.00

# Custom formatting with Decimal for precision
from decimal import Decimal, ROUND_HALF_UP

def format_inr_precise(amount):
    """Format with proper rounding"""
    decimal_amount = Decimal(str(amount)).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )

    # Format integer part
    rupees = int(decimal_amount)
    paise = int((decimal_amount - rupees) * 100)

    # Apply Indian number format
    formatted = format_indian_number(rupees)
    return f"₹{formatted}.{paise:02d}"
```

### 2.2 GST (Goods and Services Tax) Display

**GST Structure**:
- CGST (Central GST)
- SGST (State GST) / IGST (Integrated GST)
- Standard rates: 0%, 5%, 12%, 18%, 28%

**Rounding Rules** (Section 170, CGST Act):
- > 50 paise: Round up to nearest rupee
- ≤ 50 paise: Round down to nearest rupee
- Round separately for each tax component (CGST, SGST, IGST)

```javascript
// GST Calculation with proper rounding
const calculateGST = (amount, gstRate, isIGST = false) => {
  const gstAmount = (amount * gstRate) / 100;

  if (isIGST) {
    // Interstate: IGST only
    return {
      baseAmount: amount,
      igst: Math.round(gstAmount),  // Round to nearest rupee
      cgst: 0,
      sgst: 0,
      total: amount + Math.round(gstAmount)
    };
  } else {
    // Intrastate: CGST + SGST
    const halfGst = gstAmount / 2;
    const cgst = Math.round(halfGst);
    const sgst = Math.round(halfGst);

    return {
      baseAmount: amount,
      cgst: cgst,
      sgst: sgst,
      igst: 0,
      total: amount + cgst + sgst
    };
  }
};

// Example: ₹10,000 with 18% GST (Intrastate)
const invoice = calculateGST(10000, 18, false);
console.log(invoice);
// {
//   baseAmount: 10000,
//   cgst: 900,   // 9% rounded
//   sgst: 900,   // 9% rounded
//   igst: 0,
//   total: 11800
// }

// Format GST Invoice
const formatGSTInvoice = (items) => {
  let subtotal = 0;
  let totalCGST = 0;
  let totalSGST = 0;
  let totalIGST = 0;

  items.forEach(item => {
    const gst = calculateGST(item.amount, item.gstRate, item.isIGST);
    subtotal += gst.baseAmount;
    totalCGST += gst.cgst;
    totalSGST += gst.sgst;
    totalIGST += gst.igst;
  });

  return {
    subtotal: formatINR(subtotal),
    cgst: formatINR(totalCGST),
    sgst: formatINR(totalSGST),
    igst: formatINR(totalIGST),
    total: formatINR(subtotal + totalCGST + totalSGST + totalIGST)
  };
};
```

**GST Invoice Requirements (2024-25)**:
1. Supplier's GSTIN, name, address
2. Unique invoice number and date
3. Recipient's GSTIN (if registered), name, address
4. HSN/SAC code
5. Description of goods/services
6. Quantity and unit (for goods)
7. Taxable value (pre-tax)
8. GST rate and amount (CGST, SGST, or IGST)
9. Total amount payable

```javascript
// Complete GST Invoice Template
const generateGSTInvoice = (invoiceData) => {
  return {
    invoiceNumber: invoiceData.invoiceNumber,
    invoiceDate: formatIndianDate(new Date()),

    // Supplier Details
    supplier: {
      gstin: invoiceData.supplier.gstin,
      name: invoiceData.supplier.name,
      address: invoiceData.supplier.address
    },

    // Customer Details
    customer: {
      gstin: invoiceData.customer.gstin || 'N/A',
      name: invoiceData.customer.name,
      address: invoiceData.customer.address
    },

    // Line Items
    items: invoiceData.items.map(item => {
      const gst = calculateGST(item.price * item.quantity, item.gstRate, item.isIGST);
      return {
        description: item.description,
        hsnCode: item.hsnCode,
        quantity: item.quantity,
        unit: item.unit,
        rate: formatINR(item.price),
        taxableValue: formatINR(gst.baseAmount),
        gstRate: `${item.gstRate}%`,
        cgst: formatINR(gst.cgst),
        sgst: formatINR(gst.sgst),
        igst: formatINR(gst.igst),
        totalAmount: formatINR(gst.total)
      };
    }),

    // Summary
    summary: formatGSTInvoice(invoiceData.items)
  };
};
```

### 2.3 Paise Display

**Rule**: Always show 2 decimal places for currency

```javascript
// Ensure 2 decimal places
const formatPaise = (amount) => {
  return amount.toFixed(2);
};

// Convert paise to rupees
const paiseToRupees = (paise) => {
  return (paise / 100).toFixed(2);
};

console.log(paiseToRupees(12599)); // 125.99
```

---

## 3. Cultural Considerations

### 3.1 Communication Style

**Formal vs Informal**:
- **Business/Official**: Formal tone preferred
- **Addressing**: Use title + surname unless invited otherwise (Mr. Sharma, Dr. Patel)
- **Hierarchy**: Respect hierarchical levels in communication
- **Face-to-face**: Preferred over written communication

**AI Communication Guidelines**:

```javascript
// Communication tone adapter
const adaptTone = (message, context) => {
  const toneRules = {
    business: {
      greeting: 'Good morning/afternoon',
      closing: 'Thank you for your time',
      politeness: 'Could you please...',
      formality: 'high'
    },
    customer_support: {
      greeting: 'Hello, how may I assist you?',
      closing: 'Is there anything else I can help you with?',
      politeness: 'I would be happy to help you with...',
      formality: 'medium-high'
    },
    casual: {
      greeting: 'Hi there!',
      closing: 'Have a great day!',
      politeness: 'Please let me know if...',
      formality: 'medium'
    }
  };

  return {
    tone: toneRules[context] || toneRules.business,
    adaptedMessage: message
  };
};
```

**Language Mixing (Hinglish)**:
- Common practice: Mix Hindi and English
- AI should understand and optionally respond in mixed language

```python
# Simple Hinglish detection
def detect_hinglish(text):
    """Detect if text contains Hindi+English mix"""
    hindi_chars = set('अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ')
    english_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

    has_hindi = any(char in hindi_chars for char in text)
    has_english = any(char in english_chars for char in text)

    return has_hindi and has_english

# Example
text = "Aaj ka weather kaisa hai?"  # "How is today's weather?"
print(detect_hinglish(text))  # True
```

### 3.2 Regional Diversity

**22 Official Languages** + 100+ regional languages

**Top Languages by Speakers**:
1. Hindi (43.6%)
2. Bengali (8%)
3. Marathi (6.9%)
4. Telugu (6.7%)
5. Tamil (5.7%)
6. Gujarati (4.5%)
7. Urdu (4.2%)
8. Kannada (3.6%)
9. Malayalam (3%)
10. Punjabi (2.8%)

```javascript
// Multi-language support configuration
const INDIAN_LANGUAGES = {
  hi: { name: 'Hindi', nativeName: 'हिन्दी', script: 'Devanagari' },
  bn: { name: 'Bengali', nativeName: 'বাংলা', script: 'Bengali' },
  te: { name: 'Telugu', nativeName: 'తెలుగు', script: 'Telugu' },
  mr: { name: 'Marathi', nativeName: 'मराठी', script: 'Devanagari' },
  ta: { name: 'Tamil', nativeName: 'தமிழ்', script: 'Tamil' },
  gu: { name: 'Gujarati', nativeName: 'ગુજરાતી', script: 'Gujarati' },
  kn: { name: 'Kannada', nativeName: 'ಕನ್ನಡ', script: 'Kannada' },
  ml: { name: 'Malayalam', nativeName: 'മലയാളം', script: 'Malayalam' },
  pa: { name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', script: 'Gurmukhi' }
};

// Detect user's preferred language
const detectPreferredLanguage = (userProfile) => {
  // Priority: 1. User setting, 2. Browser, 3. Location
  return userProfile.language
    || navigator.language
    || 'en-IN';  // Default to English (India)
};
```

### 3.3 Festivals and Holidays

**Major National Holidays**:
- Republic Day (January 26)
- Independence Day (August 15)
- Gandhi Jayanti (October 2)

**Major Festivals** (dates vary by lunar calendar):
- Diwali (October/November) - Festival of Lights
- Holi (March) - Festival of Colors
- Eid al-Fitr & Eid al-Adha (Islamic calendar)
- Durga Puja (September/October) - Regional (Bengal)
- Navratri/Dussehra (September/October)
- Pongal (January 14-17) - Regional (Tamil Nadu)
- Onam (August/September) - Regional (Kerala)
- Christmas (December 25)

```javascript
// Festival-aware scheduling
const isIndianHoliday = (date) => {
  // Static holidays
  const staticHolidays = [
    { month: 0, day: 26, name: 'Republic Day' },
    { month: 7, day: 15, name: 'Independence Day' },
    { month: 9, day: 2, name: 'Gandhi Jayanti' },
    { month: 11, day: 25, name: 'Christmas' }
  ];

  const month = date.getMonth();
  const day = date.getDate();

  return staticHolidays.some(h =>
    h.month === month && h.day === day
  );
};

// Festival greetings
const getFestivalGreeting = (date) => {
  // This would typically integrate with a lunar calendar API
  // for dynamic festivals
  const greetings = {
    diwali: 'Happy Diwali! Wishing you prosperity and happiness.',
    holi: 'Happy Holi! May your life be filled with colors of joy.',
    eid: 'Eid Mubarak! May this day bring peace and happiness.'
  };

  // Return appropriate greeting based on date
  // Implementation would check lunar calendar
};
```

### 3.4 Color and Design Preferences

**Cultural Color Meanings**:
- **Red & Gold**: Auspicious, weddings, celebrations, courage
- **Orange/Saffron**: Sacred, spiritual, energy
- **Green**: Fertility, prosperity, Islam
- **Yellow**: Knowledge, learning, spring
- **White**: Purity (but also mourning in some contexts)
- **Black**: Generally avoided for celebrations

**Design Preferences**:
- Vibrant, colorful designs (vs. minimalist Western style)
- More visual density acceptable
- Rich patterns and decorative elements
- Festival-specific themes

```javascript
// Indian color palette
const INDIAN_COLOR_PALETTE = {
  primary: {
    saffron: '#FF9933',
    white: '#FFFFFF',
    green: '#138808',
    navy: '#000080'
  },
  auspicious: {
    red: '#FF0000',
    gold: '#FFD700',
    yellow: '#FFFF00',
    orange: '#FFA500'
  },
  festivals: {
    diwali: ['#FF6B35', '#F7931E', '#FDC830'],
    holi: ['#FF006E', '#8338EC', '#3A86FF', '#FFBE0B']
  }
};

// Theme adaptation
const getThemeForFestival = (festival) => {
  return {
    colors: INDIAN_COLOR_PALETTE.festivals[festival] || INDIAN_COLOR_PALETTE.primary,
    pattern: 'decorative',
    density: 'high'
  };
};
```

### 3.5 Religious and Cultural Sensitivity

**Guidelines**:
- Avoid religious comparisons or hierarchies
- Respect dietary restrictions (vegetarian options prominent)
- Be aware of caste sensitivity (never ask about caste)
- Respect regional customs
- Gender sensitivity in communication

```javascript
// Content filtering for cultural sensitivity
const culturalSensitivityCheck = (content) => {
  const sensitiveTopics = [
    'caste',
    'religious comparison',
    'beef',  // Sensitive for Hindus
    'pork'   // Sensitive for Muslims
  ];

  // Implement content checking logic
  // Flag potentially sensitive content for review

  return {
    isSafe: true,
    warnings: [],
    suggestions: []
  };
};

// Dietary preference handling
const DIETARY_PREFERENCES = {
  vegetarian: { icon: '🟢', label: 'Veg', color: 'green' },
  nonVegetarian: { icon: '🔴', label: 'Non-Veg', color: 'red' },
  vegan: { icon: '🟢', label: 'Vegan', color: 'green' },
  jain: { icon: '🟡', label: 'Jain', color: 'yellow' }  // No root vegetables
};
```

---

## 4. User Experience Patterns

### 4.1 Mobile-First Design

**Statistics**:
- 750+ million smartphone users
- 83% of digital payments via mobile (UPI)
- Mobile-first or mobile-only access for many users

**Design Principles**:

```javascript
// Responsive breakpoints for India
const INDIAN_BREAKPOINTS = {
  mobile: '320px',      // Entry-level smartphones
  mobileMd: '375px',    // Common smartphone size
  mobileLg: '414px',    // Large smartphones
  tablet: '768px',
  desktop: '1024px'
};

// Mobile-first CSS
const mobileFirstStyles = {
  base: {
    fontSize: '16px',      // Minimum for readability
    touchTarget: '48px',   // Minimum touch target (iOS guideline)
    padding: '16px',
    lineHeight: 1.5
  },
  buttons: {
    minHeight: '48px',     // Easy tapping
    minWidth: '88px',
    fontSize: '16px',
    borderRadius: '8px'
  }
};
```

### 4.2 Low Bandwidth Optimization

**Strategies**:
1. Image compression
2. Lazy loading
3. Progressive enhancement
4. Reduced animation
5. Text-based fallbacks

```javascript
// Image optimization for low bandwidth
const optimizeImageForIndia = (imageUrl, quality = 'medium') => {
  const qualitySettings = {
    low: { width: 480, quality: 60 },
    medium: { width: 720, quality: 75 },
    high: { width: 1080, quality: 85 }
  };

  const settings = qualitySettings[quality];

  return {
    src: imageUrl,
    srcset: `
      ${imageUrl}?w=${settings.width}&q=${settings.quality} 1x,
      ${imageUrl}?w=${settings.width * 1.5}&q=${settings.quality} 1.5x
    `,
    loading: 'lazy',
    decoding: 'async'
  };
};

// Network-aware loading
const loadBasedOnConnection = () => {
  if ('connection' in navigator) {
    const connection = navigator.connection;
    const effectiveType = connection.effectiveType;

    switch(effectiveType) {
      case 'slow-2g':
      case '2g':
        return 'text-only';
      case '3g':
        return 'low-quality';
      case '4g':
        return 'high-quality';
      default:
        return 'medium-quality';
    }
  }
  return 'medium-quality';  // Default
};

// Data saver mode detection
const isDataSaverEnabled = () => {
  return navigator.connection?.saveData === true;
};
```

### 4.3 Offline-First Capabilities

**Implementation using Service Workers**:

```javascript
// Service Worker for offline support
// sw.js

const CACHE_NAME = 'india-app-v1';
const OFFLINE_URL = '/offline.html';

const CRITICAL_ASSETS = [
  '/',
  '/offline.html',
  '/styles/main.css',
  '/scripts/main.js',
  '/images/logo.png'
];

// Install - cache critical assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CRITICAL_ASSETS))
  );
});

// Fetch - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;  // Serve from cache
        }

        return fetch(event.request)
          .then(response => {
            // Cache new responses
            if (response.status === 200) {
              const responseClone = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => cache.put(event.request, responseClone));
            }
            return response;
          })
          .catch(() => {
            // Offline fallback
            return caches.match(OFFLINE_URL);
          });
      })
  );
});

// Register service worker
// main.js
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
    .then(reg => console.log('SW registered'))
    .catch(err => console.log('SW registration failed'));
}
```

**IndexedDB for offline data**:

```javascript
// Offline data storage
const initDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('IndiaAppDB', 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      // Create object stores
      if (!db.objectStoreNames.contains('user_data')) {
        db.createObjectStore('user_data', { keyPath: 'id' });
      }

      if (!db.objectStoreNames.contains('offline_queue')) {
        db.createObjectStore('offline_queue', { autoIncrement: true });
      }
    };
  });
};

// Queue actions when offline
const queueOfflineAction = async (action) => {
  const db = await initDB();
  const tx = db.transaction('offline_queue', 'readwrite');
  const store = tx.objectStore('offline_queue');

  await store.add({
    action: action,
    timestamp: Date.now()
  });
};

// Sync when back online
window.addEventListener('online', async () => {
  const db = await initDB();
  const tx = db.transaction('offline_queue', 'readonly');
  const store = tx.objectStore('offline_queue');
  const actions = await store.getAll();

  // Process queued actions
  for (const item of actions) {
    await processAction(item.action);
  }

  // Clear queue
  const clearTx = db.transaction('offline_queue', 'readwrite');
  await clearTx.objectStore('offline_queue').clear();
});
```

### 4.4 Voice Interfaces

**Considerations**:
- Popular in India (low literacy, convenience)
- Must handle multiple accents and dialects
- Hinglish support crucial
- Background noise tolerance

```javascript
// Voice interface implementation
const initVoiceInterface = () => {
  if (!('webkitSpeechRecognition' in window)) {
    console.log('Speech recognition not supported');
    return;
  }

  const recognition = new webkitSpeechRecognition();

  // Configuration for India
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'hi-IN';  // Hindi (India)
  // Also support: 'en-IN', 'ta-IN', 'te-IN', 'ml-IN', 'kn-IN', etc.

  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(result => result[0].transcript)
      .join('');

    handleVoiceCommand(transcript);
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error', event.error);
    // Provide text fallback
  };

  return recognition;
};

// Multi-language voice support
const VOICE_LANGUAGES = {
  'Hindi': 'hi-IN',
  'English': 'en-IN',
  'Tamil': 'ta-IN',
  'Telugu': 'te-IN',
  'Bengali': 'bn-IN',
  'Marathi': 'mr-IN',
  'Gujarati': 'gu-IN',
  'Kannada': 'kn-IN',
  'Malayalam': 'ml-IN',
  'Punjabi': 'pa-IN'
};

// Voice command handling
const handleVoiceCommand = (command) => {
  // Parse and execute command
  // Support both English and regional language commands

  // Example patterns:
  // "Show me my balance" / "मेरा बैलेंस दिखाओ"
  // "Pay 500 rupees" / "500 रुपये भेजो"
  // "Book a ticket" / "टिकट बुक करो"
};

// Text-to-Speech for responses
const speak = (text, language = 'en-IN') => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = 0.9;  // Slightly slower for clarity
    speechSynthesis.speak(utterance);
  }
};
```

### 4.5 Vernacular UI Best Practices

**Typography Considerations**:

```javascript
// Font recommendations for Indian scripts
const INDIAN_FONT_STACKS = {
  devanagari: '"Noto Sans Devanagari", "Ek Type Anek", "Baloo 2", sans-serif',
  bengali: '"Noto Sans Bengali", "Baloo Da 2", sans-serif',
  tamil: '"Noto Sans Tamil", "Baloo Thambi 2", sans-serif',
  telugu: '"Noto Sans Telugu", "Baloo Tamma 2", sans-serif',
  kannada: '"Noto Sans Kannada", "Baloo Tamma 2", sans-serif',
  malayalam: '"Noto Sans Malayalam", "Baloo Chettan 2", sans-serif',
  gujarati: '"Noto Sans Gujarati", "Baloo Bhai 2", sans-serif'
};

// Text expansion handling
const TEXT_EXPANSION_FACTORS = {
  'hi': 1.2,  // Hindi expands ~20%
  'bn': 1.15,
  'ta': 1.25,
  'te': 1.3,
  'kn': 1.3,
  'ml': 1.4,  // Malayalam can expand significantly
  'gu': 1.2
};

// Dynamic font sizing
const getLocalizedFontSize = (baseSize, language) => {
  const baseSizeNum = parseInt(baseSize);
  const factor = TEXT_EXPANSION_FACTORS[language] || 1;

  // Some scripts need larger base size for readability
  const scriptBoost = ['ta', 'te', 'kn', 'ml'].includes(language) ? 2 : 0;

  return `${baseSizeNum + scriptBoost}px`;
};
```

**Language Selector Design**:

```javascript
// Language selector component
const LanguageSelector = () => {
  const languages = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
    { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
    { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
    { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
    { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
    { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
    { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
    { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ' }
  ];

  return {
    type: 'dropdown',
    position: 'header-right',
    displayFormat: 'nativeName',  // Show "हिन्दी" not "Hindi"
    showIcon: true,
    languages: languages
  };
};
```

---

## 5. Address and Location

### 5.1 Indian Address Format

**Standard Structure**:
```
Name
House/Building Number and Name
Street/Road Name
Locality/Area
City/Town - PIN Code
District (optional)
State
Country (for international)
```

**Example**:
```
Mr. Rajesh Kumar
Flat 301, Sunrise Apartments
MG Road
Koramangala
Bangalore - 560034
Karnataka
India
```

### 5.2 Address Form Implementation

```javascript
// Indian address form structure
const IndianAddressForm = {
  fields: [
    {
      name: 'fullName',
      label: 'Full Name',
      type: 'text',
      required: true,
      placeholder: 'Mr. Rajesh Kumar'
    },
    {
      name: 'addressLine1',
      label: 'House/Building Number and Name',
      type: 'text',
      required: true,
      placeholder: 'Flat 301, Sunrise Apartments'
    },
    {
      name: 'addressLine2',
      label: 'Street/Road Name',
      type: 'text',
      required: false,
      placeholder: 'MG Road'
    },
    {
      name: 'locality',
      label: 'Locality/Area',
      type: 'text',
      required: true,
      placeholder: 'Koramangala'
    },
    {
      name: 'city',
      label: 'City/Town',
      type: 'text',
      required: true,
      placeholder: 'Bangalore'
    },
    {
      name: 'pincode',
      label: 'PIN Code',
      type: 'text',
      pattern: '^[1-9][0-9]{5}$',  // 6 digits, not starting with 0
      required: true,
      placeholder: '560034',
      maxLength: 6
    },
    {
      name: 'state',
      label: 'State',
      type: 'select',
      required: true,
      options: INDIAN_STATES
    },
    {
      name: 'landmark',
      label: 'Landmark (Optional)',
      type: 'text',
      required: false,
      placeholder: 'Near Forum Mall'
    },
    {
      name: 'phoneNumber',
      label: 'Phone Number',
      type: 'tel',
      pattern: '^[6-9][0-9]{9}$',  // Indian mobile: starts with 6-9, 10 digits
      required: true,
      placeholder: '9876543210'
    }
  ]
};

// PIN code validation
const validatePINCode = (pincode) => {
  // Indian PIN codes: 6 digits, first digit 1-9
  const pincodeRegex = /^[1-9][0-9]{5}$/;
  return pincodeRegex.test(pincode);
};

// Auto-fill city/state from PIN code
const lookupPINCode = async (pincode) => {
  if (!validatePINCode(pincode)) {
    return { error: 'Invalid PIN code' };
  }

  try {
    // Use India Post API or third-party service
    const response = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
    const data = await response.json();

    if (data[0].Status === 'Success') {
      const postOffice = data[0].PostOffice[0];
      return {
        city: postOffice.District,
        state: postOffice.State,
        district: postOffice.District,
        locality: postOffice.Name
      };
    }
  } catch (error) {
    console.error('PIN code lookup failed', error);
  }

  return { error: 'PIN code not found' };
};
```

### 5.3 Indian States and Union Territories

```javascript
// Complete list of Indian States and Union Territories (2024)
const INDIAN_STATES = [
  // States (28)
  { code: 'AP', name: 'Andhra Pradesh', type: 'state' },
  { code: 'AR', name: 'Arunachal Pradesh', type: 'state' },
  { code: 'AS', name: 'Assam', type: 'state' },
  { code: 'BR', name: 'Bihar', type: 'state' },
  { code: 'CT', name: 'Chhattisgarh', type: 'state' },
  { code: 'GA', name: 'Goa', type: 'state' },
  { code: 'GJ', name: 'Gujarat', type: 'state' },
  { code: 'HR', name: 'Haryana', type: 'state' },
  { code: 'HP', name: 'Himachal Pradesh', type: 'state' },
  { code: 'JH', name: 'Jharkhand', type: 'state' },
  { code: 'KA', name: 'Karnataka', type: 'state' },
  { code: 'KL', name: 'Kerala', type: 'state' },
  { code: 'MP', name: 'Madhya Pradesh', type: 'state' },
  { code: 'MH', name: 'Maharashtra', type: 'state' },
  { code: 'MN', name: 'Manipur', type: 'state' },
  { code: 'ML', name: 'Meghalaya', type: 'state' },
  { code: 'MZ', name: 'Mizoram', type: 'state' },
  { code: 'NL', name: 'Nagaland', type: 'state' },
  { code: 'OR', name: 'Odisha', type: 'state' },
  { code: 'PB', name: 'Punjab', type: 'state' },
  { code: 'RJ', name: 'Rajasthan', type: 'state' },
  { code: 'SK', name: 'Sikkim', type: 'state' },
  { code: 'TN', name: 'Tamil Nadu', type: 'state' },
  { code: 'TG', name: 'Telangana', type: 'state' },
  { code: 'TR', name: 'Tripura', type: 'state' },
  { code: 'UP', name: 'Uttar Pradesh', type: 'state' },
  { code: 'UT', name: 'Uttarakhand', type: 'state' },
  { code: 'WB', name: 'West Bengal', type: 'state' },

  // Union Territories (8)
  { code: 'AN', name: 'Andaman and Nicobar Islands', type: 'ut' },
  { code: 'CH', name: 'Chandigarh', type: 'ut' },
  { code: 'DN', name: 'Dadra and Nagar Haveli and Daman and Diu', type: 'ut' },
  { code: 'DL', name: 'Delhi', type: 'ut' },
  { code: 'JK', name: 'Jammu and Kashmir', type: 'ut' },
  { code: 'LA', name: 'Ladakh', type: 'ut' },
  { code: 'LD', name: 'Lakshadweep', type: 'ut' },
  { code: 'PY', name: 'Puducherry', type: 'ut' }
];

// GST State Codes (for invoicing)
const GST_STATE_CODES = {
  'Jammu and Kashmir': '01',
  'Himachal Pradesh': '02',
  'Punjab': '03',
  'Chandigarh': '04',
  'Uttarakhand': '05',
  'Haryana': '06',
  'Delhi': '07',
  'Rajasthan': '08',
  'Uttar Pradesh': '09',
  'Bihar': '10',
  'Sikkim': '11',
  'Arunachal Pradesh': '12',
  'Nagaland': '13',
  'Manipur': '14',
  'Mizoram': '15',
  'Tripura': '16',
  'Meghalaya': '17',
  'Assam': '18',
  'West Bengal': '19',
  'Jharkhand': '20',
  'Odisha': '21',
  'Chhattisgarh': '22',
  'Madhya Pradesh': '23',
  'Gujarat': '24',
  'Dadra and Nagar Haveli and Daman and Diu': '26',
  'Maharashtra': '27',
  'Andhra Pradesh': '28',
  'Karnataka': '29',
  'Goa': '30',
  'Lakshadweep': '31',
  'Kerala': '32',
  'Tamil Nadu': '33',
  'Puducherry': '34',
  'Andaman and Nicobar Islands': '35',
  'Telangana': '36',
  'Ladakh': '38'
};
```

### 5.4 Phone Number Formatting

```javascript
// Indian mobile number validation
const validateIndianMobile = (number) => {
  // Remove spaces, dashes, and +91 country code
  const cleaned = number.replace(/[\s\-+]/g, '');

  // Check if starts with country code
  if (cleaned.startsWith('91') && cleaned.length === 12) {
    return cleaned.substring(2);  // Remove country code
  }

  // Check if valid 10-digit number starting with 6-9
  const mobileRegex = /^[6-9][0-9]{9}$/;
  if (mobileRegex.test(cleaned)) {
    return cleaned;
  }

  return null;  // Invalid
};

// Format for display
const formatIndianMobile = (number, includeCountryCode = false) => {
  const validated = validateIndianMobile(number);
  if (!validated) return null;

  // Format: +91 98765 43210 or 98765 43210
  const formatted = `${validated.slice(0, 5)} ${validated.slice(5)}`;

  return includeCountryCode ? `+91 ${formatted}` : formatted;
};

console.log(formatIndianMobile('9876543210', true));  // +91 98765 43210
```

### 5.5 Location Services

```javascript
// Google Maps integration for India
const initIndianMap = (containerId, options = {}) => {
  const defaultOptions = {
    center: { lat: 20.5937, lng: 78.9629 },  // Center of India
    zoom: 5,
    language: 'en-IN',
    region: 'IN'
  };

  const map = new google.maps.Map(
    document.getElementById(containerId),
    { ...defaultOptions, ...options }
  );

  return map;
};

// Common Indian city coordinates
const INDIAN_CITIES = {
  'Delhi': { lat: 28.6139, lng: 77.2090 },
  'Mumbai': { lat: 19.0760, lng: 72.8777 },
  'Bangalore': { lat: 12.9716, lng: 77.5946 },
  'Hyderabad': { lat: 17.3850, lng: 78.4867 },
  'Chennai': { lat: 13.0827, lng: 80.2707 },
  'Kolkata': { lat: 22.5726, lng: 88.3639 },
  'Pune': { lat: 18.5204, lng: 73.8567 },
  'Ahmedabad': { lat: 23.0225, lng: 72.5714 },
  'Jaipur': { lat: 26.9124, lng: 75.7873 },
  'Lucknow': { lat: 26.8467, lng: 80.9462 }
};

// Distance calculation (km)
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};
```

---

## 6. Documentation and Help

### 6.1 Support Channel Preferences

**Priority Order** (based on popularity in India):
1. **WhatsApp** (Most preferred)
2. **Phone call**
3. **In-app chat**
4. **Email**
5. **Self-service/FAQ**

```javascript
// Multi-channel support configuration
const SUPPORT_CHANNELS = {
  whatsapp: {
    enabled: true,
    number: '+919876543210',
    businessAccountId: 'YOUR_WABA_ID',
    priority: 1,
    label: 'Chat on WhatsApp',
    icon: 'whatsapp',
    hours: '24/7'
  },
  phone: {
    enabled: true,
    numbers: {
      tollfree: '1800-123-4567',
      support: '+91-80-1234-5678'
    },
    priority: 2,
    label: 'Call Us',
    icon: 'phone',
    hours: '9 AM - 9 PM IST'
  },
  chat: {
    enabled: true,
    provider: 'intercom',
    priority: 3,
    label: 'Live Chat',
    icon: 'message',
    hours: '9 AM - 6 PM IST'
  },
  email: {
    enabled: true,
    address: 'support@company.com',
    priority: 4,
    label: 'Email Support',
    icon: 'email',
    responseTime: '24 hours'
  }
};

// WhatsApp Business integration
const initiateWhatsAppSupport = (message = '') => {
  const phone = SUPPORT_CHANNELS.whatsapp.number.replace(/[^\d]/g, '');
  const encodedMessage = encodeURIComponent(message || 'Hi, I need help with...');

  const whatsappURL = `https://wa.me/${phone}?text=${encodedMessage}`;
  window.open(whatsappURL, '_blank');
};

// Click-to-call functionality
const initiatePhoneCall = (numberType = 'tollfree') => {
  const number = SUPPORT_CHANNELS.phone.numbers[numberType];
  window.location.href = `tel:${number}`;
};
```

### 6.2 Documentation Style

**Best Practices**:
- Step-by-step tutorials with screenshots
- Video tutorials (Hindi and English)
- Simple language, avoid jargon
- Visual guides preferred
- Examples with Indian context

```javascript
// Documentation structure
const documentationConfig = {
  languages: ['en', 'hi'],  // English and Hindi minimum
  formats: {
    text: {
      maxParagraphLength: 4,  // Keep paragraphs short
      includeExamples: true,
      contextualizeForIndia: true
    },
    video: {
      maxDuration: 3,  // 3 minutes max
      languages: ['en', 'hi', 'regional'],
      subtitles: true,
      transcripts: true
    },
    interactive: {
      tooltips: true,
      walkthroughs: true,
      sandbox: true
    }
  },
  searchOptimization: {
    hinglish: true,  // Support mixed language queries
    voiceSearch: true,
    autocomplete: true
  }
};

// Contextual help system
const provideContextualHelp = (context) => {
  return {
    tooltip: getTooltip(context),
    helpLink: getHelpArticle(context),
    videoTutorial: getVideoTutorial(context),
    quickActions: getSuggestedActions(context),
    contactSupport: {
      whatsapp: true,
      chat: true,
      email: true
    }
  };
};
```

### 6.3 Onboarding Best Practices

```javascript
// Indian user onboarding flow
const onboardingFlow = {
  steps: [
    {
      id: 'language_selection',
      title: 'Choose Your Language',
      description: 'अपनी भाषा चुनें',
      type: 'language_picker',
      skippable: false,
      languages: INDIAN_LANGUAGES
    },
    {
      id: 'phone_verification',
      title: 'Verify Your Phone Number',
      type: 'otp',
      method: 'sms',  // SMS OTP is standard in India
      duration: 180,  // 3 minutes
      resendDelay: 30
    },
    {
      id: 'basic_profile',
      title: 'Complete Your Profile',
      fields: ['name', 'email', 'city'],
      optional: ['photo', 'dob'],
      skippable: true
    },
    {
      id: 'tutorial',
      title: 'Quick Tour',
      type: 'interactive',
      duration: 60,  // 1 minute
      format: 'tooltip_walkthrough',
      skippable: true
    },
    {
      id: 'preferences',
      title: 'Customize Your Experience',
      settings: ['notifications', 'theme', 'data_saver'],
      skippable: true
    }
  ],

  options: {
    progressIndicator: true,
    allowBack: true,
    saveProgress: true,
    skipToEnd: true,
    estimatedTime: '2-3 minutes'
  }
};

// OTP verification (common in India)
const sendOTP = async (mobileNumber) => {
  const validated = validateIndianMobile(mobileNumber);
  if (!validated) {
    throw new Error('Invalid mobile number');
  }

  // Send OTP via SMS gateway
  const otp = generateOTP(6);  // 6-digit OTP

  await sendSMS({
    to: `+91${validated}`,
    message: `Your OTP is ${otp}. Valid for 3 minutes. Do not share with anyone.`,
    templateId: 'OTP_TEMPLATE'  // DLT registered template
  });

  // Store OTP hash with expiry
  await storeOTP(validated, otp, 180);  // 3 minutes

  return { success: true, expiresIn: 180 };
};

// Generate OTP
const generateOTP = (length = 6) => {
  return Math.floor(
    Math.random() * (10 ** length - 10 ** (length - 1)) + 10 ** (length - 1)
  ).toString();
};
```

### 6.4 Multi-Language Documentation

```javascript
// Documentation translation system
const documentationSystem = {
  // Primary languages
  primaryLanguages: ['en', 'hi'],

  // Regional languages (based on user base)
  regionalLanguages: ['ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml'],

  // Translation priority
  translationPriority: {
    critical: ['getting_started', 'payments', 'security', 'support'],
    high: ['features', 'tutorials', 'faq'],
    medium: ['advanced_features', 'api_docs'],
    low: ['blog', 'updates']
  },

  // Localization options
  localization: {
    dateFormat: 'DD/MM/YYYY',
    timeFormat: '12h',
    currency: 'INR',
    numberFormat: 'en-IN',
    examples: 'indian_context'  // Use Indian names, cities, scenarios
  }
};

// Smart language detection
const detectUserLanguage = () => {
  // Priority: 1. User preference, 2. Browser, 3. Location
  const userPreference = localStorage.getItem('preferredLanguage');
  if (userPreference) return userPreference;

  const browserLang = navigator.language || navigator.userLanguage;
  const langCode = browserLang.split('-')[0];

  // Check if it's an Indian language
  const indianLangCodes = Object.keys(INDIAN_LANGUAGES);
  if (indianLangCodes.includes(langCode)) {
    return langCode;
  }

  return 'en';  // Default to English
};
```

---

## 7. Payment Integration

### 7.1 UPI Integration

**UPI Overview**:
- 83% of India's digital payments
- Instant, 24/7 transfers
- No transaction fees for consumers
- Popular apps: PhonePe, Google Pay, Paytm, BHIM

```javascript
// UPI Payment Integration
const initiateUPIPayment = (paymentDetails) => {
  const {
    amount,
    merchantName,
    merchantVPA,  // Virtual Payment Address
    transactionRef,
    transactionNote
  } = paymentDetails;

  // UPI Deep Link format
  const upiURL = `upi://pay?` +
    `pa=${merchantVPA}` +  // Payee address
    `&pn=${encodeURIComponent(merchantName)}` +  // Payee name
    `&am=${amount}` +  // Amount
    `&cu=INR` +  // Currency
    `&tn=${encodeURIComponent(transactionNote)}` +  // Transaction note
    `&tr=${transactionRef}`;  // Transaction reference

  // For mobile web - opens UPI app
  if (isMobileDevice()) {
    window.location.href = upiURL;
  } else {
    // For desktop - show QR code
    generateUPIQRCode(upiURL);
  }

  return {
    method: 'UPI',
    status: 'initiated',
    transactionRef: transactionRef
  };
};

// UPI QR Code generation
const generateUPIQRCode = (upiString) => {
  // Use QR code library (e.g., qrcode.js)
  const qr = new QRCode(document.getElementById('qrcode'), {
    text: upiString,
    width: 256,
    height: 256,
    colorDark: '#000000',
    colorLight: '#ffffff'
  });

  return qr;
};

// Verify UPI ID format
const validateUPI = (upiId) => {
  // Format: username@bankname
  const upiRegex = /^[\w.-]+@[\w.-]+$/;
  return upiRegex.test(upiId);
};

// Check payment status
const checkUPIPaymentStatus = async (transactionRef) => {
  // Call payment gateway API
  const response = await fetch(`/api/payment/status/${transactionRef}`);
  const data = await response.json();

  return {
    status: data.status,  // SUCCESS, PENDING, FAILED
    transactionId: data.transactionId,
    amount: data.amount,
    timestamp: data.timestamp
  };
};
```

### 7.2 Payment Gateway Integration

```javascript
// Multi-payment gateway support
const PAYMENT_GATEWAYS = {
  razorpay: {
    enabled: true,
    methods: ['UPI', 'Cards', 'NetBanking', 'Wallets'],
    apiKey: 'YOUR_KEY',
    features: {
      savedCards: true,
      recurring: true,
      instantRefunds: true
    }
  },
  paytm: {
    enabled: true,
    methods: ['UPI', 'Paytm Wallet', 'Cards', 'NetBanking'],
    merchantId: 'YOUR_MERCHANT_ID',
    features: {
      wallet: true,
      postpaid: true
    }
  },
  phonepe: {
    enabled: true,
    methods: ['UPI', 'Cards', 'Wallets'],
    merchantId: 'YOUR_MERCHANT_ID',
    features: {
      creditLineOnUPI: true,  // New 2024 feature
      upiCircle: true  // Family payment feature
    }
  },
  cashfree: {
    enabled: true,
    methods: ['UPI', 'Cards', 'NetBanking', 'Wallets', 'EMI'],
    appId: 'YOUR_APP_ID'
  }
};

// Initialize payment
const initiatePayment = async (orderDetails) => {
  const {
    amount,
    currency = 'INR',
    orderId,
    customerDetails,
    preferredMethod
  } = orderDetails;

  // Create order
  const order = await createPaymentOrder({
    amount: Math.round(amount * 100),  // Convert to paise
    currency: currency,
    receipt: orderId,
    notes: {
      customer_name: customerDetails.name,
      customer_phone: customerDetails.phone
    }
  });

  // Initialize payment UI
  const options = {
    key: PAYMENT_GATEWAYS.razorpay.apiKey,
    amount: order.amount,
    currency: order.currency,
    name: 'Your Company Name',
    description: orderDetails.description,
    order_id: order.id,

    // Customer details
    prefill: {
      name: customerDetails.name,
      email: customerDetails.email,
      contact: customerDetails.phone
    },

    // Preferred payment method
    method: preferredMethod || 'upi',

    // Callback handlers
    handler: function(response) {
      verifyPayment(response);
    },

    modal: {
      ondismiss: function() {
        handlePaymentCancelled();
      }
    },

    // Theme
    theme: {
      color: '#3399cc'
    },

    // Display preferences
    image: 'https://your-logo-url.com/logo.png',

    // UPI specific options
    config: {
      display: {
        blocks: {
          banks: {
            name: 'Pay via UPI',
            instruments: [
              {
                method: 'upi',
                flows: ['qr', 'intent']  // QR code + app intent
              }
            ]
          }
        },
        sequence: ['block.banks'],
        preferences: {
          show_default_blocks: true
        }
      }
    }
  };

  const rzp = new Razorpay(options);
  rzp.open();
};

// Payment verification
const verifyPayment = async (paymentResponse) => {
  const {
    razorpay_order_id,
    razorpay_payment_id,
    razorpay_signature
  } = paymentResponse;

  // Verify signature on backend
  const verification = await fetch('/api/payment/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      order_id: razorpay_order_id,
      payment_id: razorpay_payment_id,
      signature: razorpay_signature
    })
  });

  const result = await verification.json();

  if (result.verified) {
    handlePaymentSuccess(paymentResponse);
  } else {
    handlePaymentFailure('Verification failed');
  }
};
```

### 7.3 Payment Method Display

```javascript
// Popular payment methods in India
const PAYMENT_METHODS = [
  {
    id: 'upi',
    name: 'UPI',
    icon: '📱',
    popular: true,
    description: 'Pay via PhonePe, Google Pay, Paytm',
    processingTime: 'Instant',
    fees: 'Free'
  },
  {
    id: 'cards',
    name: 'Credit/Debit Cards',
    icon: '💳',
    description: 'Visa, Mastercard, RuPay',
    processingTime: 'Instant',
    fees: '2% + GST'
  },
  {
    id: 'netbanking',
    name: 'Net Banking',
    icon: '🏦',
    description: 'Pay via your bank account',
    processingTime: 'Instant',
    fees: 'Free'
  },
  {
    id: 'wallets',
    name: 'Wallets',
    icon: '👛',
    description: 'Paytm, PhonePe, Amazon Pay',
    processingTime: 'Instant',
    fees: 'Free'
  },
  {
    id: 'emi',
    name: 'EMI',
    icon: '📊',
    description: 'Pay in monthly installments',
    processingTime: 'Instant',
    fees: 'Varies'
  },
  {
    id: 'cod',
    name: 'Cash on Delivery',
    icon: '💵',
    description: 'Pay when you receive',
    processingTime: 'On delivery',
    fees: '₹50'
  }
];

// Display payment options
const renderPaymentOptions = (amount) => {
  return PAYMENT_METHODS.map(method => ({
    ...method,
    available: isMethodAvailable(method.id, amount),
    recommended: method.id === 'upi'  // UPI is most popular
  }));
};
```

### 7.4 Payment Success Rates

**Best Practices for High Success Rates**:
1. Multiple payment options
2. Retry logic for failed transactions
3. Smart routing based on success rates
4. Saved cards/UPI IDs
5. Clear error messages

```javascript
// Retry failed payments
const retryFailedPayment = async (failedPaymentId) => {
  const paymentDetails = await getPaymentDetails(failedPaymentId);

  // Suggest alternative payment method
  const alternatives = PAYMENT_METHODS.filter(
    method => method.id !== paymentDetails.attemptedMethod
  );

  return {
    orderId: paymentDetails.orderId,
    amount: paymentDetails.amount,
    suggestedMethods: alternatives,
    message: 'Payment failed. Please try another payment method.'
  };
};

// Save successful payment methods
const savePaymentMethod = async (userId, paymentMethod) => {
  if (paymentMethod.type === 'upi') {
    // Save UPI ID for future use
    await saveUserPreference(userId, {
      savedUPI: paymentMethod.vpa
    });
  } else if (paymentMethod.type === 'card') {
    // Tokenize and save card
    await saveCardToken(userId, paymentMethod.token);
  }
};
```

---

## 8. Data Privacy and Compliance

### 8.1 DPDPA (Digital Personal Data Protection Act) 2023

**Status**: Passed in August 2023, rules pending (not yet effective as of Nov 2024)

**Key Requirements**:

```javascript
// DPDPA Compliance Framework
const DPDPACompliance = {
  // 1. Consent Management
  consent: {
    required: true,
    type: 'explicit',  // Clear, specific, informed
    granular: true,  // Per-purpose consent
    withdrawable: true,  // Easy withdrawal mechanism

    implementation: {
      consentForm: {
        clear: true,
        specific: true,
        purpose: 'Must state exact purpose',
        language: 'Simple, understandable language',
        noPreChecked: true  // No pre-checked boxes
      }
    }
  },

  // 2. Data Minimization
  dataCollection: {
    principle: 'Collect only necessary data',
    purpose: 'Specified and lawful purpose only',
    retention: 'Delete after purpose fulfilled'
  },

  // 3. Data Principal Rights
  userRights: {
    access: 'Right to access their data',
    correction: 'Right to correct inaccuracies',
    deletion: 'Right to erasure',
    portability: 'Right to data portability',
    grievance: 'Right to grievance redressal'
  },

  // 4. Data Breach Notification
  breachNotification: {
    authority: 'Data Protection Board',
    timeline: 'As specified in rules (TBD)',
    users: 'Affected users must be notified'
  },

  // 5. Penalties
  penalties: {
    min: '₹10,000 (~$120)',
    max: '₹250 crores (~$30 million)'
  }
};
```

### 8.2 Consent Management

```javascript
// Consent management system
class ConsentManager {
  constructor(userId) {
    this.userId = userId;
    this.consents = {};
  }

  // Request consent
  async requestConsent(purpose, description) {
    const consent = {
      purpose: purpose,
      description: description,
      requestedAt: new Date().toISOString(),
      status: 'pending',
      language: detectUserLanguage()
    };

    // Show consent dialog
    const userResponse = await showConsentDialog(consent);

    if (userResponse.accepted) {
      consent.status = 'granted';
      consent.grantedAt = new Date().toISOString();
    } else {
      consent.status = 'denied';
      consent.deniedAt = new Date().toISOString();
    }

    // Store consent record
    await this.storeConsent(purpose, consent);

    return consent;
  }

  // Check if consent exists
  async hasConsent(purpose) {
    const consent = await this.getConsent(purpose);
    return consent && consent.status === 'granted';
  }

  // Withdraw consent
  async withdrawConsent(purpose) {
    const consent = await this.getConsent(purpose);

    if (consent) {
      consent.status = 'withdrawn';
      consent.withdrawnAt = new Date().toISOString();
      await this.storeConsent(purpose, consent);

      // Delete associated data
      await this.deleteDataForPurpose(purpose);
    }

    return consent;
  }

  // Get all consents
  async getAllConsents() {
    return await db.consents.find({ userId: this.userId });
  }

  // Store consent
  async storeConsent(purpose, consent) {
    await db.consents.upsert({
      userId: this.userId,
      purpose: purpose,
      ...consent
    });
  }

  // Get consent
  async getConsent(purpose) {
    return await db.consents.findOne({
      userId: this.userId,
      purpose: purpose
    });
  }

  // Delete data after purpose fulfilled
  async deleteDataForPurpose(purpose) {
    // Implement data deletion logic
    await db.userData.deleteMany({
      userId: this.userId,
      purpose: purpose
    });
  }
}

// Consent dialog component
const showConsentDialog = async (consent) => {
  return new Promise((resolve) => {
    const dialog = {
      title: 'Data Collection Consent',
      content: `
        <h3>Purpose: ${consent.purpose}</h3>
        <p>${consent.description}</p>

        <h4>We will collect:</h4>
        <ul>
          <li>Your name and contact details</li>
          <li>Usage information</li>
          <li>[Specific data points]</li>
        </ul>

        <h4>How we'll use it:</h4>
        <p>[Specific usage description]</p>

        <h4>Your rights:</h4>
        <ul>
          <li>You can withdraw consent anytime</li>
          <li>You can request data deletion</li>
          <li>You can access your data</li>
        </ul>
      `,
      buttons: [
        {
          text: 'I Accept',
          action: () => resolve({ accepted: true })
        },
        {
          text: 'I Decline',
          action: () => resolve({ accepted: false })
        }
      ]
    };

    // Display dialog to user
    displayDialog(dialog);
  });
};
```

### 8.3 Data Subject Rights Implementation

```javascript
// Data Subject Access Request (DSAR)
class DSARHandler {
  constructor(userId) {
    this.userId = userId;
  }

  // Right to Access
  async handleAccessRequest() {
    const userData = await this.getAllUserData();

    return {
      personalInfo: userData.profile,
      activityLog: userData.activities,
      consents: userData.consents,
      dataSharing: userData.thirdPartySharing,
      retentionPeriod: userData.retentionDetails,
      exportFormat: 'JSON',  // Also support CSV, PDF
      requestId: generateRequestId(),
      generatedAt: new Date().toISOString()
    };
  }

  // Right to Correction
  async handleCorrectionRequest(corrections) {
    const validatedCorrections = this.validateCorrections(corrections);

    for (const correction of validatedCorrections) {
      await this.updateUserData(correction.field, correction.newValue);
    }

    return {
      status: 'completed',
      correctedFields: validatedCorrections.map(c => c.field),
      updatedAt: new Date().toISOString()
    };
  }

  // Right to Deletion (Erasure)
  async handleDeletionRequest() {
    // Check if data can be deleted
    const obligations = await this.checkLegalObligations();

    if (obligations.mustRetain) {
      return {
        status: 'partial_deletion',
        retained: obligations.reasons,
        message: 'Some data must be retained for legal compliance'
      };
    }

    // Soft delete user data
    await this.softDeleteUserData();

    // Schedule hard delete after retention period
    await this.scheduleHardDelete(90);  // 90 days

    return {
      status: 'deletion_initiated',
      softDeletedAt: new Date().toISOString(),
      hardDeleteScheduled: new Date(Date.now() + 90*24*60*60*1000).toISOString(),
      message: 'Your data will be permanently deleted in 90 days'
    };
  }

  // Right to Data Portability
  async handlePortabilityRequest(format = 'json') {
    const userData = await this.getAllUserData();

    let exportData;
    switch(format.toLowerCase()) {
      case 'json':
        exportData = JSON.stringify(userData, null, 2);
        break;
      case 'csv':
        exportData = this.convertToCSV(userData);
        break;
      case 'pdf':
        exportData = await this.generatePDF(userData);
        break;
      default:
        exportData = JSON.stringify(userData, null, 2);
    }

    return {
      data: exportData,
      format: format,
      generatedAt: new Date().toISOString(),
      downloadLink: await this.generateSecureDownloadLink(exportData)
    };
  }

  // Grievance handling
  async submitGrievance(grievance) {
    const ticket = {
      ticketId: generateTicketId(),
      userId: this.userId,
      type: grievance.type,
      description: grievance.description,
      status: 'submitted',
      submittedAt: new Date().toISOString(),
      slaResolutionTime: '30 days'  // As per DPDPA
    };

    await db.grievances.insert(ticket);

    // Notify user
    await sendNotification(this.userId, {
      title: 'Grievance Submitted',
      body: `Your grievance (ID: ${ticket.ticketId}) has been submitted and will be resolved within 30 days.`,
      channel: 'email_and_sms'
    });

    return ticket;
  }

  // Get all user data
  async getAllUserData() {
    return {
      profile: await db.users.findOne({ id: this.userId }),
      activities: await db.activities.find({ userId: this.userId }),
      consents: await db.consents.find({ userId: this.userId }),
      payments: await db.payments.find({ userId: this.userId }),
      preferences: await db.preferences.findOne({ userId: this.userId })
    };
  }

  // Check legal obligations for retention
  async checkLegalObligations() {
    // Check financial records (7 years GST requirement)
    const hasFinancialRecords = await db.payments.exists({ userId: this.userId });

    // Check ongoing legal proceedings
    const hasLegalCases = await db.legalCases.exists({ userId: this.userId });

    return {
      mustRetain: hasFinancialRecords || hasLegalCases,
      reasons: {
        financial: hasFinancialRecords ? '7 years GST retention requirement' : null,
        legal: hasLegalCases ? 'Ongoing legal proceedings' : null
      }
    };
  }
}
```

### 8.4 Privacy Policy Template

```javascript
// Generate India-compliant privacy policy
const generatePrivacyPolicy = (companyDetails) => {
  return {
    sections: [
      {
        title: 'Data Fiduciary Information',
        content: `
          Company Name: ${companyDetails.name}
          Address: ${companyDetails.address}
          Contact: ${companyDetails.email}
          Grievance Officer: ${companyDetails.grievanceOfficer}
        `
      },
      {
        title: 'Data Collection',
        content: `
          We collect the following data:
          - Personal information (name, email, phone)
          - Usage data
          - Device information

          Purpose: [Specific purposes]
          Legal Basis: Consent / Contractual / Legal Obligation
        `
      },
      {
        title: 'Data Usage',
        content: `
          Your data is used for:
          1. Providing services
          2. Communication
          3. Analytics
          4. [Other purposes]

          We do NOT use your data for purposes beyond what you consented to.
        `
      },
      {
        title: 'Data Sharing',
        content: `
          We may share data with:
          - Service providers (with data processing agreements)
          - Legal authorities (when required by law)

          We do NOT sell your personal data.
        `
      },
      {
        title: 'Your Rights under DPDPA',
        content: `
          You have the right to:
          1. Access your data
          2. Correct inaccuracies
          3. Request deletion
          4. Data portability
          5. Withdraw consent
          6. Grievance redressal

          To exercise these rights, contact: ${companyDetails.email}
        `
      },
      {
        title: 'Data Security',
        content: `
          We implement industry-standard security measures:
          - Encryption (in transit and at rest)
          - Access controls
          - Regular security audits
          - Incident response procedures
        `
      },
      {
        title: 'Data Retention',
        content: `
          We retain your data:
          - As long as you use our services
          - For legal/regulatory requirements (e.g., 7 years for financial records)
          - After deletion request: soft delete immediately, hard delete after 90 days
        `
      },
      {
        title: 'International Data Transfers',
        content: `
          If we transfer data outside India, we ensure:
          - Adequate data protection measures
          - Compliance with DPDPA requirements
          - User consent where required
        `
      },
      {
        title: 'Children\'s Privacy',
        content: `
          Users under 18 require parental consent.
          We implement age verification mechanisms.
        `
      },
      {
        title: 'Updates to Policy',
        content: `
          Last updated: ${new Date().toLocaleDateString('en-IN')}
          We will notify you of material changes via email/in-app notification.
        `
      }
    ],

    languages: ['en', 'hi'],  // Provide in multiple languages
    lastUpdated: new Date().toISOString(),
    version: '1.0'
  };
};
```

### 8.5 Security Best Practices

```javascript
// Security configuration for Indian applications
const securityConfig = {
  // Authentication
  authentication: {
    mfa: {
      enabled: true,
      methods: ['otp_sms', 'otp_email', 'authenticator_app'],
      mandatory: true  // For sensitive operations
    },
    passwordPolicy: {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
      expiryDays: 90
    },
    sessionManagement: {
      timeout: 30,  // 30 minutes
      renewalThreshold: 5  // Renew 5 min before expiry
    }
  },

  // Data encryption
  encryption: {
    inTransit: {
      protocol: 'TLS 1.3',
      enforceHTTPS: true
    },
    atRest: {
      algorithm: 'AES-256',
      keyRotation: 90  // days
    }
  },

  // Access control
  accessControl: {
    principle: 'least_privilege',
    rbac: true,  // Role-based access control
    logging: true,
    auditTrail: true
  },

  // Compliance
  compliance: {
    dpdpa: true,
    iso27001: true,
    pciDss: true,  // If handling card payments
    certIn: true  // Indian CERT guidelines
  }
};
```

---

## Summary: Key Implementation Checklist

### Must-Have Features

✅ **Number & Currency**:
- [ ] Indian number formatting (lakhs, crores)
- [ ] INR currency display with ₹ symbol
- [ ] GST calculation with proper rounding
- [ ] Fiscal year (April-March) support

✅ **Date & Time**:
- [ ] DD/MM/YYYY date format
- [ ] IST timezone (UTC+5:30)
- [ ] 12-hour time format

✅ **Language & Communication**:
- [ ] Multi-language support (Hindi + regional)
- [ ] Hinglish understanding
- [ ] Formal communication tone
- [ ] Native script display

✅ **Mobile & Performance**:
- [ ] Mobile-first responsive design
- [ ] Low bandwidth optimization
- [ ] Offline capability
- [ ] Large touch targets (48px minimum)

✅ **Payments**:
- [ ] UPI integration (primary)
- [ ] Multiple payment gateways
- [ ] Support for all popular payment methods
- [ ] Instant payment confirmation

✅ **Location**:
- [ ] Indian address format
- [ ] PIN code validation & lookup
- [ ] State/UT dropdown
- [ ] Indian mobile number format

✅ **Support**:
- [ ] WhatsApp Business integration
- [ ] Phone support (with toll-free)
- [ ] Multi-language documentation
- [ ] Visual tutorials

✅ **Privacy**:
- [ ] DPDPA compliance (when effective)
- [ ] Explicit consent management
- [ ] Data subject rights (access, deletion, portability)
- [ ] Grievance redressal mechanism

✅ **Cultural**:
- [ ] Festival-aware features
- [ ] Vegetarian/Non-veg indicators
- [ ] Cultural sensitivity checks
- [ ] Regional customization

---

## Additional Resources

### APIs & Services:
- **India Post PIN Code API**: https://www.postalpincode.in/api-details.php
- **GST API**: https://gst.gov.in/
- **UPI Payment Gateway**: Razorpay, Paytm, PhonePe, Cashfree
- **Indian Fonts**: Google Fonts (Noto Sans, Baloo family)

### Regulatory:
- **DPDPA**: https://www.meity.gov.in/
- **RBI Payment Guidelines**: https://www.rbi.org.in/
- **GST Portal**: https://www.gst.gov.in/

### Testing:
- Test with Indian mobile numbers format
- Test with various Indian payment methods
- Test with low bandwidth (3G simulation)
- Test in multiple Indian languages
- Test during Indian business hours (9 AM - 6 PM IST)

---

*Document Version: 1.0*
*Last Updated: November 6, 2024*
*Based on 2024-2025 research and requirements*
