# Outline

## Multi-View Navigation Feature

### Overview
Add multiple views to the TUI application to display different git insights, with the ability to navigate between them. This enhancement will provide users with a more comprehensive understanding of their repository's activity patterns.

### Views to Implement
1. Commits by Hour (existing)
   - Bar chart showing commit frequency by hour of day
   - Helps identify peak coding times

2. Commits by Author
   - Bar chart showing commit count per author
   - Helps understand contributor activity levels
   - Sort by commit count descending

3. Recent Commits Table
   - Tabular view of recent commits
   - Show: hash (short), author, date, message
   - Limit to latest 20 commits
   - Allow scrolling through commits

### Technical Implementation Plan

#### 1. Navigation System
- Implement a tab-like navigation system at the top
- Use Textual's built-in tab components or custom widgets
- Keyboard shortcuts for quick navigation (1,2,3 or left/right arrows)
- Visual indication of current view

#### 2. View Components
- Create separate classes for each view type
- CommitTimeChart (existing)
- AuthorCommitChart (new)
- RecentCommitsTable (new)
- Base class for common functionality

#### 3. Data Management
- Centralize git data fetching
- Cache results to avoid repeated git operations
- Implement reactive updates when switching views

#### 4. UI/UX Considerations
- Consistent styling across views
- Clear navigation indicators
- Loading states during data fetching
- Error handling and user feedback

### Implementation Steps
1. Refactor existing code to support multiple views
2. Create new chart/table components
3. Implement navigation system
4. Add data management layer
5. Style and polish UI
6. Add keyboard shortcuts and help screen

### Future Enhancements
- File change heatmap
- Branch visualization
- Commit message word cloud
- Custom date range filtering