# 🎨 Bitcoin DeFi Visual Reference

## Quick Color Reference

```
Backgrounds:
├─ True Void        #030304  ███████  Main background
├─ Dark Matter      #0F1115  ███████  Cards, surfaces
└─ Black/Transparent variants for layering

Accents:
├─ Bitcoin Orange   #F7931A  ███████  Primary CTA, links, data
├─ Burnt Orange     #EA580C  ███████  Secondary, gradients
└─ Digital Gold     #FFD600  ███████  Success, highlights

Text:
├─ White            #FFFFFF  ███████  Headings, primary text
└─ Stardust         #94A3B8  ███████  Secondary, labels

Borders:
└─ Dim Boundary     #1E293B  ███████  At 10-20% opacity
```

---

## Component Patterns

### 🔘 Buttons

```tsx
// Primary - Gradient Pill
<button className="
  px-8 py-4 
  bg-gradient-to-r from-burnt-orange to-bitcoin-orange 
  text-white rounded-full 
  font-bold uppercase tracking-widest 
  shadow-orange-glow 
  hover:scale-105 hover:shadow-orange-glow-lg 
  transition-all duration-300
">
  Action
</button>

// Secondary - Outline
<button className="
  px-8 py-4 
  bg-white/10 border-2 border-white/20 
  text-white rounded-full 
  font-bold uppercase tracking-widest 
  hover:bg-white/20 hover:border-bitcoin-orange/50 
  transition-all duration-300
">
  Cancel
</button>

// Icon Button
<button className="
  p-3 
  bg-white/10 border border-white/20 
  rounded-lg 
  hover:bg-bitcoin-orange/20 hover:border-bitcoin-orange/50 
  transition-all duration-300
">
  <Icon className="w-5 h-5 text-white" />
</button>
```

---

### 📦 Cards

```tsx
// Standard Card
<div className="
  bg-dark-matter 
  rounded-2xl 
  border border-white/10 
  p-8 
  shadow-card-elevation 
  transition-all duration-300 
  hover:-translate-y-1 
  hover:border-bitcoin-orange/30
">
  Content
</div>

// Glass Card
<div className="
  bg-black/40 
  backdrop-blur-lg 
  border border-white/10 
  rounded-2xl 
  p-6
">
  Floating content
</div>

// Stat Card with Glow
<div className="
  bg-bitcoin-orange/10 
  border border-bitcoin-orange/30 
  p-4 
  rounded-xl 
  backdrop-blur-sm
">
  <p className="text-xs text-stardust font-mono uppercase tracking-wider">
    Label
  </p>
  <p className="text-2xl font-bold font-mono text-bitcoin-orange mt-1">
    1,234
  </p>
</div>
```

---

### 📝 Form Elements

```tsx
// Input (Bottom Border Style)
<input 
  type="text"
  className="
    w-full h-12 
    px-4 
    bg-black/50 
    border-b-2 border-white/20 
    text-white text-sm 
    focus-visible:border-bitcoin-orange 
    focus-visible:outline-none 
    focus-visible:shadow-input-focus 
    transition-all duration-200 
    placeholder:text-white/30
  "
  placeholder="Enter value"
/>

// Label
<label className="
  block text-sm 
  font-mono font-medium 
  text-stardust 
  mb-2 
  uppercase tracking-wider
">
  Field Name
</label>

// Select/Dropdown (styled similarly to input)
<select className="
  w-full h-12 
  px-4 
  bg-black/50 
  border-b-2 border-white/20 
  text-white text-sm 
  focus-visible:border-bitcoin-orange 
  focus-visible:outline-none
">
  <option>Option 1</option>
</select>
```

---

### 🎯 Badges & Tags

```tsx
// Status Badge
<span className="
  px-3 py-1 
  rounded-lg 
  text-sm font-mono font-semibold 
  uppercase tracking-wider 
  bg-bitcoin-orange/20 
  text-bitcoin-orange 
  border border-bitcoin-orange/50
">
  Active
</span>

// Colored Dots
<div className="
  w-3 h-3 
  bg-bitcoin-orange 
  rounded-full 
  shadow-[0_0_8px_rgba(247,147,26,0.6)]
" />
```

---

### 🎨 Typography

```tsx
// Hero Title with Gradient
<h1 className="
  text-4xl sm:text-5xl md:text-7xl 
  font-heading font-bold 
  text-white leading-tight
">
  Regular Text <span className="gradient-text">Highlighted</span>
</h1>

// Section Heading
<h2 className="
  text-2xl font-heading font-semibold 
  text-white mb-6 
  flex items-center gap-2
">
  <span className="text-bitcoin-orange">━</span> 
  Section Title
</h2>

// Body Text
<p className="text-stardust text-base leading-relaxed">
  Lorem ipsum dolor sit amet...
</p>

// Technical/Data Text
<span className="font-mono text-sm text-bitcoin-orange uppercase tracking-wider">
  FRAME: 123
</span>
```

---

### ✨ Special Effects

