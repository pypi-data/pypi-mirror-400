## Plan: Building a Lexos Web App for File Upload and Text Scrubbing

Create a web application with a Bootstrap 5 frontend and a Python backend using Flask, integrating the Lexos library for file loading (via `io.Loader`) and text preprocessing (via `scrubber.Scrubber`). The app will manage a session-based corpus (using `corpus.Corpus`) with three views: uploader for loading files/URLs, manager for file oversight and actions, and scrubber for configurable text cleaning. Include tooltips, branding header, navigation, and a footer showing active document count.

### Steps
1. Set up project structure with uv in a directory outside the lexos project: Create directories for backend (Flask app with routes), frontend (HTML templates, static CSS/JS with Bootstrap 5), and session data (corpus directory). Install dependencies (Flask, Lexos, Bootstrap 5 via CDN).
   - **Implemented:** Created `../lexos_webapp` directory, initialized with `uv init`, added Flask, set up src/app/templates, src/app/static, src/session_data. Lexos installation pending due to network issues with spacy models; will use local import for now.
2. Implement uploader view backend: Create route to handle multipart file uploads and URL inputs; use `lexos.io.Loader` to auto-detect file types (text, PDF, DOCX, ZIP) and load into a session `lexos.corpus.Corpus`; store in SQLite database using `lexos.corpus.sqlite`.
3. Implement uploader view frontend: Design drag-drop zone and URL input field with Bootstrap components; add JS for file validation and upload progress; include question mark icons with tooltips for options.
4. Implement manager view backend: Create route to retrieve corpus records; handle actions (preview, edit title/class, delete, merge, activate/deactivate) via POST requests; implement export as ZIP using `lexos.io` utilities.
5. Implement manager view frontend: Build table with columns (ID, Title, Class, Source, Preview, Status); add right-click context menu with JS; include export button; display previews in modals.
6. Implement scrubber view backend: Create routes for applying scrubbing (lowercase, remove digits/spaces/tabs/newlines/punctuation, keep hyphens/apostrophes/ampersands, scrub tags via `scrubber.tags`); use `scrubber.Scrubber` pipeline for lemmas, consolidations, stop/keep words, special chars; support apply (preview), save (replace originals), save-as (ZIP).
7. Implement scrubber view frontend: Divide into 6 panels with Bootstrap grid; add checkboxes/options buttons (disable tags if not detected); use JS for dynamic previews, apply/save dialogs, and gears icon for pipeline order adjustment.
8. Add header and navigation: Include Lexos branding (logo/link to docs), nav links to views; add footer with active document count from corpus.
9. Integrate tooltips: Use Bootstrap tooltips on question mark icons for option descriptions.
10. Test and validate: Run end-to-end tests for file loading, scrubbing pipelines, and UI interactions; ensure no data loss on apply/save.

### Further Considerations
1. Session management: Use SQLite to persist corpus across requests and Flask sessions to handle user state; handle cleanup of temp files.
2. Error handling: Add try-except blocks for Lexos exceptions; display user-friendly messages in modals.
3. Security: Limit file sizes/uploads; sanitize inputs.
4. Performance: For large corpora, implement async loading/scrubbing; add loading spinners in UI.
5. Accessibility: Ensure tooltips and context menus are keyboard-navigable; test with screen readers.
