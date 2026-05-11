# VIN Decoder Pro — GUI Description

## Application Overview

**VIN Decoder Pro** is a professional desktop application built with Python Tkinter featuring a modern light-blue theme. The interface is designed for automotive professionals who need quick, reliable access to vehicle specifications.

---

## Window Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  VIN DECODER PRO          Professional Vehicle Identification      │  ← Blue Header Bar
├──────────┬──────────────────────────────────────────────────────────┤
│          │  ENTER VEHICLE IDENTIFICATION NUMBER                   │
│  SEARCH  │                                                          │
│ HISTORY  │  ┌─────────────────────────────┐ [Paste] [DECODE VIN]   │
│          │  │ VIN: [____________________] │                        │
│ 1A4RR... │  └─────────────────────────────┘                        │
│ 1FTFW... │  Ready — Enter a 17-character VIN number                │
│ JN1BJ... │                                                          │
│ ...      │  [ Results ] [ Raw JSON ]                               │
│          │  ┌────────────────────────────────────────────────────┐ │
│ [Export] │  │ QUICK SUMMARY                              [Copy All]│ │
│ [Clear]  │  │ VIN: 1A4RR5DG9BC123456                    [📋]     │ │
│          │  │ Vehicle: 2011 Dodge Durango               [📋]     │ │
│ 15 srchs │  │ Engine: ERB 3.6L 6cyl                     [📋]     │ │
│          │  │ Fuel: Gasoline                              [📋]     │ │
│          │  └────────────────────────────────────────────────────┘ │
│          │  ┌────────────────────────────────────────────────────┐ │
│          │  │ VEHICLE IDENTITY                           [Copy All]│ │
│          │  │ Make: Dodge                                 [📋]   │ │
│          │  │ Model: Durango                              [📋]   │ │
│          │  │ Model Year: 2011                            [📋]   │ │
│          │  │ ...                                         [📋]   │ │
│          │  └────────────────────────────────────────────────────┘ │
│          │  ┌────────────────────────────────────────────────────┐ │
│          │  │ ENGINE SPECIFICATIONS                      [Copy All]│ │
│          │  │ Engine Model: ERB                           [📋]   │ │
│          │  │ Displacement (L): 3.6                       [📋]   │ │
│          │  │ Engine Cylinders: 6                         [📋]   │ │
│          │  │ ...                                         [📋]   │ │
│          │  └────────────────────────────────────────────────────┘ │
│          │                                                          │
│          │  2026 3bHussein | ECU Tuning Solutions                   │
└──────────┴──────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Header Bar (Top)
- **Background**: Solid blue (`#1976d2`)
- **Content**: Application title + subtitle
- **Height**: 60px
- **Purpose**: Brand identity and visual anchor

### 2. Left Sidebar — Search History
- **Background**: Light blue (`#e1f0fa`)
- **Width**: 300px (resizable via sash)
- **Components**:
  - **Title Bar**: Blue header with "SEARCH HISTORY" text
  - **Instructions**: Double-click / right-click hints
  - **Listbox**: Scrollable list of decoded VINs
    - Format: `VIN | Year Make Model`
    - Font: Consolas 10pt (monospace for VIN alignment)
    - Selection: Blue highlight with white text
  - **Action Buttons**:
    - `Export CSV` — Exports all history to CSV file
    - `Clear All` — Deletes entire history (with confirmation)
  - **Stats Label**: Shows count of saved searches

### 3. Right Panel — Main Content

#### 3.1 Input Card
- **Background**: White with light blue border
- **Padding**: 25px
- **Components**:
  - **Title**: "ENTER VEHICLE IDENTIFICATION NUMBER" (bold, blue)
  - **Subtitle**: Instructions text (muted gray)
  - **Input Row**:
    - **VIN Entry Field**: Light blue background, 13pt font, 2px blue focus border
    - **Paste Button**: "Paste" text, auto-cleans clipboard content
    - **Decode Button**: "DECODE VIN" — primary action, blue background, white text

#### 3.2 Status Bar
- **Background**: Main background color
- **Text Color**: Changes dynamically:
  - Gray = Ready
  - Orange = Loading
  - Green = Success
  - Red = Error
- **Content**: Current operation status + timestamp

