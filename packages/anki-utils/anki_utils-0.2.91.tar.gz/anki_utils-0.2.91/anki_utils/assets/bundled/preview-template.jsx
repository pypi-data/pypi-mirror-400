import { useState, useCallback, useMemo, useEffect } from "react";

// ============================================================
// CARD DATA - Claude injects this via sed replacement
// ============================================================
const cardData = __CARD_DATA_PLACEHOLDER__;
// ============================================================

// ============================================================
// PURE FUNCTIONS - Imported from shared module (window.PureFunctions)
// Source of truth: anki_utils/assets/pure-functions.js
// ============================================================
// =============================================================================
// PURE FUNCTIONS (Inlined by bundle-artifacts.py)
// Source: anki_utils/assets/pure-functions.js
// =============================================================================
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
// END PURE FUNCTIONS
// =============================================================================
// ============================================================
// THEME CSS - Injected by Claude skill from anki-utils CLI
// ============================================================
// Source of truth: anki_utils/themes.py
// Injection: anki-utils themes --all-json
// Structure: { minimal: { base, conceptInstruction, image, person, io }, ... }
// ============================================================
const THEME_CSS = __THEMES_PLACEHOLDER__;

// Wrapper for getCardCSS that binds the local THEME_CSS
// (The shared function takes THEME_CSS as first parameter for testability)
function getCardCSS(theme, cardType) {
  return _getCardCSS(THEME_CSS, theme, cardType);
}

const PERSON_TEMPLATE_KEYS = [
  { key: 'person.city', label: 'City', field: 'current_city' },
  { key: 'person.photo', label: 'Photo', field: 'photo' },
  { key: 'person.title', label: 'Title', field: 'title' },
  { key: 'person.manager', label: 'Manager', field: 'reports_to' },
  { key: 'person.reports', label: 'Direct Reports', field: 'direct_reports' },
  { key: 'person.partner', label: 'Partner', field: 'partner_name' },
  { key: 'person.hobbies', label: 'Hobbies', field: 'hobbies' },
  { key: 'person.birthday', label: 'Birthday', field: 'birthday' },
  { key: 'person.company', label: 'Company', field: 'company' },
];


// =============================================================================
// NATIVE ANKI TEMPLATES - Exact qfmt/afmt from create_anki_package.py
// =============================================================================

const ANKI_TEMPLATES = {
  'front-back': {
    qfmt: `<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>
  <br>
  <div class="question">
    {{Question}}
  </div>`,
    afmt: `{{FrontSide}}

  <br>
  <div class="answer">
    {{Answer}}
  </div>

  <div class="extra-info">
    {{Extra Info}}
  </div>
</div>`,
  },

  'concept': {
    // Card 1: Term → Definition
    card1: {
      qfmt: `<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc)}}</p>
    <p>By {{Author Name}}</p>
  </div>
<br>
  <div class="concept-instruction">
    Define the concept
  </div>
  <div class="question">
    {{Concept}}
  </div>`,
      afmt: `{{FrontSide}}

  <br>
  <div class="answer">
    {{Definition}}
  </div>

  <div class="extra-info">
    <br>{{Example}}
  </div>

  <div class="extra-info">
    <br>{{Extra Info}}
  </div>
</div>`,
    },
    // Card 2: Definition → Term
    card2: {
      qfmt: `<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc)}}</p>
    <p>By {{Author Name}}</p>
  </div>
<br>
  <div class="concept-instruction">
    Name the concept
  </div>
  <div class="answer">
    {{Definition}}
  </div>`,
      afmt: `<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc)}}</p>
    <p>By {{Author Name}}</p>
  </div>
<br>
  <div class="concept-instruction">
    Name the concept
  </div>
  <div class="question">
    {{Concept}}
  </div>
<br>
<br>
  <div class="answer">
    {{Definition}}
  </div>

  <div class="extra-info">
    <br>{{Example}}
  </div>

  <div class="extra-info">
    <br>{{Extra Info}}
  </div>
</div>`,
    },
  },

  'cloze': {
    qfmt: `<div class="card">
  <!-- Title and Author -->
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>

  <br>
  <div class="answer">{{cloze:Cloze Question & Answer}}

  </div>`,
    afmt: `<div class="card">
  <!-- Title and Author -->
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>

  <br>
  <div class="answer">
    {{cloze:Cloze Question & Answer}}
  </div>

  <div class="extra-info">
    <br>{{Example}}
  </div>

  <div class="extra-info">
    <br>{{Extra Info}}
  </div>
</div>`,
  },

  'image': {
    qfmt: `<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>

  <div class="prompt">{{Prompt}}</div>

  <div class="image-container">
    {{Image}}
  </div>
</div>`,
    afmt: `<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>

  <div class="prompt">{{Prompt}}</div>

  <div class="answer">{{Answer}}</div>

  <div class="image-container">
    {{Image}}
  </div>

  <div class="extra-info">
    {{Extra Info}}
  </div>
</div>`,
  },

  'person': {
    // Each person field generates a separate card template
    templates: [
      {
        name: 'Location', field: 'Current City',
        qfmt: `{{#Current City}}<div style='font-family: "Arial"; font-size: 20px;'>Where does {{Full Name}} live?</div><hr>{{/Current City}}`,
        afmt: `{{#Current City}}<div style='font-family: "Arial"; font-size: 20px;'>Where does {{Full Name}} live?</div><hr>{{Current City}}{{/Current City}}`,
      },
      {
        name: 'Photo', field: 'Photo',
        qfmt: `{{#Photo}}<div style='font-family: "Arial"; font-size: 20px;'>Who is this?<br><hr>{{Photo}}</div>{{/Photo}}`,
        afmt: `{{#Photo}}<div style='font-family: "Arial"; font-size: 20px;'>Who is this?<br><hr></div>{{Full Name}}{{/Photo}}`,
      },
      {
        name: 'Title', field: 'Title or Role',
        qfmt: `{{#Title or Role}}<div style='font-family: "Arial"; font-size: 20px;'>What is {{Full Name}}'s current role?</div><hr>{{/Title or Role}}`,
        afmt: `{{#Title or Role}}<div style='font-family: "Arial"; font-size: 20px;'>What is {{Full Name}}'s current role?</div><hr>{{Title or Role}}{{/Title or Role}}`,
      },
      {
        name: 'Manager', field: 'Reports to',
        qfmt: `{{#Reports to}}<div style='font-family: "Arial"; font-size: 20px;'>Who is {{Full Name}}'s current manager?</div><hr>{{/Reports to}}`,
        afmt: `{{#Reports to}}<div style='font-family: "Arial"; font-size: 20px;'>Who is {{Full Name}}'s current manager?</div><hr>{{Reports to}}{{/Reports to}}`,
      },
      {
        name: 'Direct Reports', field: 'Direct Reports',
        qfmt: `{{#Direct Reports}}<div style='font-family: "Arial"; font-size: 20px;'>Who does {{Full Name}} manage?</div><hr>{{/Direct Reports}}`,
        afmt: `{{#Direct Reports}}<div style='font-family: "Arial"; font-size: 20px;'>Who does {{Full Name}} manage?</div><hr>{{Direct Reports}}{{/Direct Reports}}`,
      },
      {
        name: 'Partner', field: "Partner's name",
        qfmt: `{{#Partner's name}}<div style='font-family: "Arial"; font-size: 20px;'>Who is {{Full Name}}'s partner?</div><hr>{{/Partner's name}}`,
        afmt: `{{#Partner's name}}<div style='font-family: "Arial"; font-size: 20px;'>Who is {{Full Name}}'s partner?</div><hr>{{Partner's name}}{{/Partner's name}}`,
      },
      {
        name: 'Hobbies', field: 'Hobbies and Interests',
        qfmt: `{{#Hobbies and Interests}}<div style='font-family: "Arial"; font-size: 20px;'>What are {{Full Name}}'s hobbies and interests?</div><hr>{{/Hobbies and Interests}}`,
        afmt: `{{#Hobbies and Interests}}<div style='font-family: "Arial"; font-size: 20px;'>What are {{Full Name}}'s hobbies and interests?</div><hr>{{Hobbies and Interests}}{{/Hobbies and Interests}}`,
      },
      {
        name: 'Birthday', field: 'Birthday',
        qfmt: `{{#Birthday}}<div style='font-family: "Arial"; font-size: 20px;'>When is {{Full Name}}'s birthday?</div><hr>{{/Birthday}}`,
        afmt: `{{#Birthday}}<div style='font-family: "Arial"; font-size: 20px;'>When is {{Full Name}}'s birthday?</div><hr>{{Birthday}}{{/Birthday}}`,
      },
      {
        name: 'Company', field: 'Company',
        qfmt: `{{#Company}}<div style='font-family: "Arial"; font-size: 20px;'>What company does {{Full Name}} work for?</div><hr>{{/Company}}`,
        afmt: `{{#Company}}<div style='font-family: "Arial"; font-size: 20px;'>What company does {{Full Name}} work for?</div><hr>{{Company}}{{/Company}}`,
      },
    ],
  },

  'image-occlusion': {
    qfmt: `<div class="io-card">
{{#Header}}<div class="io-header">{{Header}}</div>{{/Header}}
<div class="io-container">{{Image}}</div>
<div class="io-cloze-data">{{cloze:Occlusions}}</div>
</div>`,
    afmt: `<div class="io-card io-back">
{{#Header}}<div class="io-header">{{Header}}</div>{{/Header}}
<div class="io-container">{{Image}}</div>
<div class="io-answer">{{cloze:Occlusions}}</div>
{{#BackExtra}}<div class="io-back-extra">{{BackExtra}}</div>{{/BackExtra}}
</div>`,
  },
};

