/**
 * Rule: shell-complexity
 *
 * Warn when Shell functions are too complex and should be split.
 * Shell functions should orchestrate I/O, not contain complex business logic.
 *
 * Detects:
 * - High cyclomatic complexity (many branches)
 * - Too many statements (>20 lines of logic)
 * - Multiple nested control structures
 */
import type { Rule } from 'eslint';
export declare const shellComplexity: Rule.RuleModule;
export default shellComplexity;
//# sourceMappingURL=shell-complexity.d.ts.map