#### 3.3 Notebook Tabs
- **Tab 1: Results** — Formatted vehicle data cards
- **Tab 2: Raw JSON** — Complete API response
- **Styling**: Blue selected tab, gray unselected tabs

### 4. Results Cards

Each card follows this structure:
```
┌─────────────────────────────────────────────────────────────┐
│ ████ Blue accent line (4px)                                 │
│                                                             │
│  CARD TITLE                                    [Copy All]   │
│ ─────────────────────────────────────────────────────────── │
│  Label Name:          Value Text                  [📋]      │
│  Label Name:          Value Text                  [📋]      │
│  Label Name:          Value Text                  [📋]      │
└─────────────────────────────────────────────────────────────┘
```

**Card Design**:
- White background
- Light blue border (`#bbdefb`)
- Blue top accent line (4px)
- 20px padding
- 12px margin between cards

**Copy Button Behavior**:
- Default: 📋 clipboard icon (blue)
- Click: ✓ checkmark (green) for 1.5 seconds
- Then returns to 📋

### 5. Raw JSON Tab
- **Text Area**: Monospace font (Consolas), light blue background
- **Toolbar**:
  - `Copy All` — Copies entire JSON to clipboard
  - `Save JSON` — Opens save dialog for .json file
- **Scrollbar**: Styled to match theme

---

## Color Palette

| Element | Color Code | Usage |
|---------|-----------|-------|
| Primary Blue | `#1976d2` | Header, buttons, accents |
| Primary Dark | `#1565c0` | Button hover/press |
| Primary Light | `#42a5f5` | Selection highlight |
| Background Main | `#f0f7ff` | Window background |
| Background Card | `#ffffff` | Cards, panels |
| Background Input | `#e8f4fd` | Entry fields |
| Background Sidebar | `#e1f0fa` | History sidebar |
| Border | `#bbdefb` | Card borders, dividers |
| Text Dark | `#1a237e` | Card titles |
| Text Primary | `#263238` | Values, important text |
| Text Secondary | `#546e7a` | Labels, descriptions |
| Text Muted | `#78909c` | Status, hints |
| Success | `#2e7d32` | Success states |
| Warning | `#ed6c02` | Loading, warnings |
| Danger | `#d32f2f` | Errors |

---

## Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| App Title | Segoe UI | 18pt | Bold |
| Card Title | Segoe UI | 14pt | Bold |
| Labels | Segoe UI | 10pt | Normal |
| Values | Segoe UI | 10pt | Bold |
| VIN Input | Segoe UI | 13pt | Normal |
| History Items | Consolas | 10pt | Normal |
| Raw JSON | Consolas | 10pt | Normal |
| Status | Segoe UI | 9pt | Normal |
| Buttons | Segoe UI | 10-12pt | Bold |

---

## Interaction Design

### Input Field
- **Focus**: Blue border appears (2px)
- **Right-click**: Context menu with Cut/Copy/Paste/Select All
- **Enter key**: Triggers decode

### History Listbox
- **Hover**: Subtle highlight
- **Double-click**: Loads VIN and decodes
- **Right-click**: Context menu (Load / Copy VIN / Delete)

### Buttons
- **Hover**: Background darkens slightly
- **Press**: Background darkens further
- **Active**: Visual feedback on click

### Scrollbars
- **Track**: Light background
- **Thumb**: Blue when active
- **Behavior**: Smooth scrolling with mouse wheel

---

## Responsive Behavior

- **Window Resize**: Canvas auto-adjusts card width
- **Minimum Size**: 950×650 pixels
- **Sidebar**: Resizable via sash drag
- **Text Wrapping**: Long values wrap at 400px

---

## Accessibility

- High contrast text (dark on light)
- Clear visual hierarchy
- Status messages with color coding
- Keyboard shortcuts (Enter, Ctrl+A, Ctrl+C, Ctrl+V)
- Large click targets (buttons minimum 44px height)

---

## Files Generated at Runtime

| File | Purpose | Format |
|------|---------|--------|
| `vin_history.json` | Search history database | JSON |
| `vin_history.csv` | Legacy CSV export | CSV |

---

*GUI designed for automotive professionals requiring fast, reliable vehicle data access.*
