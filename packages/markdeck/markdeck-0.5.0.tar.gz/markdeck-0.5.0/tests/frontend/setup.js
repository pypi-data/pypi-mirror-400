/**
 * Jest setup file for frontend tests
 * Sets up global polyfills required for jsdom
 */

import { TextEncoder, TextDecoder } from 'util';

// Polyfill TextEncoder/TextDecoder for jsdom
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
