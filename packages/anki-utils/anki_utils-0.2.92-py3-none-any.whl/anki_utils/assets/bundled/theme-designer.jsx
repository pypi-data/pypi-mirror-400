import { useState, useCallback, useMemo } from "react";

// ============================================================
// DATA INJECTION - Claude populates these via the launch script
// ============================================================
const PRODUCTION_THEMES = __PRODUCTION_THEMES_PLACEHOLDER__;
const WORKING_THEMES = __WORKING_THEMES_PLACEHOLDER__;
const SAMPLE_CARDS = __SAMPLE_CARDS_PLACEHOLDER__;
// ============================================================

// Card type labels for UI
const CARD_TYPE_LABELS = {
  'front-back': 'Front → Back',
  'concept': 'Concept',
  'cloze': 'Cloze',
  'image': 'Image',
  'person': 'Person',
  'image-occlusion': 'Image Occlusion',
};

// Card types available for preview
const CARD_TYPES = ['front-back', 'concept', 'cloze', 'image', 'person', 'image-occlusion'];

// =============================================================================
// ANKI TEMPLATES - Exact qfmt/afmt for accurate rendering
// =============================================================================

const ANKI_TEMPLATES = {
  'front-back': {
    qfmt: `<div class="card">
  <div class="card-header">
    <p>{{Source}}</p>
    <p>By {{Author}}</p>
  </div>
  <br>
  <div class="question">{{Question}}</div>`,
    afmt: `{{FrontSide}}
  <br>
  <div class="answer">{{Answer}}</div>
  <div class="extra-info">{{Extra}}</div>
</div>`,
  },
  'concept': {
    qfmt: `<div class="card">
  <div class="card-header">
    <p>{{Source}}</p>
    <p>By {{Author}}</p>
  </div>
  <br>
  <div class="concept-instruction">Define the concept</div>
  <div class="question">{{Concept}}</div>`,
    afmt: `{{FrontSide}}
  <br>
  <div class="answer">{{Definition}}</div>
  <div class="extra-info">{{Example}}</div>
</div>`,
  },
  'cloze': {
    qfmt: `<div class="card">
  <div class="card-header">
    <p>{{Source}}</p>
    <p>By {{Author}}</p>
  </div>
  <br>
  <div class="card-content">
    <div class="question">{{ClozeText}}</div>
  </div>
</div>`,
    afmt: `<div class="card">
  <div class="card-header">
    <p>{{Source}}</p>
    <p>By {{Author}}</p>
  </div>
  <br>
  <div class="card-content">
    <div class="question">{{ClozeAnswer}}</div>
  </div>
</div>`,
  },
  'image': {
    qfmt: `<div class="card">
  <div class="prompt">{{Prompt}}</div>
  <div class="image-container">
    <img src="{{ImageSrc}}" alt="Card image" />
  </div>
</div>`,
    afmt: `<div class="card">
  <div class="prompt">{{Prompt}}</div>
  <div class="image-container">
    <img src="{{ImageSrc}}" alt="Card image" />
  </div>
  <div class="answer">{{Answer}}</div>
  <div class="extra-info">{{Extra}}</div>
</div>`,
  },
  'person': {
    qfmt: `<div class="card">
  <div class="question">Who is this?</div>
  <hr>
  <img src="{{PhotoSrc}}" alt="Person" />
</div>`,
    afmt: `<div class="card">
  <div class="question">Who is this?</div>
  <hr>
  <img src="{{PhotoSrc}}" alt="Person" />
  <hr>
  <div class="answer">{{FullName}}</div>
</div>`,
  },
  'image-occlusion': {
    qfmt: `<div class="io-card">
{{#Header}}<div class="io-header">{{Header}}</div>{{/Header}}
<div class="io-container">
  {{IOPreview}}
</div>
<div class="io-cloze-data">{{ClozeText}}</div>
</div>`,
    afmt: `<div class="io-card io-back">
{{#Header}}<div class="io-header">{{Header}}</div>{{/Header}}
<div class="io-container">
  {{IOPreview}}
</div>
<div class="io-answer">{{ClozeAnswer}}</div>
{{#BackExtra}}<div class="io-back-extra">{{BackExtra}}</div>{{/BackExtra}}
</div>`,
  },
};

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Get all sample cards for a card type
function getCardsOfType(cardType) {
  if (!SAMPLE_CARDS?.cards) return [];
  return SAMPLE_CARDS.cards.filter(c => c.type === cardType);
}

