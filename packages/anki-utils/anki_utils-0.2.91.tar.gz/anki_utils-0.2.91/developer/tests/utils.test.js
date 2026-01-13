/**
 * Unit tests for card utility functions
 */
import { describe, it, expect } from 'vitest';
import {
  escapeHtml,
  getClozeNumbers,
  getImageSource,
  getEditableFields,
  getCardPreview,
} from './card-utils.js';

describe('escapeHtml', () => {
  it('escapes special HTML characters', () => {
    expect(escapeHtml('<div>')).toBe('&lt;div&gt;');
    expect(escapeHtml('a & b')).toBe('a &amp; b');
    expect(escapeHtml('"quoted"')).toBe('&quot;quoted&quot;');
    expect(escapeHtml("it's")).toBe('it&#039;s');
  });

  it('returns empty string for falsy values', () => {
    expect(escapeHtml('')).toBe('');
    expect(escapeHtml(null)).toBe('');
    expect(escapeHtml(undefined)).toBe('');
  });

  it('converts non-strings to strings', () => {
    expect(escapeHtml(123)).toBe('123');
  });
});

describe('getClozeNumbers', () => {
  it('extracts cloze numbers from text', () => {
    expect(getClozeNumbers('{{c1::answer}}')).toEqual([1]);
    expect(getClozeNumbers('{{c1::first}} and {{c2::second}}')).toEqual([1, 2]);
    expect(getClozeNumbers('{{c3::three}} before {{c1::one}}')).toEqual([1, 3]);
  });

  it('handles duplicate cloze numbers', () => {
    expect(getClozeNumbers('{{c1::a}} and {{c1::b}}')).toEqual([1]);
  });

  it('returns empty array for text without clozes', () => {
    expect(getClozeNumbers('plain text')).toEqual([]);
    expect(getClozeNumbers('')).toEqual([]);
    expect(getClozeNumbers()).toEqual([]);
  });
});

describe('getImageSource', () => {
  it('prioritizes data over url over path for images', () => {
    const card = {
      image_data: 'data:image/png;base64,...',
      image_url: 'https://example.com/img.png',
      image_path: '/path/to/img.png',
    };
    expect(getImageSource(card)).toBe('data:image/png;base64,...');
  });

  it('falls back to url if data is missing', () => {
    const card = {
      image_url: 'https://example.com/img.png',
      image_path: '/path/to/img.png',
    };
    expect(getImageSource(card)).toBe('https://example.com/img.png');
  });

  it('falls back to path if data and url are missing', () => {
    const card = { image_path: '/path/to/img.png' };
    expect(getImageSource(card)).toBe('/path/to/img.png');
  });

  it('handles photo field for person cards', () => {
    const card = {
      photo_data: 'data:image/jpeg;base64,...',
      photo_url: 'https://example.com/photo.jpg',
    };
    expect(getImageSource(card, 'photo')).toBe('data:image/jpeg;base64,...');
  });

  it('returns empty string for null/undefined card', () => {
    expect(getImageSource(null)).toBe('');
    expect(getImageSource(undefined)).toBe('');
  });
});

describe('getEditableFields', () => {
  it('returns correct fields for front-back cards', () => {
    const fields = getEditableFields({ type: 'front-back' });
    expect(fields).toHaveLength(5);
    expect(fields.map(f => f.value)).toContain('question');
    expect(fields.map(f => f.value)).toContain('answer');
  });

  it('returns correct fields for concept cards', () => {
    const fields = getEditableFields({ type: 'concept' });
    expect(fields).toHaveLength(6);
    expect(fields.map(f => f.value)).toContain('concept');
    expect(fields.map(f => f.value)).toContain('definition');
  });

  it('returns correct fields for cloze cards', () => {
    const fields = getEditableFields({ type: 'cloze', _clozeNum: 2 });
    expect(fields).toHaveLength(5);
    expect(fields[0].label).toBe('Cloze text (c2)');
  });

  it('returns correct fields for person cards', () => {
    const fields = getEditableFields({ type: 'person' });
    expect(fields).toHaveLength(9);
    expect(fields.map(f => f.value)).toContain('full_name');
  });

  it('returns correct fields for image-occlusion cards', () => {
    const fields = getEditableFields({ type: 'image-occlusion' });
    expect(fields).toHaveLength(2);
    expect(fields.map(f => f.value)).toContain('header');
  });

  it('returns empty array for null/undefined card', () => {
    expect(getEditableFields(null)).toEqual([]);
    expect(getEditableFields(undefined)).toEqual([]);
  });

  it('returns empty array for unknown card type', () => {
    expect(getEditableFields({ type: 'unknown' })).toEqual([]);
  });
});

describe('getCardPreview', () => {
  it('returns question for front-back cards', () => {
    const card = { type: 'front-back', question: 'What is 2+2?' };
    expect(getCardPreview(card)).toBe('What is 2+2?');
  });

  it('returns concept for concept cards', () => {
    const card = { type: 'concept', concept: 'Photosynthesis' };
    expect(getCardPreview(card)).toBe('Photosynthesis');
  });

  it('replaces cloze markers with [...] for cloze cards', () => {
    const card = { type: 'cloze', cloze_text: 'The capital of France is {{c1::Paris}}' };
    expect(getCardPreview(card)).toBe('The capital of France is [...]');
  });

  it('returns prompt for image cards', () => {
    const card = { type: 'image', prompt: 'What is shown in this image?' };
    expect(getCardPreview(card)).toBe('What is shown in this image?');
  });

  it('returns full_name for person cards', () => {
    const card = { type: 'person', full_name: 'John Doe' };
    expect(getCardPreview(card)).toBe('John Doe');
  });

  it('returns header for image-occlusion cards', () => {
    const card = { type: 'image-occlusion', header: 'Anatomy of the heart' };
    expect(getCardPreview(card)).toBe('Anatomy of the heart');
  });

  it('truncates long text to 60 characters', () => {
    const longQuestion = 'This is a very long question that exceeds the maximum length allowed for preview text in the UI';
    const card = { type: 'front-back', question: longQuestion };
    const preview = getCardPreview(card);
    expect(preview.length).toBe(63); // 60 chars + '...'
    expect(preview.endsWith('...')).toBe(true);
  });

  it('returns empty string for null card', () => {
    expect(getCardPreview(null)).toBe('');
  });
});
