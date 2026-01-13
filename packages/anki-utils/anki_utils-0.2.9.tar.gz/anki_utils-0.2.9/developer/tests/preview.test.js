/**
 * Unit tests for preview-template.jsx pure logic functions.
 *
 * These tests verify the pure logic functions from the shared pure-functions.js module.
 * By importing directly from the source, tests always verify the actual production code.
 *
 * Source: anki_utils/assets/pure-functions.js
 */

import { describe, it, expect } from 'vitest';

// Import pure functions from the shared module (source of truth)
import {
  CARD_TYPE_LABELS,
  THEME_LABELS,
  CLOZE_PATTERN,
  getCardCSS,
  getImageSource,
  escapeHtml,
  getClozeNumbers,
  buildClozeFromOcclusions,
  getCardPreview,
} from '../../anki_utils/assets/pure-functions.js';

// ============================================================
// MOCK THEME_CSS for testing
// ============================================================
// The real THEME_CSS is injected at runtime. For tests, we use mock values
// that let us verify the function logic without depending on actual CSS.

const THEME_CSS = {
  minimal: {
    base: '.minimal-base {}',
    conceptInstruction: '.minimal-concept {}',
    image: '.minimal-image {}',
    io: '.minimal-io {}',
    person: '.minimal-person {}',
  },
  classic: {
    base: '.classic-base {}',
    conceptInstruction: '.classic-concept {}',
    image: '.classic-image {}',
    io: '.classic-io {}',
    person: '.classic-person {}',
  },
  'high-contrast': {
    base: '.high-contrast-base {}',
    conceptInstruction: '.high-contrast-concept {}',
    image: '.high-contrast-image {}',
    io: '.high-contrast-io {}',
    person: '.high-contrast-person {}',
  },
  calm: {
    base: '.calm-base {}',
    conceptInstruction: '.calm-concept {}',
    image: '.calm-image {}',
    io: '.calm-io {}',
    person: '.calm-person {}',
  },
};

// ============================================================
// TESTS
// ============================================================

describe('CARD_TYPE_LABELS constant', () => {
  it('should have all 6 card types', () => {
    expect(Object.keys(CARD_TYPE_LABELS)).toHaveLength(6);
  });

  it('should contain expected card types', () => {
    const expectedTypes = ['front-back', 'concept', 'cloze', 'image', 'image-occlusion', 'person'];
    expectedTypes.forEach(type => {
      expect(CARD_TYPE_LABELS).toHaveProperty(type);
    });
  });

  it('should have human-readable labels', () => {
    expect(CARD_TYPE_LABELS['front-back']).toBe('Front → Back');
    expect(CARD_TYPE_LABELS['concept']).toBe('Bidirectional Concept');
    expect(CARD_TYPE_LABELS['cloze']).toBe('Cloze Deletion');
    expect(CARD_TYPE_LABELS['image']).toBe('Image Recognition');
    expect(CARD_TYPE_LABELS['image-occlusion']).toBe('Image Occlusion');
    expect(CARD_TYPE_LABELS['person']).toBe('Person');
  });
});

describe('THEME_LABELS constant', () => {
  it('should have all 4 themes', () => {
    expect(Object.keys(THEME_LABELS)).toHaveLength(4);
  });

  it('should contain expected themes', () => {
    const expectedThemes = ['minimal', 'classic', 'high-contrast', 'calm'];
    expectedThemes.forEach(theme => {
      expect(THEME_LABELS).toHaveProperty(theme);
    });
  });

  it('should have human-readable labels', () => {
    expect(THEME_LABELS['minimal']).toBe('Minimal');
    expect(THEME_LABELS['classic']).toBe('Classic');
    expect(THEME_LABELS['high-contrast']).toBe('High Contrast');
    expect(THEME_LABELS['calm']).toBe('Calm');
  });
});

