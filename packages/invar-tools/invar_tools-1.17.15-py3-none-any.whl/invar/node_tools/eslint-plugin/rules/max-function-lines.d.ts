/**
 * Rule: max-function-lines
 *
 * Enforce maximum function length with layer-based limits.
 *
 * TypeScript layered limits (LX-10, Python × 1.3):
 * - Core: 65 lines (strict, pure logic)
 * - Shell: 130 lines (I/O operations)
 * - Tests: 260 lines (test functions)
 * - Default: 104 lines (other files)
 */
import type { Rule } from 'eslint';
export declare const maxFunctionLines: Rule.RuleModule;
export default maxFunctionLines;
//# sourceMappingURL=max-function-lines.d.ts.map