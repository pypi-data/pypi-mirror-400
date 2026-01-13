/**
 * Utility functions for card processing
 * Extracted from preview-template.jsx for testability
 */

/**
 * Escape HTML special characters for safe rendering
 */
export function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Regex pattern for Anki cloze deletions: {{c1::answer}}
 */
export const CLOZE_PATTERN = /\{\{c(\d+)::([^}]+)\}\}/g;

/**
 * Get the list of cloze numbers present in a cloze card.
 */
export function getClozeNumbers(text = '') {
  const numbers = new Set();
  let match;
  const regex = new RegExp(CLOZE_PATTERN);
  while ((match = regex.exec(text)) !== null) {
    numbers.add(Number(match[1]));
  }
  return Array.from(numbers).sort((a, b) => a - b);
}

/**
 * Get image/photo source from card (handles data, url, and path variants)
 */
export function getImageSource(card, field = 'image') {
  if (!card) return '';
  if (field === 'photo') {
    return card.photo_data || card.photo_url || card.photo_path || '';
  }
  return card.image_data || card.image_url || card.image_path || '';
}

/**
 * Get editable fields for a card type
 */
export function getEditableFields(card) {
  if (!card) return [];
  switch (card.type) {
    case 'front-back':
      return [
        { value: 'question', label: 'Question' },
        { value: 'answer', label: 'Answer' },
        { value: 'extra_info', label: 'Extra info' },
        { value: 'source', label: 'Source' },
        { value: 'author', label: 'Author' },
      ];
    case 'concept':
      return [
        { value: 'concept', label: 'Concept' },
        { value: 'definition', label: 'Definition' },
        { value: 'example', label: 'Example' },
        { value: 'extra_info', label: 'Extra info' },
        { value: 'source', label: 'Source' },
        { value: 'author', label: 'Author' },
      ];
    case 'cloze':
      return [
        { value: 'cloze_text', label: `Cloze text (c${card._clozeNum || 1})` },
        { value: 'example', label: 'Example' },
        { value: 'extra_info', label: 'Extra info' },
        { value: 'source', label: 'Source' },
        { value: 'author', label: 'Author' },
      ];
    case 'image':
      return [
        { value: 'prompt', label: 'Prompt' },
        { value: 'answer', label: 'Answer' },
        { value: 'extra_info', label: 'Extra info' },
        { value: 'source', label: 'Source' },
        { value: 'author', label: 'Author' },
      ];
    case 'person':
      return [
        { value: 'full_name', label: 'Full name' },
        { value: 'current_city', label: 'Current city' },
        { value: 'title', label: 'Title or role' },
        { value: 'reports_to', label: 'Reports to' },
        { value: 'direct_reports', label: 'Direct reports' },
        { value: 'partner_name', label: "Partner's name" },
        { value: 'hobbies', label: 'Hobbies and interests' },
        { value: 'birthday', label: 'Birthday' },
        { value: 'company', label: 'Company' },
      ];
    case 'image-occlusion':
      return [
        { value: 'header', label: 'Header' },
        { value: 'back_extra', label: 'Back extra' },
      ];
    default:
      return [];
  }
}

/**
 * Get content preview for summary cards
 */
export function getCardPreview(card) {
  if (!card) return '';
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