describe('getCardCSS', () => {
  describe('theme selection', () => {
    it('should return minimal CSS for minimal theme', () => {
      const css = getCardCSS(THEME_CSS, 'minimal', 'front-back');
      expect(css).toContain('minimal');
    });

    it('should return classic CSS for classic theme', () => {
      const css = getCardCSS(THEME_CSS, 'classic', 'front-back');
      expect(css).toContain('classic');
    });

    it('should return high-contrast CSS for high-contrast theme', () => {
      const css = getCardCSS(THEME_CSS, 'high-contrast', 'front-back');
      expect(css).toContain('high-contrast');
    });

    it('should return calm CSS for calm theme', () => {
      const css = getCardCSS(THEME_CSS, 'calm', 'front-back');
      expect(css).toContain('calm');
    });
  });

  describe('theme fallback', () => {
    it('should fallback to minimal for unknown theme', () => {
      const css = getCardCSS(THEME_CSS, 'unknown-theme', 'front-back');
      expect(css).toContain('minimal');
    });

    it('should fallback to minimal for undefined theme', () => {
      const css = getCardCSS(THEME_CSS, undefined, 'front-back');
      expect(css).toContain('minimal');
    });

    it('should fallback to minimal for null theme', () => {
      const css = getCardCSS(THEME_CSS, null, 'front-back');
      expect(css).toContain('minimal');
    });
  });

  describe('card type CSS combinations', () => {
    const themes = ['minimal', 'classic', 'high-contrast', 'calm'];

    themes.forEach(theme => {
      it(`should return base CSS for front-back cards with ${theme} theme`, () => {
        const css = getCardCSS(THEME_CSS, theme, 'front-back');
        expect(css).toBe(THEME_CSS[theme].base);
      });

      it(`should return base + conceptInstruction CSS for concept cards with ${theme} theme`, () => {
        const css = getCardCSS(THEME_CSS, theme, 'concept');
        expect(css).toBe(THEME_CSS[theme].base + THEME_CSS[theme].conceptInstruction);
      });

      it(`should return base + image CSS for image cards with ${theme} theme`, () => {
        const css = getCardCSS(THEME_CSS, theme, 'image');
        expect(css).toBe(THEME_CSS[theme].base + THEME_CSS[theme].image);
      });

      it(`should return base + io CSS for image-occlusion cards with ${theme} theme`, () => {
        const css = getCardCSS(THEME_CSS, theme, 'image-occlusion');
        expect(css).toBe(THEME_CSS[theme].base + THEME_CSS[theme].io);
      });

      it(`should return person CSS for person cards with ${theme} theme`, () => {
        const css = getCardCSS(THEME_CSS, theme, 'person');
        expect(css).toBe(THEME_CSS[theme].person);
      });

      it(`should return base CSS for cloze cards with ${theme} theme`, () => {
        const css = getCardCSS(THEME_CSS, theme, 'cloze');
        expect(css).toBe(THEME_CSS[theme].base);
      });
    });
  });

  describe('unknown card type handling', () => {
    it('should return base CSS for unknown card types', () => {
      const css = getCardCSS(THEME_CSS, 'minimal', 'unknown-type');
      expect(css).toBe(THEME_CSS.minimal.base);
    });
  });
});