// =============================================================================
// TEMPLATE SUBSTITUTION ENGINE
// =============================================================================

/**
 * Generate SVG overlay for image occlusion cards
 * This pre-renders the SVG since JavaScript doesn't run in the sandboxed iframe
 */
function generateIOEmbeddedSvg(card, showAnswer) {
  // NEW APPROACH: Embed image INSIDE SVG so they scale together
  // This fixes the mask drift issue where image and overlay scaled independently
  const occlusions = card.occlusions || [];
  const currentCloze = card._clozeNum || 1;
  const mode = card.occlusion_mode || 'hide_all_guess_one';

  // Get image source and dimensions
  const imgSrc = getImageSource(card);
  const imgWidth = card.image_width || 800;
  const imgHeight = card.image_height || 600;

  if (!imgSrc) return '';

  let shapes = '';

  occlusions.forEach((region) => {
    const isCurrent = region.cloze_num === currentCloze;

    let shouldShow = false;
    let cssClass = 'io-mask';

    if (showAnswer) {
      if (isCurrent) {
        cssClass = 'io-revealed';
        shouldShow = true;
      } else if (mode === 'hide_all_guess_one') {
        shouldShow = true;
      }
    } else {
      if (mode === 'hide_all_guess_one') {
        shouldShow = true;
        if (isCurrent) cssClass = 'io-mask-active';
      } else {
        if (isCurrent) {
          shouldShow = true;
          cssClass = 'io-mask-active';
        }
      }
    }

    if (!shouldShow) return;

    // Convert normalized (0-1) to pixel coordinates
    const left = (region.left || 0) * imgWidth;
    const top = (region.top || 0) * imgHeight;
    const width = (region.width || 0.1) * imgWidth;
    const height = (region.height || 0.1) * imgHeight;

    // Always use rect for cleaner appearance
    shapes += `<rect x="${left}" y="${top}" width="${width}" height="${height}" class="${cssClass}" />`;
  });

  // Return complete SVG with embedded image - viewBox matches image dimensions
  // so image and masks scale together proportionally
  return `<svg class="io-embedded-svg" viewBox="0 0 ${imgWidth} ${imgHeight}" preserveAspectRatio="xMidYMid meet" style="max-width:100%;max-height:55vh;display:block;margin:0 auto;">
    <image href="${imgSrc}" x="0" y="0" width="${imgWidth}" height="${imgHeight}" />
    ${shapes}
  </svg>`;
}

/**
 * Map card JSON fields to Anki field names for substitution
 */
