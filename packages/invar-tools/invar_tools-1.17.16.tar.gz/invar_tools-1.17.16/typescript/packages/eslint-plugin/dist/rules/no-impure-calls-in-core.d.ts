/**
 * Rule: no-impure-calls-in-core
 *
 * Forbid Core functions calling Shell functions.
 * Core should be pure - no imports from shell/ directories.
 *
 * Detects:
 * - Imports from ../shell/ in core/ files
 * - Imports from shell/ in core/ files
 */
import type { Rule } from 'eslint';
export declare const noImpureCallsInCore: Rule.RuleModule;
export default noImpureCallsInCore;
//# sourceMappingURL=no-impure-calls-in-core.d.ts.map