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

// Export for consumption by other scripts in the test launcher environment
window.SharedCardPreview = SharedCardPreview;