function getFieldMap(card) {
  // Handle image field - convert path/url/data to <img> tag
  let imageHtml = '';
  const imgSrc = getImageSource(card);
  if (imgSrc) {
    imageHtml = `<img src="${escapeHtml(imgSrc)}" class="io-image" alt="Card image" onerror="this.outerHTML='<div class=\\'image-placeholder\\'>[Image: ${escapeHtml(imgSrc.split('/').pop() || 'not loaded')}]</div>'" />`;
  }

  // Handle photo field for person cards
  let photoHtml = '';
  const photoSrc = getImageSource(card, 'photo');
  if (photoSrc) {
    photoHtml = `<img src="${escapeHtml(photoSrc)}" alt="${escapeHtml(card.full_name || 'Person')}" onerror="this.outerHTML='<div class=\\'image-placeholder\\'>[Photo: ${escapeHtml(photoSrc.split('/').pop() || 'not loaded')}]</div>'" />`;
  }

  return {
    // Front-back fields
    'Question': escapeHtml(card.question || ''),
    'Answer': card.answer || '', // Don't escape - may contain HTML from markdown conversion
    'Extra Info': escapeHtml(card.extra_info || ''),
    'Source (book, article, etc.)': escapeHtml(card.source || ''),
    'Source (book, article, etc)': escapeHtml(card.source || ''), // Note: variant without period
    'Author Name': escapeHtml(card.author || 'Claude'),

    // Concept fields
    'Concept': escapeHtml(card.concept || ''),
    'Definition': escapeHtml(card.definition || ''),
    'Example': escapeHtml(card.example || ''),

    // Cloze fields
    'Cloze Question & Answer': card.cloze_text || '',

    // Image fields
    'Image': imageHtml,
    'Prompt': escapeHtml(card.prompt || ''),

    // Person fields
    'Full Name': escapeHtml(card.full_name || ''),
    'Photo': photoHtml,
    'Current City': escapeHtml(card.current_city || ''),
    'Title or Role': escapeHtml(card.title || ''),
    'Reports to': escapeHtml(card.reports_to || ''),
    'Direct Reports': escapeHtml(card.direct_reports || ''),
    "Partner's name": escapeHtml(card.partner_name || ''),
    'Hobbies and Interests': escapeHtml(card.hobbies || ''),
    'Birthday': escapeHtml(card.birthday || ''),
    'Company': escapeHtml(card.company || ''),

    // Image occlusion fields
    'Header': escapeHtml(card.header || ''),
    'Occlusions': buildClozeFromOcclusions(card.occlusions),
    'BackExtra': escapeHtml(card.back_extra || ''),
  };
}

/**
 * Process Anki conditional syntax: {{#Field}}...{{/Field}}
 * Shows content only if field has a value
 */
function processConditionals(template, fieldMap) {
  // Match {{#FieldName}}content{{/FieldName}}
  return template.replace(/\{\{#([^}]+)\}\}([\s\S]*?)\{\{\/\1\}\}/g, (match, fieldName, content) => {
    const value = fieldMap[fieldName];
    if (value && value.trim()) {
      // Field has value - show the content (but still needs field substitution)
      return content;
    }
    // Field is empty - hide the content
    return '';
  });
}

/**
 * Process cloze deletion syntax for display
 * Front: {{cloze:Field}} shows [...] for deletions
 * Back: {{cloze:Field}} shows the revealed text
 */
function processCloze(template, fieldMap, showAnswer, currentCloze = 1) {
  return template.replace(/\{\{cloze:([^}]+)\}\}/g, (match, fieldName) => {
    const clozeText = fieldMap[fieldName] || '';
    return clozeText.replace(CLOZE_PATTERN, (clozeMatch, clozeNum, clozeValue) => {
      const clozeIndex = Number(clozeNum);
      if (clozeIndex === currentCloze) {
        if (showAnswer) {
          return `<span class="cloze">${clozeValue}</span>`;
        }
        return '<span class="cloze">[...]</span>';
      }
      return clozeValue;
    });
  });
}

/**
 * Substitute all {{FieldName}} placeholders with values
 */
function substituteFields(template, fieldMap) {
  let result = template;
  for (const [field, value] of Object.entries(fieldMap)) {
    // Escape special regex characters in field name
    const escapedField = field.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    result = result.replace(new RegExp(`\\{\\{${escapedField}\\}\\}`, 'g'), value || '');
  }
  return result;
}

/**
 * Main render function - processes template with all substitutions
 */
function renderCardFromTemplate(card, showAnswer) {
  const fieldMap = getFieldMap(card);
  let qfmt, afmt;

  // Get the appropriate templates based on card type
  switch (card.type) {
    case 'front-back':
      qfmt = ANKI_TEMPLATES['front-back'].qfmt;
      afmt = ANKI_TEMPLATES['front-back'].afmt;
      break;

    case 'concept':
      // Use card1 (term→def) or card2 (def→term) based on direction
      const conceptCard = card._direction === 'definition'
        ? ANKI_TEMPLATES['concept'].card2
        : ANKI_TEMPLATES['concept'].card1;
      qfmt = conceptCard.qfmt;
      afmt = conceptCard.afmt;
      break;

    case 'cloze':
      qfmt = ANKI_TEMPLATES['cloze'].qfmt;
      afmt = ANKI_TEMPLATES['cloze'].afmt;
      break;

    case 'image':
      qfmt = ANKI_TEMPLATES['image'].qfmt;
      afmt = ANKI_TEMPLATES['image'].afmt;
      break;

    case 'person':
      // Person cards use the template for their specific field
      const personTemplates = ANKI_TEMPLATES['person'].templates;
      const templateIndex = card._fieldIndex || 0;
      const personTemplate = personTemplates[templateIndex] || personTemplates[0];
      qfmt = personTemplate.qfmt;
      afmt = personTemplate.afmt;
      break;

    case 'image-occlusion':
      qfmt = ANKI_TEMPLATES['image-occlusion'].qfmt;
      afmt = ANKI_TEMPLATES['image-occlusion'].afmt;
      break;

    default:
      return '<div class="card-content">Unknown card type</div>';
  }

  // Process the front template
  let frontHtml = qfmt;

  // For IO cards, replace the Image placeholder with embedded SVG BEFORE field substitution
  // This prevents the large base64 img tag from being injected
  if (card.type === 'image-occlusion') {
    const embeddedSvg = generateIOEmbeddedSvg(card, false);
    frontHtml = frontHtml.replace(
      '<div class="io-container">{{Image}}</div>',
      `<div class="io-container">${embeddedSvg}</div>`
    );
  }

  frontHtml = processConditionals(frontHtml, fieldMap);
  frontHtml = processCloze(frontHtml, fieldMap, false, card._clozeNum || 1);
  frontHtml = substituteFields(frontHtml, fieldMap);

  if (!showAnswer) {
    return frontHtml;
  }

  // Process the back template
  let backHtml = afmt;

  // For IO cards, replace Image placeholder BEFORE field substitution
  if (card.type === 'image-occlusion') {
    const embeddedSvg = generateIOEmbeddedSvg(card, true);
    backHtml = backHtml.replace(
      '<div class="io-container">{{Image}}</div>',
      `<div class="io-container">${embeddedSvg}</div>`
    );
  }

  // Handle {{FrontSide}} - replace with rendered front
  backHtml = backHtml.replace('{{FrontSide}}', frontHtml);

  backHtml = processConditionals(backHtml, fieldMap);
  backHtml = processCloze(backHtml, fieldMap, true, card._clozeNum || 1);
  backHtml = substituteFields(backHtml, fieldMap);

  return backHtml;
}

// =============================================================================
// PERSON CARD FIELD DETECTION (for card expansion)
// =============================================================================

/**
 * Get the list of person fields that have values - used for card expansion.
 * The order must match ANKI_TEMPLATES.person.templates indices.
 */
