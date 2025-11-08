# Agentverse Study Buddy - Design Guidelines

## Design Approach

**System Selection**: Material Design 3 foundation with modern productivity tool influences (Linear, Notion, educational platforms)

**Rationale**: This is a utility-focused, information-dense productivity application requiring clear hierarchy, efficient navigation, and trust-building UI patterns. The design must balance technical sophistication with learner-friendly accessibility.

## Typography System

**Font Stack**:
- Primary: Inter (via Google Fonts) - headings, UI elements, body text
- Monospace: JetBrains Mono - code snippets, agent logs, technical data

**Hierarchy**:
- Page Titles: text-4xl font-bold
- Section Headers: text-2xl font-semibold
- Card Titles: text-lg font-medium
- Body Text: text-base font-normal
- Captions/Metadata: text-sm font-normal
- Agent Console/Logs: text-xs font-mono

## Layout System

**Spacing Primitives**: Use Tailwind units of 2, 4, 6, 8, 12, 16 consistently
- Component padding: p-4, p-6
- Section spacing: gap-6, gap-8
- Page margins: px-6, py-8
- Card spacing: p-6

**Grid Structure**:
- Dashboard: 3-column grid (lg:grid-cols-3) for stat cards, 2-column for main content + sidebar
- Practice/Learn: Single column max-w-4xl for reading comfort
- Mock Test: Full-width single column for focus
- Placement: 2-column split (coding pad + output/instructions)

**Container Strategy**:
- App shell: Fixed sidebar (w-64) + main content area
- Content max-width: max-w-7xl mx-auto
- Reading content: max-w-3xl for optimal line length

## Component Library

### Navigation
- **Sidebar**: Fixed left navigation (w-64), icons + labels, keyboard shortcuts visible (text-xs opacity-60)
- **Header**: Slim top bar (h-14) with breadcrumbs, user profile, agent status indicator
- **Keyboard Shortcuts**: Visible hints throughout UI (g+i, g+l, g+p, etc.)

### Dashboard Components
- **Progress Rings**: Circular progress indicators for topic mastery (120px diameter)
- **Stat Cards**: Elevated cards (shadow-md) with icon, metric, label, trend indicator
- **Study Blocks Timeline**: Vertical timeline with time slots, color-coded by activity type
- **Quick Actions Grid**: 2x3 grid of action cards with icons and labels

### Learning Interface
- **Micro-Lesson Cards**: Full-width cards with clear typography hierarchy
- **Citation Badges**: Small pills (rounded-full, text-xs) linking to source materials
- **Confidence Indicators**: Badge system (Low/Med/High) with subtle background treatment
- **Step Progression**: Numbered steps with connecting vertical line, expandable sections

### Practice & Testing
- **Question Card**: Elevated card with question, difficulty badge, topic tag, action buttons
- **Hint System**: Accordion-style reveals (Hint → Steps → Full Solution)
- **Timer Component**: Fixed top-right, large readable numerals (text-2xl font-mono)
- **Answer Input**: Large textarea with character count, auto-save indicator

### Mock Exam Mode
- **Full-Screen Layout**: Minimal chrome, centered question (max-w-3xl), fixed timer + navigation
- **Question Navigator**: Side panel (toggle-able) showing all questions as grid with status (answered/flagged/skipped)
- **Submit Modal**: Confirmation dialog with summary stats before final submission

### Agent Console
- **Activity Stream**: Scrollable log with distinct entry types (Plan/Action/Reflection)
- **Entry Cards**: Left border accent, timestamp, agent name badge, collapsible details
- **Status Indicators**: Animated pulse for "thinking", checkmark for completed, spinner for in-progress
- **JSON Viewers**: Syntax-highlighted collapsible code blocks for plan/action data

### Flashcards
- **Card Flip Interface**: 3D flip animation, centered card (max-w-md), large readable text
- **Review Buttons**: Row of 4 buttons (Again/Hard/Good/Easy) with spacing (gap-4)
- **Progress Bar**: Show cards remaining in session
- **Next Review Badge**: Display SM-2 schedule with human-readable timing

### Placement Mode
- **Company Profile Header**: Banner-style with company name, role, profile completeness indicator
- **Rounds Tabs**: Horizontal tab navigation for different interview rounds
- **Code Editor**: Monaco-inspired split view (code + output), language selector, run button with loading state
- **Test Cases**: Expandable list showing input/expected/actual with pass/fail indicators

### Forms & Inputs
- **Upload Zone**: Dashed border drag-and-drop area with file type icons, progress bars for uploads
- **Topic Extraction**: Auto-generated pill badges with importance scores (1-10 scale as small badge)
- **Date Pickers**: Calendar interface for study plan deadline selection
- **Multi-Select**: Checkbox groups for topic selection with select all/none

### Feedback & States
- **Toast Notifications**: Bottom-right slide-in, auto-dismiss, with icon + message
- **Loading States**: Skeleton screens for cards, spinner for actions, progress bars for uploads
- **Empty States**: Illustration + message + primary action for empty lists/sections
- **Error States**: Alert boxes with icon, message, retry action

## Images

**Hero Section**: None - this is a productivity tool, not a marketing site. Dashboard launches directly into functional interface.

**Illustrations**:
- Empty states: Simple line illustrations (undraw.co style) for "No study plans yet", "Upload your first document", etc.
- Tutorial walkthroughs: Screenshots with annotations for first-time user guidance
- Company logos: Small logos (h-8) in placement profile headers

## Interaction Patterns

**Minimize Animations**: Only use for meaningful feedback
- Card hover: subtle lift (translate-y-1)
- Button press: scale-95 on active state
- Page transitions: simple fade (150ms)
- Agent console: gentle pulse on new entries
- Flashcard flip: 3D flip animation (500ms)

**Focus Management**:
- Visible focus rings (ring-2 ring-offset-2) for keyboard navigation
- Skip to main content link
- Logical tab order through forms and interfaces

## Responsive Behavior

**Breakpoints**:
- Mobile (base): Single column, bottom nav, hamburger menu
- Tablet (md:): Retain sidebar, 2-column grids become single column
- Desktop (lg:): Full 3-column layouts, side-by-side panels

**Mobile Adaptations**:
- Sidebar becomes bottom nav bar with 5 primary actions
- Agent console becomes full-screen modal
- Mock test mode remains full-screen
- Flashcards use full viewport width
- Code editor becomes tabbed (code/output toggle)

## Accessibility

- WCAG AA contrast ratios maintained throughout
- Form labels always visible (no placeholder-only inputs)
- Button text visible, icon-only buttons include aria-labels
- Timer alerts for approaching mock exam deadlines
- Keyboard shortcuts documented and accessible via ? key
- Screen reader announcements for agent actions and score updates