```tsx
// Icon Container with Glow
<div className="
  bg-bitcoin-orange/20 
  border border-bitcoin-orange/50 
  rounded-lg p-3
">
  <Icon className="w-6 h-6 text-bitcoin-orange" />
</div>

// Pulsing Indicator
<div className="relative">
  <div className="
    w-4 h-4 
    bg-bitcoin-orange 
    rounded-full 
    shadow-orange-glow 
    animate-pulse
  " />
  <div className="
    absolute inset-0 
    w-4 h-4 
    bg-bitcoin-orange 
    rounded-full 
    animate-ping 
    opacity-50
  " />
</div>

// Floating Animation
<div className="animate-float">
  <YourComponent />
</div>

// Orbital Rings
<div className="relative w-16 h-16">
  {/* Outer ring - clockwise */}
  <div className="
    absolute inset-0 
    border-2 border-bitcoin-orange/30 
    rounded-full 
    animate-spin-slow
  " />
  
  {/* Inner ring - counter-clockwise */}
  <div className="
    absolute inset-2 
    border-2 border-digital-gold/30 
    rounded-full 
    animate-spin-reverse
  " />
  
  {/* Center glow */}
  <div className="
    absolute inset-0 
    flex items-center justify-center
  ">
    <div className="
      w-4 h-4 
      bg-bitcoin-orange 
      rounded-full 
      shadow-orange-glow 
      animate-pulse
    " />
  </div>
</div>
```

---

## Layout Patterns

### 📐 Container
```tsx
<div className="max-w-7xl mx-auto px-4 py-24">
  {/* Content */}
</div>
```

### 📊 Grid Layouts
```tsx
// 2 Column (responsive)
<div className="grid grid-cols-1 md:grid-cols-2 gap-8">
  {/* Items */}
</div>

// 3 Column (responsive)
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  {/* Items */}
</div>

// 4 Column Stats
<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
  {/* Stat cards */}
</div>
```

### 🔄 Flex Layouts
```tsx
// Centered
<div className="flex items-center justify-center gap-4">
  {/* Items */}
</div>

// Space Between
<div className="flex items-center justify-between">
  {/* Left and right items */}
</div>

// Vertical Stack
<div className="space-y-8">
  {/* Stacked items */}
</div>
```

---

## Responsive Breakpoints

```
sm:  640px  - Small tablets
md:  768px  - Tablets, small laptops
lg:  1024px - Laptops, desktops
xl:  1280px - Large desktops
```

### Responsive Typography
```tsx
<h1 className="text-4xl sm:text-5xl md:text-7xl">
  Scales up on larger screens
</h1>
```

### Responsive Grids
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  Mobile: 1 column
  Tablet: 2 columns
  Desktop: 3 columns
</div>
```

---

## Common Combinations

### Card Header
```tsx
<div className="flex items-center gap-3 mb-6">
  <div className="bg-bitcoin-orange/20 border border-bitcoin-orange/50 rounded-lg p-2">
    <Icon className="w-6 h-6 text-bitcoin-orange" />
  </div>
  <h2 className="text-2xl font-heading font-semibold text-white">
    Card Title
  </h2>
</div>
```

### Error State
```tsx
<div className="
  p-6 
  bg-red-500/10 
  border border-red-500/50 
  rounded-2xl 
  backdrop-blur-sm 
  shadow-[0_0_20px_rgba(239,68,68,0.3)]
">
  <h3 className="text-red-400 font-heading font-semibold mb-2">
    Error
  </h3>
  <p className="text-red-300 text-sm">
    Error message
  </p>
</div>
```

### Loading Spinner
```tsx
<div className="flex items-center justify-center">
  <div className="relative">
    {/* Outer ring */}
    <div className="
      w-16 h-16 
      border-2 border-bitcoin-orange/30 
      rounded-full 
      animate-spin-slow
    " />
    
    {/* Inner ring */}
    <div className="
      absolute inset-2 
      border-2 border-digital-gold/30 
      rounded-full 
      animate-spin-reverse
    " />
    
    {/* Center */}
    <div className="
      absolute inset-0 
      flex items-center justify-center
    ">
      <div className="
        w-4 h-4 
        bg-bitcoin-orange 
        rounded-full 
        shadow-orange-glow 
        animate-pulse
      " />
    </div>
  </div>
</div>
```

---

## Utility Classes

### Custom Utilities (in globals.css)
- `.gradient-text` - Bitcoin orange to gold gradient text
- `.bg-grid-pattern` - Blockchain grid background
- `.glass-card` - Glass morphism effect
- `.holographic-gradient` - Ambient gradient background
- `.text-glow` - Text shadow glow

### Spacing Scale
```
p-1  = 4px     p-6  = 24px
p-2  = 8px     p-8  = 32px
p-3  = 12px    p-12 = 48px
p-4  = 16px    p-24 = 96px
```

### Border Radius
```
rounded-lg   = 8px   (inputs, small elements)
rounded-xl   = 12px  (stat cards)
rounded-2xl  = 16px  (major cards)
rounded-full = 9999px (buttons, dots)
```

---

## Animation Timing

- **Instant**: `duration-200` (200ms) - Input focus, small interactions
- **Standard**: `duration-300` (300ms) - Buttons, card hovers
- **Slow**: `duration-500` (500ms) - Page transitions

### Easing
```tsx
transition-all      // All properties
transition-colors   // Only colors
transition-transform // Only transforms
```

---

## 🎯 Pro Tips

1. **Always use defined colors**: `text-bitcoin-orange` not `text-[#F7931A]`
2. **Maintain hover states**: Add lift + glow intensification
3. **Use monospace for data**: Technical precision matters
4. **Stack transparencies**: Layer `bg-white/10` with `backdrop-blur`
5. **Add subtle borders**: `border border-white/10` creates structure
6. **Generous spacing**: Don't be afraid of whitespace (24-32px gaps)
7. **Colored shadows**: Use orange/gold tints instead of black

---

**Quick Start**: Copy any pattern above and customize for your needs!