function getPersonFields(card) {
  const fields = [];
  // Index 0: Location (Current City)
  if (card.current_city) {
    fields.push({ key: 'city', templateIndex: 0, label: 'City', value: card.current_city });
  }
  // Index 1: Photo
  if (getImageSource(card, 'photo')) {
    fields.push({ key: 'photo', templateIndex: 1, label: 'Name', value: card.full_name });
  }
  // Index 2: Title or Role
  if (card.title) {
    fields.push({ key: 'title', templateIndex: 2, label: 'Role', value: card.title });
  }
  // Index 3: Reports to (Manager)
  if (card.reports_to) {
    fields.push({ key: 'manager', templateIndex: 3, label: 'Manager', value: card.reports_to });
  }
  // Index 4: Direct Reports
  if (card.direct_reports) {
    fields.push({ key: 'reports', templateIndex: 4, label: 'Direct Reports', value: card.direct_reports });
  }
  // Index 5: Partner's name
  if (card.partner_name) {
    fields.push({ key: 'partner', templateIndex: 5, label: 'Partner', value: card.partner_name });
  }
  // Index 6: Hobbies and Interests
  if (card.hobbies) {
    fields.push({ key: 'hobbies', templateIndex: 6, label: 'Hobbies', value: card.hobbies });
  }
  // Index 7: Birthday
  if (card.birthday) {
    fields.push({ key: 'birthday', templateIndex: 7, label: 'Birthday', value: card.birthday });
  }
  // Index 8: Company
  if (card.company) {
    fields.push({ key: 'company', templateIndex: 8, label: 'Company', value: card.company });
  }
  return fields;
}


// Get HTML for a card (front or back) - now uses native Anki templates
function getCardHtml(card, showAnswer) {
  if (!card) return '';
  return renderCardFromTemplate(card, showAnswer);
}

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
 * CardIframe - Wrapper for SharedCardPreview that handles card data transformation
 * This maintains backward compatibility with existing usage in this file.
 */
function CardIframe({ card, showAnswer, theme, isDarkMode, onTap }) {
  const cardCss = getCardCSS(theme, card?.type);
  const cardHtml = getCardHtml(card, showAnswer);
  const needsCardBody = card?.type === 'person';

  return (
    <SharedCardPreview
      html={cardHtml}
      css={cardCss}
      isDarkMode={isDarkMode}
      onTap={onTap}
      needsCardBody={needsCardBody}
    />
  );
}

// =============================================================================
// CARD EXPANSION - Sequential numbering (1, 2, 3...)
// =============================================================================

function expandCards(cards) {
  const expanded = [];
  let sequentialId = 1;

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    // Store original index for JSON export reference
    const originalIndex = i;
    const noteId = `note-${String(originalIndex).padStart(4, '0')}`;

    if (card.type === 'concept') {
      expanded.push({
        ...card,
        _originalIndex: originalIndex,
        _noteId: noteId,
        _templateKey: 'concept.term',
        _cardInstanceId: `${noteId}::concept.term`,
        _direction: 'term',
        _displayId: sequentialId++,
        _subLabel: 'Term → Definition'
      });
      expanded.push({
        ...card,
        _originalIndex: originalIndex,
        _noteId: noteId,
        _templateKey: 'concept.definition',
        _cardInstanceId: `${noteId}::concept.definition`,
        _direction: 'definition',
        _displayId: sequentialId++,
        _subLabel: 'Definition → Term'
      });
    } else if (card.type === 'person') {
      const fields = getPersonFields(card);
      fields.forEach((f) => {
        const personTemplate = PERSON_TEMPLATE_KEYS[f.templateIndex];
        const templateKey = personTemplate?.key || `person.field-${f.templateIndex}`;
        expanded.push({
          ...card,
          _originalIndex: originalIndex,
          _noteId: noteId,
          _templateKey: templateKey,
          _cardInstanceId: `${noteId}::${templateKey}`,
          _fieldIndex: f.templateIndex,
          _displayId: sequentialId++,
          _subLabel: f.label
        });
      });
    } else if (card.type === 'cloze') {
      const clozeNumbers = getClozeNumbers(card.cloze_text || '');
      clozeNumbers.forEach((clozeNum) => {
        const templateKey = `cloze.c${clozeNum}`;
        expanded.push({
          ...card,
          _originalIndex: originalIndex,
          _noteId: noteId,
          _templateKey: templateKey,
          _cardInstanceId: `${noteId}::${templateKey}`,
          _clozeNum: clozeNum,
          _displayId: sequentialId++,
          _subLabel: `Cloze ${clozeNum}`
        });
      });
      if (clozeNumbers.length === 0) {
        expanded.push({
          ...card,
          _originalIndex: originalIndex,
          _noteId: noteId,
          _templateKey: 'cloze.c1',
          _cardInstanceId: `${noteId}::cloze.c1`,
          _clozeNum: 1,
          _displayId: sequentialId++
        });
      }
    } else if (card.type === 'image-occlusion') {
      // Expand image-occlusion cards - one card per occlusion region
      const occlusions = card.occlusions || [];
      occlusions.forEach((occ, occIdx) => {
        const clozeNum = occ.cloze_num || (occIdx + 1);
        const templateKey = `image-occlusion.c${clozeNum}`;
        expanded.push({
          ...card,
          _originalIndex: originalIndex,
          _noteId: noteId,
          _templateKey: templateKey,
          _cardInstanceId: `${noteId}::${templateKey}`,
          _clozeNum: clozeNum,
          _displayId: sequentialId++,
          _subLabel: `Region ${clozeNum}: ${occ.label || 'Unknown'}`
        });
      });
      // If no occlusions, add single card
      if (occlusions.length === 0) {
        expanded.push({
          ...card,
          _originalIndex: originalIndex,
          _noteId: noteId,
          _templateKey: 'image-occlusion.c1',
          _cardInstanceId: `${noteId}::image-occlusion.c1`,
          _clozeNum: 1,
          _displayId: sequentialId++
        });
      }
    } else {
      const templateKey = card.type === 'image' ? 'image.main' : 'front-back.main';
      expanded.push({
        ...card,
        _originalIndex: originalIndex,
        _noteId: noteId,
        _templateKey: templateKey,
        _cardInstanceId: `${noteId}::${templateKey}`,
        _displayId: sequentialId++
      });
    }
  }
  return expanded;
}

// =============================================================================
// CHROME STYLES
// =============================================================================

const FIXED_HEIGHT = 900;