// Get display label for a card (truncated preview text)
function getCardLabel(card, cardType) {
  if (!card) return '';
  const maxLen = 40;
  let text = '';

  switch (cardType) {
    case 'front-back':
      text = card.question || '';
      break;
    case 'concept':
      text = card.concept || '';
      break;
    case 'cloze':
      text = (card.cloze_text || '').replace(/\{\{c\d+::([^}]+)\}\}/g, '[$1]');
      break;
    case 'image':
      text = card.prompt || card.answer || '';
      break;
    case 'person':
      text = card.full_name || '';
      break;
    case 'image-occlusion':
      text = card.header || `IO: ${(card.occlusions || []).length} occlusions`;
      break;
    default:
      text = '';
  }

  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text;
}

// Generate SVG overlay for image occlusion
function generateIOPreview(card, showAnswer) {
  const imgSrc = card.image_data || card.image_url || '';
  const occlusions = card.occlusions || [];

  if (!imgSrc) {
    return '<div style="padding: 20px; text-align: center; color: #888;">No image available</div>';
  }

  // Generate SVG masks based on occlusion coordinates
  const svgMasks = occlusions.map((occ, idx) => {
    const x = (occ.left * 100).toFixed(2);
    const y = (occ.top * 100).toFixed(2);
    const width = (occ.width * 100).toFixed(2);
    const height = (occ.height * 100).toFixed(2);

    // Determine mask class based on state
    let maskClass = 'io-mask';
    if (showAnswer) {
      // On back: first occlusion is revealed, others stay masked
      maskClass = idx === 0 ? 'io-revealed' : 'io-mask';
    } else {
      // On front: first occlusion is active (being asked), others are masked
      maskClass = idx === 0 ? 'io-mask-active' : 'io-mask';
    }

    if (occ.shape === 'ellipse') {
      const cx = (occ.left + occ.width / 2) * 100;
      const cy = (occ.top + occ.height / 2) * 100;
      const rx = (occ.width / 2) * 100;
      const ry = (occ.height / 2) * 100;
      return `<ellipse cx="${cx.toFixed(2)}%" cy="${cy.toFixed(2)}%" rx="${rx.toFixed(2)}%" ry="${ry.toFixed(2)}%" class="${maskClass}" />`;
    }
    return `<rect x="${x}%" y="${y}%" width="${width}%" height="${height}%" class="${maskClass}" />`;
  }).join('\n    ');

  return `<img src="${imgSrc}" alt="Occlusion image" />
<svg class="io-svg-overlay" viewBox="0 0 100 100" preserveAspectRatio="none">
    ${svgMasks}
</svg>`;
}

