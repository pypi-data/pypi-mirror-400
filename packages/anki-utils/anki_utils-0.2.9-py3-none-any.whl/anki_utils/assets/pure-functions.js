/**
 * Pure utility functions shared between preview-template.jsx and tests.
 *
 * These functions contain logic that doesn't depend on React or runtime-injected data.
 * By centralizing them here, tests always test the actual production code.
 *
 * Usage:
 * - In browser (test-launcher): Functions are attached to window.PureFunctions
 * - In tests (vitest): Import directly with ES modules
 */

// =============================================================================
// CONSTANTS
// =============================================================================

const CARD_TYPE_LABELS = {
  'front-back': 'Front → Back',
  'concept': 'Bidirectional Concept',
  'cloze': 'Cloze Deletion',
  'image': 'Image Recognition',
  'image-occlusion': 'Image Occlusion',
  'person': 'Person',
};

const THEME_LABELS = {
  'minimal': 'Minimal',
  'classic': 'Classic',
  'high-contrast': 'High Contrast',
  'calm': 'Calm',
};

// Regex pattern for Anki cloze deletions: {{c1::answer}}
const CLOZE_PATTERN = /\{\{c(\d+)::([^}]+)\}\}/g;

// =============================================================================
// PURE FUNCTIONS
// =============================================================================

/**
 * Get combined CSS for a card type and theme.
 *
 * Named with underscore prefix because preview-template.jsx wraps this
 * with a version that binds the runtime THEME_CSS.
 *
 * @param {Object} THEME_CSS - The theme CSS object (injected at runtime or mocked in tests)
 * @param {string} theme - Theme name (e.g., 'minimal', 'classic')
 * @param {string} cardType - Card type (e.g., 'front-back', 'concept')
 * @returns {string} Combined CSS for the card
 */
function _getCardCSS(THEME_CSS, theme, cardType) {
  const t = THEME_CSS[theme] || THEME_CSS.minimal;
  switch (cardType) {
    case 'concept':
      return t.base + t.conceptInstruction;
    case 'image':
      return t.base + t.image;
    case 'image-occlusion':
      return t.base + t.io;
    case 'person':
      return t.person;
    default:
      return t.base;
  }
}

/**
 * Get image/photo source from card (handles data, url, and path variants).
 *
 * @param {Object} card - The card object
 * @param {string} field - 'image' or 'photo'
 * @returns {string} The image source URL/path/data
 */
function getImageSource(card, field = 'image') {
  if (field === 'photo') {
    return card.photo_data || card.photo_url || card.photo_path || '';
  }
  return card.image_data || card.image_url || card.image_path || '';
}

/**
 * Escape HTML special characters.
 *
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Get the list of cloze numbers present in a cloze text.
 *
 * @param {string} text - Text containing cloze deletions
 * @returns {number[]} Sorted array of unique cloze numbers
 */
function getClozeNumbers(text = '') {
  const numbers = new Set();
  let match;
  const regex = new RegExp(CLOZE_PATTERN);
  while ((match = regex.exec(text)) !== null) {
    numbers.add(Number(match[1]));
  }
  return Array.from(numbers).sort((a, b) => a - b);
}

/**
 * Build cloze-formatted text from occlusions array.
 *
 * @param {Array} occlusions - Array of occlusion objects with cloze_num and label
 * @returns {string} Cloze-formatted text
 */
function buildClozeFromOcclusions(occlusions) {
  if (!occlusions || occlusions.length === 0) return '';
  return occlusions.map(occ =>
    `{{c${occ.cloze_num || 1}::${occ.label || 'Unknown'}}}`
  ).join(' · ');
}

/**
 * Get content preview for summary cards.
 *
 * @param {Object} card - The card object
 * @returns {string} Truncated preview text
 */
function getCardPreview(card) {
  const maxLength = 60;
  const truncate = (str) => str?.length > maxLength
    ? str.substring(0, maxLength) + '...'
    : str;

  switch (card.type) {
    case 'front-back':
      return truncate(card.question);
    case 'concept':
      return truncate(card.concept);
    case 'cloze':
      return truncate(card.cloze_text?.replace(CLOZE_PATTERN, '[...]'));
    case 'image':
      return truncate(card.prompt);
    case 'image-occlusion':
      return truncate(card.header || 'Image Occlusion');
    case 'person':
      return card.full_name;
    default:
      return '';
  }
}

// =============================================================================
// EXPORTS
// =============================================================================

// ES module exports (for vitest and modern bundlers)
// Note: _getCardCSS is exported as getCardCSS for cleaner test imports
export {
  CARD_TYPE_LABELS,
  THEME_LABELS,
  CLOZE_PATTERN,
  _getCardCSS as getCardCSS,
  getImageSource,
  escapeHtml,
  getClozeNumbers,
  buildClozeFromOcclusions,
  getCardPreview,
};

// Browser global export (for test-launcher environment)
if (typeof window !== 'undefined') {
  window.PureFunctions = {
    CARD_TYPE_LABELS,
    THEME_LABELS,
    CLOZE_PATTERN,
    getCardCSS: _getCardCSS,
    getImageSource,
    escapeHtml,
    getClozeNumbers,
    buildClozeFromOcclusions,
    getCardPreview,
  };
}