describe('getImageSource', () => {
  describe('image field priority', () => {
    it('should prioritize image_data over image_url and image_path', () => {
      const card = {
        image_data: 'data:image/png;base64,abc123',
        image_url: 'https://example.com/image.png',
        image_path: '/path/to/image.png',
      };
      expect(getImageSource(card)).toBe('data:image/png;base64,abc123');
    });

    it('should use image_url when image_data is not present', () => {
      const card = {
        image_url: 'https://example.com/image.png',
        image_path: '/path/to/image.png',
      };
      expect(getImageSource(card)).toBe('https://example.com/image.png');
    });

    it('should use image_path when image_data and image_url are not present', () => {
      const card = {
        image_path: '/path/to/image.png',
      };
      expect(getImageSource(card)).toBe('/path/to/image.png');
    });

    it('should return empty string when no image source is present', () => {
      const card = {};
      expect(getImageSource(card)).toBe('');
    });
  });

  describe('photo field priority', () => {
    it('should prioritize photo_data over photo_url and photo_path', () => {
      const card = {
        photo_data: 'data:image/jpeg;base64,xyz789',
        photo_url: 'https://example.com/photo.jpg',
        photo_path: '/path/to/photo.jpg',
      };
      expect(getImageSource(card, 'photo')).toBe('data:image/jpeg;base64,xyz789');
    });

    it('should use photo_url when photo_data is not present', () => {
      const card = {
        photo_url: 'https://example.com/photo.jpg',
        photo_path: '/path/to/photo.jpg',
      };
      expect(getImageSource(card, 'photo')).toBe('https://example.com/photo.jpg');
    });

    it('should use photo_path when photo_data and photo_url are not present', () => {
      const card = {
        photo_path: '/path/to/photo.jpg',
      };
      expect(getImageSource(card, 'photo')).toBe('/path/to/photo.jpg');
    });

    it('should return empty string when no photo source is present', () => {
      const card = {};
      expect(getImageSource(card, 'photo')).toBe('');
    });
  });

  describe('field independence', () => {
    it('should not confuse image and photo fields', () => {
      const card = {
        image_data: 'image-data',
        photo_data: 'photo-data',
      };
      expect(getImageSource(card, 'image')).toBe('image-data');
      expect(getImageSource(card, 'photo')).toBe('photo-data');
    });
  });

  describe('edge cases', () => {
    it('should handle empty string values', () => {
      const card = {
        image_data: '',
        image_url: 'https://example.com/image.png',
      };
      // Empty string is falsy, so should fall through to url
      expect(getImageSource(card)).toBe('https://example.com/image.png');
    });

    it('should handle null card', () => {
      // This might throw, but that's expected behavior for invalid input
      expect(() => getImageSource(null)).toThrow();
    });
  });
});

describe('CLOZE_PATTERN regex', () => {
  it('should match valid cloze syntax {{c1::answer}}', () => {
    const text = '{{c1::answer}}';
    const regex = new RegExp(CLOZE_PATTERN);
    const match = regex.exec(text);
    expect(match).not.toBeNull();
    expect(match[1]).toBe('1');
    expect(match[2]).toBe('answer');
  });

  it('should match cloze with multi-digit numbers', () => {
    const text = '{{c12::answer}}';
    const regex = new RegExp(CLOZE_PATTERN);
    const match = regex.exec(text);
    expect(match).not.toBeNull();
    expect(match[1]).toBe('12');
    expect(match[2]).toBe('answer');
  });

  it('should match cloze with spaces in content', () => {
    const text = '{{c1::the answer is here}}';
    const regex = new RegExp(CLOZE_PATTERN);
    const match = regex.exec(text);
    expect(match).not.toBeNull();
    expect(match[2]).toBe('the answer is here');
  });

  it('should match multiple cloze deletions in text', () => {
    const text = 'The {{c1::quick}} brown {{c2::fox}}';
    const matches = [];
    let match;
    const regex = new RegExp(CLOZE_PATTERN);
    while ((match = regex.exec(text)) !== null) {
      matches.push({ num: match[1], content: match[2] });
    }
    expect(matches).toHaveLength(2);
    expect(matches[0]).toEqual({ num: '1', content: 'quick' });
    expect(matches[1]).toEqual({ num: '2', content: 'fox' });
  });

  it('should not match invalid cloze syntax', () => {
    const invalidPatterns = [
      '{{c::answer}}',      // missing number
      '{{1::answer}}',      // missing 'c'
      '{{c1:answer}}',      // single colon
      '{{c1::}}',           // empty content (regex requires at least one char)
      '{c1::answer}',       // single braces
    ];

    invalidPatterns.forEach(pattern => {
      const regex = new RegExp(CLOZE_PATTERN);
      const match = regex.exec(pattern);
      expect(match).toBeNull();
    });
  });
});

