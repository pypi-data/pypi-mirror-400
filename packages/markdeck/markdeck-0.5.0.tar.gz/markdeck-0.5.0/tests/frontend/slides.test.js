/**
 * Tests for SlideShow class from markdeck/static/slides.js
 *
 * These tests cover basic functionality:
 * - Navigation (next, previous, goTo)
 * - Keyboard shortcuts
 * - UI toggles (grid, help, fullscreen)
 *
 * @jest-environment jsdom
 */

// Import Jest globals for ES modules
import { jest, describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Read the slides.js file
const slidesJsPath = join(__dirname, '../../markdeck/static/slides.js');
const slidesJsCode = readFileSync(slidesJsPath, 'utf-8');

// Remove the DOMContentLoaded event listener at the bottom
const slidesJsWithoutAutoInit = slidesJsCode.replace(
  /document\.addEventListener\('DOMContentLoaded'.*$/s,
  ''
);

describe('SlideShow', () => {
  let slideshow;
  let SlideShow;

  beforeEach(() => {
    // Setup DOM with all required elements
    document.body.innerHTML = `
      <div id="loading"></div>
      <div id="presentation" class="hidden"></div>
      <div id="slide-container">
        <div id="slide-content"></div>
      </div>
      <div id="current-slide">1</div>
      <div id="total-slides">0</div>
      <div id="progress-fill" style="width: 0%"></div>
      <div id="grid-overlay" class="hidden">
        <div id="grid-container"></div>
        <button id="close-grid">Close</button>
      </div>
      <div id="help-overlay" class="hidden">
        <button id="close-help">Close</button>
      </div>
      <div id="error" class="hidden">
        <div id="error-message"></div>
      </div>
    `;

    // Mock global dependencies
    global.marked = {
      parse: jest.fn((content) => `<p>${content}</p>`),
      setOptions: jest.fn(),
      Renderer: function() {
        this.code = jest.fn();
      }
    };

    global.hljs = {
      highlightElement: jest.fn(),
      highlight: jest.fn((code) => ({ value: code })),
      highlightAuto: jest.fn((code) => ({ value: code })),
      getLanguage: jest.fn(() => true)
    };

    global.mermaid = {
      run: jest.fn()
    };

    global.renderMathInElement = jest.fn();

    // Mock fetch API
    global.fetch = jest.fn();

    // Mock WebSocket
    global.WebSocket = jest.fn();

    // Mock fullscreen API
    document.fullscreenElement = null;
    document.documentElement.requestFullscreen = jest.fn();
    document.exitFullscreen = jest.fn();

    // Execute the slides.js code to define SlideShow class
    // We need to eval it in a way that makes the class accessible
    // eslint-disable-next-line no-eval
    const result = eval(`(function() { ${slidesJsWithoutAutoInit}; return SlideShow; })()`);
    SlideShow = result;

    // Create a SlideShow instance manually (skip init to avoid async issues)
    slideshow = Object.create(SlideShow.prototype);
    slideshow.slides = [
      { content: '# Slide 1' },
      { content: '# Slide 2' },
      { content: '# Slide 3' }
    ];
    slideshow.currentSlideIndex = 0;
    slideshow.totalSlides = 3;
    slideshow.title = 'Test Presentation';
    slideshow.isFullscreen = false;

    // Set up elements reference
    slideshow.elements = {
      loading: document.getElementById('loading'),
      presentation: document.getElementById('presentation'),
      slideContainer: document.getElementById('slide-container'),
      slideContent: document.getElementById('slide-content'),
      currentSlide: document.getElementById('current-slide'),
      totalSlidesEl: document.getElementById('total-slides'),
      progressFill: document.getElementById('progress-fill'),
      gridOverlay: document.getElementById('grid-overlay'),
      gridContainer: document.getElementById('grid-container'),
      closeGrid: document.getElementById('close-grid'),
      helpOverlay: document.getElementById('help-overlay'),
      closeHelp: document.getElementById('close-help'),
      error: document.getElementById('error'),
      errorMessage: document.getElementById('error-message')
    };
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Navigation', () => {
    test('nextSlide advances to next slide', () => {
      slideshow.showSlide = jest.fn();
      slideshow.currentSlideIndex = 0;
      slideshow.totalSlides = 3;

      slideshow.nextSlide();

      expect(slideshow.showSlide).toHaveBeenCalledWith(1);
    });

    test('nextSlide does not advance past last slide', () => {
      slideshow.showSlide = jest.fn();
      slideshow.currentSlideIndex = 2;
      slideshow.totalSlides = 3;

      slideshow.nextSlide();

      expect(slideshow.showSlide).not.toHaveBeenCalled();
    });

    test('previousSlide goes to previous slide', () => {
      slideshow.showSlide = jest.fn();
      slideshow.currentSlideIndex = 2;

      slideshow.previousSlide();

      expect(slideshow.showSlide).toHaveBeenCalledWith(1);
    });

    test('previousSlide does not go before first slide', () => {
      slideshow.showSlide = jest.fn();
      slideshow.currentSlideIndex = 0;

      slideshow.previousSlide();

      expect(slideshow.showSlide).not.toHaveBeenCalled();
    });

    test('goToSlide jumps to specific slide', () => {
      slideshow.showSlide = jest.fn();

      slideshow.goToSlide(1);

      expect(slideshow.showSlide).toHaveBeenCalledWith(1);
    });
  });

  describe('Keyboard Handling', () => {
    beforeEach(() => {
      // Mock navigation methods
      slideshow.nextSlide = jest.fn();
      slideshow.previousSlide = jest.fn();
      slideshow.goToSlide = jest.fn();
      slideshow.toggleGrid = jest.fn();
      slideshow.toggleHelp = jest.fn();
      slideshow.toggleFullscreen = jest.fn();
      slideshow.exitFullscreen = jest.fn();
    });

    test('ArrowRight calls nextSlide', () => {
      const event = new KeyboardEvent('keydown', { key: 'ArrowRight' });
      slideshow.handleKeyPress(event);

      expect(slideshow.nextSlide).toHaveBeenCalled();
    });

    test('Space calls nextSlide', () => {
      const event = new KeyboardEvent('keydown', { key: ' ' });
      slideshow.handleKeyPress(event);

      expect(slideshow.nextSlide).toHaveBeenCalled();
    });

    test('PageDown calls nextSlide', () => {
      const event = new KeyboardEvent('keydown', { key: 'PageDown' });
      slideshow.handleKeyPress(event);

      expect(slideshow.nextSlide).toHaveBeenCalled();
    });

    test('ArrowLeft calls previousSlide', () => {
      const event = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
      slideshow.handleKeyPress(event);

      expect(slideshow.previousSlide).toHaveBeenCalled();
    });

    test('PageUp calls previousSlide', () => {
      const event = new KeyboardEvent('keydown', { key: 'PageUp' });
      slideshow.handleKeyPress(event);

      expect(slideshow.previousSlide).toHaveBeenCalled();
    });

    test('Home calls goToSlide(0)', () => {
      const event = new KeyboardEvent('keydown', { key: 'Home' });
      slideshow.handleKeyPress(event);

      expect(slideshow.goToSlide).toHaveBeenCalledWith(0);
    });

    test('End calls goToSlide with last slide index', () => {
      const event = new KeyboardEvent('keydown', { key: 'End' });
      slideshow.totalSlides = 3;
      slideshow.handleKeyPress(event);

      expect(slideshow.goToSlide).toHaveBeenCalledWith(2);
    });

    test('lowercase o calls toggleGrid', () => {
      const event = new KeyboardEvent('keydown', { key: 'o' });
      slideshow.handleKeyPress(event);

      expect(slideshow.toggleGrid).toHaveBeenCalled();
    });

    test('uppercase O calls toggleGrid', () => {
      const event = new KeyboardEvent('keydown', { key: 'O' });
      slideshow.handleKeyPress(event);

      expect(slideshow.toggleGrid).toHaveBeenCalled();
    });

    test('lowercase f calls toggleFullscreen', () => {
      const event = new KeyboardEvent('keydown', { key: 'f' });
      slideshow.handleKeyPress(event);

      expect(slideshow.toggleFullscreen).toHaveBeenCalled();
    });

    test('uppercase F calls toggleFullscreen', () => {
      const event = new KeyboardEvent('keydown', { key: 'F' });
      slideshow.handleKeyPress(event);

      expect(slideshow.toggleFullscreen).toHaveBeenCalled();
    });

    test('? calls toggleHelp', () => {
      const event = new KeyboardEvent('keydown', { key: '?' });
      slideshow.handleKeyPress(event);

      expect(slideshow.toggleHelp).toHaveBeenCalled();
    });

    test('Escape exits fullscreen when in fullscreen mode', () => {
      slideshow.isFullscreen = true;
      const event = new KeyboardEvent('keydown', { key: 'Escape' });
      slideshow.handleKeyPress(event);

      expect(slideshow.exitFullscreen).toHaveBeenCalled();
    });

    test('Escape closes grid when grid is open', () => {
      slideshow.isFullscreen = false;
      slideshow.elements.gridOverlay.classList.remove('hidden');
      const event = new KeyboardEvent('keydown', { key: 'Escape' });
      slideshow.handleKeyPress(event);

      expect(slideshow.toggleGrid).toHaveBeenCalled();
    });

    test('Escape closes help when help is open', () => {
      slideshow.isFullscreen = false;
      slideshow.elements.gridOverlay.classList.add('hidden');
      slideshow.elements.helpOverlay.classList.remove('hidden');
      const event = new KeyboardEvent('keydown', { key: 'Escape' });
      slideshow.handleKeyPress(event);

      expect(slideshow.toggleHelp).toHaveBeenCalled();
    });
  });

  describe('UI Toggles', () => {
    test('toggleHelp toggles help overlay visibility', () => {
      expect(slideshow.elements.helpOverlay.classList.contains('hidden')).toBe(true);

      slideshow.toggleHelp();
      expect(slideshow.elements.helpOverlay.classList.contains('hidden')).toBe(false);

      slideshow.toggleHelp();
      expect(slideshow.elements.helpOverlay.classList.contains('hidden')).toBe(true);
    });

    test('toggleGrid shows grid when hidden', () => {
      slideshow.buildGrid = jest.fn();
      slideshow.elements.gridOverlay.classList.add('hidden');

      slideshow.toggleGrid();

      expect(slideshow.buildGrid).toHaveBeenCalled();
      expect(slideshow.elements.gridOverlay.classList.contains('hidden')).toBe(false);
    });

    test('toggleGrid hides grid when visible', () => {
      slideshow.buildGrid = jest.fn();
      slideshow.elements.gridOverlay.classList.remove('hidden');

      slideshow.toggleGrid();

      expect(slideshow.buildGrid).not.toHaveBeenCalled();
      expect(slideshow.elements.gridOverlay.classList.contains('hidden')).toBe(true);
    });

    test('toggleFullscreen requests fullscreen when not in fullscreen', () => {
      document.fullscreenElement = null;

      slideshow.toggleFullscreen();

      expect(document.documentElement.requestFullscreen).toHaveBeenCalled();
      expect(slideshow.isFullscreen).toBe(true);
      expect(document.body.classList.contains('fullscreen')).toBe(true);
    });

    test('toggleFullscreen exits fullscreen when in fullscreen', () => {
      slideshow.exitFullscreen = jest.fn();
      document.fullscreenElement = document.documentElement;

      slideshow.toggleFullscreen();

      expect(slideshow.exitFullscreen).toHaveBeenCalled();
    });

    test('exitFullscreen calls document.exitFullscreen and updates state', () => {
      document.fullscreenElement = document.documentElement;
      slideshow.isFullscreen = true;
      document.body.classList.add('fullscreen');

      slideshow.exitFullscreen();

      expect(document.exitFullscreen).toHaveBeenCalled();
      expect(slideshow.isFullscreen).toBe(false);
      expect(document.body.classList.contains('fullscreen')).toBe(false);
    });
  });

  describe('Slide Display', () => {
    test('showSlide updates current slide index', () => {
      slideshow.notifySlideChange = jest.fn();

      slideshow.showSlide(1);

      expect(slideshow.currentSlideIndex).toBe(1);
    });

    test('showSlide does not change slide for out of bounds index', () => {
      slideshow.notifySlideChange = jest.fn();
      slideshow.currentSlideIndex = 1;

      slideshow.showSlide(-1);
      expect(slideshow.currentSlideIndex).toBe(1);

      slideshow.showSlide(10);
      expect(slideshow.currentSlideIndex).toBe(1);
    });

    test('showSlide renders markdown content', () => {
      slideshow.notifySlideChange = jest.fn();

      slideshow.showSlide(0);

      expect(global.marked.parse).toHaveBeenCalledWith('# Slide 1');
      expect(slideshow.elements.slideContent.innerHTML).toContain('Slide 1');
    });

    test('showSlide updates progress indicator', () => {
      slideshow.notifySlideChange = jest.fn();
      slideshow.totalSlides = 3;

      slideshow.showSlide(1);

      expect(slideshow.elements.currentSlide.textContent).toBe('2');
      expect(slideshow.elements.progressFill.style.width).toBe('66.66666666666666%');
    });
  });

  describe('Grid Building', () => {
    test('buildGrid creates grid items for all slides', () => {
      slideshow.buildGrid();

      const gridSlides = slideshow.elements.gridContainer.querySelectorAll('.grid-slide');
      expect(gridSlides.length).toBe(3);
    });

    test('buildGrid marks current slide', () => {
      slideshow.currentSlideIndex = 1;

      slideshow.buildGrid();

      const gridSlides = slideshow.elements.gridContainer.querySelectorAll('.grid-slide');
      expect(gridSlides[1].classList.contains('current')).toBe(true);
      expect(gridSlides[0].classList.contains('current')).toBe(false);
    });

    test('buildGrid renders slide numbers', () => {
      slideshow.buildGrid();

      const slideNumbers = slideshow.elements.gridContainer.querySelectorAll('.grid-slide-number');
      expect(slideNumbers[0].textContent).toBe('1');
      expect(slideNumbers[1].textContent).toBe('2');
      expect(slideNumbers[2].textContent).toBe('3');
    });

    test('buildGrid adds click handlers to navigate to slides', () => {
      slideshow.goToSlide = jest.fn();
      slideshow.toggleGrid = jest.fn();

      slideshow.buildGrid();

      const gridSlides = slideshow.elements.gridContainer.querySelectorAll('.grid-slide');
      gridSlides[1].click();

      expect(slideshow.goToSlide).toHaveBeenCalledWith(1);
      expect(slideshow.toggleGrid).toHaveBeenCalled();
    });
  });
});