// Substitute template placeholders with card data
function renderTemplate(template, card, cardType, showAnswer = false) {
  if (!card) return '<div class="no-data">No sample card available</div>';

  let html = template;

  // Common substitutions
  html = html.replace(/\{\{Source\}\}/g, escapeHtml(card.source || ''));
  html = html.replace(/\{\{Author\}\}/g, escapeHtml(card.author || 'Claude'));
  html = html.replace(/\{\{Extra\}\}/g, escapeHtml(card.extra_info || ''));

  // Type-specific substitutions
  switch (cardType) {
    case 'front-back':
      html = html.replace(/\{\{Question\}\}/g, escapeHtml(card.question || ''));
      html = html.replace(/\{\{Answer\}\}/g, escapeHtml(card.answer || ''));
      break;
    case 'concept':
      html = html.replace(/\{\{Concept\}\}/g, escapeHtml(card.concept || ''));
      html = html.replace(/\{\{Definition\}\}/g, escapeHtml(card.definition || ''));
      html = html.replace(/\{\{Example\}\}/g, escapeHtml(card.example || ''));
      break;
    case 'cloze':
      const clozeText = card.cloze_text || '';
      const clozeFront = clozeText.replace(/\{\{c\d+::([^}]+)\}\}/g, '<span class="cloze">[...]</span>');
      const clozeBack = clozeText.replace(/\{\{c\d+::([^}]+)\}\}/g, '<span class="cloze">$1</span>');
      html = html.replace(/\{\{ClozeText\}\}/g, clozeFront);
      html = html.replace(/\{\{ClozeAnswer\}\}/g, clozeBack);
      break;
    case 'image':
      html = html.replace(/\{\{Prompt\}\}/g, escapeHtml(card.prompt || ''));
      html = html.replace(/\{\{Answer\}\}/g, escapeHtml(card.answer || ''));
      const imgSrc = card.image_data || card.image_url || 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150"><rect fill="#e0e0e0" width="200" height="150"/><text x="100" y="75" text-anchor="middle" fill="#888" font-family="sans-serif" font-size="14">[Image]</text></svg>');
      html = html.replace(/\{\{ImageSrc\}\}/g, imgSrc);
      break;
    case 'person':
      html = html.replace(/\{\{FullName\}\}/g, escapeHtml(card.full_name || ''));
      const photoSrc = card.photo_data || card.photo_url || 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150" viewBox="0 0 150 150"><rect fill="#e0e0e0" width="150" height="150"/><circle cx="75" cy="55" r="30" fill="#ccc"/><ellipse cx="75" cy="130" rx="45" ry="35" fill="#ccc"/></svg>');
      html = html.replace(/\{\{PhotoSrc\}\}/g, photoSrc);
      break;
    case 'image-occlusion':
      // Handle IO-specific fields
      html = html.replace(/\{\{#Header\}\}([\s\S]*?)\{\{\/Header\}\}/g, card.header ? '$1' : '');
      html = html.replace(/\{\{Header\}\}/g, escapeHtml(card.header || ''));
      html = html.replace(/\{\{#BackExtra\}\}([\s\S]*?)\{\{\/BackExtra\}\}/g, card.back_extra ? '$1' : '');
      html = html.replace(/\{\{BackExtra\}\}/g, escapeHtml(card.back_extra || ''));

      // Generate IO preview with SVG overlays
      const ioPreview = generateIOPreview(card, showAnswer);
      html = html.replace(/\{\{IOPreview\}\}/g, ioPreview);

      // Generate cloze text from occlusions
      const occlusions = card.occlusions || [];
      const clozeLabels = occlusions.map(o => o.label).join(', ');
      const clozeFrontIO = occlusions.length > 0
        ? `<span class="cloze">[${occlusions[0].label}]</span>`
        : '';
      const clozeBackIO = occlusions.length > 0
        ? `<span class="cloze">${occlusions[0].label}</span>`
        : '';
      html = html.replace(/\{\{ClozeText\}\}/g, clozeFrontIO);
      html = html.replace(/\{\{ClozeAnswer\}\}/g, clozeBackIO);
      break;
  }

  // Handle {{FrontSide}} for answer templates
  if (html.includes('{{FrontSide}}')) {
    const frontHtml = renderTemplate(ANKI_TEMPLATES[cardType].qfmt, card, cardType);
    html = html.replace('{{FrontSide}}', frontHtml);
  }

  return html;
}

// Get CSS for a theme and card type
function getThemeCSS(themeData, cardType) {
  if (!themeData) return '';

  switch (cardType) {
    case 'concept':
      return (themeData.base || '') + (themeData.conceptInstruction || '');
    case 'image':
      return (themeData.base || '') + (themeData.image || '');
    case 'person':
      return themeData.person || themeData.base || '';
    case 'image-occlusion':
      return (themeData.base || '') + (themeData.io || '');
    default:
      return themeData.base || '';
  }
}

// =============================================================================
// SHARED CARD PREVIEW COMPONENT
// =============================================================================
// This component is synced with preview-template.jsx
// Dimensions: iPhone 16 Pro logical dimensions (393 × 852 pixels)
// =============================================================================

// =============================================================================
// SHARED CARD PREVIEW COMPONENT
// =============================================================================
// This component is now loaded from shared-preview.jsx
// =============================================================================
// =============================================================================
// SHARED CARD PREVIEW COMPONENT (Inlined by bundle-artifacts.py)
// Source: anki_utils/assets/shared-preview.jsx
// =============================================================================
// =============================================================================
// SHARED CARD PREVIEW COMPONENT
// =============================================================================
// This component is the canonical card preview renderer.
// Used by: preview-template.jsx, theme-designer.jsx
// Dimensions: iPhone 16 Pro logical dimensions (393 × 852 pixels)
// =============================================================================

// iPhone 16 Pro logical dimensions
const IPHONE_16_PRO_WIDTH = 393;
// Issue #53: Standardized aspect ratio (~0.58), not full device height
const IPHONE_16_PRO_HEIGHT = 678;

/**
 * SharedCardPreview - Unified card preview component for Anki cards
 *
 * @param {string} html - The rendered card HTML content
 * @param {string} css - The theme CSS to apply
 * @param {boolean} isDarkMode - Whether to use dark mode (adds night_mode class)
 * @param {function} onTap - Click handler for card interaction
 * @param {boolean} needsCardBody - Whether to add 'card' class to body (for person cards)
 * @param {number} width - Preview width in pixels (default: iPhone 16 Pro width)
 * @param {number} height - Preview height in pixels (default: iPhone 16 Pro height)
 */
function SharedCardPreview({
  html,
  css,
  isDarkMode,
  onTap,
  needsCardBody = false,
  width = IPHONE_16_PRO_WIDTH,
  height = IPHONE_16_PRO_HEIGHT,
}) {
  const hasTap = typeof onTap === 'function';
  // Build the full iframe document
  const iframeDoc = `<!DOCTYPE html>
<html class="${isDarkMode ? 'night_mode' : ''}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { height: 100%; }
    /* Hide scrollbar but allow scrolling */
    html { overflow-y: auto; overflow-x: hidden; scrollbar-width: none; -ms-overflow-style: none; }
    html::-webkit-scrollbar { display: none; }
    ${css}
  </style>
</head>
<body class="${needsCardBody ? 'card' : ''}">
  ${html}
</body>
</html>`;

  // Use a transparent overlay for click handling since iframe sandbox may block scripts
  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div style={{
        width: `${width}px`,
        maxWidth: '100%',
        height: `${height}px`,
        maxHeight: '100%',
        position: 'relative',
        aspectRatio: `${width} / ${height}`,
      }}>
        <iframe
          title="Anki Card Preview"
          srcDoc={iframeDoc}
          style={{
            display: 'block',
            width: '100%',
            height: '100%',
            border: 'none',
            background: 'transparent',
          }}
          sandbox="allow-same-origin"
        />
        {hasTap && (
          <div
            onClick={onTap}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              cursor: 'pointer',
            }}
          />
        )}
      </div>
    </div>
  );
}
// =============================================================================
// END SHARED CARD PREVIEW COMPONENT
// =============================================================================
/**
 * CardPreview - Wrapper for SharedCardPreview used in theme designer
 * Handles card data transformation specific to the theme designer's template system.
 */
function CardPreview({ card, cardType, showAnswer, isDarkMode, css, onTap }) {
  const template = showAnswer
    ? ANKI_TEMPLATES[cardType]?.afmt
    : ANKI_TEMPLATES[cardType]?.qfmt;
  const cardHtml = renderTemplate(template || '', card, cardType, showAnswer);
  const needsCardBody = cardType === 'person';

  return (
    <SharedCardPreview
      html={cardHtml}
      css={css}
      isDarkMode={isDarkMode}
      onTap={onTap}
      needsCardBody={needsCardBody}
    />
  );
}

// =============================================================================
// CSS EDITOR PANEL (SIDE PANEL)
// =============================================================================

function CSSEditorPanel({
  css,
  onChange,
  onClose,
  themeName,
  cardType,
  isProduction,
  hasChanges
}) {
  return (
    <div className="css-editor-panel">
      <div className="editor-header">
        <div className="editor-header-info">
          <span className="editor-title">Edit CSS</span>
          <div className="editor-meta">
            <span className={`theme-badge ${isProduction ? 'production' : 'working'}`}>
              {themeName}
            </span>
            <span className="card-type-badge">{CARD_TYPE_LABELS[cardType]}</span>
            {hasChanges && <span className="unsaved-badge">Unsaved</span>}
          </div>
        </div>
        <button className="editor-close-btn" onClick={onClose}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div className="editor-body">
        <textarea
          value={css}
          onChange={e => onChange(e.target.value)}
          className="css-textarea"
          spellCheck={false}
          placeholder="/* Enter CSS here */"
        />
      </div>
      <div className="editor-footer">
        <span className="editor-hint">Changes apply live to preview</span>
      </div>
    </div>
  );
}

// =============================================================================
// EXPORT MODAL
// =============================================================================

function ExportModal({ themeName, themeData, onClose }) {
  const [copied, setCopied] = useState(false);

  // Format theme data for themes.py
  const exportText = `# Theme: ${themeName}
# Copy the sections below into themes.py

${themeName.toUpperCase()}_BASE = '''${themeData.base || ''}'''

${themeName.toUpperCase()}_CONCEPT_INSTRUCTION = '''${themeData.conceptInstruction || ''}'''

${themeName.toUpperCase()}_IMAGE = '''${themeData.image || ''}'''

${themeName.toUpperCase()}_PERSON = '''${themeData.person || ''}'''

${themeName.toUpperCase()}_IO = '''${themeData.io || ''}'''
`;

  const handleCopy = () => {
    navigator.clipboard.writeText(exportText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="export-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Export Theme: {themeName}</span>
          <div className="modal-actions">
            <button
              className={`btn btn-primary ${copied ? 'btn-success' : ''}`}
              onClick={handleCopy}
            >
              {copied ? '✓ Copied!' : 'Copy All'}
            </button>
            <button className="btn" onClick={onClose}>Close</button>
          </div>
        </div>
        <pre className="export-content">{exportText}</pre>
      </div>
    </div>
  );
}

// =============================================================================
// CHEVRON ICONS
// =============================================================================

function ChevronLeft() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="16" height="16">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="16" height="16">
      <path d="M9 18l6-6-6-6" />
    </svg>
  );
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ThemeDesigner() {
  // Combine production and working themes
  const allThemes = useMemo(() => {
    const themes = {};

    // Add production themes
    if (PRODUCTION_THEMES) {
      Object.entries(PRODUCTION_THEMES).forEach(([name, data]) => {
        themes[name] = { ...data, isProduction: true };
      });
    }

    // Add working themes
    if (WORKING_THEMES) {
      Object.entries(WORKING_THEMES).forEach(([name, data]) => {
        themes[name] = { ...data, isProduction: false };
      });
    }

    return themes;
  }, []);

  const productionThemeNames = useMemo(() =>
    Object.entries(allThemes).filter(([_, t]) => t.isProduction).map(([n]) => n),
    [allThemes]
  );

  const workingThemeNames = useMemo(() =>
    Object.entries(allThemes).filter(([_, t]) => !t.isProduction).map(([n]) => n),
    [allThemes]
  );

  // State
  const [selectedTheme, setSelectedTheme] = useState(
    workingThemeNames[0] || productionThemeNames[0] || 'minimal'
  );
  const [cardType, setCardType] = useState('front-back');
  const [cardIndex, setCardIndex] = useState(0);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showCSSEditor, setShowCSSEditor] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [customCSS, setCustomCSS] = useState('');
  const [isCustomCSSActive, setIsCustomCSSActive] = useState(false);
  const [scale, setScale] = useState(0.85);

  // Get cards for current type
  const cardsOfType = useMemo(() => getCardsOfType(cardType), [cardType]);
  const currentCard = cardsOfType[cardIndex] || cardsOfType[0] || null;
  const totalCards = cardsOfType.length;

  // Get current theme data and CSS
  const currentTheme = allThemes[selectedTheme] || {};
  const baseCSS = getThemeCSS(currentTheme, cardType);
  const activeCSS = isCustomCSSActive ? customCSS : baseCSS;

  // Handle theme change
  const handleThemeChange = useCallback((theme) => {
    setSelectedTheme(theme);
    setIsCustomCSSActive(false);
    setCustomCSS('');
  }, []);

  // Handle card type change
  const handleCardTypeChange = useCallback((type) => {
    setCardType(type);
    setCardIndex(0);
    setIsCustomCSSActive(false);
    setCustomCSS('');
  }, []);

  // Card navigation
  const goToPrevCard = useCallback(() => {
    if (cardIndex > 0) {
      setCardIndex(cardIndex - 1);
    }
  }, [cardIndex]);

  const goToNextCard = useCallback(() => {
    if (cardIndex < totalCards - 1) {
      setCardIndex(cardIndex + 1);
    }
  }, [cardIndex, totalCards]);

  // Toggle CSS editor
  const toggleCSSEditor = useCallback(() => {
    if (!showCSSEditor && !isCustomCSSActive) {
      setCustomCSS(baseCSS);
    }
    setShowCSSEditor(!showCSSEditor);
  }, [showCSSEditor, isCustomCSSActive, baseCSS]);

  // Handle CSS change
  const handleCSSChange = useCallback((newCSS) => {
    setCustomCSS(newCSS);
    setIsCustomCSSActive(true);
  }, []);

  // =============================================================================
  // STYLES
  // =============================================================================

  const styles = `
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    :root {
      --bg-primary: #1c1c1e;
      --bg-secondary: #2c2c2e;
      --bg-tertiary: #3a3a3c;
      --text-primary: #ffffff;
      --text-secondary: #ebebf5;
      --text-tertiary: #8e8e93;
      --separator: #48484a;
      --blue: #0a84ff;
      --green: #30d158;
      --yellow: #ffd60a;
      --orange: #ff9f0a;
    }

    .designer-root {
      min-height: 100vh;
      background: #000;
      font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .app-container {
      width: fit-content;
      max-width: 100%;
      height: fit-content;
      min-height: 0;
      background: rgba(20, 20, 20, 0.95); /* Deep translucent dark grey */
      border: 1px solid #333;
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 0 0 1px #000, 0 40px 80px rgba(0,0,0,0.6);
      backdrop-filter: blur(20px);
    }

    /* ============ TOOLBAR ============ */
    .toolbar {
      background: var(--bg-secondary);
      padding: 12px 16px;
      border-bottom: 1px solid var(--separator);
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      flex-shrink: 0;
    }

    .toolbar-group {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .toolbar-label {
      font-size: 12px;
      color: var(--text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }

    select {
      background: var(--bg-tertiary);
      border: none;
      color: var(--text-primary);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 14px;
      cursor: pointer;
      min-width: 110px;
    }

    select:focus {
      outline: 2px solid var(--blue);
      outline-offset: 1px;
    }

    optgroup {
      background: var(--bg-secondary);
      color: var(--text-tertiary);
      font-weight: 600;
    }

    option {
      background: var(--bg-tertiary);
      color: var(--text-primary);
    }

    .theme-status {
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .theme-status.production {
      background: rgba(48, 209, 88, 0.2);
      color: var(--green);
    }

    .theme-status.working {
      background: rgba(255, 159, 10, 0.2);
      color: var(--orange);
    }

    .toggle-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--text-secondary);
    }

    .toggle-switch {
      width: 44px;
      height: 26px;
      background: var(--bg-tertiary);
      border-radius: 13px;
      cursor: pointer;
      position: relative;
      transition: background 0.2s;
    }

    .toggle-switch.on {
      background: var(--blue);
    }

    .toggle-switch::after {
      content: '';
      position: absolute;
      width: 22px;
      height: 22px;
      background: white;
      border-radius: 11px;
      top: 2px;
      left: 2px;
      transition: transform 0.2s;
    }

    .toggle-switch.on::after {
      transform: translateX(18px);
    }

    .toolbar-spacer {
      flex: 1;
      min-width: 8px;
    }

    .btn {
      background: var(--bg-tertiary);
      border: none;
      color: var(--text-primary);
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .btn:hover {
      background: #4a4a4c;
    }

    .btn-primary {
      background: var(--blue);
    }

    .btn-primary:hover {
      background: #0070dd;
    }

    .btn-success {
      background: var(--green);
    }

    .btn.active {
      background: var(--blue);
    }

    /* ============ MAIN CONTENT ============ */
    .main-content {
      display: flex;
      flex-direction: column; /* Allow content to dictate height */
    }

    /* ============ PREVIEW AREA ============ */
    .preview-area {
      display: flex;
      flex-direction: column;
      padding: 24px;
      background: transparent; /* Remove bg to let container shine through */
      gap: 24px;
    }

    .preview-grid {
      display: grid;
      grid-template-columns: repeat(2, auto); /* Strict columns based on content */
      gap: 40px; /* Distinct separation */
      padding: 0 20px;
      justify-content: center;
    }

    .preview-column {
      display: flex;
      flex-direction: column;
      min-height: 0;
      align-items: center; /* Center the constrained wrapper */
    }

    .preview-title {
      font-size: 11px;
      color: var(--text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin-bottom: 8px;
    }

    .card-preview-wrapper {
      /* Fixed dimensions to match card size (Issue #53) */
      width: 393px;
      height: 678px;
      flex-shrink: 0;
      /* Issue #55: Removed border-radius for accurate Anki card preview (sharp corners) */
      overflow: hidden;
      position: relative;
      /* Apply scale here to zoom the whole "phone"/card unit */
      transform: scale(var(--preview-scale));
      transform-origin: top center;
      /* Add margin to account for scale if needed, or just let it hang */
      margin-bottom: 20px;
    }

    .card-preview-wrapper.dark-mode {
      background: #1a1a1a;
    }

    .card-preview-wrapper.light-mode {
      background: transparent;
      border: 1px solid var(--separator);
    }

    .card-preview-container {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* ============ CARD SELECTOR ============ */
    .card-selector {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      padding: 12px;
      background: var(--bg-secondary);
      border-radius: 12px;
      margin-top: 16px;
      position: relative;
      z-index: 2;
    }

    .card-nav-btn {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      border: none;
      background: var(--bg-tertiary);
      color: var(--text-primary);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: opacity 0.15s, background 0.15s;
    }

    .card-nav-btn:hover:not(:disabled) {
      background: #4a4a4c;
    }

    .card-nav-btn:disabled {
      opacity: 0.3;
      cursor: not-allowed;
    }

    .card-info {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      min-width: 150px;
    }

    .card-counter {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .card-label {
      font-size: 12px;
      color: var(--text-tertiary);
      max-width: 200px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    /* ============ CSS EDITOR PANEL ============ */
    .css-editor-panel {
      width: 400px;
      background: var(--bg-primary);
      border-left: 1px solid var(--separator);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }

    .editor-header {
      padding: 12px 16px;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--separator);
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }

    .editor-header-info {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .editor-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .editor-meta {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .theme-badge {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 500;
    }

    .theme-badge.production {
      background: rgba(48, 209, 88, 0.2);
      color: var(--green);
    }

    .theme-badge.working {
      background: rgba(255, 159, 10, 0.2);
      color: var(--orange);
    }

    .card-type-badge {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 500;
      background: rgba(10, 132, 255, 0.2);
      color: var(--blue);
    }

    .unsaved-badge {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 500;
      background: rgba(255, 214, 10, 0.2);
      color: var(--yellow);
    }

    .editor-close-btn {
      width: 28px;
      height: 28px;
      border-radius: 6px;
      border: none;
      background: var(--bg-tertiary);
      color: var(--text-secondary);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .editor-close-btn:hover {
      background: #4a4a4c;
    }

    .editor-close-btn svg {
      width: 14px;
      height: 14px;
    }

    .editor-body {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
      padding: 12px;
    }

    .css-textarea {
      flex: 1;
      background: #0d0d0d;
      color: #e0e0e0;
      border: 1px solid var(--separator);
      border-radius: 8px;
      padding: 12px;
      font-family: 'SF Mono', 'Menlo', 'Monaco', 'Consolas', monospace;
      font-size: 13px;
      line-height: 1.5;
      resize: none;
      outline: none;
      min-height: 300px;
    }

    .css-textarea:focus {
      border-color: var(--blue);
    }

    .css-textarea::placeholder {
      color: var(--text-tertiary);
    }

    .editor-footer {
      padding: 10px 16px;
      border-top: 1px solid var(--separator);
      background: var(--bg-secondary);
    }

    .editor-hint {
      font-size: 12px;
      color: var(--text-tertiary);
    }

    /* ============ MODALS ============ */
    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }

    .export-modal {
      background: var(--bg-primary);
      border-radius: 12px;
      width: 100%;
      max-width: 700px;
      max-height: calc(100vh - 40px);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .modal-header {
      padding: 16px 20px;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--separator);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }

    .modal-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .modal-actions {
      display: flex;
      gap: 8px;
    }

    .export-content {
      flex: 1;
      overflow: auto;
      background: #0d0d0d;
      color: #e0e0e0;
      padding: 16px;
      margin: 0;
      font-family: 'SF Mono', 'Menlo', 'Monaco', 'Consolas', monospace;
      font-size: 12px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-all;
    }

    /* ============ RESPONSIVE ============ */
    @media (max-width: 900px) {
      .css-editor-panel {
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        width: 100%;
        max-width: 400px;
        z-index: 100;
        box-shadow: -4px 0 20px rgba(0,0,0,0.5);
      }

      .preview-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 600px) {
      .toolbar {
        padding: 10px 12px;
        gap: 8px;
      }

      .toolbar-group {
        flex-wrap: wrap;
      }

      select {
        min-width: 90px;
        font-size: 13px;
        padding: 6px 10px;
      }

      .btn {
        padding: 6px 10px;
        font-size: 13px;
      }

      .css-editor-panel {
        max-width: 100%;
      }
    }

    /* ============ NO CARDS STATE ============ */
    .no-cards {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px;
      text-align: center;
      color: var(--text-tertiary);
    }

    .no-cards-icon {
      font-size: 48px;
      margin-bottom: 16px;
      opacity: 0.5;
    }

    .no-cards-title {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }

    .no-cards-message {
      font-size: 14px;
      line-height: 1.5;
    }

  `;

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <>
      <style>{styles}</style>
      <div className="designer-root" style={{ '--preview-scale': scale }}>
        <div className="app-container">
          {/* Toolbar */}
          <div className="toolbar">
            <div className="toolbar-group">
              <span className="toolbar-label">Theme</span>
              <select value={selectedTheme} onChange={e => handleThemeChange(e.target.value)}>
                {productionThemeNames.length > 0 && (
                  <optgroup label="Production">
                    {productionThemeNames.map(name => (
                      <option key={name} value={name}>{name}</option>
                    ))}
                  </optgroup>
                )}
                {workingThemeNames.length > 0 && (
                  <optgroup label="Working">
                    {workingThemeNames.map(name => (
                      <option key={name} value={name}>{name}</option>
                    ))}
                  </optgroup>
                )}
              </select>
              <span className={`theme-status ${currentTheme.isProduction ? 'production' : 'working'}`}>
                {currentTheme.isProduction ? 'Production' : 'Working'}
              </span>
            </div>

            <div className="toolbar-group">
              <span className="toolbar-label">Card Type</span>
              <select value={cardType} onChange={e => handleCardTypeChange(e.target.value)}>
                {CARD_TYPES.map(type => (
                  <option key={type} value={type}>{CARD_TYPE_LABELS[type]}</option>
                ))}
              </select>
            </div>

            <div className="toolbar-group">
              <div className="toggle-item">
                <span>{isDarkMode ? '🌙' : '☀️'}</span>
                <div
                  className={`toggle-switch ${isDarkMode ? 'on' : ''}`}
                  onClick={() => setIsDarkMode(!isDarkMode)}
                />
              </div>
            </div>

            <div className="toolbar-spacer" />

            <div className="toolbar-group">
              <button
                className={`btn ${showCSSEditor ? 'active' : ''}`}
                onClick={toggleCSSEditor}
              >
                {showCSSEditor ? 'Hide CSS' : 'Edit CSS'}
              </button>
              <button className="btn btn-primary" onClick={() => setShowExport(true)}>
                Export
              </button>
            </div>

            <div className="toolbar-spacer" />

            <div className="toolbar-group">
              <span className="toolbar-label">Scale: {Math.round(scale * 100)}%</span>
              <input
                type="range"
                min="0.5"
                max="1.2"
                step="0.05"
                value={scale}
                onChange={(e) => setScale(parseFloat(e.target.value))}
                style={{ width: '80px' }}
              />
            </div>
          </div>

          {/* Main content */}
          <div className="main-content">
            {/* Preview area */}
            <div className="preview-area">
              {totalCards > 0 ? (
                <>
                  <div className="preview-grid">
                    <div className="preview-column">
                      <div className="preview-title">Front</div>
                      <div className={`card-preview-wrapper ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
                        <div className="card-preview-container">
                          <CardPreview
                            card={currentCard}
                            cardType={cardType}
                            showAnswer={false}
                            isDarkMode={isDarkMode}
                            css={activeCSS}
                          />
                        </div>
                      </div>
                    </div>
                    <div className="preview-column">
                      <div className="preview-title">Back</div>
                      <div className={`card-preview-wrapper ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
                        <div className="card-preview-container">
                          <CardPreview
                            card={currentCard}
                            cardType={cardType}
                            showAnswer={true}
                            isDarkMode={isDarkMode}
                            css={activeCSS}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Card selector */}
                  <div className="card-selector">
                    <button
                      className="card-nav-btn"
                      onClick={goToPrevCard}
                      disabled={cardIndex === 0}
                    >
                      <ChevronLeft />
                    </button>
                    <div className="card-info">
                      <span className="card-counter">
                        Card {cardIndex + 1} / {totalCards}
                      </span>
                      <span className="card-label">
                        {getCardLabel(currentCard, cardType)}
                      </span>
                    </div>
                    <button
                      className="card-nav-btn"
                      onClick={goToNextCard}
                      disabled={cardIndex >= totalCards - 1}
                    >
                      <ChevronRight />
                    </button>
                  </div>

                </>
              ) : (
                <div className="no-cards">
                  <div className="no-cards-icon">📭</div>
                  <div className="no-cards-title">No sample cards</div>
                  <div className="no-cards-message">
                    No sample cards available for "{CARD_TYPE_LABELS[cardType]}" type.<br />
                    Add cards to test-cards.json to preview this type.
                  </div>
                </div>
              )}
            </div>

            {/* CSS Editor Panel */}
            {showCSSEditor && (
              <CSSEditorPanel
                css={customCSS || baseCSS}
                onChange={handleCSSChange}
                onClose={() => setShowCSSEditor(false)}
                themeName={selectedTheme}
                cardType={cardType}
                isProduction={currentTheme.isProduction}
                hasChanges={isCustomCSSActive}
              />
            )}

          </div>

          {/* Export Modal */}
          {showExport && (
            <ExportModal
              themeName={selectedTheme}
              themeData={isCustomCSSActive ? {
                ...currentTheme,
                base: customCSS,
              } : currentTheme}
              onClose={() => setShowExport(false)}
            />
          )}
        </div>
      </div>
    </>
  );
}
