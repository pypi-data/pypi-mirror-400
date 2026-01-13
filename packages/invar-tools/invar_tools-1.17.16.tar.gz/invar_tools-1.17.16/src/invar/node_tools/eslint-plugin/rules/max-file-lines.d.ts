/**
 * Rule: max-file-lines
 *
 * Enforce maximum file length with layer-based limits.
 *
 * TypeScript layered limits (LX-10, Python × 1.3):
 * - Core: 650 lines (strict, pure logic)
 * - Shell: 910 lines (I/O operations)
 * - Tests: 1300 lines (test files)
 * - Default: 780 lines (other files)
 */
import type { Rule } from 'eslint';
export declare const maxFileLines: Rule.RuleModule;
export default maxFileLines;
//# sourceMappingURL=max-file-lines.d.ts.map