describe('escapeHtml', () => {
  it('should escape ampersand', () => {
    expect(escapeHtml('A & B')).toBe('A &amp; B');
  });

  it('should escape less than', () => {
    expect(escapeHtml('A < B')).toBe('A &lt; B');
  });

  it('should escape greater than', () => {
    expect(escapeHtml('A > B')).toBe('A &gt; B');
  });

  it('should escape double quotes', () => {
    expect(escapeHtml('A "B" C')).toBe('A &quot;B&quot; C');
  });

  it('should escape single quotes', () => {
    expect(escapeHtml("A 'B' C")).toBe('A &#039;B&#039; C');
  });

  it('should escape multiple special characters', () => {
    expect(escapeHtml('<script>alert("XSS")</script>')).toBe(
      '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
    );
  });

  it('should return empty string for null', () => {
    expect(escapeHtml(null)).toBe('');
  });

  it('should return empty string for undefined', () => {
    expect(escapeHtml(undefined)).toBe('');
  });

  it('should return empty string for empty string', () => {
    expect(escapeHtml('')).toBe('');
  });

  it('should convert numbers to string', () => {
    expect(escapeHtml(123)).toBe('123');
  });

  it('should handle text without special characters', () => {
    expect(escapeHtml('Hello World')).toBe('Hello World');
  });
});

describe('getClozeNumbers', () => {
  it('should return empty array for empty string', () => {
    expect(getClozeNumbers('')).toEqual([]);
  });

  it('should return empty array for undefined', () => {
    expect(getClozeNumbers(undefined)).toEqual([]);
  });

  it('should extract single cloze number', () => {
    expect(getClozeNumbers('{{c1::answer}}')).toEqual([1]);
  });

  it('should extract multiple cloze numbers in order', () => {
    expect(getClozeNumbers('{{c1::first}} and {{c2::second}}')).toEqual([1, 2]);
  });

  it('should return sorted unique numbers', () => {
    expect(getClozeNumbers('{{c3::third}} {{c1::first}} {{c2::second}}')).toEqual([1, 2, 3]);
  });

  it('should handle duplicate cloze numbers', () => {
    expect(getClozeNumbers('{{c1::first}} and {{c1::also first}}')).toEqual([1]);
  });

  it('should handle multi-digit cloze numbers', () => {
    expect(getClozeNumbers('{{c10::tenth}} {{c2::second}}')).toEqual([2, 10]);
  });

  it('should return empty array for text without cloze deletions', () => {
    expect(getClozeNumbers('Just plain text')).toEqual([]);
  });
});

describe('buildClozeFromOcclusions', () => {
  it('should return empty string for empty array', () => {
    expect(buildClozeFromOcclusions([])).toBe('');
  });

  it('should return empty string for undefined', () => {
    expect(buildClozeFromOcclusions(undefined)).toBe('');
  });

  it('should return empty string for null', () => {
    expect(buildClozeFromOcclusions(null)).toBe('');
  });

  it('should build cloze text from single occlusion', () => {
    const occlusions = [{ cloze_num: 1, label: 'Heart' }];
    expect(buildClozeFromOcclusions(occlusions)).toBe('{{c1::Heart}}');
  });

  it('should build cloze text from multiple occlusions', () => {
    const occlusions = [
      { cloze_num: 1, label: 'Heart' },
      { cloze_num: 2, label: 'Lungs' },
    ];
    expect(buildClozeFromOcclusions(occlusions)).toBe('{{c1::Heart}} · {{c2::Lungs}}');
  });

  it('should default to cloze_num 1 when not provided', () => {
    const occlusions = [{ label: 'Part' }];
    expect(buildClozeFromOcclusions(occlusions)).toBe('{{c1::Part}}');
  });

  it('should default to "Unknown" when label not provided', () => {
    const occlusions = [{ cloze_num: 1 }];
    expect(buildClozeFromOcclusions(occlusions)).toBe('{{c1::Unknown}}');
  });

  it('should handle missing both cloze_num and label', () => {
    const occlusions = [{}];
    expect(buildClozeFromOcclusions(occlusions)).toBe('{{c1::Unknown}}');
  });
});

