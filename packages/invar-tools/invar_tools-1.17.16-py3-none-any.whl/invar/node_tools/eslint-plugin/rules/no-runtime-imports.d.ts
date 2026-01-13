/**
 * Rule: no-runtime-imports
 *
 * Forbid imports inside functions (runtime imports).
 * All imports should be at module top-level for predictability and performance.
 *
 * Detects:
 * - require() calls inside functions
 * - dynamic import() calls inside functions
 */
import type { Rule } from 'eslint';
export declare const noRuntimeImports: Rule.RuleModule;
export default noRuntimeImports;
//# sourceMappingURL=no-runtime-imports.d.ts.map