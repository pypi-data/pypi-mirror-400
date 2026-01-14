/**
 * Unit tests for GitHub Markdown Alerts Extension
 */

import { processAlerts, postProcessAlerts } from '../utils';

describe('processAlerts', () => {
  describe('basic alert detection', () => {
    it('should convert NOTE alert syntax', () => {
      const input = `> [!NOTE]
> This is a note.`;
      const result = processAlerts(input);
      expect(result).toContain('<!--ALERT_START:NOTE-->');
      expect(result).toContain('This is a note.');
      expect(result).toContain('<!--ALERT_END:NOTE-->');
    });

    it('should convert TIP alert syntax', () => {
      const input = `> [!TIP]
> This is a tip.`;
      const result = processAlerts(input);
      expect(result).toContain('<!--ALERT_START:TIP-->');
      expect(result).toContain('This is a tip.');
      expect(result).toContain('<!--ALERT_END:TIP-->');
    });

    it('should convert IMPORTANT alert syntax', () => {
      const input = `> [!IMPORTANT]
> This is important.`;
      const result = processAlerts(input);
      expect(result).toContain('<!--ALERT_START:IMPORTANT-->');
      expect(result).toContain('This is important.');
      expect(result).toContain('<!--ALERT_END:IMPORTANT-->');
    });

    it('should convert WARNING alert syntax', () => {
      const input = `> [!WARNING]
> This is a warning.`;
      const result = processAlerts(input);
      expect(result).toContain('<!--ALERT_START:WARNING-->');
      expect(result).toContain('This is a warning.');
      expect(result).toContain('<!--ALERT_END:WARNING-->');
    });

    it('should convert CAUTION alert syntax', () => {
      const input = `> [!CAUTION]
> This is a caution.`;
      const result = processAlerts(input);
      expect(result).toContain('<!--ALERT_START:CAUTION-->');
      expect(result).toContain('This is a caution.');
      expect(result).toContain('<!--ALERT_END:CAUTION-->');
    });
  });

  describe('table handling', () => {
    it('should preserve table structure with consecutive rows', () => {
      const input = `> [!NOTE]
> | Header 1 | Header 2 |
> |----------|----------|
> | Cell 1   | Cell 2   |`;
      const result = processAlerts(input);
      // Tables require consecutive lines - single newlines between rows
      expect(result).toContain('| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |');
    });

    it('should not insert blank lines between table rows', () => {
      const input = `> [!WARNING]
> | A | B |
> |---|---|
> | 1 | 2 |
> | 3 | 4 |`;
      const result = processAlerts(input);
      // Verify no double newlines between table rows
      expect(result).not.toMatch(/\|[^\n]*\n\n\|/);
    });
  });

  describe('paragraph separation', () => {
    it('should preserve empty lines for paragraph separation', () => {
      const input = `> [!NOTE]
> First paragraph.
>
> Second paragraph.`;
      const result = processAlerts(input);
      // Empty line in original should create paragraph break
      expect(result).toContain('First paragraph.\n\nSecond paragraph.');
    });

    it('should handle multiple paragraphs', () => {
      const input = `> [!TIP]
> Paragraph one.
>
> Paragraph two.
>
> Paragraph three.`;
      const result = processAlerts(input);
      expect(result).toContain('Paragraph one.\n\nParagraph two.\n\nParagraph three.');
    });
  });

  describe('list handling', () => {
    it('should preserve bullet list structure', () => {
      const input = `> [!WARNING]
> - Item one
> - Item two
> - Item three`;
      const result = processAlerts(input);
      expect(result).toContain('- Item one\n- Item two\n- Item three');
    });

    it('should preserve numbered list structure', () => {
      const input = `> [!NOTE]
> 1. First item
> 2. Second item
> 3. Third item`;
      const result = processAlerts(input);
      expect(result).toContain('1. First item\n2. Second item\n3. Third item');
    });
  });

  describe('code block handling', () => {
    it('should not process alerts inside backtick code blocks', () => {
      const input = `\`\`\`markdown
> [!NOTE]
> This is inside a code block.
\`\`\``;
      const result = processAlerts(input);
      // Should not be converted to alert markers
      expect(result).not.toContain('<!--ALERT_START:NOTE-->');
      expect(result).toContain('> [!NOTE]');
    });

    it('should not process alerts inside tilde code blocks', () => {
      const input = `~~~markdown
> [!WARNING]
> This is inside a code block.
~~~`;
      const result = processAlerts(input);
      expect(result).not.toContain('<!--ALERT_START:WARNING-->');
      expect(result).toContain('> [!WARNING]');
    });

    it('should process alerts after code block ends', () => {
      const input = `\`\`\`
code
\`\`\`

> [!NOTE]
> This is after the code block.`;
      const result = processAlerts(input);
      expect(result).toContain('<!--ALERT_START:NOTE-->');
      expect(result).toContain('This is after the code block.');
    });
  });

  describe('edge cases', () => {
    it('should handle alert with no content', () => {
      const input = `> [!NOTE]`;
      const result = processAlerts(input);
      // No content lines, should not create alert
      expect(result).not.toContain('<!--ALERT_START');
    });

    it('should handle regular blockquotes (not alerts)', () => {
      const input = `> This is a regular blockquote.
> It should not be converted.`;
      const result = processAlerts(input);
      expect(result).not.toContain('<!--ALERT_START');
      expect(result).toContain('> This is a regular blockquote.');
    });

    it('should handle multiple alerts in same document', () => {
      const input = `> [!NOTE]
> First alert.

Some text between.

> [!WARNING]
> Second alert.`;
      const result = processAlerts(input);
      expect(result).toContain('<!--ALERT_START:NOTE-->');
      expect(result).toContain('<!--ALERT_END:NOTE-->');
      expect(result).toContain('<!--ALERT_START:WARNING-->');
      expect(result).toContain('<!--ALERT_END:WARNING-->');
    });
  });
});