const chromeStyles = `
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
    --red: #ff453a;
  }

  .preview-wrapper {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    /* Issue #55: Reduced padding for tighter layout (was 16px) */
    padding: 0;
    background: #000;
    min-height: 100vh;
    overflow: auto;
  }

  .app-container {
    width: 100%;
    max-width: 420px;
    min-width: 320px;
    height: ${FIXED_HEIGHT}px;
    min-height: 520px;
    max-height: calc(100vh - 32px);
    display: flex;
    flex-direction: column;
    background-color: var(--bg-primary);
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
    color: var(--text-primary);
    border-radius: 20px;
    overflow: hidden;
    position: relative;
  }

  /* Error state */
  .error-screen {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 24px;
    text-align: center;
  }
  .error-icon { font-size: 48px; margin-bottom: 20px; opacity: 0.6; }
  .error-title { font-size: 20px; font-weight: 600; margin-bottom: 8px; }
  .error-message { font-size: 15px; color: var(--text-tertiary); line-height: 1.5; }

  /* Header bar - contains progress and info */
  .header-bar {
    background: var(--bg-secondary);
    padding: 12px 16px;
    border-bottom: 1px solid var(--separator);
    flex-shrink: 0;
  }
  .progress-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }
  .progress-bar {
    flex: 1;
    height: 4px;
    background: var(--bg-tertiary);
    border-radius: 2px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    background: var(--blue);
    border-radius: 2px;
    transition: width 0.2s ease-out;
  }
  .progress-counter {
    font-size: 12px;
    color: var(--text-secondary);
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
  }
  .header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .card-type-label {
    font-size: 12px;
    color: var(--text-secondary);
  }
  .deck-label {
    font-size: 12px;
    color: var(--text-tertiary);
  }

  .card-face-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    background: var(--bg-tertiary);
    padding: 4px;
    border-radius: 8px;
  }
  .card-face-indicator span {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-tertiary);
    padding: 2px 6px;
    border-radius: 6px;
    transition: all 0.2s ease;
  }
  .card-face-indicator span.active {
    background: var(--bg-primary);
    color: var(--text-secondary);
  }

  /* Card area - full height, iframe fills it */
  .card-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }
  .card-iframe-container {
    flex: 1;
    min-height: 0;
    overflow: hidden;
    cursor: pointer;
  }
  .flip-hint {
    position: absolute;
    bottom: 140px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
    color: var(--text-tertiary);
    background: rgba(0,0,0,0.6);
    padding: 6px 12px;
    border-radius: 12px;
    z-index: 5;
  }

  /* Bottom action bar - contained in clear bar */
  .bottom-bar {
    background: var(--bg-secondary);
    border-top: 1px solid var(--separator);
    padding: 16px 20px 24px;
    flex-shrink: 0;
  }
  .action-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
  }

  .nav-btn {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: none;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 18px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.15s;
  }
  .nav-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
  .nav-btn svg {
    width: 20px;
    height: 20px;
  }

  .action-btn {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    border: 2px solid transparent;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 22px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
  }
  .action-btn.approve { border-color: var(--green); color: var(--green); }
  .action-btn.approve.selected { background: var(--green); color: #000; }
  .action-btn.edit { border-color: var(--yellow); color: var(--yellow); }
  .action-btn.edit.selected { background: var(--yellow); color: #000; }
  .action-btn.remove { border-color: var(--red); color: var(--red); }
  .action-btn.remove.selected { background: var(--red); color: #fff; }
  
  /* Disabled state for action buttons */
  .action-btn.disabled {
    opacity: 0.3;
    cursor: not-allowed;
    pointer-events: none;
  }

  .action-btn svg {
    width: 24px;
    height: 24px;
  }

  /* Edit overlay */
  .edit-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--bg-secondary);
    border-radius: 20px 20px 0 0;
    padding: 20px;
    z-index: 30;
    transform: translateY(100%);
    transition: transform 0.25s ease-out;
  }
  .edit-overlay.visible {
    transform: translateY(0);
  }
  .edit-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    text-align: center;
    margin-bottom: 16px;
  }
  .edit-row {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 12px;
  }
  .edit-label {
    font-size: 12px;
    color: var(--text-tertiary);
  }
  .edit-select,
  .edit-input {
    width: 100%;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid var(--separator);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 14px;
  }
  .edit-input::placeholder {
    color: var(--text-tertiary);
  }
  .edit-help {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-bottom: 12px;
  }
  .edit-textarea {
    width: 100%;
    background: var(--bg-tertiary);
    border: none;
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 15px;
    color: var(--text-primary);
    font-family: inherit;
    resize: none;
    min-height: 100px;
    line-height: 1.4;
    margin-bottom: 16px;
  }
  .edit-textarea::placeholder {
    color: var(--text-tertiary);
  }
  .edit-buttons {
    display: flex;
    gap: 12px;
  }
  .edit-cancel-btn {
    flex: 1;
    padding: 14px;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }
  .edit-submit-btn {
    flex: 2;
    padding: 14px;
    background: var(--blue);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }
  .edit-submit-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Settings button */
  .settings-btn {
    background: var(--bg-tertiary);
    border: none;
    border-radius: 8px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: var(--text-secondary);
    font-size: 16px;
  }

  /* Settings overlay backdrop */
  .settings-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 24;
    display: none;
  }
  .settings-backdrop.visible { display: block; }

  /* Settings panel */
  .settings-panel {
    position: absolute;
    top: 70px;
    left: 16px;
    right: 16px;
    background: var(--bg-secondary);
    border-radius: 16px;
    padding: 20px;
    z-index: 25;
    display: none;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  }
  .settings-panel.visible { display: block; }
  .settings-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
  }
  .settings-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid var(--separator);
  }
  .settings-row:last-child { border-bottom: none; }
  .settings-label {
    font-size: 15px;
    color: var(--text-primary);
  }
  .settings-row select {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    min-width: 100px;
  }
  /* Toggle switch */
  .toggle-switch {
    width: 51px;
    height: 31px;
    background: var(--bg-tertiary);
    border-radius: 16px;
    position: relative;
    cursor: pointer;
    transition: background 0.2s;
  }
  .toggle-switch.on { background: var(--blue); }
  .toggle-switch::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 27px;
    height: 27px;
    background: white;
    border-radius: 50%;
    transition: transform 0.2s;
  }
  .toggle-switch.on::after { transform: translateX(20px); }
  .settings-close-btn {
    width: 100%;
    margin-top: 16px;
    padding: 12px;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }

  /* Onboarding screen */
  .onboarding {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 40px 24px;
    text-align: center;
    justify-content: center;
  }
  .onboarding-icon { font-size: 48px; margin-bottom: 24px; }
  .onboarding-title { font-size: 24px; font-weight: 700; margin-bottom: 12px; }
  .onboarding-subtitle { font-size: 15px; color: var(--text-tertiary); margin-bottom: 24px; line-height: 1.5; }
  .onboarding-instructions {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 24px;
    text-align: left;
  }
  .onboarding-instructions p {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 8px;
    line-height: 1.4;
  }
  .onboarding-instructions p:last-child { margin-bottom: 0; }
  .onboarding-instructions strong { color: var(--text-primary); }
  .start-btn {
    padding: 16px 32px;
    font-size: 17px;
    font-weight: 600;
    color: white;
    background: var(--blue);
    border: none;
    border-radius: 14px;
    cursor: pointer;
    margin-bottom: 16px;
  }
  .card-count { font-size: 14px; color: var(--text-tertiary); }

  /* Summary screen - compact layout */
  .summary-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--separator);
    flex-shrink: 0;
  }
  .summary-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .summary-title { font-size: 18px; font-weight: 600; }
  .summary-stats-inline {
    display: flex;
    gap: 12px;
    font-size: 13px;
  }
  .summary-stat-inline {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .summary-stat-inline .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  .summary-stat-inline .dot.approved { background: var(--green); }
  .summary-stat-inline .dot.edited { background: var(--yellow); }
  .summary-stat-inline .dot.removed { background: var(--red); }
  .summary-stat-inline span { color: var(--text-secondary); }
  
  .summary-instruction {
    font-size: 12px;
    color: var(--text-tertiary);
    padding: 8px 16px;
  }
  .summary-list {
    flex: 1;
    overflow-y: auto;
    padding: 0 16px;
  }
  .summary-card {
    display: flex;
    align-items: center;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 10px;
    margin-bottom: 6px;
    cursor: pointer;
    transition: background 0.15s;
  }
  .summary-card:active { background: var(--bg-tertiary); }
  .summary-card-status {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 12px;
    flex-shrink: 0;
    background: var(--text-tertiary);
  }
  .summary-card-status.approved { background: var(--green); }
  .summary-card-status.needs_edit { background: var(--yellow); }
  .summary-card-status.remove { background: var(--red); }
  .summary-card-info { flex: 1; min-width: 0; }
  .summary-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 2px;
  }
  .summary-card-id { 
    font-size: 13px; 
    font-weight: 600;
    color: var(--text-primary);
  }
  .summary-card-type {
    font-size: 10px;
    color: var(--text-tertiary);
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: 4px;
  }
  .summary-card-preview { 
    font-size: 13px; 
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .summary-card-note { 
    font-size: 11px; 
    color: var(--yellow); 
    margin-top: 4px;
    padding: 4px 8px;
    background: rgba(255, 214, 10, 0.1);
    border-radius: 4px;
  }
  .summary-card-edit {
    color: var(--text-tertiary);
    font-size: 16px;
    margin-left: 10px;
    flex-shrink: 0;
  }
  .export-section {
    padding: 12px 16px;
    border-top: 1px solid var(--separator);
    flex-shrink: 0;
  }
  .export-btn {
    width: 100%;
    padding: 14px;
    font-size: 16px;
    font-weight: 600;
    color: white;
    background: var(--blue);
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: background 0.2s;
    text-align: center;
  }
  .export-btn.copied {
    background: var(--green);
  }
  .export-hint { font-size: 11px; color: var(--text-tertiary); text-align: center; margin-top: 6px; }

  /* Keyboard hints bar */
  .keyboard-hints {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    padding: 8px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--separator);
    flex-shrink: 0;
    flex-wrap: wrap;
  }
  .keyboard-hint {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: var(--text-tertiary);
  }
  .keyboard-hint kbd {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    height: 18px;
    padding: 0 5px;
    background: var(--bg-tertiary);
    border: 1px solid var(--separator);
    border-radius: 4px;
    font-size: 10px;
    font-family: inherit;
    color: var(--text-secondary);
  }
  /* Hide keyboard shortcuts on mobile - they don't work on touch devices */
  @media (max-width: 768px) {
    .keyboard-hints { display: none; }
  }
`;

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function AnkiReviewer() {
  // Check for valid card data
  const hasValidData = cardData && cardData.cards && cardData.cards.length > 0;

  const [screen, setScreen] = useState('onboarding');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [feedback, setFeedback] = useState({});
  const [showAnswer, setShowAnswer] = useState(false);
  const [hasFlippedOnce, setHasFlippedOnce] = useState(false); // Track if user has ever flipped (for hint)
  const [hasFlippedCurrent, setHasFlippedCurrent] = useState(false); // Track if current card has been flipped (for auto-advance)
  const [theme, setTheme] = useState(cardData?.theme || 'minimal');
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [showEditOverlay, setShowEditOverlay] = useState(false);
  const [editFeedback, setEditFeedback] = useState('');
  const [returnToSummary, setReturnToSummary] = useState(false); // Track if we came from summary
  const [copied, setCopied] = useState(false); // Track copy button feedback

  const expandedCards = useMemo(() => hasValidData ? expandCards(cardData.cards) : [], [hasValidData]);
  const totalCards = expandedCards.length;
  const currentCard = expandedCards[currentIndex];
  const currentFeedback = feedback[currentIndex] || {};
  const canSaveEdit = editFeedback.trim().length > 0;


  const handleCardTap = useCallback(() => {
    if (!showAnswer) {
      // First tap: flip to back and auto-approve
      setShowAnswer(true);
      setHasFlippedCurrent(true);
      if (!hasFlippedOnce) setHasFlippedOnce(true);

      // Auto-approve the card (user can still override with Edit/Remove)
      setFeedback(prev => ({
        ...prev,
        [currentIndex]: { ...prev[currentIndex], status: 'approved' }
      }));
    } else if (hasFlippedCurrent) {
      // Second tap on back: advance to next card
      if (returnToSummary) {
        setScreen('summary');
        setReturnToSummary(false);
      } else if (currentIndex < totalCards - 1) {
        setCurrentIndex(prev => prev + 1);
        setShowAnswer(false);
        setHasFlippedCurrent(false);
      } else {
        setScreen('summary');
      }
    } else {
      // Edge case: on back but hasn't flipped current (e.g., navigated here)
      setShowAnswer(false);
    }
  }, [showAnswer, hasFlippedOnce, hasFlippedCurrent, currentIndex, totalCards, returnToSummary]);

  const handleActionClick = useCallback((status) => {
    const currentStatus = feedback[currentIndex]?.status;

    // If clicking the same status, toggle it off (unselect)
    if (currentStatus === status) {
      setFeedback(prev => ({
        ...prev,
        [currentIndex]: { ...prev[currentIndex], status: undefined }
      }));
      // Don't auto-advance when unselecting
      return;
    }

    // Set the new status
    setFeedback(prev => ({
      ...prev,
      [currentIndex]: { ...prev[currentIndex], status }
    }));

    if (status === 'needs_edit') {
      setShowEditOverlay(true);
      const existingEdit = feedback[currentIndex]?.edit || {};
      setEditFeedback(existingEdit.feedback || '');
    } else {
      // Auto-advance on approve or remove (unless returning to summary)
      if (returnToSummary) {
        // Go back to summary instead of advancing
        setTimeout(() => {
          setScreen('summary');
          setReturnToSummary(false);
        }, 150);
      } else {
        setTimeout(() => {
          if (currentIndex < totalCards - 1) {
            setCurrentIndex(prev => prev + 1);
            setShowAnswer(false);
          } else {
            setScreen('summary');
          }
        }, 150);
      }
    }
  }, [currentIndex, totalCards, feedback, returnToSummary]);

  const submitEdit = useCallback(() => {
    const editPayload = {
      feedback: editFeedback.trim(),
    };
    if (currentCard?.type === 'cloze') {
      editPayload.clozeNum = currentCard._clozeNum || 1;
    }
    if (currentCard?.type === 'image-occlusion') {
      editPayload.occlusionClozeNum = currentCard._clozeNum || 1;
    }
    setFeedback(prev => ({
      ...prev,
      [currentIndex]: { ...prev[currentIndex], edit: editPayload }
    }));
    setShowEditOverlay(false);

    // Return to summary if we came from there, otherwise advance
    if (returnToSummary) {
      setTimeout(() => {
        setScreen('summary');
        setReturnToSummary(false);
      }, 150);
    } else {
      setTimeout(() => {
        if (currentIndex < totalCards - 1) {
          setCurrentIndex(prev => prev + 1);
          setShowAnswer(false);
        } else {
          setScreen('summary');
        }
      }, 150);
    }
  }, [currentIndex, editFeedback, totalCards, returnToSummary, currentCard]);

  const cancelEdit = useCallback(() => {
    // Remove the needs_edit status if canceling
    setFeedback(prev => ({
      ...prev,
      [currentIndex]: { ...prev[currentIndex], status: undefined, edit: undefined }
    }));
    setShowEditOverlay(false);
  }, [currentIndex]);

  const goNext = useCallback(() => {
    if (currentIndex < totalCards - 1) {
      setCurrentIndex(prev => prev + 1);
      setShowAnswer(false);
    } else {
      setScreen('summary');
    }
  }, [currentIndex, totalCards]);

  const goPrev = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
      setShowAnswer(false);
    }
  }, [currentIndex]);

  const goToCard = useCallback((idx) => {
    setCurrentIndex(idx);
    setShowAnswer(false);
    setReturnToSummary(true); // Mark that we came from summary
    setScreen('review');
  }, []);

  // Keyboard shortcuts for desktop review
  useEffect(() => {
    if (screen !== 'review') return;

    const handleKeyDown = (e) => {
      // Don't handle shortcuts when typing in input fields
      const activeEl = document.activeElement;
      const isTyping = activeEl && (
        activeEl.tagName === 'INPUT' ||
        activeEl.tagName === 'TEXTAREA' ||
        activeEl.tagName === 'SELECT' ||
        activeEl.isContentEditable
      );

      // Handle edit overlay shortcuts
      if (showEditOverlay) {
        if (e.key === 'Escape') {
          e.preventDefault();
          cancelEdit();
        } else if (e.key === 'Enter' && !isTyping && canSaveEdit) {
          e.preventDefault();
          submitEdit();
        }
        return;
      }

      // Don't handle other shortcuts when typing
      if (isTyping) return;

      switch (e.key) {
        case ' ':
          e.preventDefault();
          handleCardTap();
          break;
        case 'a':
        case 'A':
          e.preventDefault();
          handleActionClick('approved');
          break;
        case 'e':
        case 'E':
          e.preventDefault();
          handleActionClick('needs_edit');
          break;
        case 'x':
        case 'X':
        case 'd':
        case 'D':
          e.preventDefault();
          handleActionClick('remove');
          break;
        case 'ArrowLeft':
          e.preventDefault();
          goPrev();
          break;
        case 'ArrowRight':
          e.preventDefault();
          goNext();
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [screen, showEditOverlay, canSaveEdit, cancelEdit, submitEdit, handleCardTap, handleActionClick, goPrev, goNext]);

  const generateExportData = () => {
    const instructions = "Apply the following feedback to the card batch. Each cardInstance includes an explicit templateKey and optional edit payload with free-form feedback describing desired changes. Remove only the referenced card instance (not the entire note if it has multiple cards).";
    const legacyFeedback = expandedCards.map((card, idx) => {
      const f = feedback[idx] || {};
      const entry = {
        cardNumber: card._displayId,
        originalIndex: card._originalIndex,
        type: card.type,
        status: f.status || 'unreviewed',
      };
      if (card._direction) {
        entry.direction = card._direction;
      }
      if (card._subLabel) {
        entry.subCard = card._subLabel;
      }
      if (f.edit) {
        entry.edit = f.edit;
      }
      return entry;
    });

    const notesMap = new Map();
    expandedCards.forEach((card, idx) => {
      const f = feedback[idx] || {};
      const noteId = card._noteId;
      if (!notesMap.has(noteId)) {
        notesMap.set(noteId, {
          noteId,
          originalIndex: card._originalIndex,
          type: card.type,
          cardInstances: [],
        });
      }
      notesMap.get(noteId).cardInstances.push({
        cardInstanceId: card._cardInstanceId,
        templateKey: card._templateKey,
        cardNumber: card._displayId,
        status: f.status || 'unreviewed',
        edit: f.edit || null,
      });
    });

    return JSON.stringify({
      schemaVersion: 'preview-feedback-v2',
      instructions,
      deckName: cardData.deck_name,
      theme,
      notes: Array.from(notesMap.values()),
      legacyFeedback,
    }, null, 2);
  };

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(generateExportData());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [generateExportData]);

  // Error state - no valid card data
  if (!hasValidData) {
    return (
      <>
        <style>{chromeStyles}</style>
        <div className="preview-wrapper">
          <div className="app-container">
            <div className="error-screen">
              <div className="error-icon">⚠️</div>
              <div className="error-title">No Card Data</div>
              <div className="error-message">
                No card data loaded. Please ensure card data is properly injected into the preview template.
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  // Onboarding
  if (screen === 'onboarding') {
    return (
      <>
        <style>{chromeStyles}</style>
        <div className="preview-wrapper">
          <div className="app-container">
            <div className="onboarding">
              <div className="onboarding-icon">📝</div>
              <div className="onboarding-title">Review Your Cards</div>
              <div className="onboarding-subtitle">
                Review the Anki cards Claude generated. Approve good cards, request edits, or remove ones you don't want.
              </div>
              <div className="onboarding-instructions">
                <p><strong>How it works:</strong></p>
                <p>• Tap a card to flip it — this auto-approves the card</p>
                <p>• Tap again to advance to the next card</p>
                <p>• Use Edit or Remove buttons to change a card's status</p>
                <p><strong>Important:</strong> When you're done, click "Copy feedback for Claude" and paste it back into your Claude conversation to apply changes.</p>
              </div>
              <button className="start-btn" onClick={() => setScreen('review')}>
                Start Reviewing
              </button>
              <div className="card-count">{totalCards} cards to review</div>
            </div>
          </div>
        </div>
      </>
    );
  }

  // Summary
  if (screen === 'summary') {
    const stats = { approved: 0, needs_edit: 0, remove: 0 };
    Object.values(feedback).forEach(f => {
      if (stats[f.status] !== undefined) stats[f.status]++;
    });

    return (
      <>
        <style>{chromeStyles}</style>
        <div className="preview-wrapper">
          <div className="app-container">
            <div className="summary-header">
              <div className="summary-title-row">
                <div className="summary-title">Review Complete</div>
                <div className="summary-stats-inline">
                  <div className="summary-stat-inline">
                    <div className="dot approved"></div>
                    <span>{stats.approved}</span>
                  </div>
                  <div className="summary-stat-inline">
                    <div className="dot edited"></div>
                    <span>{stats.needs_edit}</span>
                  </div>
                  <div className="summary-stat-inline">
                    <div className="dot removed"></div>
                    <span>{stats.remove}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="summary-instruction">Tap any card to review or change your feedback</div>
            <div className="summary-list">
              {expandedCards.map((card, idx) => {
                const fb = feedback[idx] || {};
                return (
                  <div key={idx} className="summary-card" onClick={() => goToCard(idx)}>
                    <div className={`summary-card-status ${fb.status || ''}`}></div>
                    <div className="summary-card-info">
                      <div className="summary-card-header">
                        <span className="summary-card-id">Card {card._displayId}</span>
                        <span className="summary-card-type">
                          {CARD_TYPE_LABELS[card.type] || card.type}
                          {card._subLabel ? ` · ${card._subLabel}` : ''}
                        </span>
                      </div>
                      <div className="summary-card-preview">{getCardPreview(card)}</div>
                      {fb.edit?.feedback && <div className="summary-card-note">✎ {fb.edit.feedback}</div>}
                    </div>
                    <div className="summary-card-edit">›</div>
                  </div>
                );
              })}
            </div>
            <div className="export-section">
              <button className={`export-btn ${copied ? 'copied' : ''}`} onClick={handleCopy}>
                {copied ? '✓ Copied!' : 'Copy Feedback for Claude'}
              </button>
              <div className="export-hint">Paste into Claude to apply your changes</div>
            </div>
          </div>
        </div>
      </>
    );
  }

  // Review screen
  return (
    <>
      <style>{chromeStyles}</style>
      <div className="preview-wrapper">
        <div className="app-container">
          {/* Header bar */}
          <div className="header-bar">
            <div className="progress-row">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${((currentIndex + 1) / totalCards) * 100}%` }}
                />
              </div>
              <span className="progress-counter">{currentIndex + 1} of {totalCards}</span>
            </div>
            <div className="header-row">
              <span className="card-type-label">
                Card {currentCard?._displayId} · {CARD_TYPE_LABELS[currentCard?.type] || currentCard?.type}
                {currentCard?._subLabel ? ` · ${currentCard._subLabel}` : ''}
              </span>
              <div className="card-face-indicator">
                <span className={!showAnswer ? 'active' : ''}>Front</span>
                <span className={showAnswer ? 'active' : ''}>Back</span>
              </div>
              <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>⚙</button>
            </div>
          </div>

          {/* Keyboard shortcuts hint bar */}
          <div className="keyboard-hints">
            <span className="keyboard-hint"><kbd>Space</kbd> Flip / Next</span>
            <span className="keyboard-hint"><kbd>E</kbd> Edit</span>
            <span className="keyboard-hint"><kbd>X</kbd> Remove</span>
            <span className="keyboard-hint"><kbd>←</kbd><kbd>→</kbd> Navigate</span>
          </div>

          {/* Settings backdrop (click to close) */}
          <div
            className={`settings-backdrop ${showSettings ? 'visible' : ''}`}
            onClick={() => setShowSettings(false)}
          />

          {/* Settings panel */}
          <div className={`settings-panel ${showSettings ? 'visible' : ''}`}>
            <div className="settings-title">{cardData.deck_name || 'Settings'}</div>
            <div className="settings-row">
              <span className="settings-label">Theme</span>
              <select value={theme} onChange={e => setTheme(e.target.value)}>
                {Object.keys(THEME_CSS).map(key => (
                  <option key={key} value={key}>{THEME_LABELS[key] || key}</option>
                ))}
              </select>
            </div>
            <div className="settings-row">
              <span className="settings-label">Dark Mode</span>
              <div
                className={`toggle-switch ${isDarkMode ? 'on' : ''}`}
                onClick={() => setIsDarkMode(!isDarkMode)}
              />
            </div>
            <button className="settings-close-btn" onClick={() => setShowSettings(false)}>
              Close
            </button>
          </div>

          {/* Card area */}
          <div className="card-area">
            <div className="card-iframe-container">
              <CardIframe
                card={currentCard}
                showAnswer={showAnswer}
                theme={theme}
                isDarkMode={isDarkMode}
                onTap={handleCardTap}
              />
            </div>
          </div>

          {!hasFlippedOnce && <div className="flip-hint">Tap to flip and approve</div>}

          {/* Bottom bar with actions */}
          <div className="bottom-bar">
            <div className="action-bar">
              <button className="nav-btn" onClick={goPrev} disabled={currentIndex === 0}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M15 18l-6-6 6-6" />
                </svg>
              </button>

              <button
                className={`action-btn approve ${currentFeedback.status === 'approved' ? 'selected' : ''}`}
                onClick={() => handleActionClick('approved')}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <path d="M5 13l4 4L19 7" />
                </svg>
              </button>

              <button
                className={`action-btn edit ${currentFeedback.status === 'needs_edit' ? 'selected' : ''}`}
                onClick={() => handleActionClick('needs_edit')}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              </button>

              <button
                className={`action-btn remove ${currentFeedback.status === 'remove' ? 'selected' : ''}`}
                onClick={() => handleActionClick('remove')}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>

              <button className="nav-btn" onClick={goNext}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </button>
            </div>
          </div>

          {/* Edit overlay */}
          <div className={`edit-overlay ${showEditOverlay ? 'visible' : ''}`}>
            <div className="edit-title">What would you like changed?</div>
            <textarea
              className="edit-textarea"
              placeholder="Describe what you'd like changed, e.g.&#10;• Make the answer more concise&#10;• Fix the typo in the question&#10;• Add more context to the explanation"
              value={editFeedback}
              onChange={(e) => setEditFeedback(e.target.value)}
              autoFocus
            />
            <div className="edit-buttons">
              <button className="edit-cancel-btn" onClick={cancelEdit}>Cancel</button>
              <button className="edit-submit-btn" onClick={submitEdit} disabled={!canSaveEdit}>Save</button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
