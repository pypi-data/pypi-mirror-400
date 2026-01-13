/**
 * Rule: thin-entry-points
 *
 * Detect entry point files that contain substantial logic.
 * Entry points should be thin - just importing and delegating to Core/Shell.
 *
 * Detects:
 * - index.ts, main.ts, cli.ts with >10 non-import statements
 * - Complex logic in entry points (functions, classes, etc.)
 * - Entry points should export/re-export, not implement
 */
import type { Rule } from 'eslint';
export declare const thinEntryPoints: Rule.RuleModule;
export default thinEntryPoints;
//# sourceMappingURL=thin-entry-points.d.ts.map