describe('postProcessAlerts', () => {
  it('should wrap alert markers with styled div', () => {
    const input = '<!--ALERT_START:NOTE-->Content here<!--ALERT_END:NOTE-->';
    const result = postProcessAlerts(input, false);
    expect(result).toContain('class="markdown-alert markdown-alert-note"');
    expect(result).toContain('class="markdown-alert-title"');
    expect(result).toContain('Content here');
    expect(result).toContain('</div>');
  });

  it('should add background class when showBackgrounds is true', () => {
    const input = '<!--ALERT_START:WARNING-->Warning content<!--ALERT_END:WARNING-->';
    const result = postProcessAlerts(input, true);
    expect(result).toContain('markdown-alert-with-backgrounds');
  });

  it('should not add background class when showBackgrounds is false', () => {
    const input = '<!--ALERT_START:TIP-->Tip content<!--ALERT_END:TIP-->';
    const result = postProcessAlerts(input, false);
    expect(result).not.toContain('markdown-alert-with-backgrounds');
  });

  it('should include correct title for each alert type', () => {
    const types = ['NOTE', 'TIP', 'IMPORTANT', 'WARNING', 'CAUTION'];
    const titles = ['Note', 'Tip', 'Important', 'Warning', 'Caution'];

    types.forEach((type, index) => {
      const input = `<!--ALERT_START:${type}-->Content<!--ALERT_END:${type}-->`;
      const result = postProcessAlerts(input, false);
      expect(result).toContain(`>${titles[index]}</p>`);
    });
  });

  it('should include icon images for light and dark themes', () => {
    const input = '<!--ALERT_START:NOTE-->Content<!--ALERT_END:NOTE-->';
    const result = postProcessAlerts(input, false);
    expect(result).toContain('class="octicon octicon-info octicon-light');
    expect(result).toContain('class="octicon octicon-info octicon-dark');
    expect(result).toContain('data:image/svg+xml;base64');
  });
});