describe('getCardPreview', () => {
  it('should return question for front-back cards', () => {
    const card = { type: 'front-back', question: 'What is 2+2?' };
    expect(getCardPreview(card)).toBe('What is 2+2?');
  });

  it('should return concept for concept cards', () => {
    const card = { type: 'concept', concept: 'Photosynthesis' };
    expect(getCardPreview(card)).toBe('Photosynthesis');
  });

  it('should return cloze text with [...] for cloze cards', () => {
    const card = { type: 'cloze', cloze_text: 'The {{c1::sun}} rises in the east' };
    expect(getCardPreview(card)).toBe('The [...] rises in the east');
  });

  it('should return prompt for image cards', () => {
    const card = { type: 'image', prompt: 'Identify this structure' };
    expect(getCardPreview(card)).toBe('Identify this structure');
  });

  it('should return header for image-occlusion cards', () => {
    const card = { type: 'image-occlusion', header: 'Human Anatomy' };
    expect(getCardPreview(card)).toBe('Human Anatomy');
  });

  it('should return default text for image-occlusion without header', () => {
    const card = { type: 'image-occlusion' };
    expect(getCardPreview(card)).toBe('Image Occlusion');
  });

  it('should return full_name for person cards', () => {
    const card = { type: 'person', full_name: 'John Doe' };
    expect(getCardPreview(card)).toBe('John Doe');
  });

  it('should return empty string for unknown card types', () => {
    const card = { type: 'unknown' };
    expect(getCardPreview(card)).toBe('');
  });

  it('should truncate long text to 60 characters', () => {
    const longQuestion = 'A'.repeat(100);
    const card = { type: 'front-back', question: longQuestion };
    const preview = getCardPreview(card);
    expect(preview.length).toBe(63); // 60 chars + '...'
    expect(preview.endsWith('...')).toBe(true);
  });

  it('should not truncate text at exactly 60 characters', () => {
    const exactQuestion = 'A'.repeat(60);
    const card = { type: 'front-back', question: exactQuestion };
    const preview = getCardPreview(card);
    expect(preview.length).toBe(60);
    expect(preview.endsWith('...')).toBe(false);
  });

  it('should handle undefined fields gracefully', () => {
    const card = { type: 'front-back' };
    expect(getCardPreview(card)).toBeUndefined();
  });
});

describe('Theme x Card Type Matrix', () => {
  const themes = ['minimal', 'classic', 'high-contrast', 'calm'];
  const cardTypes = ['front-back', 'concept', 'cloze', 'image', 'image-occlusion', 'person'];

  themes.forEach(theme => {
    cardTypes.forEach(cardType => {
      it(`should return valid CSS for ${theme} theme with ${cardType} card`, () => {
        const css = getCardCSS(THEME_CSS, theme, cardType);
        expect(typeof css).toBe('string');
        expect(css.length).toBeGreaterThan(0);
      });
    });
  });
});

describe('Edge cases', () => {
  describe('getImageSource with malformed input', () => {
    it('should handle card with only irrelevant properties', () => {
      const card = { foo: 'bar', baz: 123 };
      expect(getImageSource(card)).toBe('');
      expect(getImageSource(card, 'photo')).toBe('');
    });
  });

  describe('getClozeNumbers with malformed cloze', () => {
    it('should handle nested braces', () => {
      const text = '{{c1::{{nested}}}}';
      // The regex won't match this correctly due to greedy matching
      const numbers = getClozeNumbers(text);
      expect(Array.isArray(numbers)).toBe(true);
    });
  });

  describe('getCardPreview with empty values', () => {
    it('should handle empty question', () => {
      const card = { type: 'front-back', question: '' };
      expect(getCardPreview(card)).toBe('');
    });

    it('should handle null values', () => {
      const card = { type: 'front-back', question: null };
      expect(getCardPreview(card)).toBeNull();
    });
  });
});
